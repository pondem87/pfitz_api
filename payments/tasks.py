from __future__ import absolute_import, unicode_literals
from .models import Payment
from .pay_func import check_payment_status

import logging

logger = logging.getLogger(__name__)

from celery import shared_task

@shared_task
def print_stuff():
    print("The payments shared task is running now")

@shared_task
def update_payment_status(payment_id):
    # get payment to check
    try:
        payment = Payment.objects.get(uuid=payment_id)

        # check and update status
        check_payment_status(payment)

    except Payment.DoesNotExist as error:
        logger.error("Could not find payment with id: ", str(payment_id))
