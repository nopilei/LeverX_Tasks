"""
All API views
"""
from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from . import serializers, models
from .utils import api_description, base_viewsets, permissions


@api_description.courses_api_description(models.Course)
class CourseViewSet(base_viewsets.ParentModelViewSet, mixins.CreateModelMixin):
    """
    List all available courses
    Create/Read/Delete available course
    Add/delete user to/from available course
    List all related lectures
    Add new lecture
    """
    serializer_class = serializers.CourseSerializer
    related_name = 'lectures'
    foreign_key_field_name = 'course'
    child_serializer_class = serializers.LectureSerializer
    permission_classes = [permissions.IsLecturerOrStudentSafe]
    #  Lookup field for working with users
    user_lookup = 'pk'

    @action(methods=['POST', 'DELETE'], detail=True, url_path='users')
    def process_user(self, *args, **kwargs):
        """
        Add new user to course or delete student
        """
        course = self.get_object()
        #  Ensure that we've got proper user data
        filter_params = {self.user_lookup: self.request.data.get(self.user_lookup, -1)}
        user = get_object_or_404(models.User, **filter_params)
        if self.request.method == 'POST':
            models.Membership.objects.create(user=user, course=course)
            return Response(status=status.HTTP_200_OK)
        elif user.is_student:
            models.Membership.objects.filter(user=user, course=course).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            #  Lecturer cannot delete another lecturer from the course
            return Response(status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        return self.request.user.available_courses.all()

    def perform_create(self, serializer):
        course = serializer.save()
        models.Membership.objects.create(user=self.request.user, course=course)


@api_description.lectures_api_description(models.Lecture)
class LectureViewSet(base_viewsets.ParentModelViewSet):
    """
    List all available lectures
    Create/Read/Delete available lecture
    List all related hometasks
    Create new hometask
    """
    related_name = 'hometasks'
    foreign_key_field_name = 'lecture'
    child_serializer_class = serializers.HometaskSerializer
    serializer_class = serializers.LectureSerializer
    permission_classes = [permissions.IsLecturerOrStudentSafe]

    def get_queryset(self):
        courses = self.request.user.available_courses.all()
        return models.Lecture.objects.filter(course__in=courses)


@api_description.hometasks_api_description(models.Hometask)
class HometaskViewSet(base_viewsets.ParentModelViewSet):
    """
    List all available hometasks
    Create/Read/Delete available hometask
    List all related finished tasks
    Create new finished task
    """
    related_name = 'finished_tasks'
    foreign_key_field_name = 'task'
    child_serializer_class = serializers.FinishedTaskSerializer
    serializer_class = serializers.HometaskSerializer
    permission_classes = [permissions.IsLecturerOrStudentSafe]

    @action(methods=['POST', 'GET'], detail=True, permission_classes=[permissions.FinishedTasksAccess])
    def process_child(self, *args, **kwargs):
        self.request.data.update({'user': self.request.user.pk})
        return super().process_child()

    def get_queryset(self):
        courses = self.request.user.available_courses.all()
        return models.Hometask.objects.filter(lecture__course__in=courses)

    def get_children(self):
        queryset = super().get_children()
        if self.request.user.is_student:
            queryset = queryset.filter(user=self.request.user)
        return queryset


@api_description.finished_task_api_description(models.FinishedTask)
class FinishedTaskViewSet(base_viewsets.ParentModelViewSet):
    """
    List all available finished tasks
    Create/Read/Delete available finished task
    List all related comments
    Create new comment
    """
    related_name = 'comments'
    foreign_key_field_name = 'finished_task'
    child_serializer_class = serializers.CommentSerializer
    serializer_class = serializers.FinishedTaskSerializer
    permission_classes = [permissions.FinishedTasksAccess]

    @action(methods=['POST', 'GET'], detail=True, permission_classes=[permissions.IsLecturerOrStudent])
    def process_child(self, *args, **kwargs):
        self.request.data.update({'user': self.request.user.pk})
        return super().process_child()

    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = serializers.FinishedTaskResultSerializer
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.is_student:
            return self.request.user.finished.all()
        else:
            courses = self.request.user.available_courses.all()
            return models.FinishedTask.objects.filter(task__lecture__course__in=courses)


@api_description.comments_api_description(models.Comment)
class CommentViewSet(base_viewsets.BaseModelViewSet):
    """
    List all available comments
    Create/Read/Delete available comment
    """
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.CommentsAccess]

    def get_queryset(self):
        if self.request.user.is_student:
            finished_tasks = self.request.user.finished.all()
            return models.Comment.objects.filter(finished_task__in=finished_tasks)
        else:
            courses = self.request.user.available_courses.all()
            return models.Comment.objects.filter(finished_task__task__lecture__course__in=courses)


@api_description.users_api_description
class UserViewSet(CreateAPIView, GenericViewSet):
    """
    Create new user
    """
    authentication_classes = []
    serializer_class = serializers.UserSerializer