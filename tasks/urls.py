from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskCategoryViewSet, ContextEntryViewSet, TaskRecommendationViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', TaskCategoryViewSet, basename='category')
router.register(r'context', ContextEntryViewSet, basename='context')
router.register(r'recommendations', TaskRecommendationViewSet, basename='recommendation')
router.register(r'profile', UserProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
