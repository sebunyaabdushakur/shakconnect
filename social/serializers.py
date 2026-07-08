from rest_framework import serializers
from .models import Follow, Message
from users.models import Student


class StudentMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'full_name', 'student_number', 'course', 'year', 'profile_photo']


class FollowSerializer(serializers.ModelSerializer):
    follower = StudentMiniSerializer(read_only=True)
    following = StudentMiniSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = StudentMiniSerializer(read_only=True)
    receiver = StudentMiniSerializer(read_only=True)
    receiver_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'receiver',
            'receiver_id',
            'content',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['sender', 'is_read', 'created_at']

    def validate_receiver_id(self, value):
        try:
            Student.objects.get(pk=value)
        except Student.DoesNotExist:
            raise serializers.ValidationError('Student not found')
        return value

    def create(self, validated_data):
        receiver_id = validated_data.pop('receiver_id')
        receiver = Student.objects.get(pk=receiver_id)
        message = Message.objects.create(
            sender=self.context['request'].user,
            receiver=receiver,
            **validated_data
        )
        return message


class ConversationSerializer(serializers.ModelSerializer):
    other_student = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['other_student', 'last_message', 'unread_count']

    def get_other_student(self, obj):
        return StudentMiniSerializer(obj).data

    def get_last_message(self, obj):
        request_user = self.context['request'].user
        last = Message.objects.filter(
            sender__in=[obj, request_user],
            receiver__in=[obj, request_user]
        ).last()
        if last:
            return {
                'content': last.content,
                'created_at': last.created_at,
                'is_mine': last.sender == request_user
            }
        return None

    def get_unread_count(self, obj):
        request_user = self.context['request'].user
        return Message.objects.filter(
            sender=obj,
            receiver=request_user,
            is_read=False
        ).count()