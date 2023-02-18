from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Payment(models.Model):
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_PENDING = 'PENDING'

    status_choices = [
        (STATUS_APPROVED, "Approved"),
        (STATUS_PENDING, "Pending"),
        (STATUS_REJECTED, "Rejected")
    ]

    user = models.ForeignKey(user=get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=status_choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    method = models.CharField(max_length=50)
    poll_url = models.CharField(max_length=256)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField()


