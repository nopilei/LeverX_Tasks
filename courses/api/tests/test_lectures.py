from django.urls import reverse
from rest_framework import status
from functools import partial
from .utils import BaseTestCase, auth_and_request
from api import models


class LecturesTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_lecture = models.Lecture.objects.create(course=cls.test_course, theme='test')
        cls.lecture_data = {'theme': 'test', 'course': cls.test_course.pk,
                            'presentation': cls.test_lecture.presentation}


class TestListLectures(LecturesTest):
    """
    /lectures endpoint tests
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('lectures-list')

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_can_list_available_lectures(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn({**self.lecture_data, 'id': 1}, response.data)

    def test_lecturer_cannot_list_inaccessible_lectures(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)

    def test_student_can_list_available_lectures(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn({**self.lecture_data, 'id': 1}, response.data)

    def test_student_cannot_list_inaccessible_lectures(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)


class TestDetailLectures(LecturesTest):
    """
    /lectures/<id> endpoint test
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('lectures-detail', args=[cls.test_lecture.pk])

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_retrieve_lecture(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set({**self.lecture_data, 'id': 1}.items()))

    def test_lecturer_stranger_cannot_retrieve_inaccessible_lecture(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_can_retrieve_lecture(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set({**self.lecture_data, 'id': 1}.items()))

    def test_student_stranger_cannot_retrieve_inaccessible_lecture(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      PATCH
    # =======================================================

    def test_lecturer_member_can_modify_available_lecture_patch(self):
        request = partial(self.client.patch, self.url,
                          {'theme': self.test_lecture.theme}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set({**self.lecture_data, 'id': 1}.items()))

    def test_lecturer_stranger_cannot_modify_inaccessible_lecture_patch(self):
        request = partial(self.client.patch, self.url,
                          {'theme': self.test_lecture.theme}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_modify_available_lecture_patch(self):
        request = partial(self.client.patch, self.url,
                          {'theme': self.test_lecture.theme}, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_modify_inaccessible_lecture_patch(self):
        request = partial(self.client.patch, self.url,
                          {'theme': self.test_lecture.theme}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =======================================================
    #                      PUT
    # =======================================================

    def test_lecturer_member_can_modify_available_lecture_put(self):
        data = {'theme': self.test_lecture.theme, 'course': self.test_lecture.course.pk}
        request = partial(self.client.put, self.url, data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set({**self.lecture_data, 'id': 1}.items()))

    def test_lecturer_stranger_cannot_modify_inaccessible_lecture_put(self):
        data = {'theme': self.test_lecture.theme, 'course': self.test_lecture.course.pk}
        request = partial(self.client.put, self.url, data, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_modify_available_lecture_put(self):
        data = {'theme': self.test_lecture.theme, 'course': self.test_lecture.course.pk}
        request = partial(self.client.put, self.url, data, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_modify_inaccessible_lecture_put(self):
        data = {'theme': self.test_lecture.theme, 'course': self.test_lecture.course.pk}
        request = partial(self.client.put, self.url, data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =======================================================
    #                      DELETE
    # =======================================================

    def test_lecturer_member_can_delete_available_lecture(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lecturer_stranger_cannot_delete_inaccessible_lecture(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_delete_available_lecture(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_delete_available_lecture(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestHometasksLectures(LecturesTest):
    """
    /lectures/<id>/hometasks endpoint test
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_hometask = models.Hometask.objects.create(task='test', lecture=cls.test_lecture)
        cls.hometask_data = {'task':  cls.test_hometask.task, 'lecture': cls.test_lecture.pk}
        cls.url = reverse('lectures-process-child', args=[cls.test_lecture.pk])

    # =======================================================
    #                      POST
    # =======================================================

    def test_student_member_cannot_add_hometask_to_available_lecture(self):
        request = partial(self.client.post, self.url, self.hometask_data, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_add_hometask_to_inaccessible_lecture(self):
        request = partial(self.client.post, self.url, self.hometask_data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_member_can_add_hometask_to_available_lecture(self):
        request = partial(self.client.post, self.url, self.hometask_data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.items()), set({**self.hometask_data, 'id': 2}.items()))

    def test_lecturer_stranger_cannot_add_hometask_to_inaccessible_lecture(self):
        request = partial(self.client.post, self.url, self.hometask_data, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_list_hometasks_of_available_lecture(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn({**self.hometask_data, 'id': 1}, response.data)

    def test_student_member_can_list_hometasks_of_available_lecture(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn({**self.hometask_data, 'id': 1}, response.data)

    def test_lecturer_stranger_cannot_list_hometasks_of_inaccessible_lecture(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_stranger_cannot_list_hometasks_of_inaccessible_lecture(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
