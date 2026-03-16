import os
from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

print(f"[celery_app] REDIS_URL = {REDIS_URL}")

celery_app = Celery(
    "legalbert_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.classify_task"],  # picks up both tasks automatically
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_pool="solo",
    broker_connection_retry_on_startup=True,
    # Route fast and slow tasks to separate queues
    task_routes={
        "app.tasks.classify_task.classify_document_task": {"queue": "classify"},
        "app.tasks.classify_task.index_document_task": {"queue": "index"},
    },
)