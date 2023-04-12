from __future__ import absolute_import, unicode_literals

from celery import shared_task
from pfitz_api.celery import app

import openai as oai
from openai.error import OpenAIError
from decouple import config
from django.contrib.auth import get_user_model
from user_accounts.random_str import get_random_str
from .models import Profile
from .wa_chat_state import WAChatState, WAChatStateSerializer
from .models import ClientCompletionResponse, APIRequest
from .serializers import UpstreamChatCompletionResponseSerializer, ClientCompletionResponseSerializer
from .util import num_tokens_from_string, subtract_used_tokens, base_chat_prompt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
import logging

logger = logging.getLogger(__name__)

oai.organization = config('OPENAI_ORG')
oai.api_key = config('OPENAI_API_KEY')

model = config('OPENAI_COMPLETION_MODEL')
model_max_tokens = config('OPENAI_COMPLETION_MODEL_MAX_TOKENS', cast=int)
model_encoder = config('OPENAI_COMPLETION_MODEL_ENCODER')
chat_completion_temp = config('OPENAI_CHAT_COMPLETION_TEMP', default=0.5, cast=float)

bonus_tokens = config('INITIAL_ONBOARDING_TOKENS', default=0, cast=int)

panctuation = [',', '.', '!', '?', ':', ';']

@app.task(name="process_whatsapp_state_input")
def process_whatsapp_state_input(user_num: str, name: str, wamid: str, message: str):

    new_password = None

    # check for profile and user and create if they do not exist for the number
    # if new user is generated then a random password is created for online login

    try:
        user_profile = Profile.objects.get(user__phone_number=user_num)
    except Profile.DoesNotExist:
        logger.debug("Creating new profile for %s", user_num)

        user = get_user_model().objects.create(
            phone_number=user_num,
            name="",
            is_active=True,
            verified=True
        )

        # generate random password
        new_password = get_random_str(8)
        user.set_password(new_password)
        user.save()

        user_profile = Profile(user=user, tokens_remaining=bonus_tokens)
        user_profile.save()

    # retrieve chat state data which maintains chat memory
    chat_state_data = user_profile.wa_chat_state

    logger.debug("Retrieved chat state data: %s", chat_state_data)

    state_machine = None

    # use chat state data if available to instantiate the state machine object for the request
    # if there is no state data i.e. for new users, create a new state machine object
    if chat_state_data:
        serializer = WAChatStateSerializer(data=chat_state_data)
        if serializer.is_valid(raise_exception=True):
            state_machine = serializer.save()
    else:
        state_machine = WAChatState(user_num=user_num, user_name=name, new_password=new_password)
        serializer = WAChatStateSerializer(state_machine)
        user_profile.wa_chat_state = serializer.data
        user_profile.save()

    logger.debug("Applying state transition: wamid: %s, input: %s", wamid, message)

    # pass the incoming message to the state machine to determine the required transition
    if state_machine:
        state_machine.transition(user_profile.user, wamid=wamid, input=message)
        logger.debug("State machine transition ran!!:-)")
        #save the state data
        serializer = WAChatStateSerializer(state_machine)
        user_profile = Profile.objects.get(user=user_profile.user)
        user_profile.wa_chat_state = serializer.data
        user_profile.save()
    else:
        logger.error("Failed to retrieve state object. user: %s", user_num)



