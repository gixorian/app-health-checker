from celery import Celery
import time
import os

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
app = Celery("tasks", broker=broker_url)


@app.task
def process():
    time.sleep(10)
