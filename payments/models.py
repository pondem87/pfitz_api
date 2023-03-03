from django.db import models
from django.contrib.auth import get_user_model
import uuid

# Create your models here.
class Payment(models.Model):
    STATUS_APPROVED = 'APPROVED'
    STATUS_REFUNDED = 'REFUNDED'
    STATUS_PENDING = 'PENDING'
    STATUS_INITIATED = 'INITIATED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_PAID = 'PAID'

    status_choices = [
        (STATUS_APPROVED, "Approved"),
        (STATUS_PENDING, "Pending"),
        (STATUS_REFUNDED, "Refunded"),
        (STATUS_INITIATED, 'Initiated'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_PAID, 'Paid')
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    product = models.ForeignKey("Product", on_delete=models.RESTRICT)
    external_ref = models.CharField(max_length=256, null=True, blank=True)
    method = models.CharField(max_length=50)
    mobile_wallet_number = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=10, choices=status_choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    poll_url = models.CharField(max_length=256, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

class Product(models.Model):
    APP_ZIMGPT = 'APP_ZIMGPT'

    app_choices = [
        (APP_ZIMGPT, "ZimGPT")
    ]

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    app_name = models.CharField(max_length=50)
    product_name = models.CharField(max_length=50)
    product_description = models.TextField()
    product_unit = models.CharField(max_length=20)
    units_offered = models.IntegerField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    active = models.BooleanField(default=True)
    discontinued_on = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)


