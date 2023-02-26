from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.WebhookAPIView.as_view()),
]