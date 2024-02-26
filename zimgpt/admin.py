from django.contrib import admin

# Register your models here.
from .models import Profile, APIRequest, TokenReload, DailyMetrics

admin.site.register([
    Profile,
    APIRequest,
    TokenReload,
    DailyMetrics
])
