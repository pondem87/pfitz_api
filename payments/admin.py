from django.contrib import admin

# Register your models here.
from .models import Payment, Product

admin.site.register([
    Product,
    Payment,
])
