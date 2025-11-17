from celery import Celery
from app.core.celery_config import *

# Create Celery app instance
celery_app = Celery("spam_detection")

# Load configuration
celery_app.config_from_object("app.core.celery_config")

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])