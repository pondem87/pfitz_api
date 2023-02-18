from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .aux_func import get_chat_completion

# Create your views here.
@api_view(["POST",])
def chat(request):
    try:
        print(request.data)
        text = request.data["text"]
        if request.data["history"]:
            history = request.data["history"]
        else:
            history = None
        response = get_chat_completion(text, history)
        data = {
            "response": {
                "text": response["text"],
                "history": response["history"],
                "tokens_used": response["tokens_used"],
                "token_remaining": None
            },
            "error": None
        }
        return Response(data, status=status.HTTP_200_OK)
    except:
        return Response({
            "response": None,
            "error": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)