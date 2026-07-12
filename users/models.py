from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class StudentManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Student(AbstractBaseUser, PermissionsMixin):
    YEAR_CHOICES = [
        ('1', 'Year 1'),
        ('2', 'Year 2'),
        ('3', 'Year 3'),
        ('4', 'Year 4'),
    ]

    COURSE_CHOICES = [
        ('BIT', 'Bachelor of Information Technology'),
        ('BCS', 'Bachelor of Computer Science'),
        ('BSE', 'Bachelor of Software Engineering'),
        ('BBA', 'Bachelor of Business Administration'),
        ('BCOM', 'Bachelor of Commerce'),
        ('OTHER', 'Other'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    student_number = models.CharField(max_length=50, unique=True)
    course = models.CharField(max_length=10, choices=COURSE_CHOICES)
    year = models.CharField(max_length=1, choices=YEAR_CHOICES)
    bio = models.TextField(blank=True)
    profile_photo = models.CharField(
    max_length=500,
    blank=True,
    null=True
)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)
    ban_reason = models.TextField(blank=True)
    banned_at = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = StudentManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'student_number', 'course', 'year']

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.full_name} ({self.student_number})"