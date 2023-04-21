from rest_framework import status
from paynow import Paynow
from decouple import config
from .models import Payment
import logging

logger = logging.getLogger(__name__)


def initiate_payment(user, product, method, phone_number, email):
    # start payment
    # create payment in database
    db_payment = Payment.objects.create(
        user=user,
        product=product,
        method=method,
        mobile_wallet_number=phone_number,
        status=Payment.STATUS_INITIATED,
        amount=product.price
    )

    # create paynow instance for each payment
    paynow = Paynow(
            config("PAYNOW_INTEGRATION_ID"),
            config("PAYNOW_INTEGRATION_KEY"),
            config("PAYNOW_RETURN_URL"),
            config("PAYNOW_RESULT_URL")
        )

    # create payment
    payment = paynow.create_payment(db_payment.uuid, email)

    payment.items = []

    logger.debug("New trans for: %s", product.price)

    payment.add(product.product_name, product.price)

    response = paynow.send_mobile(payment, phone_number, method)

    if response.success:
        # Get the link to redirect the user to, then use it as you see fit
        instructions = response.instruction
        # Get the poll url (used to check the status of a transaction). You might want to save this in your DB
        db_payment.poll_url = response.poll_url
        db_payment.save()

        logger.debug("Paynow response: %s", str(response))

        return (instructions, status.HTTP_200_OK)

    else:
        # failed request
        logger.error("Paynow error: %s", str(response))

        db_payment.status = Payment.STATUS_REJECTED
        db_payment.save()

        return (response.error, status.HTTP_400_BAD_REQUEST)


def check_payment_status(payment):

    if not (payment.status == Payment.STATUS_PAID or payment.status == Payment.STATUS_CANCELLED or payment.status == Payment.STATUS_REJECTED or payment.status == Payment.STATUS_REFUNDED):

        paynow = Paynow(
            config("PAYNOW_INTEGRATION_ID"),
            config("PAYNOW_INTEGRATION_KEY"),
            config("PAYNOW_RETURN_URL"),
            config("PAYNOW_RESULT_URL")
        )

        response = paynow.check_transaction_status(payment.poll_url)

        if response.paid:

            payment.status = Payment.STATUS_PAID

        elif response.status.lower().strip() == "created":

            payment.status = Payment.STATUS_INITIATED

        elif response.status.lower().strip() == "sent":

            payment.status = Payment.STATUS_PENDING

        elif response.status.lower().strip() == "cancelled":

            payment.status = Payment.STATUS_CANCELLED

        elif response.status.lower().strip() == "refunded":

            payment.status = Payment.STATUS_REFUNDED

        elif response.status.lower().strip() == "delivered" or response.status.lower().strip() == "awaiting delivery":

            payment.status = Payment.STATUS_APPROVED

        else:

            payment.status = Payment.STATUS_PENDING

        payment.external_ref = response.paynow_reference
        payment.save()
