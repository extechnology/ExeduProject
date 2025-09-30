from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r"attendance", AttendanceViewSet, basename="attendance")
router.register(r"student/profile", StudentProfileViewset, basename="profile")
router.register(r"notification", NotificationViewSet, basename="notification")
router.register(r"batches", BatchViewSet, basename="batches")
router.register(r"tutor", TutorViewSet, basename="tutor")
router.register(r"session", SessionViewSet, basename="session")
router.register(r"student-session", StudentSessionViewSet, basename="student-session")
router.register(r"works", StudentWorksViewSet, basename="works")



urlpatterns = [
    
    path("", include(router.urls)),
    
    path('register/',RegisterView.as_view()),
    
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    
    path('google-auth/', GoogleAuthView.as_view(), name='google-login'),
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path('uploaded-images/',UploadedImagesView.as_view(),name='uploaded-images'),

    path('section-images/',SectionImagesView.as_view(),name='section-images'),
    
    path('upload-image/',UploadedImagesView.as_view(),name='upload-image'),
    
    path('course/',CourseView.as_view(),name='course'),
    
     path("course/<int:pk>/", CourseUpdateView.as_view(), name="course-update"),
    
    path('course-options/', CourseOptionsView.as_view(), name='course-options'),
        
    path('course-page-details/',CoursePageDetailsView.as_view(),name='course-page-details'),
    
    path('course-single-page/',CourseSinglePageView.as_view(),name='course-single-page'),
    
    path('enroll-form/',EnrollFormView.as_view(),name='enroll'),
    
    path('profile/', ProfileListView.as_view(), name='profile-list'),
    
    path('public-profile/<uuid:unique_id>/', PublicProfileView.as_view(), name='public-profile'),
    
    path('auth/validate-token/', ValidateTokenView.as_view(), name='validate-token'),
    
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    
    path('profile/user/<int:user_id>/', ProfileByUserView.as_view(), name='profile-by-user'),
    
    path("request-profile-access/", request_profile_access, name="request-profile-access"),
    
    path('certificate/',CertificateListCreateView.as_view(),name='certificate'),
    
    path("certificates/<int:pk>/", CertificateDetailView.as_view(), name="certificate-detail"),
    
    path("public-certificates/<uuid:unique_id>/", public_certificates),

    path("profile/meta/<uuid:unique_id>/", profile_meta_preview, name="profile-meta"),
    
    path('contact/',ContactView.as_view(),name='contact'),
    
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    
]