@app.task(name="get_chat_completion_streamed")
def get_chat_completion_streamed(user_number, prompt_text, messages=None):

    logger.debug("get_chat_completion_streamed method called")

    # get user
    user = get_user(user_number)

    # check if tokens enough
    # get profile
    profile = user.profile

    # get channel layer
    ch_layer = get_channel_layer()
    event_type = "chat_completion"

    # base prompt
    base_prompt = base_chat_prompt
    
    logger.debug("get_chat_completion_streamed: generating prompt")

    if messages is not None:
        logger.debug("get_chat_completion_streamed: received messages = %s", messages)
        prompt = json.loads(messages)
        prompt.append({"role": "user", "content": prompt_text})
    else:
        prompt = base_prompt + [{"role": "user", "content": prompt_text}]

    prompt_tokens = num_tokens_from_string(str(prompt), model_encoder)

    if prompt_tokens > 4000:
        prompt = base_prompt + [{"role": "user", "content": prompt_text}]
        prompt_tokens = num_tokens_from_string(str(prompt), model_encoder)

    logger.debug("get_chat_completion_streamed: checking required tokens")
    required_tokens = model_max_tokens
    completion_max_tokens = model_max_tokens - (prompt_tokens + 100)

    if (profile.tokens_remaining < required_tokens):
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_ACCESS_VALIDATION, "You are low on tokens. You need at least {0} tokens".format(required_tokens))
        completion = ClientCompletionResponse(None, error)

        completion_serializer = ClientCompletionResponseSerializer(completion)
    
        # send response to channel
        send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

        return

    logger.debug("get_chat_completion: calling API")

    try:
        response = oai.ChatCompletion.create(
            model=model,
            messages=prompt,
            temperature=chat_completion_temp,
            max_tokens=completion_max_tokens,
            stream=True
        )

        logger.debug("Openai response object: %s", str(response))

        delta = {
            "prompt": json.dumps(prompt),
            "content": "",
            "prompt_tokens": prompt_tokens,
            "tokens_used": prompt_tokens
        }

        token_buf = []

        for chunk in response:
            serializer = UpstreamChatCompletionResponseSerializer(data=chunk)
            if serializer.is_valid():
                # create response object
                obj = serializer.save()

                logger.debug("Chunk! is {%s}", str(obj.choices[0].delta))

                if not delta.get("model", None):
                    delta["model"] = obj.model

                # subtract used tokens
                if obj.choices[0].delta:
                    if obj.choices[0].delta.content:
                        if obj.choices[0].delta.content in panctuation:
                            processed_content = "".join(token_buf) + obj.choices[0].delta.content
                            token_buf.clear()
                            # punctuation reached
                            delta["content"] = delta["content"] + processed_content
                            logger.debug("Content phrase: '%s'", processed_content)
                            used_tokens = num_tokens_from_string(processed_content, model_encoder)
                            delta["tokens_used"] = delta["tokens_used"] + used_tokens
                            delta["tokens_remaining"] = subtract_used_tokens(profile, used_tokens)

                            # prepare and send back response
                            answer = ClientCompletionResponse.Response(
                                " " + processed_content,
                                delta["prompt_tokens"],
                                delta["tokens_used"],
                                "")
                            completion = ClientCompletionResponse(answer, None)
                            completion_serializer = ClientCompletionResponseSerializer(completion)

                            # send response to channel
                            send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

                        else:
                            token_buf.append(obj.choices[0].delta.content)



                elif not obj.choices[0].delta:
                    # end of stream

                    # update prompt history
                    prompt.append({"role": "assistant", "content": delta["content"]})    
                    # prepare and send back response
                    answer = ClientCompletionResponse.Response(
                        "",
                        delta["prompt_tokens"],
                        delta["tokens_used"],
                        json.dumps(prompt))
                    completion = ClientCompletionResponse(answer, None)
                    completion_serializer = ClientCompletionResponseSerializer(completion)

                    # send response to channel
                    send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

            else:
                logger.error("Completions API response parsing failed: %s", str(response))
                logger.error("Validation errors: %s", str(serializer.errors))
                error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_INTERNAL_SERVER, "Failed to parse an upstream response.")
                completion = ClientCompletionResponse(None, error)
                completion_serializer = ClientCompletionResponseSerializer(completion)
            
                # send response to channel
                send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

        # save api request
        save_api_request(profile, APIRequest.SERVICE_CHAT, delta)
        return
        
    except OpenAIError as error:
        logger.error("Completions API failed: %s", error.user_message)
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_API_ERROR, "An upstream service failed.")
        completion = ClientCompletionResponse(None, error)
        completion_serializer = ClientCompletionResponseSerializer(completion)

        # send response to channel
        send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

        return

