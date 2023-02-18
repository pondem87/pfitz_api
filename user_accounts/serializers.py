from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import VerificationCode

from rest_framework import serializers

### auxilliary functions

### serializer classes
class PfitzUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'name')

class CreatePfitzUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'name', 'password')
        extra_kwargs = {
            "password" : {"write_only" : True }
        }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class UpdatePfitzUserSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('phone_number', 'name', 'password', 'old_password')
        extra_kwargs = {
            "phone_number" : {"read_only" : True },
            "password" : {"write_only" : True }
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
    phone_number = serializers.CharField()
    password = serializers.CharField(style={'input': 'password'}, trim_whitespace=False)
    code = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')
        code = attrs.get('code')

        if not get_user_model().objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError("Incorect phone number and code combination")
        
        if not VerificationCode.objects.filter(user__phone_number=phone_number, code=code).exists():
            raise serializers.ValidationError("Invalid phone number and code combination")
        
        return attrs

class VerificationCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationCode
        fields = '__all__'