import tiktoken
import re
from .models import Profile
from pfitz_api.celery import celery_app
import msgpack

import logging

logger = logging.getLogger(__name__)

base_chat_prompt = [
        {"role": "system", "content": "You are an intelligent, truthful and helpful AI assistant."},
        {"role": "user", "content": "Are you able to answer any question I have."},
        {"role": "assistant", "content": "I will try to the best of my ability and admit openly if I do know the answer."},
    ]

def subtract_used_tokens(profile, used_tokens) -> int:
    logger.debug("Subtracting used tokens from profile:%s. Profile tokens=%s; Used tokens=%s", str(profile), str(profile.tokens_remaining), str(used_tokens))
    tokens_remaining = profile.tokens_remaining - used_tokens
    profile = Profile.objects.get(user=profile.user)
    profile.tokens_remaining = tokens_remaining
    profile.save()
    return tokens_remaining

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def is_single_special_char(string):
    # Remove \n and \r from the string
    string = string.replace('\n', '').replace('\r', '')
    # Use a regular expression to match the string against the criteria
    if re.match(r'^[^\w]$', string):
        return True
    else:
        return False

# This function allows celery tasks to pass messages to websockets going directly through rabbitmq
# This is possible because channels and celery are both using rabbitmq
def publish_message_to_group(message, group: str) -> None:
    with celery_app.producer_pool.acquire(block=True) as producer:
        producer.publish(
            msgpack.packb({
              "__asgi_group__": group,
              **message,
            }),
            exchange="groups",  # groups_exchange
            content_encoding="binary",
            routing_key=group,
            retry=False,  # Channel Layer at-most once semantics
        )