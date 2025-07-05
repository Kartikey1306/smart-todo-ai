#!/usr/bin/env python
"""
Script to create a superuser for the Django admin
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_todo.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    """Create a superuser if one doesn't exist"""
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("Superuser created successfully!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Superuser already exists!")

if __name__ == '__main__':
    create_superuser()
