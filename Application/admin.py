from django.contrib import admin

from .models import *

# Register your models here.

class CertificateStackedInline(admin.StackedInline):
    model = Certificate
    extra = 1

class ProfileAdmin(admin.ModelAdmin):
    inlines = [CertificateStackedInline]
    

admin.site.register(Profile, ProfileAdmin)

admin.site.register(Certificate)

admin.site.register(EmailOTP)


admin.site.register(UploadedImages)

admin.site.register(Course)

admin.site.register(CoursePageDetails)

admin.site.register(EnrollForm)


admin.site.register(Contact)