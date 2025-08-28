from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.core.mail import send_mail
import random
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import datetime
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match")
        if User.objects.filter(email=data["email"]).exists():
            raise serializers.ValidationError({"email": "Email already exists."})
        if User.objects.filter(username=data["username"]).exists():
            raise serializers.ValidationError({"username": "Username already exists."})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        email = validated_data["email"]

        # Save OTP to the database
        EmailOTP.objects.update_or_create(
            email=validated_data["email"],
            defaults={"otp": otp, "created_at": timezone.now()}
        )
 
        # Send OTP via email

        subject = "Your OTP Code"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #444;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                }}
                .header {{
                    color: #2c3e50;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .otp-box {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .otp {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #3498db;
                    letter-spacing: 3px;
                    margin: 10px 0;
                }}
                .note {{
                    font-size: 14px;
                    color: #7f8c8d;
                    margin-top: 25px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 15px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #95a5a6;
                }}
                .button {{
                    background-color: #3498db;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 4px;
                    display: inline-block;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h2>Verification Code For exedu - Hybrid AI Education</h2>
                </div>

                <p>Hello,</p>
                <p>Here's your One-Time Password (OTP) for verification:</p>

                <div class="otp-box">
                    <div class="otp">{otp}</div>
                    <small>This code expires in 5 minutes</small>
                </div>

                <p class="note">
                    <strong>Note:</strong> For your security, please don't share this code with anyone.
                    If you didn't request this code, you can safely ignore this email.
                </p>

                <div class="footer">
                    <p>© {datetime.datetime.now().year} exedu. All rights reserved.</p>
                    <p>Need help? <a href="mailto:exeduone@gmail.com">Contact our support team</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        New Verification Code

        Hello,

        As requested, here's your new One-Time Password (OTP) for verification:
        {otp}

        This code expires in 1 minute.

        Note: For your security, please don't share this code with anyone.
        If you didn't request this code, you can safely ignore this email.

        © {datetime.datetime.now().year} YourCompany. All rights reserved.
        Need help? Contact our support team at exeduone@gmail.com
        """
        msg = EmailMultiAlternatives(
            subject, text_content, "no-reply@gmail.com", [email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        return {"email": validated_data["email"], "message": "OTP sent to email"}


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["username"] = user.username
        token["user_id"] = user.id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data["email"] = self.user.email
        data["user_id"] = self.user.id
        data["username"] = self.user.username
        return data


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            otp_instance = EmailOTP.objects.get(email=data["email"])
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid email or OTP")

        if otp_instance.otp != data["otp"]:
            raise serializers.ValidationError("Incorrect OTP")

        if not otp_instance.is_valid():
            raise serializers.ValidationError("OTP has expired")

        return data

    def create(self, validated_data):
        # Create user after OTP verification
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
        )
        # Remove OTP entry after successful registration
        EmailOTP.objects.filter(email=validated_data["email"]).delete()

        return user


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email")

        try:
            otp_record = EmailOTP.objects.get(email=email)
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "No OTP found. Please request a new one."}
            )

        expiration_time = otp_record.created_at + timedelta(minutes=10)
        if timezone.now() <= expiration_time:
            otp = otp_record.otp
        else:
            otp = str(random.randint(100000, 999999))
            otp_record.otp = otp
            otp_record.created_at = timezone.now()
            otp_record.save()

        subject = "Your New OTP Code"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #444;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .email-container {{
                    background-color: #ffffff;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                }}
                .header {{
                    color: #2c3e50;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .otp-box {{
                    background-color: #f8f9fa;
                    border-left: 4px solid #3498db;
                    padding: 15px;
                    margin: 20px 0;
                    text-align: center;
                }}
                .otp {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #3498db;
                    letter-spacing: 3px;
                    margin: 10px 0;
                }}
                .note {{
                    font-size: 14px;
                    color: #7f8c8d;
                    margin-top: 25px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 15px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #95a5a6;
                }}
                .button {{
                    background-color: #3498db;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 4px;
                    display: inline-block;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <h2>New Verification Code</h2>
                </div>

                <p>Hello,</p>
                <p>As requested, here's your new One-Time Password (OTP) for verification:</p>

                <div class="otp-box">
                    <div class="otp">{otp}</div>
                    <small>This code expires in 10 minutes</small>
                </div>

                <p class="note">
                    <strong>Note:</strong> For your security, please don't share this code with anyone.
                    If you didn't request this code, you can safely ignore this email.
                </p>

                <div class="footer">
                    <p>© {datetime.datetime.now().year} exedu.in All rights reserved.</p>
                    <p>Need help? <a href="mailto:exeduone@gmail.com">Contact our support team</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        New Verification Code

        Hello,

        As requested, here's your new One-Time Password (OTP) for verification:
        {otp}

        This code expires in 10 minute.

        Note: For your security, please don't share this code with anyone.
        If you didn't request this code, you can safely ignore this email.

        © {datetime.datetime.now().year} YourCompany. All rights reserved.
        Need help? Contact our support team at exeduone@gmail.com
        """

        msg = EmailMultiAlternatives(
            subject, text_content, "no-reply@yourdomain.com", [email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        return {"message": "OTP resent to email"}


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        request = self.context.get("request")
        email = self.validated_data["email"]
        user = User.objects.get(email=email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        frontend_url = f"https://exedu.in/reset-password/{uid}/{token}"
        subject = "Password Reset Requested"
        text_message = f"Hi {user.username},\n\nClick the link below:\n{frontend_url}"

        html_message = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8" />
            <title>Password Reset</title>
          </head>
          <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; margin: 0; padding: 0;">
            <table width="100%" bgcolor="#f4f4f7" cellpadding="0" cellspacing="0">
              <tr>
                <td align="center" style="padding: 40px 0;">
                  <table width="600" bgcolor="#ffffff" cellpadding="0" cellspacing="0" style="border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                      <td align="center" 
                          style="padding: 20px; color: #ffffff; font-size: 22px; font-weight: bold; 
                                 background: linear-gradient(90deg, #8b5cf6, #d946ef);">
                        exedu
                      </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                      <td style="padding: 30px; color: #333333; font-size: 16px; line-height: 1.6;">
                        <p>Hi <b>{user.username}</b>,</p>
                        <p>We received a request to reset your password. Click the button below to set a new one:</p>
                        <p style="text-align: center; margin: 30px 0;">
                          <a href="{frontend_url}" 
                             style="background: linear-gradient(90deg, #8b5cf6, #d946ef); 
                                    color: #ffffff; text-decoration: none; 
                                    padding: 12px 24px; border-radius: 6px; 
                                    font-size: 16px; font-weight: bold; display: inline-block;">
                            Reset Password
                          </a>
                        </p>
                        <p>If you did not request a password reset, you can safely ignore this email.</p>
                        <p style="font-size: 14px; color: #666;">This link will expire in 24 hours.</p>
                      </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                      <td align="center" bgcolor="#f4f4f7" style="padding: 20px; font-size: 12px; color: #888888;">
                        © {2025} exedu. All rights reserved.
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
        </body>

        </html>
        """

        email_msg = EmailMultiAlternatives(
            subject, text_message, settings.EMAIL_HOST_USER, [email]
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send()


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")

        try:
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid reset link.")

        if not default_token_generator.check_token(self.user, data["token"]):
            raise serializers.ValidationError("Invalid or expired token.")

        return data

    def save(self):
        password = self.validated_data["password"]
        self.user.set_password(password)
        self.user.save()
        return self.user


class UploadedImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedImages
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class SectionImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionImages
        fields = "__all__"


class CoursePageDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoursePageDetails
        fields = "__all__"


class CourseSinglePageSerializer(serializers.ModelSerializer):
    title = serializers.StringRelatedField()

    class Meta:
        model = CourseSinglePage
        fields = "__all__"


class EnrollFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrollForm
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class PublicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "unique_id",
            "profile_image",
            "name",
            "secondary_school",
            "secondary_year",
            "university",
            "university_major",
            "university_year",
            "career_objective",
            "skills",
            "experience",
            "interests",
            "is_public",
        ]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = "__all__"


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

# class StudentCourseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentCourse
#         fields = '__all__'

# class StudentAttendanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StudentAttendance
#         fields = '__all__'