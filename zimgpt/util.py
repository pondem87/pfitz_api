import tiktoken
import re

base_chat_prompt = [
        {"role": "system", "content": "You are an intelligent, truthful and helpful AI assistant."},
        {"role": "user", "content": "Are you able to answer any question I have."},
        {"role": "assistant", "content": "I will try to the best of my ability and admit openly if I do know the answer."},
    ]

def subtract_used_tokens(profile, used_tokens) -> int:
    profile.tokens_remaining = int(profile.tokens_remaining) - int(used_tokens)
    profile.save()
    return profile.tokens_remaining

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
