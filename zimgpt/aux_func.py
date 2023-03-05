import openai as oai
from openai.error import OpenAIError
from decouple import config
import logging
from .models import ClientCompletionResponse, APIRequest
from .serializers import UpstreamCompletionResponseSerializer
import tiktoken

logger = logging.getLogger(__name__)

oai.organization = config('OPENAI_ORG')
oai.api_key = config('OPENAI_API_KEY')

def get_chat_completion(user, prompt_text, prompt_history=None):

    # check if tokens enough
    # get profile
    profile = user.profile
    chat_max_tokens = profile.chat_max_tokens

    start_sequence = "\nAI:"
    restart_sequence = "\nHuman: "

    if prompt_history:
        prompt = prompt_history + restart_sequence + prompt_text + start_sequence
    else:
        prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?" + restart_sequence + prompt_text + start_sequence


    required_tokens = num_tokens_from_string(prompt) + chat_max_tokens

    if (profile.tokens_remaining < required_tokens):
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_ACCESS_VALIDATION, "You are low on tokens. You need at least {0} tokens".format(required_tokens))
        return ClientCompletionResponse(None, error)

    try:
        response = oai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.8,
        max_tokens=chat_max_tokens,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
        )

        logger.debug("Openai response object: %s", str(response))

        serializer = UpstreamCompletionResponseSerializer(data=response)
        if serializer.is_valid():
            # create response object
            obj = serializer.save()

            # subtract used tokens
            tokens_remaining = subtract_used_tokens(profile, obj.usage.total_tokens)

            # save api request
            APIRequest.objects.create(
                service = APIRequest.SERVICE_CHAT,
                prompt = prompt,
                prompt_tokens = obj.usage.prompt_tokens,
                tokens_used = obj.usage.total_tokens,
                tokens_remaining = tokens_remaining,
                ai_model = obj.model,
                response_text = obj.choices[0].text,
                profile = profile
            )

            # prepare and send back response
            answer = ClientCompletionResponse.Response(
                obj.choices[0].text,
                obj.usage.prompt_tokens,
                obj.usage.total_tokens,
                prompt + obj.choices[0].text)
            return ClientCompletionResponse(answer, None)
        else:
            logger.error("Completions API response parsing failed: %s", str(response))
            logger.error("Validation errors: %s", str(serializer.errors))
            error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_INTERNAL_SERVER, "Failed to parse an upstream response.")
            return ClientCompletionResponse(None, error)
    except OpenAIError as error:
        logger.error("Completions API failed: %s", error.user_message)
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_API_ERROR, "An upstream service failed.")
        return ClientCompletionResponse(None, error)
    

def get_answer_completion(user, prompt_text, citations, words):

    citations = " including in-line numbered citations to be listed at the bottom," if citations else ","
    prompt = "Answer the following question like a scholar" + citations + " in about " + str(words) + " words:\n\n" + prompt_text

    # check if tokens enough
    # get profile
    profile = user.profile

    logger.debug("Called get_answer_completion. prompt= %s", prompt)

    approx_completion_tokens = int(int(words)/0.75)

    required_tokens = num_tokens_from_string(prompt) + approx_completion_tokens

    if (profile.tokens_remaining < required_tokens):
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_ACCESS_VALIDATION, "You are low on tokens. You need at least {0} tokens".format(required_tokens))
        return ClientCompletionResponse(None, error)

    try:
        response = oai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.4,
        max_tokens=4000 - num_tokens_from_string(prompt),
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=["STOP"]
        )

        logger.debug("Openai response object: %s", str(response))

        serializer = UpstreamCompletionResponseSerializer(data=response)
        if serializer.is_valid():
            # create response object
            obj = serializer.save()

            # subtract used tokens
            tokens_remaining = subtract_used_tokens(profile, obj.usage.total_tokens)

            # save api request
            APIRequest.objects.create(
                service = APIRequest.SERVICE_ANSWERS,
                prompt = prompt_text,
                prompt_tokens = obj.usage.prompt_tokens,
                tokens_used = obj.usage.total_tokens,
                tokens_remaining = tokens_remaining,
                ai_model = obj.model,
                response_text = obj.choices[0].text,
                profile = profile
            )

            # prepare and send back response
            answer = ClientCompletionResponse.Response(
                obj.choices[0].text,
                obj.usage.prompt_tokens,
                obj.usage.total_tokens,
                prompt_text)
            return ClientCompletionResponse(answer, None)
        else:
            logger.error("Completions API response parsing failed: %s", str(response))
            logger.error("Validation errors: %s", str(serializer.errors))
            error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_INTERNAL_SERVER, "Failed to parse an upstream response.")
            return ClientCompletionResponse(None, error)
    except OpenAIError as error:
        logger.error("Completions API failed: %s", error.user_message)
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_API_ERROR, "An upstream service failed.")
        return ClientCompletionResponse(None, error)
    

def subtract_used_tokens(profile, used_tokens) -> int:
    profile.tokens_remaining = profile.tokens_remaining - used_tokens
    profile.save()
    return profile.tokens_remaining

def num_tokens_from_string(string: str, encoding_name: str = "p50k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens