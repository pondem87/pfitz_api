from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import ProductSerializer, PaymentSerializer, InitiatePaymentSerializer
from .models import Product, Payment
from .paynow import paynow
from rest_framework.permissions import IsAuthenticated, AllowAny
from user_accounts.permissions import IsVerifiedUser
from rest_framework.settings import api_settings
from .pay_func import initiate_payment, check_payment_status
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class UpdatePaymentAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):

        logger.info("Upstream API initiated payment status update: %s", str(request.data))

        if request.data.get("pollurl", None):

            response = paynow.check_transaction_status(request.data.get("pollurl"))

            payment: Payment = get_object_or_404(Payment, uuid=response.reference)
            

            if response.paid:
                
                payment.status = Payment.STATUS_PAID

            elif response.status.lower().strip() == "created":

                payment.status = Payment.STATUS_INITIATED

            elif response.status.lower().strip() == "sent":

                payment.status = Payment.STATUS_PENDING

            elif response.status.lower().strip() == "cancelled":

                payment.status = Payment.STATUS_CANCELLED

            elif response.status.lower().strip() == "refunded":

                payment.status = Payment.STATUS_REFUNDED
            
            elif response.status.lower().strip() == "delivered" or response.status.lower().strip() == "awaiting delivery":
                
                payment.status = Payment.STATUS_APPROVED
            
            else:

                payment.status = Payment.STATUS_PENDING

            payment.external_ref = response.paynow_reference
            payment.save()

            return Response(None, status=status.HTTP_200_OK)

            
        else:
            logger.error("Payment update from API failed.")
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ZimGPTListProductsAPIView(generics.ListAPIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)
    serializer_class = ProductSerializer
    queryset = Product.objects.filter(app_name=Product.APP_ZIMGPT, active=True).order_by('price')
    pagination_class = None

class PaymentListAPIView(generics.ListAPIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created')
    
class InitiatePaymentAPIView(generics.GenericAPIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)

    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):

            email: str = serializer.validated_data.get("email")
            phone_number: str = serializer.validated_data.get("phone_number")
            method: str = serializer.validated_data.get("method")
            product: Product = serializer.validated_data.get("product")

            logger.info("Validated payment request: Number=%s, Method=%s, Product=%s",
                        phone_number, method, product.uuid)
            
            #start payment
            response = initiate_payment(request.user, product, method, phone_number, email)

            return Response(response[0], status=response[1])


class GetPaymentAPIView(generics.GenericAPIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)
    
    def get(self, request, uuid):
        # Get payment form db
        
        payment: Payment = get_object_or_404(Payment.objects.filter(user=request.user), uuid=uuid)

        check_payment_status(payment)

        # return object
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)