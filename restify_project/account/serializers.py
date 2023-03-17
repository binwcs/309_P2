from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.admin import User

from .models import User


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['bio', 'location', 'birth_date']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile
        instance = super().update(instance, validated_data)
        for key, value in profile_data.items():
            setattr(profile, key, value)
        profile.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'content', 'author', 'created_at']


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'account', 'start_date', 'end_date', 'created_at']
