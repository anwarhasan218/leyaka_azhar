# Celery production configuration
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitness_project.production_settings')

# Create Celery app
app = Celery('fitness_project')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

# Production-specific settings
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
    worker_max_memory_per_child=200000,  # 200MB
    
    # Beat settings
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
        'cleanup-database': {
            'task': 'fitness_management.tasks.cleanup_database',
            'schedule': 2592000.0,  # 30 days
        },
        'optimize-database': {
            'task': 'fitness_management.tasks.optimize_database',
            'schedule': 604800.0,  # 7 days
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
    
    # Result settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Security settings
    security_key=os.environ.get('CELERY_SECURITY_KEY'),
    security_certificate=os.environ.get('CELERY_SECURITY_CERTIFICATE'),
    security_cert_store=os.environ.get('CELERY_SECURITY_CERT_STORE'),
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_always_eager=False,
    
    # Logging
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s',
)

# Task error handling
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# Error handling for tasks
@app.task(bind=True)
def error_handler(self, task_id, exc, traceback):
    print(f'Task {task_id} failed: {exc}')
    print(f'Traceback: {traceback}') 