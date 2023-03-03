from rest_framework import serializers
from .models import Product, Payment

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class InitiatePaymentSerializer(serializers.Serializer):
    product_uuid = serializers.UUIDField()
    phone_number = serializers.CharField()
    email = serializers.EmailField()
    method = serializers.CharField()

    def validate(self, attrs):
        product_uuid = attrs.get("product_uuid")
        try:
            product = Product.objects.get(uuid=product_uuid, active=True)
            attrs["product"] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        return super().validate(attrs)