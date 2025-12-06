# Create your models here.
# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    COURSE_CHOICES = [
        ('CS', 'Computer Science'),
        ('ENG', 'Engineering'),
        ('BUS', 'Business Administration'),
        # … add as needed
    ]
    YEAR_CHOICES = [
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
    ]

    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    year = models.CharField(max_length=3, choices=YEAR_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.course}-{self.year})"


class UserProfile(models.Model):
    """Extended user profile with additional information"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/%Y/%m/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself")
    program_of_study = models.CharField(max_length=200, blank=True, help_text="e.g., Computer Science, Engineering")
    year_level = models.CharField(max_length=50, blank=True, help_text="e.g., Freshman, Sophomore, Junior, Senior")
    
    # Theme preference
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    ]
    theme_preference = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return None
