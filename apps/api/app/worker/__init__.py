"""
SkillSetu X — Celery Worker Configuration
Background task processing for ingestion, embedding, scoring, notifications.
"""
import os
from celery import Celery

# Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "skillsetu",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.worker.tasks.ingestion",
        "app.worker.tasks.embedding",
        "app.worker.tasks.scoring",
        "app.worker.tasks.notifications",
        "app.worker.tasks.precompute",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Timezone
    timezone="Asia/Kolkata",
    enable_utc=True,
    
    # Task settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # Soft limit 55 min
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    # Result settings
    result_expires=86400,  # 24 hours
    
    # Rate limiting
    worker_max_tasks_per_child=100,
    
    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,
    
    # Beat schedule (periodic tasks)
    beat_schedule={
        "refresh-shi-daily": {
            "task": "app.worker.tasks.precompute.refresh_shi",
            "schedule": 86400.0,  # Daily
        },
        "refresh-embeddings-daily": {
            "task": "app.worker.tasks.precompute.refresh_embeddings",
            "schedule": 86400.0,
        },
        "check-deadlines-hourly": {
            "task": "app.worker.tasks.notifications.check_deadlines",
            "schedule": 3600.0,
        },
        "data-freshness-check-daily": {
            "task": "app.worker.tasks.precompute.check_data_freshness",
            "schedule": 86400.0,
        },
    },
)
