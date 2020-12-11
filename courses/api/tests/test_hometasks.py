from django.urls import reverse
from rest_framework import status
from functools import partial
from .utils import BaseTestCase, auth_and_request
from api import models


class HometasksTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_lecture = models.Lecture.objects.create(course=cls.test_course, theme='test')
        cls.test_hometask = models.Hometask.objects.create(lecture=cls.test_lecture, task='test')
        cls.hometask_data = {'task': cls.test_hometask.task,
                             'lecture': cls.test_lecture.pk,
                             'id': cls.test_hometask.pk}


class TestListHometasks(HometasksTest):
    """
    /hometasks endpoint tests
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('hometasks-list')

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_can_list_available_hometasks(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn(self.hometask_data, response.data)

    def test_lecturer_cannot_list_inaccessible_hometasks(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)

    def test_student_can_list_available_hometasks(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn(self.hometask_data, response.data)

    def test_student_cannot_list_inaccessible_hometasks(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)


class TestDetailHometasks(HometasksTest):
    """
    /hometasks/<id> endpoint test
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('hometasks-detail', args=[cls.test_hometask.pk])

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_retrieve_hometask(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.hometask_data.items()))

    def test_lecturer_stranger_cannot_retrieve_inaccessible_hometask(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_can_retrieve_hometask(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.hometask_data.items()))

    def test_student_stranger_cannot_retrieve_inaccessible_hometask(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      PATCH
    # =======================================================

    def test_lecturer_member_can_modify_available_hometask_patch(self):
        request = partial(self.client.patch, self.url,
                          {'task': self.test_hometask.task}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.hometask_data.items()))

    def test_lecturer_stranger_cannot_modify_inaccessible_hometask_patch(self):
        request = partial(self.client.patch, self.url,
                          {'task': self.test_hometask.task}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_modify_available_hometask_patch(self):
        request = partial(self.client.patch, self.url,
                          {'task': self.test_hometask.task}, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_modify_inaccessible_hometask_patch(self):
        request = partial(self.client.patch, self.url,
                          {'task': self.test_hometask.task}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =======================================================
    #                      PUT
    # =======================================================

    def test_lecturer_member_can_modify_available_hometask_put(self):
        request = partial(self.client.put, self.url, self.hometask_data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.hometask_data.items()))

    def test_lecturer_stranger_cannot_modify_inaccessible_hometask_put(self):
        request = partial(self.client.put, self.url, self.hometask_data, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_modify_available_hometask_put(self):
        request = partial(self.client.put, self.url, self.hometask_data, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_modify_inaccessible_hometask_put(self):
        request = partial(self.client.put, self.url, self.hometask_data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =======================================================
    #                      DELETE
    # =======================================================

    def test_lecturer_member_can_delete_available_hometask(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lecturer_stranger_cannot_delete_inaccessible_hometask(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_delete_available_hometask(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_delete_available_hometask(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestHometasksFinishedTasks(HometasksTest):
    """
    /hometasks/<id>/finished_tasks endpoint test
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_finished_task = models.FinishedTask.objects.create(user=cls.student_1,
                                                                    task=cls.test_hometask,
                                                                    answer='test')
        cls.finished_task_data = {'task': cls.test_finished_task.pk, 'answer': cls.test_finished_task.answer}
        cls.url = reverse('hometasks-process-child', args=[cls.test_hometask.pk])

    # =======================================================
    #                      POST
    # =======================================================

    def test_student_member_can_add_finished_task_to_available_hometask(self):
        request = partial(self.client.post, self.url, self.finished_task_data, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_stranger_cannot_add_finished_task_to_inaccessible_hometask(self):
        request = partial(self.client.post, self.url, self.finished_task_data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lecturer_member_cannot_add_finished_task_to_available_hometask(self):
        request = partial(self.client.post, self.url, self.finished_task_data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_stranger_cannot_add_finished_task_to_available_hometask(self):
        request = partial(self.client.post, self.url, self.finished_task_data, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_cannot_add_finished_task_with_the_result(self):
        request = partial(self.client.post, self.url, {**self.finished_task_data, 'result': 10}, format='json')
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.data['result'], None)

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_list_all_finished_tasks_of_available_hometask(self):
        request = partial(self.client.post, self.url, self.finished_task_data, format='json')
        auth_and_request(self.client, self.student_2, request,
                         {'user': self.student_2, 'course': self.test_course})
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn({**self.finished_task_data, 'id': 1, 'user': self.student_1.pk, 'result': None}, response.data)
        self.assertIn({**self.finished_task_data, 'id': 2, 'user': self.student_2.pk, 'result': None}, response.data)

    def test_student_member_can_list_his_own_finished_tasks_of_available_hometask(self):
        request = partial(self.client.post, self.url, self.finished_task_data, format='json')
        auth_and_request(self.client, self.student_2, request,
                         {'user': self.student_2, 'course': self.test_course})
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn({**self.finished_task_data, 'id': 1, 'user': self.student_1.pk, 'result': None}, response.data)
        self.assertNotIn({**self.finished_task_data, 'id': 2, 'user': self.student_2.pk, 'result': None}, response.data)

    def test_lecturer_stranger_cannot_list_finished_tasks_of_inaccessible_hometask(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_stranger_cannot_list_finished_tasks_of_inaccessible_hometask(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
