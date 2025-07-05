from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .tasks import generate_task_recommendations_for_user
from .ai_pipeline import AIPipeline
from tasks.models import Task, TimeBlockSuggestion
from tasks.serializers import TimeBlockSuggestionSerializer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_recommendations(request):
    """
    Triggers a background job to generate new task recommendations for the user.
    """
    try:
        generate_task_recommendations_for_user.delay(request.user.id)
        return Response(
            {'message': 'Task recommendation process has been started in the background.'},
            status=status.HTTP_202_ACCEPTED
        )
    except Exception as e:
        logger.error(f"Error triggering recommendations for user {request.user.id}: {e}")
        return Response(
            {'error': 'Failed to start recommendation process'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_schedule_suggestions(request):
    """
    Generates AI-powered time-blocking suggestions for a given day.
    """
    try:
        schedule_date_str = request.data.get('date')
        if not schedule_date_str:
            return Response({'error': 'Date is required in YYYY-MM-DD format.'}, status=status.HTTP_400_BAD_REQUEST)
        
        schedule_date = datetime.strptime(schedule_date_str, '%Y-%m-%d').date()

        # Fetch pending tasks and existing events (placeholder)
        pending_tasks = list(Task.objects.filter(
            user=request.user,
            status__in=['pending', 'in_progress']
        ).values('id', 'title', 'priority', 'estimated_duration'))

        # In a real app, this would fetch from an integrated calendar
        existing_events = request.data.get('existing_events', [])

        pipeline = AIPipeline(user_id=request.user.id)
        suggestions = pipeline.generate_schedule_suggestions(pending_tasks, schedule_date, existing_events)

        # Clear old suggestions for this day
        TimeBlockSuggestion.objects.filter(user=request.user, suggested_start_time__date=schedule_date).delete()

        # Create new suggestion objects
        created_suggestions = []
        for sug in suggestions:
            try:
                task = Task.objects.get(id=sug['task_id'])
                new_sug = TimeBlockSuggestion.objects.create(
                    user=request.user,
                    task=task,
                    suggested_start_time=datetime.fromisoformat(sug['suggested_start_time'].replace('Z', '+00:00')),
                    suggested_end_time=datetime.fromisoformat(sug['suggested_end_time'].replace('Z', '+00:00')),
                    reasoning=sug.get('reasoning', '')
                )
                created_suggestions.append(new_sug)
            except (Task.DoesNotExist, KeyError, ValueError) as e:
                logger.warning(f"Could not create schedule suggestion due to invalid data: {sug}. Error: {e}")
                continue
        
        serializer = TimeBlockSuggestionSerializer(created_suggestions, many=True)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"Error generating schedule for user {request.user.id}: {e}")
        return Response(
            {'error': 'Failed to generate schedule'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
