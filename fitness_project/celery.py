"""
Celery configuration for fitness_project.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_project.settings')

app = Celery('fitness_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery configuration
app.conf.update(
    # Broker settings
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Cairo',
    enable_utc=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    
    # Beat settings (for periodic tasks)
    beat_schedule={
        'backup-database-daily': {
            'task': 'fitness_management.tasks.backup_database',
            'schedule': 86400.0,  # 24 hours
        },
        'cleanup-old-files': {
            'task': 'fitness_management.tasks.cleanup_old_files',
            'schedule': 604800.0,  # 7 days
        },
        'generate-reports': {
            'task': 'fitness_management.tasks.generate_periodic_reports',
            'schedule': 3600.0,  # 1 hour
        },
    },
    
    # Task routing
    task_routes={
        'fitness_management.tasks.*': {'queue': 'fitness_tasks'},
        'accounts.tasks.*': {'queue': 'user_tasks'},
    },
    
    # Queue settings
    task_default_queue='default',
    task_default_exchange='default',
    task_default_routing_key='default',
)

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 