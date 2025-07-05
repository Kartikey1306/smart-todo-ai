from django.urls import path
from . import views

urlpatterns = [
    path('trigger-recommendations/', views.trigger_recommendations, name='ai-trigger-recommendations'),
    path('schedule-suggestions/', views.get_schedule_suggestions, name='ai-schedule-suggestions'),
]
