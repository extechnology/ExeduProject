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
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse


class GoogleAuthView(APIView):
    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response({'error': 'Missing token'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)

            email = idinfo.get('email')
            username = idinfo.get('name') or email.split('@')[0]

            if not email:
                return Response({'error': 'Email not found in token'}, status=status.HTTP_400_BAD_REQUEST)

            user, created = User.objects.get_or_create(email=email, defaults={'username': username})

            if created:
                user.username = username
                user.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'username': user.username,
                'email': user.email,
                'user_id': user.id,
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            print("Token verification failed:", e)
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'OTP sent to email'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    

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
    
class CourseSinglePageView(APIView):
    def get(self, request, format=None):
        course_details = CourseSinglePage.objects.all()
        serializer = CourseSinglePageSerializer(course_details, many=True)
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


class ProfileListView(APIView):
    def get(self, request, format=None):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

class ProfileByUserView(APIView):
    def get(self, request, user_id):
        try:
            profile = Profile.objects.get(user__id=user_id)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id):
        try:
            profile = Profile.objects.get(user__id=user_id)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)  # `partial=True` allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProfileDetailView(APIView):
    def get(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

def profile_meta_preview(request, unique_id):
    profile = get_object_or_404(Profile, unique_id=unique_id, is_public=True)
    return render(request, "public_profile_meta.html", {"profile": profile})

    
    
class PublicProfileView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, unique_id):
        try:
            profile = Profile.objects.get(unique_id=unique_id, is_public=True)
            serializer = PublicProfileSerializer(profile)
            return Response(serializer.data, status=200)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found or private"}, status=404)
        
    def put(self, request, unique_id):
        try:
            profile = Profile.objects.get(unique_id=unique_id)
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

        is_public = request.data.get("is_public")
        if is_public is not None:
            profile.is_public = is_public
            profile.save()
            serializer = PublicProfileSerializer(profile)
            return Response(serializer.data, status=200)
        
        return Response({"error": "Missing is_public field"}, status=400)




@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_profile_access(request):
    user = request.user
    profile = Profile.objects.filter(user=user).first()

    if not profile:
        return Response({"detail": "Profile not found."}, status=404)

    if profile.can_access_profile:
        return Response({"detail": "Access already granted."}, status=400)

    subject = "🔔 Profile Access Request"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [admin[1] for admin in settings.ADMINS]

    text_content = f"User {user.username} ({user.email}) has requested access to their profile."
    html_content = f"""
        <p><strong>Profile Access Request</strong></p>
        <p>User: <b>{user.username}</b></p>
        <p>Email: <a href="mailto:{user.email}">{user.email}</a></p>
        <p>Visit admin to approve: <a href="https://server.exedu.in/admin/Application/profile/{profile.unique_id}/change/">Admin Panel</a></p>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return Response({"detail": "Access request sent."})



class ValidateTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Token is valid"}, status=status.HTTP_200_OK)
    

class CertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            profile = request.user.profile  
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=404)

        certificates = Certificate.objects.filter(profile=profile)
        serializer = CertificateSerializer(certificates, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=404)
    
        data = request.data.copy()
        data['profile'] = profile.pk  # ✅ or profile.unique_id
        serializer = CertificateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny])
def public_certificates(request, unique_id):
    try:
        profile = Profile.objects.get(unique_id=unique_id, is_public=True)
        certificates = Certificate.objects.filter(profile=profile)
        serializer = CertificateSerializer(certificates, many=True)
        return Response(serializer.data)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found or private"}, status=404)


class ContactView(APIView):
    def post(self, request, format=None):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)