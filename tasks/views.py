from rest_framework import viewsets, status, filters, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
import logging
import csv
from ics import Calendar, Event

from .models import Task, TaskCategory, ContextEntry, TaskRecommendation, UserProfile
from .serializers import (
    TaskSerializer, TaskCreateSerializer, TaskCategorySerializer,
    ContextEntrySerializer, TaskRecommendationSerializer,
    TaskStatsSerializer, UserTaskSummarySerializer, UserProfileSerializer
)
from .filters import TaskFilter, ContextEntryFilter

logger = logging.getLogger(__name__)

class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profile settings like dark mode."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        obj, created = UserProfile.objects.get_or_create(user=self.request.user)
        return obj

    def list(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks with AI-enhanced features
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description', 'context_tags']
    ordering_fields = ['created_at', 'updated_at', 'deadline', 'priority']
    ordering = ['-created_at']
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).prefetch_related('categories')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """Export user's tasks to a CSV file."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="tasks_{timezone.now().strftime("%Y-%m-%d")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Title', 'Description', 'Priority', 'Status', 'Deadline', 'Created At'])

        tasks = self.get_queryset()
        for task in tasks:
            writer.writerow([
                task.id,
                task.title,
                task.description,
                task.get_priority_display(),
                task.get_status_display(),
                task.deadline.strftime("%Y-%m-%d %H:%M") if task.deadline else '',
                task.created_at.strftime("%Y-%m-%d %H:%M")
            ])
        
        return response

    @action(detail=False, methods=['post'])
    def import_csv(self, request):
        """Import tasks from a CSV file."""
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            tasks_to_create = []
            for row in reader:
                tasks_to_create.append(Task(
                    user=request.user,
                    title=row['Title'],
                    description=row.get('Description', ''),
                    priority=int(row.get('Priority', 3)),
                    status=row.get('Status', 'pending').lower(),
                    deadline=timezone.make_aware(datetime.strptime(row['Deadline'], "%Y-%m-%d %H:%M")) if row.get('Deadline') else None
                ))
            
            Task.objects.bulk_create(tasks_to_create)
            return Response({'message': f'{len(tasks_to_create)} tasks imported successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"CSV import failed for user {request.user.id}: {e}")
            return Response({'error': f'Failed to process CSV file: {e}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def export_ics(self, request, pk=None):
        """Export a single task as an iCalendar (.ics) file."""
        task = self.get_object()
        cal = Calendar()
        event = Event()
        event.name = task.title
        event.description = task.description
        if task.deadline:
            event.begin = task.deadline
            event.end = task.deadline + timedelta(hours=1) # Default 1 hour duration
        else:
            event.begin = timezone.now()
        
        cal.events.add(event)

        response = HttpResponse(str(cal), content_type='text/calendar')
        response['Content-Disposition'] = f'attachment; filename="{task.title}.ics"'
        return response

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get task statistics for the current user"""
        queryset = self.get_queryset()
        
        total_tasks = queryset.count()
        completed_tasks = queryset.filter(status='completed').count()
        pending_tasks = queryset.filter(status='pending').count()
        in_progress_tasks = queryset.filter(status='in_progress').count()
        high_priority_tasks = queryset.filter(priority=1, status__in=['pending', 'in_progress']).count()
        
        # Calculate overdue tasks
        now = timezone.now()
        overdue_tasks = queryset.filter(
            deadline__lt=now,
            status__in=['pending', 'in_progress']
        ).count()
        
        # Calculate completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average completion time
        completed_with_duration = queryset.filter(
            status='completed',
            completed_at__isnull=False
        )
        
        avg_completion_time = 0
        if completed_with_duration.exists():
            total_duration = sum([
                (task.completed_at - task.created_at).total_seconds() / 3600  # Convert to hours
                for task in completed_with_duration
            ])
            avg_completion_time = total_duration / completed_with_duration.count()
        
        stats_data = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'in_progress_tasks': in_progress_tasks,
            'high_priority_tasks': high_priority_tasks,
            'overdue_tasks': overdue_tasks,
            'completion_rate': round(completion_rate, 2),
            'avg_completion_time': round(avg_completion_time, 2)
        }
        
        serializer = TaskStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get comprehensive user task summary"""
        stats_response = self.stats(request)
        recent_tasks = self.get_queryset()[:5]
        
        summary_data = {
            'user': request.user.username,
            'stats': stats_response.data,
            'recent_tasks': TaskSerializer(recent_tasks, many=True).data,
        }
        
        serializer = UserTaskSummarySerializer(summary_data)
        return Response(serializer.data)

class TaskCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing task categories/tags
    """
    queryset = TaskCategory.objects.all()
    serializer_class = TaskCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular categories based on task count"""
        popular_categories = TaskCategory.objects.annotate(
            task_count=Count('tasks')
        ).filter(task_count__gt=0).order_by('-task_count')[:10]
        
        serializer = self.get_serializer(popular_categories, many=True)
        return Response(serializer.data)

class ContextEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing daily context entries
    """
    serializer_class = ContextEntrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ContextEntryFilter
    search_fields = ['content', 'source', 'keywords']
    ordering_fields = ['entry_date', 'created_at', 'importance_score']
    ordering = ['-entry_date', '-created_at']
    
    def get_queryset(self):
        return ContextEntry.objects.filter(user=self.request.user)

class TaskRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AI-generated task recommendations
    """
    serializer_class = TaskRecommendationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['confidence_score', 'created_at']
    ordering = ['-confidence_score', '-created_at']
    
    def get_queryset(self):
        return TaskRecommendation.objects.filter(
            user=self.request.user,
            is_dismissed=False
        ).prefetch_related('based_on_context')
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a recommendation and create a task"""
        recommendation = self.get_object()
        
        # Create task from recommendation
        task_data = {
            'title': recommendation.title,
            'description': recommendation.description,
            'priority': recommendation.suggested_priority,
            'deadline': recommendation.suggested_deadline,
            'user': request.user,
            'ai_reasoning': recommendation.reasoning,
        }
        
        task = Task.objects.create(**task_data)
        
        # Add suggested categories
        if recommendation.suggested_categories:
            for category_name in recommendation.suggested_categories:
                category, created = TaskCategory.objects.get_or_create(name=category_name)
                task.categories.add(category)
        
        # Update recommendation
        recommendation.is_accepted = True
        recommendation.created_task = task
        recommendation.save()
        
        return Response({
            'message': 'Recommendation accepted and task created',
            'task_id': task.id,
            'task': TaskSerializer(task).data
        })
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a recommendation"""
        recommendation = self.get_object()
        recommendation.is_dismissed = True
        recommendation.save()
        
        return Response({'message': 'Recommendation dismissed'})
