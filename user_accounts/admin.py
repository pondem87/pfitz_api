from django.contrib import admin
from django.contrib.auth.models import Group, Permission

# Register your models here.
from .models import PfitzUser, VerificationCode

admin.site.register([PfitzUser, VerificationCode,])

admin.site.register(Permission)