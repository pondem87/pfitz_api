from rest_framework import status
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# returns 200 OK for health checks
class HealthCheckView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        return Response(None, status=status.HTTP_200_OK)