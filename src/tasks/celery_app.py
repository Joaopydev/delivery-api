import os

from celery import Celery

BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
BACKEND_URL = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")

celery_app = Celery(
    main="delivery_api_worker",
    broker=BROKER_URL,
    backend=BACKEND_URL,
)

celery_app.conf.task_track_started = True # It allows you to see when the task actually started.
celery_app.conf.task_serializer = "json" # Send task in security format
celery_app.conf.result_serializer = "json" # Save results in JSON
celery_app.conf.accept_content = ["json"] # Reject any message that is not JSON

# Discovers automatically tasks in src
celery_app.autodiscover_tasks(["src'"])