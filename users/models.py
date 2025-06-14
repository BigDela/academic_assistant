# Create your models here.
# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

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
