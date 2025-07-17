from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import *
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_employee_profile(sender, instance, created, **kwargs):
    if created: 
        Profile.objects.create(user=instance, email=instance.email, name=instance.username)


@receiver(post_save, sender=Profile)
def send_access_granted_email(sender, instance, created, **kwargs):
    print("🚨 Profile post_save signal triggered")
    if created:
        return

    try:
        previous = Profile.objects.get(pk=instance.pk)

        print("🧪 Previous access:", previous.can_access_profile)
        print("🧪 Current access:", instance.can_access_profile)
        if instance.can_access_profile:

            subject = "✅ Access Granted to Your Profile"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [instance.email or instance.user.email]

            text_content = (
                f"Hi {instance.name or instance.user.username},\n\n"
                "Your profile access has been approved. You can now log in and complete your dashboard."
            )
            html_content = f"""
                <p>Hi <strong>{instance.name or instance.user.username}</strong>,</p>
                <p>Your profile access has been <strong>approved</strong> ✅.</p>
                <p>You can now log in to EduPortal and start using your personalized dashboard:</p>
                <p><a href="https://exedu.in/">You May Now Log In to exedu</a></p>
                <br>
                <p>— EduPortal Team</p>
            """

            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            print("✅ Email sent successfully to:", to_email)

    except Profile.DoesNotExist:
        print("⚠️ Profile does not exist yet. Skipping email.")
    except Exception as e:
        print("❌ Error sending email:", str(e))
