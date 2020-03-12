from . import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import include, url

router = DefaultRouter()
router.register(r'schedules', views.ScheduleViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'discussions', views.DiscussionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
