import django_filters
from django.db.models import Q
from .models import Task, ContextEntry

class TaskFilter(django_filters.FilterSet):
    """Filter for Task model"""
    
    priority = django_filters.ChoiceFilter(choices=Task.PRIORITY_CHOICES)
    status = django_filters.ChoiceFilter(choices=Task.STATUS_CHOICES)
    category = django_filters.CharFilter(field_name='categories__name', lookup_expr='icontains')
    deadline_from = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='gte')
    deadline_to = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='lte')
    created_from = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    has_ai_suggestions = django_filters.BooleanFilter(method='filter_has_ai_suggestions')
    is_overdue = django_filters.BooleanFilter(method='filter_is_overdue')
    
    class Meta:
        model = Task
        fields = ['priority', 'status', 'category']
    
    def filter_has_ai_suggestions(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(ai_suggested_priority__isnull=False) | 
                Q(ai_suggested_deadline__isnull=False)
            )
        return queryset.filter(
            ai_suggested_priority__isnull=True,
            ai_suggested_deadline__isnull=True
        )
    
    def filter_is_overdue(self, queryset, name, value):
        from django.utils import timezone
        now = timezone.now()
        
        if value:
            return queryset.filter(
                deadline__lt=now,
                status__in=['pending', 'in_progress']
            )
        return queryset.exclude(
            deadline__lt=now,
            status__in=['pending', 'in_progress']
        )

class ContextEntryFilter(django_filters.FilterSet):
    """Filter for ContextEntry model"""
    
    entry_type = django_filters.ChoiceFilter(choices=ContextEntry.ENTRY_TYPE_CHOICES)
    entry_date_from = django_filters.DateFilter(field_name='entry_date', lookup_expr='gte')
    entry_date_to = django_filters.DateFilter(field_name='entry_date', lookup_expr='lte')
    importance_min = django_filters.NumberFilter(field_name='importance_score', lookup_expr='gte')
    importance_max = django_filters.NumberFilter(field_name='importance_score', lookup_expr='lte')
    has_extracted_tasks = django_filters.BooleanFilter(method='filter_has_extracted_tasks')
    
    class Meta:
        model = ContextEntry
        fields = ['entry_type']
    
    def filter_has_extracted_tasks(self, queryset, name, value):
        if value:
            return queryset.exclude(extracted_tasks=[])
        return queryset.filter(extracted_tasks=[])
