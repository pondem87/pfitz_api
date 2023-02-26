from rest_framework import status
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user_accounts.permissions import IsVerifiedUser
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProfileSerializer, ClientCompletionResponseSerializer
from .models import Profile, ClientCompletionResponse
from decouple import config
from .aux_func import get_chat_completion
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

class ChatAPIView(generics.GenericAPIView):
    authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    permission_classes = (IsAuthenticated, IsVerifiedUser)

    def post(self, request):
        if request.data.get("prompt_text", None):
            prompt_text = request.data["prompt_text"]
        else:
            return Response({
                "prompt_text": "This field is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("prompt_history", None):
            if request.data["prompt_history"]:
                prompt_history = request.data["prompt_history"]
            else:
                prompt_history = None
        else:
            prompt_history = None
        
        response = get_chat_completion(request.user, prompt_text, prompt_history)

        logger.debug("response.isOkay evaluates to: %s", response.isOkay())

        if not response.isOkay():
            if response.error.source == ClientCompletionResponse.ERROR_ACCESS_VALIDATION:
                res_status = status.HTTP_402_PAYMENT_REQUIRED
            else:
                res_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            res_status = status.HTTP_200_OK

        serializer = ClientCompletionResponseSerializer(response)
        return Response(serializer.data, status=res_status)