@app.task(name="get_answer_completion_streamed")
def get_answer_completion_streamed(user_number, prompt_text, citations, words):

    logger.debug("get_answer_completion_streamed method called")

    # get user
    user = get_user(user_number)

    # check if tokens enough
    # get profile
    profile = user.profile

    # get channel layer
    ch_layer = get_channel_layer()
    event_type = "answer_completion"

    logger.debug("get_answer_completion_streamed: generating prompt")

    # make prompt
    prompt = []

    if citations:
        prompt.append({"role": "user", "content": "May you answer an academic question, discussing different schools of thought and citing their sources indicated with a number in brackets which corresponds to the harvard style reference list at the bottom."})
    else:
        prompt.append({"role": "user", "content": "May you answer an academic question, discussing different schools of thought."})
    

    prompt.append({"role": "assistant", "content": "Is there a limit on the length of the answer?"})
    prompt.append({"role": "user", "content": "Yes. The answer should be about " + str(words) + " words."})
    prompt.append({"role": "assistant", "content": "Understood, may I have the question."})
    prompt.append({"role": "user", "content": "The question is: " + prompt_text})

    prompt_tokens = num_tokens_from_string(str(prompt), model_encoder)

    logger.debug("get_answer_completion_streamed: checking required tokens")
    required_tokens = model_max_tokens
    completion_max_tokens = model_max_tokens - (prompt_tokens + 100)

    if (profile.tokens_remaining < required_tokens):
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_ACCESS_VALIDATION, "You are low on tokens. You need at least {0} tokens".format(required_tokens))
        completion = ClientCompletionResponse(None, error)

        completion_serializer = ClientCompletionResponseSerializer(completion)
    
        # send response to channel
        send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

        return

    logger.debug("get_answer_completion: calling API")

    try:
        response = oai.ChatCompletion.create(
            model=model,
            messages=prompt,
            temperature=chat_completion_temp,
            max_tokens=completion_max_tokens,
            stream=True
        )

        logger.debug("Openai response object: %s", str(response))

        delta = {
            "prompt": prompt_text,
            "content": "",
            "prompt_tokens": prompt_tokens,
            "tokens_used": prompt_tokens
        }

        token_buf = []

        for chunk in response:
            serializer = UpstreamChatCompletionResponseSerializer(data=chunk)
            if serializer.is_valid():
                # create response object
                obj = serializer.save()

                logger.debug("Chunk! is {%s}", str(obj.choices[0].delta))

                if not delta.get("model", None):
                    delta["model"] = obj.model

                # subtract used tokens
                if obj.choices[0].delta:
                    if obj.choices[0].delta.content:
                        if obj.choices[0].delta.content in panctuation:
                            processed_content = "".join(token_buf) + obj.choices[0].delta.content
                            token_buf.clear()
                            # punctuation reached
                            delta["content"] = delta["content"] + processed_content
                            logger.debug("Content phrase: '%s'", processed_content)
                            used_tokens = num_tokens_from_string(processed_content, model_encoder)
                            delta["tokens_used"] = delta["tokens_used"] + used_tokens
                            delta["tokens_remaining"] = subtract_used_tokens(profile, used_tokens)

                            # prepare and send back response
                            answer = ClientCompletionResponse.Response(
                                " " + processed_content,
                                delta["prompt_tokens"],
                                delta["tokens_used"],
                                delta["prompt"])
                            completion = ClientCompletionResponse(answer, None)
                            completion_serializer = ClientCompletionResponseSerializer(completion)

                            # send response to channel
                            send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

                        else:
                            token_buf.append(obj.choices[0].delta.content)



                elif not obj.choices[0].delta:
                    # end of stream

                    # update prompt history
                    prompt.append({"role": "assistant", "content": delta["content"]})    
                    # prepare and send back response
                    answer = ClientCompletionResponse.Response(
                        "",
                        delta["prompt_tokens"],
                        delta["tokens_used"],
                        delta["prompt"])
                    completion = ClientCompletionResponse(answer, None)
                    completion_serializer = ClientCompletionResponseSerializer(completion)

                    # send response to channel
                    send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

            else:
                logger.error("Completions API response parsing failed: %s", str(response))
                logger.error("Validation errors: %s", str(serializer.errors))
                error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_INTERNAL_SERVER, "Failed to parse an upstream response.")
                completion = ClientCompletionResponse(None, error)
                completion_serializer = ClientCompletionResponseSerializer(completion)
            
                # send response to channel
                send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

        # save api request
        save_api_request(profile, APIRequest.SERVICE_ANSWERS, delta)
        return
        
    except OpenAIError as error:
        logger.error("Completions API failed: %s", error.user_message)
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_API_ERROR, "An upstream service failed.")
        completion = ClientCompletionResponse(None, error)
        completion_serializer = ClientCompletionResponseSerializer(completion)

        # send response to channel
        send_to_channel(ch_layer, user.phone_number, event_type, completion_serializer.data)

        return

def send_to_channel(ch_layer, group, type, data):
    async_to_sync(ch_layer.group_send)(
                    group,
                    {
                        "type": type,
                        "data": json.dumps(data)
                    }
                )

def save_api_request(profile, service, delta):
    APIRequest.objects.create(
                    service = service,
                    prompt = delta["prompt"],
                    prompt_tokens = delta["prompt_tokens"],
                    tokens_used = delta["tokens_used"],
                    tokens_remaining = delta["tokens_remaining"],
                    ai_model = delta["model"],
                    response_text = delta["content"],
                    profile = profile)
    
def get_user(phone_number):
    return get_user_model().objects.get(phone_number=phone_number)
