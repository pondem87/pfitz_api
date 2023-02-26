import openai as oai
from openai.error import OpenAIError
from decouple import config
import logging
from .models import ClientCompletionResponse, APIRequest
from .serializers import UpstreamCompletionResponseSerializer
import json

logger = logging.getLogger(__name__)

oai.organization = config('OPENAI_ORG')
oai.api_key = config('OPENAI_API_KEY')

def get_chat_completion(user, prompt_text, prompt_history=None):

    # check if tokens enough
    # get profile
    profile = user.profile
    chat_max_tokens = profile.chat_max_tokens

    if (profile.tokens_remaining < chat_max_tokens):
        error = ClientCompletionResponse.Error(ClientCompletionResponse.ERROR_ACCESS_VALIDATION, "You are low on tokens. You need at least {0} tokens".format(chat_max_tokens))
        return ClientCompletionResponse(None, error)

    start_sequence = "\nAI:"
    restart_sequence = "\nHuman: "

    if prompt_history:
        prompt = prompt_history + restart_sequence + prompt_text + start_sequence
    else:
        prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?" + restart_sequence + prompt_text + start_sequence

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


def subtract_used_tokens(profile, used_tokens) -> int:
    profile.tokens_remaining = profile.tokens_remaining - used_tokens
    profile.save()
    return profile.tokens_remaining