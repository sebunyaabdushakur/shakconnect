from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Student


@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display = [
        'full_name',
        'email',
        'student_number',
        'course',
        'year',
        'is_active',
        'is_banned',
        'date_joined'
    ]
    list_filter = ['course', 'year', 'is_active', 'is_banned']
    search_fields = ['full_name', 'email', 'student_number']
    ordering = ['-date_joined']

    fieldsets = (
        ('Personal Info', {
            'fields': ('full_name', 'email', 'student_number', 'bio', 'profile_photo')
        }),
        ('Academic Info', {
            'fields': ('course', 'year')
        }),
        ('Account Status', {
            'fields': ('is_active', 'is_staff', 'is_banned', 'ban_reason', 'banned_at')
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions')
        }),
    )

    add_fieldsets = (
        ('Create Student', {
            'fields': (
                'full_name',
                'email',
                'student_number',
                'course',
                'year',
                'password1',
                'password2'
            )
        }),
    )