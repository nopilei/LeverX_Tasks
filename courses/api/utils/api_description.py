"""
Decorators to set proper description for Swagger UI
"""
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import types
import functools


def _copy_func(f):
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
                           argdefs=f.__defaults__,
                           closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g


def _suppress_swagger_attribute_error(func, model):
    def wrapper(view):
        if getattr(view, 'swagger_fake_view', False):
            return model.objects.none()
        return func(view)
    return wrapper

# ================================================
#           COURSES
# ================================================


def courses_api_description(model):
    def decorator(klass):
        klass = method_decorator(name='list', decorator=swagger_auto_schema(
                                operation_description="List all available courses.",
                                responses={200: 'All available courses returned'})
                                 )(klass)
        klass = method_decorator(name='create', decorator=swagger_auto_schema(
                                operation_description="Create new course.",
                                responses={
                                    201: 'New course created and fully available for you.',
                                    403: 'You are not allowed to create new courses.'})
                                 )(klass)
        klass = method_decorator(name='retrieve', decorator=swagger_auto_schema(
                                operation_description="Retrieve available course.",
                                responses={
                                    200: 'Course retrieved.',
                                    404: 'Could not find available course by id provided.'})
                                 )(klass)
        klass = method_decorator(name='update', decorator=swagger_auto_schema(
                                operation_description="Update available course.",
                                responses={
                                    200: 'Course updated.',
                                    403: 'You are not allowed to modify courses.',
                                    404: 'Could not update available course by id provided.'})
                                 )(klass)
        klass = method_decorator(name='partial_update', decorator=swagger_auto_schema(
                                operation_description="Update available course.",
                                responses={
                                    200: 'Course updated.',
                                    403: 'You are not allowed to modify courses.',
                                    404: 'Could not update available course by id provided.'})
                                 )(klass)
        klass = method_decorator(name='destroy', decorator=swagger_auto_schema(
                                operation_description="Delete available course.",
                                responses={
                                    204: 'Course deleted.',
                                    403: 'You are not allowed to delete courses.',
                                    404: 'Could not delete available course by id provided.'})
                                 )(klass)
        klass.get_queryset = _suppress_swagger_attribute_error(klass.get_queryset, model)
        klass.process_child = _copy_func(klass.process_child)
        klass.process_child = courses_lectures_api_description(klass.process_child)
        klass.process_user = courses_users_api_description(klass.process_user)
        return klass
    return decorator


def courses_lectures_api_description(func):
    func = swagger_auto_schema(
        operation_description="List lectures of available course.",
        method='get',
        responses={
            200: 'Retrieved all lectures of this courses.',
            404: 'Could not list lectures of available course by id provided.'})(func)

    func = swagger_auto_schema(
        operation_description="Add lecture to course.",
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title='Lecture',
            properties={
                'theme': openapi.Schema(type=openapi.TYPE_STRING,
                                        title='Theme'),
                'course': openapi.Schema(type=openapi.TYPE_INTEGER,
                                         title='Course'),
                'presentation': openapi.Schema(type=openapi.TYPE_FILE,
                                               title='Presentation'),
            },
            required=['theme', 'course']),
        responses={
            201: 'Added lecture to course.',
            403: 'You are not allowed to add lectures.',
            404: 'Could not add lecture to available course by id provided.'})(func)
    return func


def courses_users_api_description(func):
    func = swagger_auto_schema(
        operation_description="Add user to course.",
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title='User',
            properties={
                'pk': openapi.Schema(type=openapi.TYPE_INTEGER,
                                     description='Id of user to add', title='id')
            },
            required=['pk']
        ),
        responses={
            201: 'Added user to course.',
            403: 'You are not allowed to add users to courses.',
            404: 'Could not add user to available course by id provided.'})(func)

    func = swagger_auto_schema(
        operation_description="Delete user from course.",
        method='delete',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title='User',
            properties={
                'pk': openapi.Schema(type=openapi.TYPE_INTEGER,
                                     description='Id of user to delete', title='id')
            },
            required=['pk']
        ),
        responses={
            201: 'Deleted student from course.',
            403: 'You are not allowed to delete this user.',
            404: 'Could not delete user from available course by id provided.'})(func)
    return func

# ================================================
#           LECTURES
# ================================================


