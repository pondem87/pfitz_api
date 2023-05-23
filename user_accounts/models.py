from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# Create your models here.
class PfitzUserManager(BaseUserManager):
    """
    Custom user model manager where phone number is the unique identifier
    for authentication instead of username.
    """

    def create_user(self, phone_number, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not phone_number:
            raise ValueError("Phone number must be set")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        logger.info("Created new user", {'phone_number': user.phone_number })
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        """
        Create and save a SuperUser with the given phone number and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(phone_number, password, **extra_fields)


class PfitzUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField("phone number", max_length=15, unique=True)
    name = models.CharField(max_length=256)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = PfitzUserManager()

    def __str__(self):
        return self.phone_number


class VerificationCode(models.Model):
    PURPOSE_ACCOUNT_VERIFICATION = 'ACC_VERIF'
    PURPOSE_PASSWORD_RESET = 'PWD_RESET'

    purpose_choices = [
        (PURPOSE_ACCOUNT_VERIFICATION, 'Account verification'),
        (PURPOSE_PASSWORD_RESET, 'Password reset')
    ]

    user = models.ForeignKey(PfitzUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, null=False)
    purpose = models.CharField(max_length=10, choices=purpose_choices)
    created = models.DateTimeField(auto_now_add=True)