from api import models
from functools import partial
from typing import Optional
from rest_framework.test import APITestCase


class BaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lecturer_1 = models.User.objects.create_user(username='lecturer_1', password='lecturer_1', role='L')
        cls.lecturer_2 = models.User.objects.create_user(username='lecturer_2', password='lecturer_2', role='L')
        cls.student_1 = models.User.objects.create_user(username='student_1', password='student_1', role='S')
        cls.student_2 = models.User.objects.create_user(username='student_2', password='student_2', role='S')
        cls.test_course = models.Course.objects.create(title='test')
        models.Membership.objects.create(user=cls.lecturer_1, course=cls.test_course)


def auth_and_request(client, user, request: partial, membership_args: Optional[dict] = None):
    client.force_authenticate(user)
    if membership_args:
        models.Membership.objects.create(**membership_args)
    return request()