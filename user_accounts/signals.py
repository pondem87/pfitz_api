from .models import PfitzUser, VerificationCode
from .serializers import VerificationCodeSerializer
from django.dispatch import receiver
from django.db.models.signals import post_save
from .serializers import VerificationCodeSerializer
from .whatsapp import send_template
from .random_str import get_random_str
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PfitzUser)
def pfitzuser_post_save_handler(sender, instance, created, *args, **kwargs):
    if created:
        serializer = VerificationCodeSerializer(data={
            'user': instance.id,
            'code': get_random_str(6),
            'purpose': VerificationCode.PURPOSE_ACCOUNT_VERIFICATION
        })
        if serializer.is_valid():
            serializer.save()
        else:
            print("v_code fail", serializer.errors)
            logger.error("Verification code not generated", serializer.errors)


@receiver(post_save, sender=VerificationCode)
def v_code_post_save_hanlder(sender, instance, created, *args, **kwargs):
    print("v code post save running")

    params = [
        {
            "type": "text",
            "text": instance.code
        },
    ]

    if instance.purpose == VerificationCode.PURPOSE_ACCOUNT_VERIFICATION:
        template = "user_verification_code"
    elif instance.purpose == VerificationCode.PURPOSE_PASSWORD_RESET:
        template = "password_reset_code"
    else:
        template = "unknown"
    response = send_template(instance.user.phone_number, template, params, "en_GB")
    logger.info("Attempt to send verification code", response)
