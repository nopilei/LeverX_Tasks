from rest_framework import serializers
from . import models


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ['id', 'title']


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lecture
        fields = ['id', 'theme', 'presentation', 'course']


class HometaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Hometask
        fields = ['id', 'task', 'lecture']


class FinishedTaskSerializer(serializers.ModelSerializer):
    result = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.FinishedTask
        fields = ['id', 'task', 'user', 'result', 'answer']


class FinishedTaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FinishedTask
        fields = ['id', 'result']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ['id', 'finished_task', 'user', 'comment']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['id', 'username', 'password', 'role']

    def create(self, validated_data):
        user = models.User.objects.create_user(**validated_data)
        return user