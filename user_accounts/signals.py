from .models import PfitzUser, VerificationCode
from .serializers import VerificationCodeSerializer
from django.dispatch import receiver
from django.db.models.signals import post_save
from .serializers import VerificationCodeSerializer
from whatsapp.aux_func import send_template
from .random_str import get_random_str
from decouple import config
import logging

logger = logging.getLogger(__name__)

wa_temp_lang = config('WA_TEMPLATE_DEFAULT_LANG')

# signal runs after saving user and allows sending of verification code
@receiver(post_save, sender=PfitzUser)
def pfitzuser_post_save_handler(sender, instance, created, *args, **kwargs):
    # runs if new user and not verified
    # new users on mobile are automatically verified
    if created and not instance.verified:
        serializer = VerificationCodeSerializer(data={
            'user': instance.id,
            'code': get_random_str(6),
            'purpose': VerificationCode.PURPOSE_ACCOUNT_VERIFICATION
        })
        if serializer.is_valid():
            serializer.save()
        else:
            print("v_code fail", serializer.errors)
            logger.error("Verification code not generated. Serializer errors: %s", str(serializer.errors))

# signal runs after saving of verification code and allows sending of code via whatsapp
# used for user verification and password reset
@receiver(post_save, sender=VerificationCode)
def v_code_post_save_hanlder(sender, instance, created, *args, **kwargs):

    logger.debug("Running verification_code post save.")

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
    
    logger.debug("Calling send_template : %s", template)
    send_template(instance.user.phone_number, template, params, wa_temp_lang)
