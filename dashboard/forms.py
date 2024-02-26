from django.forms import ModelForm, TextInput
from django.forms.models import inlineformset_factory
from payments.models import Payment
from zimgpt.models import Profile
from django.contrib.auth import get_user_model


class UpdateProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = [
            'tokens_remaining',
            'chat_max_tokens',
            'stop_promotions',
        ]

        widgets = {
            'tokens_remaining': TextInput(attrs={"class":"form-control"}),
            'chat_max_tokens': TextInput(attrs={"class":"form-control"}),
        }

class UpdateUserForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = [
            'is_staff',
            'is_active',
            'verified',
        ]


UserFormset = inlineformset_factory(get_user_model(), Profile, UpdateProfileForm, can_delete=False)


class UpdatePaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['status']