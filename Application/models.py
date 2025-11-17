from django.db import models
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class EmailOTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)
    
    def is_valid(self):
        expiration_time = self.created_at + timezone.timedelta(minutes=10)
        return timezone.now() < expiration_time

    
    def __str__(self):
        return f"Email: {self.email}, OTP: {self.otp}"
    

class UploadedImages(models.Model):
    image = models.ImageField(upload_to='images2/')
    
    def __str__(self):
        return self.image.name
    

class SectionImages(models.Model):
    CHOICES = [
        ('hero', 'Hero'),
        ('leading_solution', 'Leading Solution'),
        ('transform_passion', 'Transform Passion'),
        ('discuss_together', 'Discuss Together'),
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
    
    COURSE_OPTIONS = [
        ('ai_advanced_digital_marketing', 'AI Advanced Digital Marketing'),
        ('graphic_design', 'Graphic Design'),
        ('ui/ux_design', 'UI/UX Design'),
        ('web_and_app_development', 'WEB & APP Development'),
        ('video_editing', 'Video Editing'),
        ('robotics', 'Robotics'),
    ] 
    
    title = models.CharField(max_length=255 , choices=COURSE_OPTIONS)
    sub_title = models.CharField(max_length=255 , null=True)
    image = models.ImageField(upload_to='images/', default=None)
    
    def __str__(self):
        return self.title
    
    
class StudentRegion(models.Model):
    region = models.CharField(max_length=255)
    image = models.ImageField(upload_to='regions/',null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.region
    


    

class TutorName(models.Model):
    name = models.CharField(max_length=500)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    image = models.ImageField(upload_to='tutors/', null=True, blank=True)
    region = models.ForeignKey(
        StudentRegion,
        on_delete=models.CASCADE,null=True, blank=True
    )

    def __str__(self):
        return self.name
    
    

    
    
class Course(models.Model):
    COURSE_OPTIONS = [
        ('ai_advanced_digital_marketing', 'AI Advanced Digital Marketing'),
        ('graphic_design', 'Graphic Design'),
        ('ui_ux_design', 'UI/UX Design'),
        ('web_and_app_development', 'Web & App Development'),
        ('video_editing', 'Video Editing'),
        ('robotics', 'Robotics'),
    ]

    title = models.CharField(
        max_length=255,
        choices=COURSE_OPTIONS,
        db_index=True,
    )
    sub_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Optional short subtitle for the course"
    )
    description = models.TextField(
        help_text="Detailed description of the course"
    )
    image = models.ImageField(
        upload_to="courses/images/",
        blank=True,
        null=True
    )
    duration = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="E.g. '6 months' or '40 hours'"
    )
    tutor = models.ForeignKey(TutorName, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True,help_text="Course price in INR (or your currency)")
    created_at = models.DateTimeField(default=timezone.now, editable=False)  
    updated_at = models.DateTimeField(auto_now=True)   
    
    region = models.ForeignKey(StudentRegion,on_delete=models.CASCADE, null=True, blank=True)   

    class Meta:
        ordering = ["title"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return dict(self.COURSE_OPTIONS).get(self.title, self.title)

    
class CourseSinglePage(models.Model):
    title = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    description = models.TextField()
    main_image = models.ImageField(upload_to='images/', default=None)
    second_image = models.ImageField(upload_to='images/', default=None)
    third_image = models.ImageField(upload_to='images/', default=None)
    points = models.TextField()
    keyPoints = models.TextField()
    specialties = models.TextField()

    def __str__(self):
        return self.title.title

class EnrollForm(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    title=models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else "Untitled Enrollment" 
    


class Batches(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='batches')    
    time_start = models.TimeField(auto_now_add=False, null=True, blank=True)
    end_date = models.DateField(auto_now_add=False, null=True, blank=True)
    date = models.DateField(auto_now_add=False, null=True, blank=True)
    batch_number = models.CharField(max_length=255, null=True, blank=True)
    region = models.ForeignKey(StudentRegion,on_delete=models.CASCADE, null=True, blank=True)   
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.course.title}"




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
    is_public = models.BooleanField(default=False) 
    can_access_profile = models.BooleanField(default=False)
    student_fee = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True,help_text="Student Course price in INR (or your currency)")
    student_region = models.ForeignKey(StudentRegion, on_delete=models.SET_NULL, null=True, blank=True)
    
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    batch = models.ForeignKey(Batches, on_delete=models.SET_NULL, null=True, blank=True)
    payment_completed = models.BooleanField(default=False)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    paid_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    progress = models.PositiveIntegerField(default=0,help_text="Overall student progress in percentage (0–100)")

    def __str__(self):
        return f"{self.user.username} - {self.progress}%"
    
    def __str__(self):
        return f"{self.name or 'Unnamed'} - {self.email or 'No Email'}"


class Certificate(models.Model):
    profile = models.ForeignKey(
        "Profile", on_delete=models.CASCADE, related_name="certificates"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    certificate_file = models.FileField(upload_to="certificates/")
    description = models.TextField(null=True, blank=True)
    certificate_number = models.UUIDField(default=uuid.uuid4,  editable=False)
    grade = models.CharField(max_length=50, null=True, blank=True)
    issued_at = models.DateTimeField(default=timezone.now, editable=False)
    region = models.ForeignKey(StudentRegion,on_delete=models.CASCADE, null=True, blank=True)   
    


    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.profile.name}"
    
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=15)
    course = models.CharField(max_length=100)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StudentWorks(models.Model):
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="works")
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='works/')
    link = models.URLField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
class Session(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True) 
    start_time = models.DateTimeField(default=timezone.now)  
    duration = models.DurationField(default=timedelta(hours=1)) 
    tutor = models.ForeignKey(
        "TutorName",  
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tutor_sessions"
    )
    students = models.ManyToManyField(
        "Profile",
        related_name="student_sessions",
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True , null=True, blank=True)
    region = models.ForeignKey(StudentRegion,on_delete=models.CASCADE, null=True, blank=True)   
    

    @property
    def end_time(self):
        return self.start_time + self.duration

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def __str__(self):
        return f"Session with {self.tutor} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class TutorAttendance(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
    ]
    tutor = models.ForeignKey(TutorName, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("tutor", "session", "date")  
        ordering = ["-date"]

    def __str__(self):
        return f"{self.tutor.name} - {self.session.title} - {self.date} ({self.status})"
    
    
class StudentAttendance(models.Model):
    
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
    ]

    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="attendance_records")
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="attendance", null=True, blank=True)
    student_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    marked_by_student = models.BooleanField(default=False)
    attended_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="marked_attendance")
    region = models.ForeignKey(StudentRegion,on_delete=models.CASCADE, null=True, blank=True)   
    

    class Meta:
        unique_together = ("student", "student_course", "date") 

    def __str__(self):
        return f"{self.student} - {self.student_course} - {self.date} ({self.status})"



class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("LOGIN", "New Login"),
        ("PROFILE", "Profile Access Request"),
        ("ENQUIRY", "Course Enquiry"),
        ("ADMISSION", "Admission Form Submission"),
        ("SESSION", "New Session"),
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="notifications",null=True, blank=True)

    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True, null=True)

    related_id = models.CharField(max_length=36, null=True, blank=True)  

    related_model = models.CharField(max_length=50, null=True, blank=True)

    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"


