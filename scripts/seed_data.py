#!/usr/bin/env python
"""
Script to seed the database with comprehensive sample data for testing.

This script creates a demo user, pre-defined task categories, and a variety
of context entries and tasks to showcase the application's features,
especially the AI-powered analysis and recommendations.
"""
import os
import django
from datetime import timedelta
from django.utils import timezone
import logging

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_todo.settings')
django.setup()

from django.contrib.auth.models import User
from tasks.models import Task, TaskCategory, ContextEntry

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def seed_data():
    """
    Main function to seed the database.
    It ensures idempotency, so it can be run multiple times without creating duplicates.
    """
    logger.info("Starting database seeding...")

    # 1. Create a demo user
    user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        logger.info("Created demo user with username 'demo' and password 'demo123'.")
    else:
        logger.info("Demo user 'demo' already exists.")

    # 2. Create task categories
    categories_data = [
        {'name': 'Work', 'color': '#3B82F6', 'description': 'All work-related tasks and projects.'},
        {'name': 'Personal', 'color': '#10B981', 'description': 'Personal errands, hobbies, and life admin.'},
        {'name': 'Health', 'color': '#F59E0B', 'description': 'Fitness, appointments, and well-being.'},
        {'name': 'Finance', 'color': '#EF4444', 'description': 'Budgeting, bills, and financial planning.'},
        {'name': 'Urgent', 'color': '#DC2626', 'description': 'Critical and time-sensitive tasks.'},
        {'name': 'Learning', 'color': '#8B5CF6', 'description': 'Courses, reading, and skill development.'},
    ]
    
    for cat_data in categories_data:
        category, created = TaskCategory.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
        if created:
            logger.info(f"Created category: {category.name}")

    # 3. Create diverse sample context entries
    now = timezone.now()
    context_data = [
        {
            'content': "Email from client: The latest delivery is unacceptable and full of bugs. We need an urgent fix deployed by tomorrow EOD. This is critical for our launch.",
            'entry_type': 'email', 'entry_date': now.date(), 'source': 'angry.client@example.com'
        },
        {
            'content': "Note to self: Plan the team offsite for next quarter. Need to book a venue, arrange travel for 15 people, and set a final agenda.",
            'entry_type': 'note', 'entry_date': now.date(), 'source': 'Personal Planning'
        },
        {
            'content': "Message from team lead: Great job on the presentation today! Everyone was really impressed with the new dashboard mockups.",
            'entry_type': 'message', 'entry_date': now.date() - timedelta(days=1), 'source': 'Slack - Team Channel'
        },
        {
            'content': "Reminder: Mom's birthday is next Saturday. Need to buy a gift and a card, and also book a table for dinner.",
            'entry_type': 'note', 'entry_date': now.date() - timedelta(days=2), 'source': 'Family Reminders'
        },
        {
            'content': "Meeting notes: Discussed Q4 budget. Finance needs all department proposals by the end of the month. My department needs to outline costs for Project Phoenix.",
            'entry_type': 'meeting', 'entry_date': now.date() - timedelta(days=3), 'source': 'Q4 Budget Sync'
        }
    ]
    
    for ctx_data in context_data:
        _, created = ContextEntry.objects.get_or_create(
            user=user, content=ctx_data['content'], defaults={'user': user, **ctx_data}
        )
        if created:
            logger.info(f"Created context entry: {ctx_data['entry_type']} - '{ctx_data['content'][:30]}...'")

    # 4. Create sample tasks based on the context
    work_cat = TaskCategory.objects.get(name='Work')
    personal_cat = TaskCategory.objects.get(name='Personal')
    health_cat = TaskCategory.objects.get(name='Health')
    finance_cat = TaskCategory.objects.get(name='Finance')

    tasks_data = [
        {
            'title': 'Fix critical bugs in client delivery', 'description': 'Address all issues raised by the client in their recent email. Deploy hotfix immediately.',
            'priority': 1, 'status': 'in_progress', 'deadline': now + timedelta(days=1),
            'categories': [work_cat, TaskCategory.objects.get(name='Urgent')]
        },
        {
            'title': 'Prepare Q4 budget proposal for Project Phoenix', 'description': 'Outline all expected costs for the project for the next quarter.',
            'priority': 1, 'status': 'pending', 'deadline': now + timedelta(days=10),
            'categories': [work_cat, finance_cat]
        },
        {
            'title': 'Buy birthday gift for Mom', 'description': 'Find a nice gift and card for her birthday next Saturday.',
            'priority': 2, 'status': 'pending', 'deadline': now + timedelta(days=5),
            'categories': [personal_cat]
        },
        {
            'title': 'Schedule annual health check-up', 'description': 'Find a suitable date and book an appointment.',
            'priority': 3, 'status': 'pending', 'deadline': now + timedelta(days=30),
            'categories': [health_cat]
        },
        {
            'title': 'Finalize dashboard mockups', 'description': 'Incorporate feedback and prepare final designs for development handoff.',
            'priority': 2, 'status': 'completed', 'completed_at': now - timedelta(days=2),
            'categories': [work_cat]
        }
    ]

    for task_data in tasks_data:
        categories = task_data.pop('categories', [])
        task, created = Task.objects.get_or_create(
            user=user, title=task_data['title'], defaults={'user': user, **task_data}
        )
        if created:
            task.categories.set(categories)
            logger.info(f"Created task: {task.title}")

    logger.info("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_data()
