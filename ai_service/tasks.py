from celery import shared_task
from django.utils import timezone
from tasks.models import Task, TaskCategory, ContextEntry, TaskRecommendation
from .ai_pipeline import AIPipeline
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_task_with_ai(task_id: str):
    """
    Celery task to process a newly created task with the full AI pipeline.
    """
    try:
        task = Task.objects.get(id=task_id)
        user = task.user

        # 1. Gather Inputs for the AI Pipeline
        # Daily context
        context_entries = list(
            ContextEntry.objects.filter(user=user)
            .order_by('-entry_date', '-created_at')[:10]
            .values('content', 'entry_type')
        )

        # Current task load
        all_tasks = Task.objects.filter(user=user, status__in=['pending', 'in_progress'])
        task_load = {
            'total': all_tasks.count(),
            'high_priority': all_tasks.filter(priority=1).count(),
            'upcoming': all_tasks.filter(deadline__gte=timezone.now(), deadline__lte=timezone.now() + timezone.timedelta(days=7)).count()
        }
        
        # User preferences (can be fetched from a UserProfile model in the future)
        user_preferences = {'work_hours': '9am-6pm'}

        # 2. Initialize and run the AI Pipeline
        pipeline = AIPipeline(user_id=user.id)
        enhanced_data = pipeline.process_new_task(
            task_details={'title': task.title, 'description': task.description, 'priority': task.priority},
            daily_context=context_entries,
            current_task_load=task_load,
            user_preferences=user_preferences
        )

        # 3. Update the Task with AI Enhancements
        task.title = enhanced_data.get('title', task.title)
        task.ai_enhanced_description = enhanced_data.get('enhanced_description', task.description)
        task.ai_suggested_priority = enhanced_data.get('priority', task.priority)
        task.priority = enhanced_data.get('priority', task.priority) # Also update the main priority
        task.ai_reasoning = enhanced_data.get('reasoning', '')
        task.context_tags = enhanced_data.get('context_tags', [])

        if enhanced_data.get('deadline'):
            try:
                from datetime import datetime
                task.deadline = datetime.fromisoformat(enhanced_data['deadline'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                logger.warning(f"AI returned invalid deadline format for task {task_id}")

        task.save()

        # Handle suggested categories
        if enhanced_data.get('suggested_categories'):
            for cat_name in enhanced_data['suggested_categories']:
                category, _ = TaskCategory.objects.get_or_create(name=cat_name.strip())
                task.categories.add(category)

        logger.info(f"Successfully processed task {task_id} with AI pipeline.")

    except Task.DoesNotExist:
        logger.error(f"Task {task_id} not found for AI processing.")
    except Exception as e:
        logger.error(f"Error in AI task processing for task {task_id}: {e}", exc_info=True)


@shared_task
def process_context_entry_with_ai(context_entry_id: str):
    """
    Celery task to analyze a new context entry with the AI pipeline.
    """
    try:
        context_entry = ContextEntry.objects.get(id=context_entry_id)
        pipeline = AIPipeline(user_id=context_entry.user.id)
        
        extracted_info = pipeline.analyze_context_entry(
            content=context_entry.content,
            entry_type=context_entry.get_entry_type_display()
        )

        if extracted_info:
            context_entry.importance_score = extracted_info.get('importance_score', 0.5)
            context_entry.sentiment = extracted_info.get('sentiment', 'neutral')
            context_entry.keywords = extracted_info.get('keywords', [])
            context_entry.extracted_tasks = extracted_info.get('potential_tasks', [])
            context_entry.extracted_deadlines = extracted_info.get('mentioned_deadlines', [])
            context_entry.extracted_people = extracted_info.get('mentioned_people', [])
            context_entry.save()

            logger.info(f"Successfully analyzed context entry {context_entry_id} with AI.")

    except ContextEntry.DoesNotExist:
        logger.error(f"Context entry {context_entry_id} not found for AI processing.")
    except Exception as e:
        logger.error(f"Error in AI context processing for entry {context_entry_id}: {e}", exc_info=True)


@shared_task
def generate_task_recommendations_for_user(user_id: int):
    """
    Celery task to generate personalized task recommendations.
    """
    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)

        # Gather context and existing tasks
        context_entries = list(ContextEntry.objects.filter(user=user).order_by('-created_at')[:20].values('content', 'entry_type'))
        existing_tasks = list(Task.objects.filter(user=user, status__in=['pending', 'in_progress']).values('title'))

        pipeline = AIPipeline(user_id=user.id)
        recommendations = pipeline.generate_task_recommendations(context_entries, existing_tasks)

        # Delete old, non-accepted recommendations
        TaskRecommendation.objects.filter(user=user, is_accepted=False, is_dismissed=False).delete()

        # Create new recommendation objects
        for rec in recommendations:
            TaskRecommendation.objects.create(
                user=user,
                title=rec.get('title'),
                description=rec.get('description'),
                suggested_priority=rec.get('priority', 3),
                reasoning=rec.get('reasoning', ''),
                confidence_score=rec.get('confidence_score', 0.75),
                suggested_categories=rec.get('suggested_categories', [])
            )
        
        logger.info(f"Generated {len(recommendations)} new recommendations for user {user_id}.")

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found for recommendation generation.")
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {e}", exc_info=True)
