from django.urls import reverse
from rest_framework import status
from functools import partial
from .utils import BaseTestCase, auth_and_request
from api import models


class CommentsTest(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.test_lecture = models.Lecture.objects.create(course=cls.test_course, theme='test')
        cls.test_hometask = models.Hometask.objects.create(lecture=cls.test_lecture, task='test')
        cls.test_finished_task = models.FinishedTask.objects.create(task=cls.test_hometask,
                                                                    user=cls.student_1,
                                                                    answer='test')
        cls.test_student_comment = models.Comment.objects.create(finished_task=cls.test_finished_task,
                                                                 user=cls.student_1,
                                                                 comment='test')
        cls.student_comment_data = {'finished_task': cls.test_finished_task.pk,
                                    'user': cls.student_1.pk,
                                    'comment': cls.test_student_comment.comment,
                                    'id': 1}

        cls.test_lecturer_comment = models.Comment.objects.create(finished_task=cls.test_finished_task,
                                                                  user=cls.lecturer_1,
                                                                  comment='test')
        cls.lecturer_comment_data = {'finished_task': cls.test_finished_task.pk,
                                     'user': cls.lecturer_1.pk,
                                     'comment': cls.test_lecturer_comment.comment,
                                     'id': 2}


class TestListComments(CommentsTest):
    """
    /comments endpoint tests
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse('comments-list')

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_can_list_available_comments(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(self.student_comment_data, response.data)

    def test_lecturer_cannot_list_inaccessible_comments(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)

    def test_student_can_list_available_comments(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(self.student_comment_data, response.data)

    def test_student_cannot_list_inaccessible_comments(self):
        request = partial(self.client.get, self.url)
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)


class TestDetailComments(CommentsTest):
    """
    /comments/<id> endpoint test
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.student_url = reverse('comments-detail', args=[cls.test_student_comment.pk])
        cls.lecturer_url = reverse('comments-detail', args=[cls.test_lecturer_comment.pk])

    # =======================================================
    #                      GET
    # =======================================================

    def test_lecturer_member_can_retrieve_his_own_comment(self):
        request = partial(self.client.get, self.lecturer_url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.lecturer_comment_data.items()))

    def test_lecturer_member_can_retrieve_another_members_comment(self):
        request = partial(self.client.get, self.student_url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.student_comment_data.items()))

    def test_lecturer_stranger_cannot_retrieve_inaccessible_comment(self):
        request = partial(self.client.get, self.student_url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_can_retrieve_his_own_comment(self):
        request = partial(self.client.get, self.student_url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.student_comment_data.items()))

    def test_student_member_can_retrieve_another_members_comment(self):
        request = partial(self.client.get, self.lecturer_url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.lecturer_comment_data.items()))

    def test_student_stranger_cannot_retrieve_inaccessible_comment(self):
        request = partial(self.client.get, self.student_url)
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      PATCH
    # =======================================================

    def test_lecturer_member_can_modify_his_own_comment_patch(self):
        request = partial(self.client.patch, self.lecturer_url, {'comment': 'comment'}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set({**self.lecturer_comment_data, 'comment': 'comment'}.items()))

    def test_lecturer_member_cannot_modify_another_members_comment_patch(self):
        request = partial(self.client.patch, self.student_url, {'comment': 'comment'}, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_stranger_cannot_modify_inaccessible_comment_patch(self):
        request = partial(self.client.patch, self.student_url, {'comment': 'comment'}, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_can_modify_his_own_comment_patch(self):
        request = partial(self.client.patch, self.student_url, {'comment': 'comment'}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set({**self.student_comment_data, 'comment': 'comment'}.items()))

    def test_student_member_cannot_modify_another_members_comment_patch(self):
        request = partial(self.client.patch, self.lecturer_url, {'comment': 'comment'}, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_modify_inaccessible_comment_patch(self):
        request = partial(self.client.patch, self.lecturer_url, {'comment': 'comment'}, format='json')
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      PUT
    # =======================================================

    def test_lecturer_member_can_modify_his_own_comment_put(self):
        request = partial(self.client.put, self.lecturer_url, self.lecturer_comment_data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.lecturer_comment_data.items()))

    def test_lecturer_member_cannot_modify_another_members_comment_put(self):
        request = partial(self.client.put, self.student_url, self.lecturer_comment_data, format='json')
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_stranger_cannot_modify_inaccessible_comment_put(self):
        request = partial(self.client.put, self.student_url, self.lecturer_comment_data, format='json')
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_can_modify_his_own_comment_put(self):
        request = partial(self.client.patch, self.student_url, self.student_comment_data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set(response.data.items()), set(self.student_comment_data.items()))

    def test_student_member_cannot_modify_another_members_comment_put(self):
        request = partial(self.client.patch, self.lecturer_url, self.lecturer_comment_data, format='json')
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_modify_inaccessible_comment_put(self):
        request = partial(self.client.patch, self.lecturer_url, self.lecturer_comment_data, format='json')
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # =======================================================
    #                      DELETE
    # =======================================================

    def test_lecturer_member_can_delete_his_own_comment(self):
        request = partial(self.client.delete, self.lecturer_url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lecturer_member_cannot_delete_another_members_comment(self):
        request = partial(self.client.delete, self.student_url)
        response = auth_and_request(self.client, self.lecturer_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lecturer_stranger_cannot_delete_inaccessible_comment(self):
        request = partial(self.client.delete, self.student_url)
        response = auth_and_request(self.client, self.lecturer_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_member_can_delete_his_own_comment(self):
        request = partial(self.client.delete, self.student_url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_student_member_cannot_delete_another_members_comment(self):
        request = partial(self.client.patch, self.lecturer_url)
        response = auth_and_request(self.client, self.student_1, request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_stranger_cannot_delete_inaccessible_comment(self):
        request = partial(self.client.patch, self.lecturer_url)
        response = auth_and_request(self.client, self.student_2, request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)