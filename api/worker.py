"""Celery worker entrypoint for docker-compose."""
from celery_tasks import celery_app

celery = celery_app
