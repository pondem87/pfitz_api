from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

# Register your models here.
from .models import PfitzUser, VerificationCode


class MyUserAdmin(UserAdmin):

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("date_joined",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "password1", "password2"),
            },
        ),
    )

    list_display = ("phone_number", "name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("phone_number", "name")
    ordering = ("phone_number",)

admin.site.register(PfitzUser, MyUserAdmin)
admin.site.register(VerificationCode)