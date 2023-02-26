from django.contrib import admin
from .models import SentMessages, ReceivedMessages

# Register your models here.
admin.site.register([SentMessages, ReceivedMessages])