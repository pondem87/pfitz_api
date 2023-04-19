from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import VerificationCode
from zimgpt.models import Profile
import re
from decouple import config
from rest_framework import serializers

bonus_tokens = config('INITIAL_ONBOARDING_TOKENS', default=0, cast=int)

### auxilliary functions
def validate_phone_number(phone_number):
    if not re.match("^263\d+$", phone_number):
        raise serializers.ValidationError("Expecting phone number starting with 263")
    return phone_number

def validate_password(password):
    if len(password) < 8:
        raise serializers.ValidationError("Password must be 8 characters or more")
    if not re.match(".*[A-Z]+.*", password):
        raise serializers.ValidationError("Password must contain at least 1 uppercase letter.")
    if not re.match(".*[a-z]+.*", password):
        raise serializers.ValidationError("Password must contain at least 1 lowercase letter.")
    if not re.match(".*\d+.*", password):
        raise serializers.ValidationError("Password must contain at least 1 numeric character.")
    if re.match(".*\s+.*", password):
        raise serializers.ValidationError("Password cannot contain blank spaces.")
    if not re.match("^\w+$", password):
        raise serializers.ValidationError("Password cannot contain special characters. Allows a-z, A-Z, 0-9 and _ only")
    return password

def validate_name(name):
    if not re.match("^\w+$", name):
        raise serializers.ValidationError("Name cannot contain special characters and spaces. Allows a-z, A-Z, 0-9 and _ only")
    return name

### serializer classes
class PfitzUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'name', 'verified')
        extra_kwargs = {
            "phone_number": {"validators" : [validate_phone_number]}
        }

class CreatePfitzUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'name', 'password')
        extra_kwargs = {
            "password" : {"write_only" : True, "validators" : [validate_password]},
            "phone_number": {"validators" : [validate_phone_number]},
            "name" : {"validators": [validate_name]}
        }
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        if get_user_model().objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("User with this number already registered.")
        return super().validate(attrs)

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        profile = Profile(user=user, tokens_remaining=bonus_tokens)
        profile.save()
        return user

class UpdatePfitzUserSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'name', 'password', 'old_password')
        extra_kwargs = {
            "phone_number" : {"read_only" : True },
            "password" : {"write_only" : True, "validators" : [validate_password]},
            "name" : {"validators": [validate_name]}
        }
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        old_password = validated_data.pop('old_password', None)
        if password:
            if not old_password:
                raise serializers.ValidationError("Old password required for password update")
            user = authenticate(self.context.get('request'), phone_number=instance.phone_number, password=old_password)
            if user:
                instance.set_password(password)
            else:
                raise serializers.ValidationError("Old password verification failed")
        return super().update(instance, validated_data)

class PfitzLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
    
    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        if not get_user_model().objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Incorrect authentication credentials")
        
        user = authenticate(self.context.get('request'), phone_number=phone_number, password=password)

        if not user:
            raise serializers.ValidationError("Incorrect authentication credentials")
        
        attrs['user'] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    phone_number = serializers.CharField(validators=[validate_phone_number])
    password = serializers.CharField(style={'input': 'password'}, trim_whitespace=False, validators=[validate_password])
    code = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        code = attrs.get('code')

        if not get_user_model().objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Incorect phone number and code combination")
        
        v_code = VerificationCode.objects.filter(user__phone_number=phone_number, code=code, purpose=VerificationCode.PURPOSE_PASSWORD_RESET).first()
        if not v_code:
            raise serializers.ValidationError("Invalid phone number and code combination")
        
        v_code.delete()
        return attrs

class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = '__all__'