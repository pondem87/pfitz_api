from django.urls import path
from . import views

urlpatterns = [
    path('getprofile/', views.GetProfileAPIView.as_view()),
    path('chat/', views.ChatAPIView.as_view()),
]