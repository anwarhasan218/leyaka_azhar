"""
Database settings for different environments
"""

import os
from decouple import config

# Database configuration based on environment
DATABASE_CONFIG = {
    'development': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
    'production_postgresql': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='fitness_project'),
        'USER': config('DB_USER', default='fitness_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    },
    'production_mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='fitness_project'),
        'USER': config('DB_USER', default='fitness_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    'hostinger': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='your_database_name'),
        'USER': config('DB_USER', default='your_database_user'),
        'PASSWORD': config('DB_PASSWORD', default='your_database_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

def get_database_config(environment='development'):
    """
    Get database configuration based on environment
    
    Args:
        environment (str): Environment name (development, production_postgresql, production_mysql, hostinger)
    
    Returns:
        dict: Database configuration
    """
    return DATABASE_CONFIG.get(environment, DATABASE_CONFIG['development'])

# Database connection pool settings for production
DATABASE_POOL_SETTINGS = {
    'max_connections': 20,
    'min_connections': 5,
    'connection_timeout': 30,
    'idle_timeout': 300,
}

# Database backup settings
BACKUP_SETTINGS = {
    'backup_dir': 'backups/',
    'retention_days': 30,
    'compress_backups': True,
    'backup_schedule': '0 2 * * *',  # Daily at 2 AM
}

# Database optimization settings
OPTIMIZATION_SETTINGS = {
    'enable_query_logging': False,
    'enable_slow_query_logging': True,
    'slow_query_threshold': 1.0,  # seconds
    'max_query_time': 30,  # seconds
} 