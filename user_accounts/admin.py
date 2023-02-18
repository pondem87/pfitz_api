from django.contrib import admin

# Register your models here.
from .models import PfitzUser, VerificationCode

admin.site.register([PfitzUser, VerificationCode,])
