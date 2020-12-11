from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

schema_view = get_schema_view(
   openapi.Info(
      title="Courses API",
      default_version='v1',
      description="API for creating and managing courses",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
router = SimpleRouter(trailing_slash=False)

router.register('courses', views.CourseViewSet, basename='courses')
router.register('lectures', views.LectureViewSet, basename='lectures')
router.register('hometasks', views.HometaskViewSet, basename='hometasks')
router.register('comments', views.CommentViewSet, basename='comments')
router.register('finished_tasks', views.FinishedTaskViewSet, basename='finished_tasks')
router.register('users', views.UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
