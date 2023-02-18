from django.db import models
from django.contrib.auth import get_user_model
from payments.models import Payment, Product

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


class TokenReload(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.OneToOneField(Product, on_delete=models.RESTRICT)
    payment = models.OneToOneField(Payment, on_delete=models.RESTRICT)
    timestamp = models.DateTimeField(auto_now_add=True)