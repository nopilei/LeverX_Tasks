from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    User. Can be either student or a lecturer
    """
    STUDENT = 'S'
    LECTURER = 'L'
    ROLES = [
        (STUDENT, 'Student'),
        (LECTURER, 'Lecturer')
    ]

    role = models.CharField(max_length=1, choices=ROLES, verbose_name='Role', default=LECTURER)
    available_courses = models.ManyToManyField('Course', through='Membership', related_name='users')

    @property
    def is_student(self):
        return self.STUDENT in self.role

    @property
    def is_lecturer(self):
        return self.LECTURER in self.role

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Course(models.Model):
    """
    Course. Can be created by lecturer.

    Lecturer can add other users to his course. After that this course and related objects, such
    as lectures or hometasks are marked as available for invited users.
    """
    title = models.CharField(max_length=100, verbose_name='Title')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


class Lecture(models.Model):
    """
    Lecture that must be attached to particular course. Can be created by lecturer.
    """
    theme = models.CharField(max_length=100, verbose_name='Theme')
    presentation = models.FileField(upload_to='presentations/',
                                    verbose_name='Presentation file', null=True, blank=True)
    course = models.ForeignKey(Course, related_name='lectures',
                               verbose_name='Course', on_delete=models.CASCADE)

    def __str__(self):
        return self.theme

    class Meta:
        verbose_name = 'Lecture'
        verbose_name_plural = 'Lectures'


class Hometask(models.Model):
    """
    Hometask that must attached to particular lecture. Can be created by lecturer
    """
    task = models.TextField(verbose_name='Task')
    lecture = models.ForeignKey(Lecture, related_name='hometasks',
                                verbose_name='Lecture', on_delete=models.CASCADE)

    def __str__(self):
        return self.task

    class Meta:
        verbose_name = 'Hometask'
        verbose_name_plural = 'Hometasks'


class FinishedTask(models.Model):
    """
    Hometask finished by user. Field 'result' can be modified by lecturer.
    """
    result = models.IntegerField(verbose_name='Result', null=True)
    task = models.ForeignKey(Hometask, related_name='finished_tasks',
                             verbose_name='Completed hometask', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='finished',
                             verbose_name='Student', on_delete=models.CASCADE)
    answer = models.TextField(verbose_name='Answer')

    def __str__(self):
        return f'{self.answer}: {self.result}'

    class Meta:
        verbose_name = 'Finished task'
        verbose_name_plural = 'Finished tasks'


class Membership(models.Model):
    """
    Intermediate table for connecting users and courses.
    When entry in this table is created, course and all dependent objects are marked as available for user
    """
    course = models.ForeignKey(Course, verbose_name='Course', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='User', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}:{self.course.title}'

    class Meta:
        verbose_name = 'Course membership'
        verbose_name_plural = 'Course memberships'


class Comment(models.Model):
    """
    Comment that can be left to finished task. Can be created by either lecturer or student
    """
    finished_task = models.ForeignKey(FinishedTask, verbose_name='Task',
                                      on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, related_name='comments',
                             verbose_name='User', on_delete=models.CASCADE)
    comment = models.TextField(verbose_name='Comment')

    def __str__(self):
        return self.comment

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
