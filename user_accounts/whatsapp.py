from decouple import config

import requests

debug = config('DEBUG', default=True, cast=bool)
whatsapp_num_id = config('WHATSAPP_TEST_NUMBER_ID') if debug else config('WHATSAPP_NUMBER_ID')
whatapp_bus_id = config('WHATSAPP_TEST_BUSINESS_ID') if debug else config('WHATSAPP_BUSINESS_ID')
whatsapp_access_token = config('WHATSAPP_ACCESS_TOKEN')
messages_url = "https://graph.facebook.com/v16.0/{num_id}/messages".format(num_id=whatsapp_num_id)
auth_header = "Bearer " + whatsapp_access_token


def send_template(dest, template, params, lang="en_US"):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": dest,
        "type": "template",
        "template": {
            "name": template,
            "language": {
                "code": lang
            },
            "components": [
                {
                    "type": "body",
                    "parameters": params
                }
            ]
        }
    }
    headers = {
        "authorization": auth_header,
    }

    response = requests.post(messages_url, headers=headers, json=data)
    return response.json()
