from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class UserProfile(models.Model):
    """Model to store user-specific preferences and settings."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    dark_mode_enabled = models.BooleanField(default=False)
    # Store other preferences as a JSON object for flexibility
    preferences = models.JSONField(default=dict, blank=True, help_text="Stores user preferences like work hours, etc.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class TaskCategory(models.Model):
    """Model for task categories/tags"""
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Task Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Task(models.Model):
    """Main Task model with AI-enhanced features"""
    
    PRIORITY_CHOICES = [
        (1, 'High'),
        (2, 'Medium'),
        (3, 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Basic fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    # Priority and status
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Dates
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # AI-enhanced fields
    ai_suggested_priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        null=True,
        blank=True,
        help_text="AI-suggested priority level"
    )
    ai_suggested_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="AI-suggested deadline"
    )
    ai_reasoning = models.TextField(
        blank=True,
        help_text="AI explanation for priority/deadline suggestions"
    )
    ai_enhanced_description = models.TextField(
        blank=True,
        help_text="AI-enhanced task description with context-aware details"
    )
    
    # Categories and context
    categories = models.ManyToManyField(TaskCategory, blank=True, related_name='tasks')
    context_tags = models.JSONField(default=list, blank=True)
    
    # Metadata
    estimated_duration = models.DurationField(null=True, blank=True)
    actual_duration = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['priority', 'deadline']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.deadline and self.status != 'completed':
            from django.utils import timezone
            return timezone.now() > self.deadline
        return False
    
    def save(self, *args, **kwargs):
        # Set completed_at when status changes to completed
        if self.status == 'completed' and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        
        super().save(*args, **kwargs)

class ContextEntry(models.Model):
    """Model for daily context entries (messages, emails, notes, meetings)"""
    
    ENTRY_TYPE_CHOICES = [
        ('message', 'Message'),
        ('email', 'Email'),
        ('note', 'Note'),
        ('meeting', 'Meeting'),
        ('call', 'Phone Call'),
        ('document', 'Document'),
    ]

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='context_entries')
    content = models.TextField()
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    entry_date = models.DateField()
    
    # Metadata
    source = models.CharField(max_length=200, blank=True, help_text="Source of the context (e.g., email sender, meeting title)")
    
    # AI-Extracted Information
    importance_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI-calculated importance score (0-1)"
    )
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, null=True, blank=True)
    keywords = models.JSONField(default=list, blank=True, help_text="AI-extracted keywords")
    extracted_tasks = models.JSONField(default=list, blank=True, help_text="AI-extracted potential tasks")
    extracted_deadlines = models.JSONField(default=list, blank=True, help_text="AI-extracted deadlines")
    extracted_people = models.JSONField(default=list, blank=True, help_text="AI-extracted people mentioned")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-entry_date', '-created_at']
        verbose_name_plural = "Context Entries"
        indexes = [
            models.Index(fields=['user', 'entry_date']),
            models.Index(fields=['entry_type']),
        ]
    
    def __str__(self):
        return f"{self.get_entry_type_display()} - {self.entry_date} ({self.user.username})"

class TaskRecommendation(models.Model):
    """Model for AI-generated task recommendations"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_recommendations')
    
    # Recommendation details
    title = models.CharField(max_length=500)
    description = models.TextField()
    suggested_priority = models.IntegerField(
        choices=Task.PRIORITY_CHOICES,
        default=3
    )
    suggested_deadline = models.DateTimeField(null=True, blank=True)
    
    # AI reasoning
    reasoning = models.TextField(help_text="AI explanation for this recommendation")
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI confidence in this recommendation (0-1)"
    )
    
    # Context
    based_on_context = models.ManyToManyField(ContextEntry, blank=True)
    suggested_categories = models.JSONField(default=list, blank=True)
    
    # Status
    is_accepted = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    created_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-confidence_score', '-created_at']
    
    def __str__(self):
        return f"Recommendation: {self.title} (Confidence: {self.confidence_score:.2f})"

class TimeBlockSuggestion(models.Model):
    """Model for AI-generated time-blocking/scheduling suggestions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedule_suggestions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='schedule_suggestions')
    suggested_start_time = models.DateTimeField()
    suggested_end_time = models.DateTimeField()
    reasoning = models.TextField(blank=True, help_text="AI explanation for this time slot.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['suggested_start_time']

    def __str__(self):
        return f"Schedule for {self.task.title} at {self.suggested_start_time}"
