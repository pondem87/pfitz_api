from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .serializers import ProductSerializer, PaymentSerializer, InitiatePaymentSerializer
from .models import Product, Payment
from .paynow import paynow
from rest_framework.permissions import IsAuthenticated, AllowAny
from user_accounts.permissions import IsVerifiedUser
from rest_framework.settings import api_settings
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class UpdatePaymentAPIView(generics.GenericAPIView):
    
    def post(self, request):

        logger.debug("API initiated payment status update: %s", str(request.data))

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
    queryset = Product.objects.filter(app_name=Product.APP_ZIMGPT, active=True)
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
            #create payment in database
            db_payment = Payment.objects.create(
                user = request.user,
                product = product,
                method = method,
                mobile_wallet_number = phone_number,
                status = Payment.STATUS_INITIATED,
                amount = product.price
            )

            payment = paynow.create_payment(db_payment.uuid, email)

            logger.debug("New trans for: %s", product.price)

            payment.add(product.product_name, product.price)

            response = paynow.send_mobile(payment, phone_number, method)

            if response.success:
                # Get the link to redirect the user to, then use it as you see fit
                instructions = response.instructions
                # Get the poll url (used to check the status of a transaction). You might want to save this in your DB
                db_payment.poll_url = response.poll_url
                db_payment.save()

                logger.debug("Paynow response: %s", str(response))
                
                return Response(instructions, status=status.HTTP_200_OK)

            else:
                # failed request
                logger.error("Paynow error: %s", str(response))

                db_payment.status = Payment.STATUS_REJECTED
                db_payment.save()

                return Response(response.error, status=status.HTTP_400_BAD_REQUEST)


class GetPaymentAPIView(generics.GenericAPIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)
    
    def get(self, request, uuid):
        # Get payment form db
        
        payment: Payment = get_object_or_404(Payment.objects.filter(user=request.user), uuid=uuid)

        if not (payment.status == Payment.STATUS_PAID or payment.status == Payment.STATUS_CANCELLED or payment.status == Payment.STATUS_REJECTED or payment.status == Payment.STATUS_REFUNDED):

            response = paynow.check_transaction_status(payment.poll_url)

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

        # return object
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_200_OK)