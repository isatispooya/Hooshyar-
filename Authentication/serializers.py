from rest_framework import serializers
from . import models  
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Auth
        fields = '__all__'


class OtpSerializer(serializers.ModelSerializer):
    class Meta :
        model = models.Otp
        fields = '__all__'


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Auth
        fields = '__all__'   


class ConsultantSerializer(serializers.ModelSerializer):
    from rest_framework import serializers
from .models import Consultant

class ConsultantSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = Consultant
        fields = '__all__'

    class Meta:
        model = models.Consultant
        fields = '__all__'   



