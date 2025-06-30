from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone


class EmailOTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)
    
    def is_valid(self):
        expiration_time = timezone.now() - timezone.timedelta(minutes=10)
        return self.created_at > expiration_time
    
    def __str__(self):
        return f"Email: {self.email}, OTP: {self.otp}"
    
    
    
    

class UploadedImages(models.Model):
    image = models.ImageField(upload_to='images2/')
    
    def __str__(self):
        return self.image.name
    
    
class Course(models.Model):
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='images/', default=None)

    def __str__(self):
        return self.title


class SectionImages(models.Model):
    CHOICES = [
        ('hero', 'Hero'),
        ('passion', 'Passion'),
        ('thumbnail', 'Thumbnail'),
        ('about_us', 'About Us'),
        ('why_us', 'Why Us'),
        ('mission', 'Mission'),
        ('confirm_career', 'Confirm Career'),
        ('contact', 'Contact'),
    ]
    section=models.CharField(max_length=255, choices=CHOICES)
    image = models.ImageField(upload_to='images_section/' , default=None , null=True)
    
    def __str__(self):
        return f"{self.section} - {self.image.name}"
    
    
class CoursePageDetails(models.Model):
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255 , null=True)
    image = models.ImageField(upload_to='images/', default=None)
    
    def __str__(self):
        return self.title
    

class EnrollForm(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    title=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else "Untitled Enrollment" 


class Profile(models.Model):
    unique_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    name=models.CharField(max_length=255,null=True)
    email = models.EmailField(default=None, null=True, blank=True)
    phone_number = models.CharField(max_length=15,null=True, blank=True)
    secondary_school = models.CharField(max_length=255,null=True, blank=True)
    secondary_year = models.CharField(max_length=4,null=True, blank=True)
    university = models.CharField(max_length=255,null=True, blank=True)
    university_major = models.CharField(max_length=255,null=True, blank=True)
    university_year = models.CharField(max_length=4,null=True, blank=True)
    career_objective = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    experience = models.TextField(null=True, blank=True)
    interests = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    def __str__(self):
        return f"{self.name or 'Unnamed'} - {self.email or 'No Email'}"



class Certificate(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="certificates")
    certificate_file = models.FileField(upload_to='certificates/')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Certificate for {self.profile.phone_number}"
    
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=15)
    course = models.CharField(max_length=100)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
