from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/',RegisterView.as_view()),
    
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    
    path('google-auth/', GoogleAuthView.as_view(), name='google-login'),
    
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    path('uploaded-images/',UploadedImagesView.as_view(),name='uploaded-images'),

    path('section-images/',SectionImagesView.as_view(),name='section-images'),
    
    path('upload-image/',UploadedImagesView.as_view(),name='upload-image'),
    
    path('course/',CourseView.as_view(),name='course'),
        
    path('course-page-details/',CoursePageDetailsView.as_view(),name='course-page-details'),
    
    path('course-single-page/',CourseSinglePageView.as_view(),name='course-single-page'),
    
    path('enroll-form/',EnrollFormView.as_view(),name='enroll'),
    
    path('profile/', ProfileListView.as_view(), name='profile-list'),
    
    path('public-profile/<uuid:unique_id>/', PublicProfileView.as_view(), name='public-profile'),
    
    path('auth/validate-token/', ValidateTokenView.as_view(), name='validate-token'),
    
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    
    path('profile/user/<int:user_id>/', ProfileByUserView.as_view(), name='profile-by-user'),
    
    path("request-profile-access/", request_profile_access, name="request-profile-access"),
    
    path('certificate/',CertificateView.as_view(),name='certificate'),
    
    path("public-certificates/<uuid:unique_id>/", public_certificates),

    path("profile/meta/<uuid:unique_id>/", profile_meta_preview, name="profile-meta"),
    

    path('contact/',ContactView.as_view(),name='contact'),

]