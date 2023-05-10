from rest_framework import status
from paynow import Paynow
from decouple import config
from .models import Payment
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from whatsapp.aux_func import send_template
from django.utils import timezone
from datetime import timedelta
import json
import logging

logger = logging.getLogger(__name__)

currency = config("BASE_CURRENCY")

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

    try:
        # Lets try this transaction so we can catch any exception that have been slipping away

        response = paynow.send_mobile(payment, phone_number, method)

        if response.success:
            # Get instructions !!This value may not exist. Another paynow bug
            default_instructions = "A prompt should appear on your phone to complete the payment. The service provider did not provide more instructions on how to initiate the transaction if there is no prompt."
            instructions = getattr(response, "instruction", default_instructions)
            # Get the poll url (used to check the status of a transaction). You might want to save this in your DB
            db_payment.poll_url = response.poll_url
            db_payment.save()

            logger.debug("Paynow response: %s", str(response))

            # trigger payment checking schedule
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=3,
                period=IntervalSchedule.MINUTES,
            )

            PeriodicTask.objects.create(
                interval=schedule,                  # we created this above.
                name=str(db_payment.uuid),          # simply describes this periodic task.
                task='payments.tasks.update_payment_status',  # name of task.
                args=json.dumps([str(db_payment.uuid),]),
                expires=timezone.now() + timedelta(minutes=18)
            )


            return (instructions, status.HTTP_200_OK)

        else:
            # failed request
            logger.error("Paynow error: %s", str(response))

            db_payment.status = Payment.STATUS_REJECTED
            db_payment.save()

            return (response.error, status.HTTP_400_BAD_REQUEST)
        
    except Exception as error:
        # lets reject the transaction and log the exception
        logger.error("Error while initiating a transaction: %s", str(error))

        db_payment.status = Payment.STATUS_REJECTED
        db_payment.save()

        return ("Transaction could not be initiated", status.HTTP_500_INTERNAL_SERVER_ERROR)


def check_payment_status(payment: Payment):

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

        # send notification
        params = [
            {
                "type": "text",
                "text": "{amount}{currency}".format(amount=str(payment.amount), currency=currency)
            },
            {
                "type": "text",
                "text": "{units} {unit}s".format(units=payment.product.units_offered, unit=payment.product.product_unit)
            }]

        if payment.status in [Payment.STATUS_APPROVED, Payment.STATUS_PAID]:
            logger.info("Notification of payment update: sucess")

            params.append({
                "type": "text",
                "text": "*successful*"
            })

        else:

            params.append({
                "type": "text",
                "text": "*declined*"
            })
        
        send_template(payment.user.phone_number, "payment_notification", params=params)

        
        
            
