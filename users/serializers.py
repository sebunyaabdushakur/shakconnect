from rest_framework import serializers
from .models import Student


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = [
            'full_name',
            'email',
            'student_number',
            'course',
            'year',
            'bio',
            'password',
            'confirm_password',
        ]

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match'})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        student = Student(**validated_data)
        student.set_password(password)
        student.save()
        return student


class StudentProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'full_name',
            'email',
            'student_number',
            'course',
            'year',
            'bio',
            'profile_photo',
            'followers_count',
            'following_count',
            'date_joined',
        ]
        read_only_fields = ['email', 'student_number', 'date_joined']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()


class StudentListSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
            'full_name',
            'student_number',
            'course',
            'year',
            'profile_photo',
            'followers_count',
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'full_name',
            'bio',
            'course',
            'year',
            'profile_photo',
        ]

    def update(self, instance, validated_data):
        photo = validated_data.pop('profile_photo', None)
        if photo:
            import cloudinary.uploader
            result = cloudinary.uploader.upload(photo)
            url = result.get('secure_url')
            Student.objects.filter(pk=instance.pk).update(profile_photo=url)
            instance.profile_photo = url
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance