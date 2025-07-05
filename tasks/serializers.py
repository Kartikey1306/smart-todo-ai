from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, TaskCategory, ContextEntry, TaskRecommendation, UserProfile, TimeBlockSuggestion

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['dark_mode_enabled', 'preferences']

class TaskCategorySerializer(serializers.ModelSerializer):
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskCategory
        fields = ['id', 'name', 'color', 'description', 'task_count', 'created_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()

class TaskSerializer(serializers.ModelSerializer):
    categories = TaskCategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=TaskCategory.objects.all(),
        many=True,
        write_only=True,
        source='categories'
    )
    is_overdue = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status', 'deadline',
            'created_at', 'updated_at', 'completed_at', 'ai_suggested_priority',
            'ai_suggested_deadline', 'ai_reasoning', 'ai_enhanced_description', 'categories', 'category_ids',
            'context_tags', 'estimated_duration', 'actual_duration', 'is_overdue',
            'user_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TaskCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for task creation with AI processing"""
    use_ai = serializers.BooleanField(default=True, write_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=TaskCategory.objects.all(),
        many=True,
        required=False,
        source='categories'
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'deadline', 'category_ids',
            'context_tags', 'estimated_duration', 'use_ai'
        ]
    
    def create(self, validated_data):
        use_ai = validated_data.pop('use_ai', True)
        validated_data['user'] = self.context['request'].user
        
        # Create the task
        task = super().create(validated_data)
        
        # Process with AI if requested
        if use_ai:
            from ai_service.tasks import process_task_with_ai
            process_task_with_ai.delay(task.id)
        
        return task

class ContextEntrySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ContextEntry
        fields = [
            'id', 'content', 'entry_type', 'entry_date', 'source',
            'importance_score', 'sentiment', 'keywords', 'extracted_tasks', 'extracted_deadlines',
            'extracted_people', 'created_at', 'updated_at', 'user_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user', 'importance_score',
                           'sentiment', 'keywords', 'extracted_tasks', 'extracted_deadlines', 'extracted_people']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        context_entry = super().create(validated_data)
        
        # Process with AI for extraction
        from ai_service.tasks import process_context_entry_with_ai
        process_context_entry_with_ai.delay(context_entry.id)
        
        return context_entry

class TaskRecommendationSerializer(serializers.ModelSerializer):
    based_on_context = ContextEntrySerializer(many=True, read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TaskRecommendation
        fields = [
            'id', 'title', 'description', 'suggested_priority', 'suggested_deadline',
            'reasoning', 'confidence_score', 'based_on_context', 'suggested_categories',
            'is_accepted', 'is_dismissed', 'created_task', 'created_at', 'user_name'
        ]
        read_only_fields = ['id', 'created_at', 'user']

class TimeBlockSuggestionSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only=True)

    class Meta:
        model = TimeBlockSuggestion
        fields = ['id', 'task', 'suggested_start_time', 'suggested_end_time', 'reasoning']

class TaskStatsSerializer(serializers.Serializer):
    """Serializer for task statistics"""
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    pending_tasks = serializers.IntegerField()
    in_progress_tasks = serializers.IntegerField()
    high_priority_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    avg_completion_time = serializers.FloatField()
    
class UserTaskSummarySerializer(serializers.Serializer):
    """Serializer for user task summary"""
    user = serializers.CharField()
    stats = TaskStatsSerializer()
    recent_tasks = TaskSerializer(many=True)
    upcoming_deadlines = TaskSerializer(many=True)
