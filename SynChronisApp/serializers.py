from rest_framework import serializers
from .models import TeacherTable  # Ensure Teacher model exists
from .models import LoginTable

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginTable
        fields = ['Username', 'Email', 'Password', 'Type', 'status']  # Fields to include
        extra_kwargs = {'Password': {'write_only': True}}  # Hide password in response

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherTable
        fields = '__all__'  # Or specify required fields
