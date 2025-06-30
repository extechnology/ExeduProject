from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': 'Email already exists.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Save OTP to the database
        EmailOTP.objects.update_or_create(email=validated_data['email'], defaults={'otp': otp})

        # Send OTP via email
        send_mail(
            'Your OTP Code',
            f'Your OTP for registration is: {otp}',
            'no-reply@yourdomain.com',
            [validated_data['email']],
            fail_silently=False,
        )

        return {'email': validated_data['email'], 'message': 'OTP sent to email'}


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            otp_instance = EmailOTP.objects.get(email=data['email'])
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid email or OTP")

        if otp_instance.otp != data['otp']:
            raise serializers.ValidationError("Incorrect OTP")

        if not otp_instance.is_valid():
            raise serializers.ValidationError("OTP has expired")

        return data

    def create(self, validated_data):
        # Create user after OTP verification
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        # Remove OTP entry after successful registration
        EmailOTP.objects.filter(email=validated_data['email']).delete()

        return user


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email")

        try:
            otp_record = EmailOTP.objects.get(email=email)
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError({"email": "No OTP found. Please request a new one."})

        # Check if OTP is still valid
        expiration_time = otp_record.created_at + timedelta(minutes=5)
        if timezone.now() <= expiration_time:
            otp = otp_record.otp  # Use the existing OTP
        else:
            # Generate a new OTP
            otp = str(random.randint(100000, 999999))
            otp_record.otp = otp
            otp_record.created_at = timezone.now()
            otp_record.save()

        # Send OTP via email
        send_mail(
            'Resend OTP Code',
            f'Your OTP for verification is: {otp}',
            'no-reply@yourdomain.com',
            [email],
            fail_silently=False,
        )

        return {"message": "OTP resent to email"}


class UploadedImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImages
        fields = '__all__'
        

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class SectionImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionImages
        fields = '__all__'
        
class CoursePageDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePageDetails
        fields = '__all__'
        
class EnrollFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollForm
        fields = '__all__'
        
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'
        
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'