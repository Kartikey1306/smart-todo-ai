from django.contrib import admin
from .models import Task, TaskCategory, ContextEntry, TaskRecommendation

@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'deadline', 'created_at']
    list_filter = ['priority', 'status', 'created_at', 'categories']
    search_fields = ['title', 'description', 'user__username']
    filter_horizontal = ['categories']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'categories')
        }),
        ('Priority & Status', {
            'fields': ('priority', 'status', 'deadline')
        }),
        ('AI Suggestions', {
            'fields': ('ai_suggested_priority', 'ai_suggested_deadline', 'ai_reasoning', 'ai_enhanced_description'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('context_tags', 'estimated_duration', 'actual_duration'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ContextEntry)
class ContextEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'entry_type', 'entry_date', 'importance_score', 'created_at']
    list_filter = ['entry_type', 'entry_date', 'importance_score']
    search_fields = ['content', 'source', 'user__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'importance_score', 
                      'extracted_tasks', 'extracted_deadlines', 'extracted_people']

@admin.register(TaskRecommendation)
class TaskRecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'suggested_priority', 'confidence_score', 'is_accepted', 'created_at']
    list_filter = ['suggested_priority', 'is_accepted', 'is_dismissed', 'confidence_score']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['id', 'created_at']
    filter_horizontal = ['based_on_context']
