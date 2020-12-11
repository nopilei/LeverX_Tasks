from django.urls import reverse
from rest_framework import status
from functools import partial
from .utils import BaseTestCase, auth_and_request
from api import models


class CoursesTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()


class TestCreateListCourses(CoursesTest):
    """
    /courses endpoint tests
    """
    def setUp(self):
        self.url = reverse('courses-list')
        self.data = {'title': 'test'}

    # =======================================================
    #                      POST
    # =======================================================

    def test_lecturer_can_create_new_course(self):
        request = partial(self.client.post, self.url, self.data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_cannot_create_new_course(self):
        request = partial(self.client.post, self.url, self.data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_list_all_available_courses(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn({**self.data, 'id': 1}, response.data)
        self.assertEqual(len(response.data), 1)

    def test_lecturer_stranger_cannot_list_inaccessible_courses(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.data, response.data)

    def test_student_stranger_cannot_list_inaccessible_courses(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.data, response.data)

    def test_student_member_can_retrieve_list_courses(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn({**self.data, 'id': 1}, response.data)
        self.assertEqual(len(response.data), 1)


class TestDetailCourses(CoursesTest):
    """
    /courses/<course_id> endpoint test
    """
    def setUp(self):
        self.url = reverse('courses-detail', args=[self.test_course.pk])
        self.data = {'title': self.test_course.title, 'id': self.test_course.pk}

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_retrieve_course(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.data.items()))

    def test_student_member_can_retrieve_course(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.data.items()))

    def test_lecturer_stranger_cannot_retrieve_inaccessible_course(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_stranger_cannot_retrieve_inaccessible_course(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      PATCH
    # =======================================================

    def test_lecturer_member_can_modify_available_course_patch(self):
        request = partial(self.client.patch, self.url,
                          {'title': self.test_course.title}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.data.items()))

    def test_lecturer_stranger_cannot_modify_inaccessible_course_patch(self):
        request = partial(self.client.patch, self.url,
                          {'title': self.test_course.title}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_modify_available_course_patch(self):
        request = partial(self.client.patch, self.url,
                          {'title': self.test_course.title}, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_modify_inaccessible_course_patch(self):
        request = partial(self.client.patch, self.url,
                          {'title': self.test_course.title}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =======================================================
    #                      PUT
    # =======================================================

    def test_lecturer_member_can_modify_available_course_put(self):
        request = partial(self.client.put, self.url,
                          {'title': self.test_course.title}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.data.items()))

    def test_lecturer_stranger_cannot_modify_inaccessible_course_put(self):
        request = partial(self.client.put, self.url,
                          {'title': self.test_course.title}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_modify_available_course_put(self):
        request = partial(self.client.put, self.url,
                          {'title': self.test_course.title}, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_modify_inaccessible_course_put(self):
        request = partial(self.client.put, self.url,
                          {'title': self.test_course.title}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =======================================================
    #                      DELETE
    # =======================================================

    def test_lecturer_member_can_delete_available_course(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lecturer_stranger_cannot_delete_inaccessible_course(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_delete_available_course(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_delete_available_course(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestLecturesCourses(CoursesTest):
    """
    /courses/<course_id>/lectures endpoint test
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_lecture = models.Lecture.objects.create(theme='test', course=cls.test_course)

    def setUp(self):
        self.url = reverse('courses-process-child', args=[self.test_course.pk])
        self.data = {'theme': self.test_lecture.theme, 'course': self.test_lecture.course.pk}

    # =======================================================
    #                      POST
    # =======================================================

    def test_student_member_cannot_add_lecture_to_course(self):
        request = partial(self.client.post, self.url, self.data, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_can_not_add_lecture_to_course(self):
        request = partial(self.client.post, self.url, self.data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_member_can_add_lecture_to_course(self):
        request = partial(self.client.post, self.url, self.data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.items()), set({**self.data, 'presentation': None, 'id': 2}.items()))

    def test_lecturer_stranger_cannot_add_lecture_to_course(self):
        request = partial(self.client.post, self.url, self.data, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_list_lectures_of_available_course(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn({**self.data, 'presentation': None, 'id': 1}, response.data)

    def test_student_member_can_list_lectures_of_available_course(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn({**self.data, 'presentation': None, 'id': 1}, response.data)

    def test_lecturer_stranger_cannot_list_lectures_of_inaccessible_course(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_stranger_can_list_lectures_of_inaccessible_course(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestUsersCourses(CoursesTest):
    """
    /courses/<course_id>/users endpoint test
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Membership.objects.create(user=cls.student_2, course=cls.test_course)

    def setUp(self):
        self.url = reverse('courses-process-user', args=[self.test_course.pk])

    # =======================================================
    #                      POST
    # =======================================================

    def test_lecturer_member_can_add_lecturer_to_available_course(self):
        request = partial(self.client.post, self.url, {'pk': self.lecturer_2.pk}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(models.Membership.objects.filter(user=self.lecturer_2).exists())

    def test_lecturer_member_can_add_student_to_available_course(self):
        request = partial(self.client.post, self.url, {'pk': self.student_1.pk}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(models.Membership.objects.filter(user=self.student_1).exists())

    def test_student_member_cannot_add_lecturer_to_available_course(self):
        request = partial(self.client.post, self.url, {'pk': self.lecturer_2.pk}, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_member_cannot_add_student_to_available_course(self):
        request = partial(self.client.post, self.url, {'pk': self.student_2.pk}, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_stranger_cannot_add_lecturer_to_inaccessible_course(self):
        models.Membership.objects.filter(user=self.lecturer_1).delete()
        request = partial(self.client.post, self.url, {'pk': self.lecturer_1.pk}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lecturer_stranger_cannot_add_student_to_inaccessible_course(self):
        request = partial(self.client.post, self.url, {'pk': self.student_1.pk}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_stranger_cannot_add_lecturer_to_inaccessible_course(self):
        models.Membership.objects.filter(user=self.lecturer_1).delete()
        request = partial(self.client.post, self.url, {'pk': self.lecturer_1.pk}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_add_student_to_inaccessible_course(self):
        request = partial(self.client.post, self.url, {'pk': self.student_1.pk}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =======================================================
    #                      DELETE
    # =======================================================

    def test_student_stranger_cannot_delete_lecturer_from_inaccessible_course(self):
        request = partial(self.client.delete, self.url, {'pk': self.lecturer_1.pk}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_delete_student_from_inaccessible_course(self):
        models.Membership.objects.create(user=self.student_1, course=self.test_course)
        request = partial(self.client.delete, self.url, {'pk': self.student_1.pk}, format='json')
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_member_can_delete_student_from_available_course(self):
        request = partial(self.client.delete, self.url, {'pk': self.student_2.pk}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(models.Membership.objects.filter(user=self.student_2).exists())

    def test_lecturer_member_cannot_delete_another_lecturer_from_available_course(self):
        request = partial(self.client.delete, self.url, {'pk': self.lecturer_1.pk}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request,
                                    {'user': self.lecturer_2, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_stranger_cannot_delete_lecturer_from_inaccessible_course(self):
        request = partial(self.client.delete, self.url, {'pk': self.lecturer_1.pk}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lecturer_stranger_cannot_delete_student_from_inaccessible_course(self):
        models.Membership.objects.create(user=self.student_1, course=self.test_course)
        request = partial(self.client.delete, self.url, {'pk': self.student_1.pk}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_delete_lecturer_from_available_course(self):
        request = partial(self.client.delete, self.url, {'pk': self.lecturer_1.pk}, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_member_cannot_delete_student_from_available_course(self):
        request = partial(self.client.post, self.url, {'pk': self.student_2.pk}, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)