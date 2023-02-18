from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from .permissions import IsVerifiedUser
from django.contrib.auth import get_user_model
from .serializers import CreatePfitzUserSerializer, UpdatePfitzUserSerializer, PfitzLoginSerializer, VerificationCodeSerializer, PasswordResetSerializer
from django.contrib.auth import get_user_model
from knox import views as knox_views
from django.contrib.auth import login
from .models import VerificationCode
from .random_str import get_random_str
import logging

logger = logging.getLogger(__name__)

# Create your views here.
class CreateUserAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = CreatePfitzUserSerializer
    permission_classes = (AllowAny,)


class UpdateUserAPIView(generics.GenericAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UpdatePfitzUserSerializer
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class LoginAPIView(knox_views.LoginView):
    permission_classes = (AllowAny,)
    serializer_class = PfitzLoginSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            login(request, user)
            response = super().post(request, format=None)
            return Response(response.data, status=status.HTTP_200_OK)


class VerifyAccountAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # check if field 'code' is present
        input_code = request.data.get("code", None)
        if not input_code:
            return Response({"code": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        # check if verification code object is available
        v_code = VerificationCode.objects.filter(user=request.user, purpose=VerificationCode.PURPOSE_ACCOUNT_VERIFICATION).first()
        if v_code:
            # compare the codes
            if v_code.code == input_code:
                request.user.verified = True
                request.user.save()
                logger.info("New account activation.", {"user": request.user})
                v_code.delete()
                user_serializer = PfitzLoginSerializer(instance=request.user)
                return Response({"user": user_serializer.data}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"non_field_errors": ["Incorrect verification code"]}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"non_field_errors": ["No verification code found"]}, status=status.HTTP_404_NOT_FOUND)
        

class RequestPasswordResetAPIView(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        phone_number = request.data.get("phone_number", None)
        # check if field 'phone_number' is present
        if not phone_number:
            return Response({"phone_number": "This field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # check if user exists
        user = get_user_model().objects.filter(phone_number=phone_number).first()

        if not user:
            return Response({"non_field_errors": ["No such user."]}, status=status.HTTP_404_NOT_FOUND)
        
        # check old code and delete if found
        v_code = VerificationCode.objects.filter(user=user, purpose=VerificationCode.PURPOSE_PASSWORD_RESET).first()
        if v_code:
            v_code.delete()
        
        # create code
        code_serializer = VerificationCodeSerializer(data={
            'user': user.id,
            'code': get_random_str(6),
            'purpose': VerificationCode.PURPOSE_PASSWORD_RESET
        })

        if code_serializer.is_valid(raise_exception=True):
            code_serializer.save()
            return Response({"detail": "code was sent to your provided whatsapp number"}, status=status.HTTP_202_ACCEPTED)


class ApplyPasswordResetAPIVIew(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        password_serializer = PasswordResetSerializer(data=request.data)
        if password_serializer.is_valid(raise_exception=True):
            user = get_user_model().objects.filter(phone_number=password_serializer.validated_data.get('phone_number')).get()
            user.set_password(password_serializer.validated_data.get('password'))
            user.save()
            return Response({"detail": "password reset successful"}, status=status.HTTP_202_ACCEPTED)

