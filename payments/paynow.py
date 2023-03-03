from paynow import Paynow
from decouple import config

paynow = Paynow(
            config("PAYNOW_INTEGRATION_ID"),
            config("PAYNOW_INTEGRATION_KEY"),
            config("PAYNOW_RETURN_URL"),
            config("PAYNOW_RESULT_URL")
        )