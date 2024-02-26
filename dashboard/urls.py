from django.urls import path
from . import views

urlpatterns = [
    path('', views.DashboardView.as_view(), name="dashboard.home"),
    path('users/', views.UsersView.as_view(), name="dashboard.users"),
    path('user/<int:pk>/', views.UserUpdateView.as_view(), name="dashboard.user"),
    path('payments/', views.PaymentsView.as_view(), name="dashboard.payments"),
    path('payment/<int:pk>/', views.PaymentUpdateView.as_view(), name="dashboard.payment"),
]