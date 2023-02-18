from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    tokens_remaining = models.IntegerField(default=0, null=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.phone_number

class APIRequest(models.Model):
    prompt = models.TextField()
    prompt_tokens = models.IntegerField()
    tokens_used = models.IntegerField()
    tokens_remaining = models.IntegerField()
    ai_model = models.CharField(max_length=256)
    response_text = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class TokenVoucher(models.Model):
    number_of_tokens = models.IntegerField()
    payment_confirmed = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)