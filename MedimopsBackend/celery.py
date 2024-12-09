
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MedimopsBackend.settings')

app = Celery('MedimopsBackend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# Function to start Celery Beat and direct logs to a file
def start_celery_beat():
    with open('/var/log/celery_beat.log', 'a') as f:
        subprocess.Popen(
            ["celery", "-A", "MedimopsBackend", "beat", "-l", "INFO"], 
            stdout=f, stderr=f
        )

# Function to stop Celery Beat
def stop_celery_beat():
    subprocess.Popen(["pkill", "-f", "celery beat"])

# Function to start Celery Worker and direct logs to a file
def start_celery_worker():
    with open('/var/log/celery_worker.log', 'a') as f:
        subprocess.Popen(
            ["celery", "-A", "MedimopsBackend", "worker", "--pool=threads", "--concurrency=10"], 
            stdout=f, stderr=f
        )

# Function to stop Celery Worker
def stop_celery_worker():
    subprocess.Popen(["pkill", "-f", "celery worker"])
