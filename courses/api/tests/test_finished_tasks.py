from django.urls import reverse
from rest_framework import status
from functools import partial
from .utils import BaseTestCase, auth_and_request
from api import models


class FinishedTasksTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_lecture = models.Lecture.objects.create(course=cls.test_course, theme='test')
        cls.test_hometask = models.Hometask.objects.create(lecture=cls.test_lecture, task='test')
        cls.test_finished_task = models.FinishedTask.objects.create(task=cls.test_hometask,
                                                                    user=cls.student_1,
                                                                    answer='test')
        cls.finished_task_data = {'task': cls.test_hometask.pk,
                                  'user': cls.student_1.pk,
                                  'answer': cls.test_finished_task.answer,
                                  'result': None,
                                  'id': 1}


class TestListFinishedTasks(FinishedTasksTest):
    """
    /finished_tasks endpoint tests
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('finished_tasks-list')

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_can_list_available_finished_tasks(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn(self.finished_task_data, response.data)

    def test_lecturer_cannot_list_inaccessible_finished_tasks(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)

    def test_student_can_list_his_own_available_finished_tasks(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request,
                                    {'user': self.student_1, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn(self.finished_task_data, response.data)

    def test_student_cannot_list_inaccessible_finished_tasks(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)


class TestDetailFinishedTasks(FinishedTasksTest):
    """
    /finished_tasks/<id> endpoint test
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('finished_tasks-detail', args=[cls.test_finished_task.pk])

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_retrieve_finished_task(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.finished_task_data.items()))

    def test_lecturer_stranger_cannot_retrieve_inaccessible_finished_task(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_can_retrieve_his_own_finished_task(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.finished_task_data.items()))

    def test_student_stranger_cannot_retrieve_inaccessible_finished_task(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_2, request,
                                    {'user': self.student_2, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      PATCH
    # =======================================================

    def test_lecturer_member_can_set_result_for_available_finished_task(self):
        request = partial(self.client.patch, self.url,
                          {'result': 10}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set({'id': 1, 'result': 10}.items()))

    def test_lecturer_stranger_cannot_set_result_for_inaccessible_finished_task(self):
        request = partial(self.client.patch, self.url,
                          {'result': 10}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_cannot_set_result_for_his_own_finished_task(self):
        request = partial(self.client.patch, self.url,
                          {'result': 10}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_modify_inaccessible_finished_task(self):
        request = partial(self.client.patch, self.url,
                          {'task': self.test_hometask.task}, format='json')
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_member_cannot_modify_other_fields(self):
        request = partial(self.client.patch, self.url,
                          {'answer': '10'}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('answer', response.data)

    # =======================================================
    #                      PUT
    # =======================================================

    def test_put_is_not_allowed_for_lecturers(self):
        request = partial(self.client.put, self.url, self.finished_task_data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_is_not_allowed_for_students(self):
        request = partial(self.client.put, self.url, self.finished_task_data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # =======================================================
    #                      DELETE
    # =======================================================

    def test_lecturer_member_cannot_delete_available_finished_task(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_stranger_cannot_delete_inaccessible_hometask(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_member_can_delete_his_own_finished_task(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_student_stranger_cannot_delete_inaccessible_finished_task(self):
        request = partial(self.client.delete, self.url, format='json')
        response = auth_and_request(self.client, self.student_2, request,
                                    {'user': self.student_2, 'course': self.test_course})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestFinishedTasksComments(FinishedTasksTest):
    """
    /finished_tasks/<id>/comments endpoint test
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_comment = models.Comment.objects.create(user=cls.student_1,
                                                         finished_task=cls.test_finished_task,
                                                         comment='test')
        cls.comment_data = {'finished_task': cls.test_finished_task.pk, 'comment': cls.test_comment.comment}
        cls.url = reverse('finished_tasks-process-child', args=[cls.test_finished_task.pk])

    # =======================================================
    #                      POST
    # =======================================================

    def test_student_can_add_comment_to_his_own_finished_task(self):
        request = partial(self.client.post, self.url, self.comment_data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_student_stranger_cannot_add_comment_to_inaccessible_finished_task(self):
        request = partial(self.client.post, self.url, self.comment_data, format='json')
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lecturer_member_can_add_comment_to_available_finished_task(self):
        request = partial(self.client.post, self.url, self.comment_data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lecturer_stranger_cannot_add_comment_to_inaccessible_finished_task(self):
        request = partial(self.client.post, self.url, self.comment_data, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_list_all_comments_of_available_finished_task(self):
        request = partial(self.client.post, self.url, self.comment_data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn({**self.comment_data, 'id': 1, 'user': self.student_1.pk}, response.data)
        self.assertIn({**self.comment_data, 'id': 2, 'user': self.lecturer_1.pk}, response.data)

    def test_student_member_can_list_all_comments_of_his_own_finished_task(self):
        request = partial(self.client.post, self.url, self.comment_data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn({**self.comment_data, 'id': 1, 'user': self.student_1.pk}, response.data)
        self.assertIn({**self.comment_data, 'id': 2, 'user': self.lecturer_1.pk}, response.data)

    def test_lecturer_stranger_cannot_list_comments_of_inaccessible_finished_task(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_stranger_cannot_list_comments_of_inaccessible_finished_task(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
