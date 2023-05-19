from typing import Any, Dict
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, ListView, UpdateView
from .forms import UpdateUserForm, UserFormset, UpdatePaymentForm
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from zimgpt.models import DailyMetrics, Profile
from .serializers import DailyMetricsSerializer
from django.db.models import Q
from decimal import Decimal
from zimgpt.models import Profile
from payments.models import Payment
from django.contrib.auth.mixins import PermissionRequiredMixin
import json
import datetime
import logging

logger = logging.getLogger(__name__)

staff_login_url = "/admin/login/"

# Create your views here.
@method_decorator(staff_member_required, name="dispatch")
class DashboardView(PermissionRequiredMixin, TemplateView):

    permission_required = 'zimgpt.view_dailymetrics'
    login_url = staff_login_url

    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        date_format = "%Y-%m-%d"

        # check query params
        start = self.request.GET.get("from", None)
        end = self.request.GET.get("to", None)

        if start is not None:
            try:
                start_date = datetime.datetime.strptime(start, date_format)
            except ValueError:
                start_date = datetime.date.today() - datetime.timedelta(days=15)
        else:
            start_date = datetime.date.today() - datetime.timedelta(days=15)

        if end is not None:
            try:
                end_date = datetime.datetime.strptime(end, date_format)
            except ValueError:
                end_date = datetime.date.today()
        else:
            end_date = datetime.date.today()

        # get the objects
        metrics = DailyMetrics.objects.filter(Q(date__gte=start_date) & Q(date__lte=end_date)).order_by("date")
        serializer = DailyMetricsSerializer(metrics, many=True)
        context["metrics"] = json.dumps(serializer.data)
        context["metrics_py"] = serializer.data
        context["total_daily_token_purchases"] = sum(metric["daily_token_purchases"] for metric in serializer.data)
        context["total_daily_token_purchase_amount"] = sum(Decimal(metric["daily_token_purchase_amount"]) for metric in serializer.data)
        context["total_daily_api_requests"] = sum(metric["daily_api_requests"] for metric in serializer.data)
        context["total_daily_token_usage"] = sum(metric["daily_token_usage"] for metric in serializer.data)

        context["live_user_total"] = Profile.objects.all().count()

        logger.debug("metrics objects: %s", context["metrics"])

        return context


@method_decorator(staff_member_required, name="dispatch")
class UsersView(PermissionRequiredMixin, ListView):

    permission_required = 'zimgpt.view_profile'
    login_url = staff_login_url

    model = Profile
    template_name = "dashboard/users.html"
    context_object_name = "profiles"
    paginate_by = 50

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.GET.get("phone_number", None) is not None:
            context["phone_number"] = self.request.GET.get("phone_number", None).strip()

        return context

    def get_queryset(self):
        if self.request.GET.get("phone_number", None) is not None:
            phone_number = self.request.GET.get("phone_number", None).strip()
            return Profile.objects.filter(user__phone_number__icontains=phone_number)
        else:
            return super().get_queryset()


@method_decorator(staff_member_required, name="dispatch")
class UserUpdateView(PermissionRequiredMixin ,UpdateView):

    permission_required = ('zimgpt.change_profile', 'user_accounts.change_pfitzuser')
    login_url = staff_login_url    

    model = get_user_model()
    template_name = "dashboard/update-user.html"
    form_class = UpdateUserForm
    success_url = "/dashboard/users/"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["next"] = self.request.POST.get("next")
            context["profile"] = UserFormset(self.request.POST, instance=self.object)
        else:
            # set return url
            context["next"] = self.request.META.get('HTTP_REFERER')
            context["phone_number"] = self.object.phone_number
            context["name"] = self.object.name
            context["last_engagement"] = self.object.profile.last_engagement
            context["date_joined"] = self.object.date_joined
            context["ref"] = self.object.profile.ref
            context["wa_chat_state"] = json.dumps(self.object.profile.wa_chat_state)
            context["profile"] = UserFormset(instance=self.object)
        return context
    
    def get_success_url(self) -> str:
        
        context = self.get_context_data()

        if context["next"] is not None:
            # Redirect to the previous URL if available
            return context["next"]
        else:
            # Fallback to a default URL if the previous URL is not available
            return super().get_success_url()
    
    
    def form_valid(self, form):
        context = self.get_context_data()
        user = context["profile"]
        self.object = form.save()
        if user.is_valid():
            user.instance = self.object
            user.save()
        return super().form_valid(form)


@method_decorator(staff_member_required, name="dispatch")
class PaymentsView(PermissionRequiredMixin, ListView):

    permission_required = 'payments.view_payment'
    login_url = staff_login_url

    model = Payment
    template_name = "dashboard/payments.html"
    context_object_name = "payments"
    paginate_by = 50

    def get_queryset(self):    
        if self.request.GET.get("phone_number", None) is not None:
            phone_number = self.request.GET.get("phone_number", None).strip()
            return Payment.objects.filter(user__phone_number__icontains=phone_number).order_by('-created')
        else:
            return Payment.objects.all().order_by('-created')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.GET.get("phone_number", None) is not None:
            context["phone_number"] = self.request.GET.get("phone_number", None).strip()

        return context
    

@method_decorator(staff_member_required, name="dispatch")
class PaymentUpdateView(PermissionRequiredMixin, UpdateView):

    permission_required = 'payments.change_payment'
    login_url = staff_login_url

    model = Payment
    form_class = UpdatePaymentForm
    success_url = "/dashboard/payments/"
    template_name = "dashboard/update-payment.html"

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["next"] = self.request.POST.get("next")
        else:
            context["next"] = self.request.META.get("HTTP_REFERER")
            context["phone_number"] = self.object.user.phone_number
            context["name"] = self.object.user.name
            context["ref"] = self.object.user.profile.ref
            context["uuid"] = self.object.uuid
            context["uuid"] = self.object.uuid
            context["mobile_wallet_number"] = self.object.mobile_wallet_number
            context["poll_url"] = self.object.poll_url
            context["created"] = self.object.created
            context["updated"] = self.object.updated
            context["method"] = self.object.method

        return context
    

    def get_success_url(self) -> str:
        context = self.get_context_data()

        if context["next"] is not None:
            # Redirect to the previous URL if available
            return context["next"]
        else:
            # Fallback to a default URL if the previous URL is not available
            return super().get_success_url()