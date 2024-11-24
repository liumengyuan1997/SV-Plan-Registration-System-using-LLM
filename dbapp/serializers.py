from rest_framework import serializers
from .models import User, Event

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(required=True)
    department = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'role', 'first_name', 'last_name', 'department']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


    def create(self, validated_data):
        return User.objects.create(**validated_data)


class EventSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(required=True)
    event_description = serializers.CharField(required=True)
    event_location = serializers.CharField(required=True)
    event_time = serializers.DateTimeField(required=True)
    event_category = serializers.CharField(required=True)
    class Meta:
        model = Event
        fields = ['event_id','event_name', 'event_description', 'event_location', 'event_time', 'event_status', 'event_category']
