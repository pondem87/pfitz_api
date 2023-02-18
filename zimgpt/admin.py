from django.contrib import admin

# Register your models here.
from .models import Profile, APIRequest, TokenReload

admin.site.register([
    Profile,
    APIRequest,
    TokenReload
])
