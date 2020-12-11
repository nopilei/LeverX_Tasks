"""
Provides superclasses for project ViewSet classes

We can see some kind of hierarchy between project models. Lecture can attached to Course, Hometask - to Lecture,
FinishedTask - to Hometask, Comment - to FinishedTask. In other words:

Course <- Lecture
Lecture <- Hometask
Hometask <- FinishedTask
FinishedTask <- Comment

This feature allows us to highlight some set of common logic and put it in the base ViewSet classes.
"""

from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.serializers import ModelSerializer


class BaseModelViewSet(RetrieveUpdateDestroyAPIView, ListModelMixin, GenericViewSet):
    pass


class ParentModelViewSet(BaseModelViewSet):
    """
    Base class for ViewSets which work with objects (parents) that can have dependent objects (children)
    """

    #  Name of function which works with children
    CHILD_ACTION_NAME: str = 'process_child'
    #  Serializer for parent
    serializer_class: ModelSerializer = None
    #  Name of 'related_name' attribute in child's foreign key
    related_name: str = None
    #  Name of child's foreign key
    foreign_key_field_name: str = None
    #  Child's serializer
    child_serializer_class: ModelSerializer = None

    @action(methods=['GET', 'POST'],  detail=True)
    def process_child(self, *args, **kwargs):
        """
        Lists all parent's children or creates a new one
        """
        if self.request.method == 'GET':
            serializer = self.child_serializer_class(self.get_children(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            #  Populate 'user' field for child object
            self.request.data.update({self.foreign_key_field_name: self.get_object().pk})
            serializer = self.child_serializer_class(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_children(self):
        #  Get all children
        return getattr(self.get_object(), self.related_name).all()

    @classmethod
    def get_extra_actions(cls):
        """
        Sets proper 'url_path' attribute for 'process_child' action to build right urls
        """
        actions = super().get_extra_actions()
        for func in actions:
            func.url_path = cls.related_name if func.__name__ == cls.CHILD_ACTION_NAME else func.url_path
        return actions