def lectures_api_description(model):
    def decorator(klass):
        klass = method_decorator(name='list', decorator=swagger_auto_schema(
                                operation_description="List all available lectures.",
                                responses={200: 'All available lectures returned'})
                                 )(klass)
        klass = method_decorator(name='retrieve', decorator=swagger_auto_schema(
                                operation_description="Retrieve available lecture.",
                                responses={
                                    200: 'Lecture retrieved.',
                                    404: 'Could not retrieve available lecture by id provided.'})
                                 )(klass)
        klass = method_decorator(name='update', decorator=swagger_auto_schema(
                                operation_description="Update available lecture.",
                                responses={
                                    200: 'Lecture updated.',
                                    403: 'You are not allowed to modify lectures.',
                                    404: 'Could not update available lecture by id provided.'})
                                 )(klass)
        klass = method_decorator(name='partial_update', decorator=swagger_auto_schema(
                                operation_description="Update available lecture.",
                                responses={
                                    200: 'Lecture updated.',
                                    403: 'You are not allowed to modify lectures.',
                                    404: 'Could not update available lecture by id provided.'})
                                 )(klass)
        klass = method_decorator(name='destroy', decorator=swagger_auto_schema(
                                operation_description="Delete available lecture.",
                                responses={
                                    204: 'Lecture deleted.',
                                    403: 'You are not allowed to delete lectures.',
                                    404: 'Could not delete available lecture by id provided.'})
                                 )(klass)
        klass.get_queryset = _suppress_swagger_attribute_error(klass.get_queryset, model)
        klass.process_child = _copy_func(klass.process_child)
        klass.process_child = lectures_hometasks_api_description(klass.process_child)
        return klass
    return decorator


def lectures_hometasks_api_description(func):
    func = swagger_auto_schema(
        operation_description="Add hometask to lecture.",
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title='Hometask',
            properties={
                'task': openapi.Schema(type=openapi.TYPE_STRING,
                                       title='Task'),
                'lecture': openapi.Schema(type=openapi.TYPE_INTEGER,
                                          title='Lecture'),
            },
            required=['task', 'lecture'],
        ),
        responses={
            201: 'Added hometask to lecture.',
            403: 'You are not allowed to add hometasks to lectures.',
            404: 'Could not add hometask to available lecture by id provided.'})(func)

    func = swagger_auto_schema(
        operation_description="List hometasks of available lecture.",
        method='get',
        responses={
            200: 'Retrieved all hometasks of this lecture.',
            404: 'Could not list hometasks of available lecture by id provided.'})(func)
    return func


# ================================================
#           HOMETASKS
# ================================================

def hometasks_api_description(model):
    def decorator(klass):
        klass = method_decorator(name='list', decorator=swagger_auto_schema(
                                operation_description="List all available hometasks.",
                                responses={200: 'All available hometasks returned'})
                                 )(klass)
        klass = method_decorator(name='retrieve', decorator=swagger_auto_schema(
                                operation_description="Retrieve available hometask.",
                                responses={
                                    200: 'Hometask retrieved.',
                                    404: 'Could not retrieve available hometask by id provided.'})
                                 )(klass)
        klass = method_decorator(name='update', decorator=swagger_auto_schema(
                                operation_description="Update available hometask.",
                                responses={
                                    200: 'Hometask updated.',
                                    403: 'You are not allowed to modify hometasks.',
                                    404: 'Could not update available hometask by id provided.'})
                                 )(klass)
        klass = method_decorator(name='partial_update', decorator=swagger_auto_schema(
                                operation_description="Update available hometask.",
                                responses={
                                    200: 'Hometask updated.',
                                    403: 'You are not allowed to modify hometasks.',
                                    404: 'Could not update available hometask by id provided.'})
                                 )(klass)
        klass = method_decorator(name='destroy', decorator=swagger_auto_schema(
                                operation_description="Delete available hometask.",
                                responses={
                                    204: 'Hometask deleted.',
                                    403: 'You are not allowed to delete hometasks.',
                                    404: 'Could not delete available hometask by id provided.'})
                                 )(klass)
        klass.get_queryset = _suppress_swagger_attribute_error(klass.get_queryset, model)
        klass.process_child = _copy_func(klass.process_child)
        klass.process_child = hometasks_finished_tasks_api_description(klass.process_child)
        return klass
    return decorator


def hometasks_finished_tasks_api_description(func):
    func = swagger_auto_schema(
        operation_description="Add finished task to hometask.",
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title='FinishedTask',
            properties={
                'answer': openapi.Schema(type=openapi.TYPE_STRING,
                                         title='Answer'),
                'task': openapi.Schema(type=openapi.TYPE_INTEGER,
                                       title='Hometask'),
            },
            required=['answer', 'task'],
        ),
        responses={
            201: 'Added finished task to hometask.',
            403: 'You are not allowed to add finished tasks.',
            404: 'Could not add finished task to available hometask by id provided.'})(func)

    func = swagger_auto_schema(
        operation_description="List finished tasks of available hometask.",
        method='get',
        responses={
            200: 'Retrieved all finished tasks for this hometask.',
            404: 'Could not list finished tasks of available hometask by id provided.'})(func)
    return func


