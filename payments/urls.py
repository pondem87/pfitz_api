from django.urls import path
from . import views

urlpatterns = [
     path('status/', views.UpdatePaymentAPIView.as_view()),
    path('', views.PaymentListAPIView.as_view()),
    path('pay/', views.InitiatePaymentAPIView.as_view()),
    path('<str:uuid>/', views.GetPaymentAPIView.as_view()),
    path('products/zimgpt/', views.ZimGPTListProductsAPIView.as_view()),
]