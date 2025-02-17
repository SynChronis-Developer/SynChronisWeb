from rest_framework import serializers
from .models import AttendanceTable, TeacherTable  # Ensure Teacher model exists
from .models import LoginTable
from .models import TimeTableTable

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginTable
        fields = ['Username', 'Email', 'Password', 'Type', 'status']  # Fields to include
        extra_kwargs = {'Password': {'write_only': True}}  # Hide password in response

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherTable
        fields = '__all__'  # Or specify required fields

# Serializer for TimeTableTable
class TimeTableSerializer(serializers.ModelSerializer):
    subjectname=serializers.CharField(source='SubjectName.SubjectName')
    teachername=serializers.CharField(source='TeacherName.TeacherName')
    classname=serializers.CharField(source='ClassName.ClassName')
    classlatitude=serializers.CharField(source='ClassName.Latitude')
    classlongitude=serializers.CharField(source='ClassName.Longitude')
    
    class Meta:
        model = TimeTableTable
        fields = ['id', 'ClassName', 'SubjectName', 'TeacherName', 'day', 'period', 'start_time', 'end_time','subjectname','teachername','classname','classlatitude','classlongitude']

# Serializer for AttendanceTable
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceTable
        fields = ['id', 'StudentName', 'Date', 'Status', 'Attendance']

