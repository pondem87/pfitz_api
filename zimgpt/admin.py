from django.contrib import admin

# Register your models here.
from .models import Profile, APIRequest, TokenVoucher

admin.site.register([
    Profile,
    APIRequest,
    TokenVoucher
])
