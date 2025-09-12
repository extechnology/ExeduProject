from rest_framework import viewsets,permissions
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,generics
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
from rest_framework.decorators import action
from django.db import transaction
from django.core.exceptions import ValidationError


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
            user = serializer.save() 

            Notification.objects.create(
                type="REGISTER",  
                title="New User Registration",
                message=f"User {user.username} has registered."
            )

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



class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


    
    
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
    
    def post(self, request, format=None):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    
    
class CourseUpdateView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Course, pk=pk)

    def patch(self, request, pk, format=None):
        course = self.get_object(pk)
        serializer = CourseSerializer(course, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        course = self.get_object(pk)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class CourseOptionsView(APIView):
    def get(self, request, format=None):
        options = [
            {"value": key, "label": label}
            for key, label in CoursePageDetails.COURSE_OPTIONS
        ]
        return Response(options)

    
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
        enroll_forms = EnrollForm.objects.all().order_by('-created_at')
        serializer = EnrollFormSerializer(enroll_forms, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = EnrollFormSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                enroll_form = serializer.save()
                
                # Create notification
                Notification.objects.create(
                    type="ADMISSION",
                    title="New Course Enquiry Form Submitted",
                    message=f"Admission request from {enroll_form.name} ({enroll_form.email}) for {enroll_form.title}",
                    related_id=enroll_form.id,
                    related_model="EnrollForm"
                )
                
                return Response(
                    {
                        "message": "Enrollment form submitted successfully!",
                        "data": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
                
            except ValidationError as e:
                return Response(
                    {"general": [str(e)]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    {"general": ["An unexpected error occurred. Please try again."]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class StudentProfileViewset(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

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

    # ---- SEND EMAIL ----
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

    Notification.objects.create(
        user=request.user,
        type="PROFILE",
        title="Profile Access Request",
        message=f"User {user.username} ({user.email}) has requested profile access.",
        related_id=str(profile.unique_id),
        related_model="Profile"
    )


    return Response({"detail": "Access request sent."})



class ValidateTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Token is valid"}, status=status.HTTP_200_OK)

# class StudentCertificateView(APIView):
#     def get(self, request, student_id):
#         try:
#             student = Student.objects.get(id=student_id)
#             certificates = Certificate.objects.filter(student=student)
#             serializer = CertificateSerializer(certificates, many=True)
#             return Response(serializer.data)
#         except Student.DoesNotExist:
#             return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Certificate.DoesNotExist:
#             return Response({'error': 'Certificate not found'}, status=status.HTTP_404_NOT_FOUND)
#     def post(self, request, student_id):
#         try:
#             student = Student.objects.get(id=student_id)
#             serializer = CertificateSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(student=student)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except Student.DoesNotExist:
#             return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

class CertificateListCreateView(generics.ListCreateAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Certificate.objects.all()  
        return Certificate.objects.filter(profile=self.request.user.profile)

    def perform_create(self, serializer):
        if self.request.user.is_staff and 'profile' in self.request.data:
            serializer.save(profile_id=self.request.data['profile'])
        else:
            serializer.save(profile=self.request.user.profile)


class CertificateDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Certificate.objects.all()
        return Certificate.objects.filter(profile=self.request.user.profile)




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
            contact = serializer.save() 

            Notification.objects.create(
                type="ENQUIRY",
                title="New Admission Enquiry",
                message=f"Enquiry from {contact.name} ({contact.email})",
                related_id=contact.id,
                related_model="Contact"
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()

    @action(detail=True, methods=["patch"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "marked as read"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["patch"], url_path="mark-all-read")
    def mark_all_read(self, request):
        notifications = self.queryset.filter(is_read=False)
        count = notifications.update(is_read=True)
        return Response({"status": f"{count} notifications marked as read"}, status=status.HTTP_200_OK)


        
        

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = StudentAttendance.objects.all().select_related("student", "student_course")
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        data = serializer.validated_data
        obj, _ = StudentAttendance.objects.update_or_create(
            student=data["student"],
            student_course=data["student_course"],
            date=data["date"],
            defaults={
                "status": data["status"],
                "marked_by": self.request.user,
                "attended_at": data.get("attended_at"),
            },
        )
        return obj

    def get_queryset(self):
        queryset = super().get_queryset()
        date = self.request.query_params.get("date")
        course_id = self.request.query_params.get("course")
        student_id = self.request.query_params.get("student")

        if date:
            queryset = queryset.filter(date=date)
        if course_id:
            queryset = queryset.filter(student_course_id=course_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        return queryset

    @action(detail=False, methods=["post"])
    def bulk(self, request):
        date = request.data.get("date")
        course_id = request.data.get("course")
        records = request.data.get("records", [])

        if not date or not course_id or not records:
            return Response(
                {"error": "date, course, and records are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, id=course_id)

        created, errors = [], []

        with transaction.atomic():
            for idx, record in enumerate(records):
                student_uuid = record.get("student")
                status_val = record.get("status")
                attended_at = record.get("attended_at")

                if not student_uuid or not status_val:
                    errors.append({"index": idx, "error": "missing student or status"})
                    continue

                try:
                    student_obj = Profile.objects.get(unique_id=student_uuid)
                except Profile.DoesNotExist:
                    errors.append({"index": idx, "error": f"student not found: {student_uuid}"})
                    continue

                obj, _ = StudentAttendance.objects.update_or_create(
                    student=student_obj,
                    student_course=course,
                    date=date,
                    defaults={
                        "status": status_val,
                        "marked_by": request.user,
                        "attended_at": attended_at,
                    },
                )
                created.append(obj)

        serializer = self.get_serializer(created, many=True)
        return Response(
            {
                "saved_count": len(created),
                "errors": errors,
                "records": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


