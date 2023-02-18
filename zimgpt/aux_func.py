import openai as oai
from decouple import config

oai.organization = config('OPENAI_ORG')
oai.api_key = config('OPENAI_API_KEY')


def get_chat_completion(text, history=None):

    start_sequence = "\nAI:"
    restart_sequence = "\nHuman: "

    if history:
        prompt = history + restart_sequence + text + start_sequence
    else:
        prompt = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?" + restart_sequence + text + start_sequence

    print(prompt)

    response = oai.Completion.create(
    model="text-davinci-003",
    prompt=prompt,
    temperature=0.9,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.6,
    stop=[" Human:", " AI:"]
    )

    print(response)

    return {
        "text" : response["choices"][0]["text"],
        "history" : prompt + response["choices"][0]["text"],
        "tokens_used" : response["usage"]["total_tokens"]
    }