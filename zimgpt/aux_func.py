import openai as oai
from openai.error import OpenAIError
from decouple import config
import logging
from .models import ClientCompletionResponse, APIRequest, Profile
from .serializers import UpstreamChatCompletionResponseSerializer
from .util import subtract_used_tokens, num_tokens_from_string, base_chat_prompt
import uuid
import json

logger = logging.getLogger(__name__)

oai.organization = config('OPENAI_ORG')
oai.api_key = config('OPENAI_API_KEY')

model = config('OPENAI_COMPLETION_MODEL')
model_max_tokens = config('OPENAI_COMPLETION_MODEL_MAX_TOKENS', cast=int)
model_encoder = config('OPENAI_COMPLETION_MODEL_ENCODER')
chat_completion_temp = config('OPENAI_CHAT_COMPLETION_TEMP', default=0.5, cast=float)

ref_reward_tokens = config('REFERRAL_REWARD_TOKENS')

# FUNCTIONS

def get_chat_completion(user, prompt_text, messages=None):

    logger.debug("get_chat_completion method called")
    # check if tokens enough
    # get profile
    profile = user.profile

    base_prompt = base_chat_prompt

    if messages is not None:
        prompt = json.loads(messages)
        prompt.append({"role": "user", "content": prompt_text})
    else:
        prompt = base_prompt + [{"role": "user", "content": prompt_text}]

    prompt_tokens = num_tokens_from_string(str(prompt), model_encoder)

    if prompt_tokens > 4000:
        prompt = base_prompt + [{"role": "user", "content": prompt_text}]
        prompt_tokens = num_tokens_from_string(str(prompt), model_encoder)

    required_tokens = model_max_tokens

    if (profile.tokens_remaining < required_tokens):
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_ACCESS_VALIDATION,
                                               "You are low on tokens. You need at least {0} tokens".format(required_tokens))
        return ClientCompletionResponse(None, error)

    completion_max_tokens = model_max_tokens - (prompt_tokens + 100)
    logger.debug("get_chat_completion: calling API")

    try:
        response = oai.ChatCompletion.create(
            model=model,
            messages=prompt,
            temperature=chat_completion_temp,
            max_tokens=completion_max_tokens
        )

        logger.debug("Openai response object: %s", str(response))

        serializer = UpstreamChatCompletionResponseSerializer(data=response)
        if serializer.is_valid():
            # create response object
            obj = serializer.save()

            # subtract used tokens
            tokens_remaining = subtract_used_tokens(profile, obj.usage.total_tokens)

            # save api request
            APIRequest.objects.create(
                service=APIRequest.SERVICE_CHAT,
                prompt=json.dumps(prompt),
                prompt_tokens=obj.usage.prompt_tokens,
                tokens_used=obj.usage.total_tokens,
                tokens_remaining=tokens_remaining,
                ai_model=obj.model,
                response_text=obj.choices[0].message.content,
                profile=profile
            )

            # prepare and send back response
            prompt.append({"role": obj.choices[0].message.role, "content": obj.choices[0].message.content})

            answer = ClientCompletionResponse.Response(
                obj.choices[0].message.content,
                obj.usage.prompt_tokens,
                obj.usage.total_tokens,
                json.dumps(prompt))
            return ClientCompletionResponse(answer, None)
        else:
            logger.error("Completions API response parsing failed: %s", str(response))
            logger.error("Validation errors: %s", str(serializer.errors))
            error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_INTERNAL_SERVER, "Failed to parse an upstream response.")
            return ClientCompletionResponse(None, error)
    except OpenAIError as error:
        logger.error("Completions API failed: %s", error.user_message)
        error = ClientCompletionResponse.Error(
            ClientCompletionResponse.ERROR_API_ERROR, "An upstream service failed.")
        return ClientCompletionResponse(None, error)




def get_completion(user, prompt_text):

    logger.debug("get_completion method called")
    # check if tokens enough
    # get profile
    profile = user.profile

    prompt = [{"role": "user", "content": prompt_text}]
    
    required_tokens = model_max_tokens

    if (profile.tokens_remaining < required_tokens):
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_ACCESS_VALIDATION, "You are low on tokens. You need at least {0} tokens".format(required_tokens))
        return ClientCompletionResponse(None, error)

    completion_max_tokens = model_max_tokens - (num_tokens_from_string(str(prompt)) + 100)
    logger.debug("get_completion: calling API")

    try:
        response = oai.ChatCompletion.create(
            model=model,
            messages=prompt,
            temperature=chat_completion_temp,
            max_tokens=completion_max_tokens
        )

        logger.debug("Openai response object: %s", str(response))

        serializer = UpstreamChatCompletionResponseSerializer(data=response)
        if serializer.is_valid():
            # create response object
            obj = serializer.save()

            # subtract used tokens
            tokens_remaining = subtract_used_tokens(profile, obj.usage.total_tokens)

            # save api request
            APIRequest.objects.create(
                service=APIRequest.SERVICE_CHAT,
                prompt=json.dumps(prompt),
                prompt_tokens=obj.usage.prompt_tokens,
                tokens_used=obj.usage.total_tokens,
                tokens_remaining=tokens_remaining,
                ai_model=obj.model,
                response_text=obj.choices[0].message.content,
                profile=profile
            )

            # prepare and send back response
            answer = ClientCompletionResponse.Response(
                obj.choices[0].message.content,
                obj.usage.prompt_tokens,
                obj.usage.total_tokens,
                json.dumps(prompt))
            return ClientCompletionResponse(answer, None)
        else:
            logger.error(
                "Completions API response parsing failed: %s", str(response))
            logger.error("Validation errors: %s", str(serializer.errors))
            error = ClientCompletionResponse.Error(
                ClientCompletionResponse.ERROR_INTERNAL_SERVER, "Failed to parse an upstream response.")
            return ClientCompletionResponse(None, error)
    except OpenAIError as error:
        logger.error("Completions API failed: %s", error.user_message)
        error = ClientCompletionResponse.Error(
            ClientCompletionResponse.ERROR_API_ERROR, "An upstream service failed.")
        return ClientCompletionResponse(None, error)


def process_ref_code(ref):

    ref_uuid = is_valid_uuid(ref)

    if not ref_uuid:
        return
    
    try:
        profile = Profile.objects.get(ref=ref_uuid)
        profile.tokens_remaining += ref_reward_tokens
        profile.save()
    except Profile.DoesNotExist:
        logger.info("Referral code failed: Code=%s", ref_uuid)


def is_valid_uuid(uuid_str):
    try:
        uuid_obj = uuid.UUID(uuid_str)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_str