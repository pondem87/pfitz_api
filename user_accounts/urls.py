from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.CreateUserAPIView.as_view()),
    path('update/', views.UpdateUserAPIView.as_view()),
    path('signin/', views.LoginAPIView.as_view()),
    path('getuser/', views.GetUserAPIView.as_view()),
    path('verify/', views.VerifyAccountAPIView.as_view()),
    path('request-pwd-reset/', views.RequestPasswordResetAPIView.as_view()),
    path('apply-pwd-reset/', views.ApplyPasswordResetAPIVIew.as_view()),
    path('', include('knox.urls')), #implements logout/ and logoutall/
]