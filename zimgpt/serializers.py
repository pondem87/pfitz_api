from rest_framework import serializers
from .models import Profile, UpstreamCompletionResponse, UpstreamChatCompletionResponse, APIRequest

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'

class AnswersAPIRequestSerializer(serializers.ModelSerializer):
    generated_text = serializers.CharField(source="response_text")
    prompt_history = serializers.CharField(source="prompt")
    used_tokens = serializers.IntegerField(source="tokens_used")

    class Meta:
        model = APIRequest
        fields = ['id','prompt_history', 'generated_text', 'used_tokens', 'prompt_tokens', 'timestamp']

class AnswersListAPIRequestSerializer(serializers.ModelSerializer):
    prompt_history = serializers.CharField(source="prompt")
    used_tokens = serializers.IntegerField(source="tokens_used")

    class Meta:
        model = APIRequest
        fields = ['id','prompt_history', 'used_tokens', 'prompt_tokens', 'timestamp']

## Serialization classes for the completions api response
class ChatChoiceDeltaSerializer(serializers.Serializer):
    role = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    content = serializers.CharField(required=False, allow_null=True, allow_blank=True, trim_whitespace=False)

    def create(self, validated_data):
        return UpstreamChatCompletionResponse.Choice.Delta(**validated_data)

class ChatChoiceMessageSerializer(serializers.Serializer):
    role = serializers.CharField()
    content = serializers.CharField()

    def create(self, validated_data):
        return UpstreamChatCompletionResponse.Choice.Message(**validated_data)

class ChatChoiceSerializer(serializers.Serializer):
    message = ChatChoiceMessageSerializer(required=False)
    delta = ChatChoiceDeltaSerializer(required=False)
    index = serializers.IntegerField()
    finish_reason = serializers.CharField(allow_null=True)

    def create(self, validated_data):
        message_data = validated_data.pop("message", None)
        if message_data:
            message = ChatChoiceMessageSerializer(data=message_data)
            message.is_valid(raise_exception=True)
            message = message.save()
        else:
            message = None
        delta_data = validated_data.pop("delta", None)
        if delta_data:
            delta = ChatChoiceDeltaSerializer(data=delta_data)
            delta.is_valid(raise_exception=True)
            delta = delta.save()
        else:
            delta = None
        return UpstreamChatCompletionResponse.Choice(**validated_data, message=message, delta=delta)

class ChoiceSerializer(serializers.Serializer):
    text = serializers.CharField()
    index = serializers.IntegerField()
    logprobs = serializers.CharField(required=False),
    finish_reason = serializers.CharField(allow_null=True)

    def create(self, validated_data):
        return UpstreamCompletionResponse.Choice(**validated_data)
    
class UsageSerializer(serializers.Serializer):
    prompt_tokens = serializers.IntegerField()
    completion_tokens = serializers.IntegerField()
    total_tokens = serializers.IntegerField()

    def create(self, validated_data):
        return UpstreamCompletionResponse.Usage(**validated_data)

class UpstreamCompletionResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    object = serializers.CharField()
    created = serializers.IntegerField()
    model = serializers.CharField()
    choices = ChoiceSerializer(many=True)
    usage = UsageSerializer()

    def create(self, validated_data):
        usage_data = validated_data.pop("usage")
        choices_data = validated_data.pop("choices")
        usage = UsageSerializer(data=usage_data)
        usage.is_valid(raise_exception=True)
        choices = []
        for data in choices_data:
            choice = ChoiceSerializer(data=data)
            choice.is_valid(raise_exception=True)
            choices.append(choice.save())
        return UpstreamCompletionResponse(**validated_data, choices=choices, usage=usage.save())

class UpstreamChatCompletionResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    object = serializers.CharField()
    created = serializers.IntegerField()
    model = serializers.CharField()
    choices = ChatChoiceSerializer(many=True)
    usage = UsageSerializer(required=False)

    def create(self, validated_data):
        usage_data = validated_data.pop("usage", None)
        choices_data = validated_data.pop("choices")
        if usage_data:
            usage = UsageSerializer(data=usage_data)
            usage.is_valid(raise_exception=True)
            usage = usage.save()
        else:
            usage = None
        choices = []
        for data in choices_data:
            choice = ChatChoiceSerializer(data=data)
            choice.is_valid(raise_exception=True)
            choices.append(choice.save())
        return UpstreamChatCompletionResponse(**validated_data, choices=choices, usage=usage)


## Serialization classes for client completion response
class ResponseSerializer(serializers.Serializer):
    generated_text = serializers.CharField()
    prompt_tokens = serializers.IntegerField()
    used_tokens = serializers.IntegerField()
    prompt_history = serializers.CharField()

class ErrorSerializer(serializers.Serializer):
    source = serializers.CharField()
    message = serializers.CharField()

class ClientCompletionResponseSerializer(serializers.Serializer):
    response = ResponseSerializer(required=False)
    error = ErrorSerializer(required=False)
