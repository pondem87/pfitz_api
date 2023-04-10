from django.urls import path
from . import views

urlpatterns = [
    path('getprofile/', views.GetProfileAPIView.as_view()),
    path('answers/<int:pk>', views.AnswersRetrieveAPIView.as_view()),
    path('answers/', views.AnswersListAPIView.as_view())
]