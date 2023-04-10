from rest_framework import status
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user_accounts.permissions import IsVerifiedUser
from rest_framework.settings import api_settings
from rest_framework.response import Response
from .serializers import ProfileSerializer, AnswersAPIRequestSerializer, AnswersListAPIRequestSerializer
from .models import Profile, APIRequest
from decouple import config
import logging

logger = logging.getLogger(__name__)

#get default bonus tokens
bonus_tokens = config('INITIAL_ONBOARDING_TOKENS', default=0, cast=int)


# Create your views here.
# Return user profile, create new profile if there isnt one
class GetProfileAPIView(generics.GenericAPIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)
    serializer_class = ProfileSerializer
    
    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = Profile(user=request.user, tokens_remaining=bonus_tokens)
            profile.save()
            logger.info("Created new profile for user: %s", request.user.phone_number)
        
        serializer = self.serializer_class(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AnswersRetrieveAPIView(generics.RetrieveAPIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)
    serializer_class = AnswersAPIRequestSerializer

    def get_queryset(self):
        return APIRequest.objects.filter(profile=self.request.user.profile, service=APIRequest.SERVICE_ANSWERS)
    
class AnswersListAPIView(generics.ListAPIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)
    serializer_class = AnswersListAPIRequestSerializer

    def get_queryset(self):
        return APIRequest.objects.filter(profile=self.request.user.profile, service=APIRequest.SERVICE_ANSWERS).order_by("-timestamp")