# ================================================
#           FINISHED TASKS
# ================================================

def finished_task_api_description(model):
    def decorator(klass):
        klass = method_decorator(name='list', decorator=swagger_auto_schema(
                                operation_description="List all available finished tasks."
                                                      " As a lecturer, you'll get finished tasks of all users, who has "
                                                      "access to the same courses as you. "
                                                      "As a student, you will get your finished tasks.",
                                responses={200: 'All available finished tasks returned'})
                                 )(klass)
        klass = method_decorator(name='retrieve', decorator=swagger_auto_schema(
                                operation_description="Retrieve available finished task.",
                                responses={
                                    200: 'Finished task retrieved.',
                                    404: 'Could not retrieve available finished task by id provided.'})
                                 )(klass)
        klass = method_decorator(name='partial_update', decorator=swagger_auto_schema(
                                operation_description="Update available finished task. "
                                                      "You can only set result as a lecturer",
                                responses={
                                    200: 'Result updated.',
                                    403: 'You are not allowed to modify finished tasks.',
                                    404: 'Could not update available finished task by id provided.'})
                                 )(klass)
        klass = method_decorator(name='update', decorator=swagger_auto_schema(
                                operation_description="PUT method is not allowed.",
                                responses={
                                    402: 'PUT is not allowed'})
                                 )(klass)
        klass = method_decorator(name='destroy', decorator=swagger_auto_schema(
                                operation_description="Delete available finished task."
                                                      " Only students can delete their finished tasks",
                                responses={
                                    204: 'Finished task deleted.',
                                    403: 'You are not allowed to delete finished tasks.',
                                    404: 'Could not delete available finished task by id provided.'})
                                 )(klass)
        klass.get_queryset = _suppress_swagger_attribute_error(klass.get_queryset, model)
        klass.process_child = _copy_func(klass.process_child)
        klass.process_child = finished_tasks_comments_api_description(klass.process_child)
        return klass
    return decorator


def finished_tasks_comments_api_description(func):
    func = swagger_auto_schema(
        operation_description="Add comment to finished task."
                              " Both lecturers and students can add comments to available finished task",
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title='Comment',
            properties={
                'finished_task': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                title='Finished task'),
                'comment': openapi.Schema(type=openapi.TYPE_STRING,
                                          title='Comment'),
            },
            required=['finished_task', 'comment'],
        ),
        responses={
            201: 'Added comment to finished task.',
            404: 'Could not add comment to available finished task by id provided.'})(func)

    func = swagger_auto_schema(
        operation_description="List comments of available finished task.",
        method='get',
        responses={
            200: 'Retrieved all comments of available finished task.',
            404: 'Could not list comments of available finished task by id provided.'})(func)
    return func


# ================================================
#           COMMENTS
# ================================================

def comments_api_description(model):
    def decorator(klass):
        klass = method_decorator(name='list', decorator=swagger_auto_schema(
                                operation_description="List all available comments.",
                                responses={200: 'All available comments returned'})
                                 )(klass)
        klass = method_decorator(name='retrieve', decorator=swagger_auto_schema(
                                operation_description="Retrieve available comment.",
                                responses={
                                    200: 'Comment retrieved.',
                                    404: 'Could not retrieve available comment by id provided.'})
                                 )(klass)
        klass = method_decorator(name='update', decorator=swagger_auto_schema(
                                operation_description="Update available comment."
                                                      " Only author of the comment can modify it",
                                responses={
                                    200: 'Comment updated.',
                                    403: 'You are not allowed to modify this comment.',
                                    404: 'Could not update available comment by id provided.'})
                                 )(klass)
        klass = method_decorator(name='partial_update', decorator=swagger_auto_schema(
                                operation_description="Update available hometask."
                                                      " Only owner of the comment can modify it",
                                responses={
                                    200: 'Comment updated.',
                                    403: 'You are not allowed to modify this comment.',
                                    404: 'Could not update available comment by id provided.'})
                                 )(klass)
        klass = method_decorator(name='destroy', decorator=swagger_auto_schema(
                                operation_description="Delete available comment. "
                                                      "Only author of the comment can delete it",
                                responses={
                                    204: 'Comment deleted.',
                                    403: 'You are not allowed to delete this comment.',
                                    404: 'Could not delete available comment by id provided.'})
                                 )(klass)
        klass.get_queryset = _suppress_swagger_attribute_error(klass.get_queryset, model)
        return klass
    return decorator


# ================================================
#           USERS
# ================================================

def users_api_description(klass):
    klass = method_decorator(name='create', decorator=swagger_auto_schema(
                            operation_description="Create new lecturer or student.",
                            responses={201: 'User created'})
                             )(klass)
    return klass