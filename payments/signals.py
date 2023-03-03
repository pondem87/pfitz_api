from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import Payment
from zimgpt.models import TokenReload
import datetime
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Payment)
def payment_post_save_handler(sender, instance: Payment, created, *args, **kwargs):
    if not created:
        # check for token reload and create if not there already
        try:
            reload: TokenReload = TokenReload.objects.get(payment=instance)
        except TokenReload.DoesNotExist:
            logger.debug("Creating new reload for payment: %s", instance.uuid)
            reload: TokenReload = TokenReload.objects.create(
                profile = instance.user.profile,
                product = instance.product,
                payment = instance
            )
        
        if instance.status == Payment.STATUS_APPROVED or instance.status == Payment.STATUS_PAID:
            # load token if not loaded
            if not reload.loaded:
                #load
                #get profile and add tokens from product
                profile = reload.profile
                profile.tokens_remaining += reload.product.units_offered
                profile.save()
                reload.loaded = True
                reload.load_timestamp = datetime.datetime.utcnow()
                reload.save()
                logger.info("Tokens loaded: user: %s; tokens: %s;", profile.user.phone_number, reload.product.units_offered)
