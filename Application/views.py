from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

class GoogleAuthView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        
        print("username:",username,"\nemail:",email)

        if not username or not email:
            return Response({'error': 'Username and email are required'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(email=email, defaults={'username': username})

        if created:
            user.username = username
            user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
    
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
        


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'OTP sent to email'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Account verified and created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SectionImagesView(APIView):
    def get(self, request, format=None):
        images = SectionImages.objects.all()
        serializer = SectionImagesSerializer(images, many=True)
        return Response(serializer.data)

class UploadedImagesView(APIView):
    def get(self, request, format=None):
        images = UploadedImages.objects.all()
        serializer = UploadedImagesSerializer(images, many=True)
        return Response(serializer.data)


class CourseView(APIView):
    def get(self, request, format=None):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    
class CoursePageDetailsView(APIView):
    def get(self, request, format=None):
        course_details = CoursePageDetails.objects.all()
        serializer = CoursePageDetailsSerializer(course_details, many=True)
        return Response(serializer.data)


class EnrollFormView(APIView):
    def get(self, request, format=None):
        enroll_forms = EnrollForm.objects.all()
        serializer = EnrollFormSerializer(enroll_forms, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = EnrollFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    def get(self, request, format=None):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)
    
    def put(self, request):
        profile = Profile.objects.get(id=request.data['id'])
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CertificateView(APIView):
    def get(self, request, format=None):
        certificates = Certificate.objects.all()
        serializer = CertificateSerializer(certificates, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = CertificateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactView(APIView):
    def post(self, request, format=None):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)