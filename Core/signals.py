# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BotControl
from .tasks import run_bot_task
from MedimopsBackend.celery import (
                                        app, 
                                        start_celery_beat, 
                                        start_celery_worker, 
                                        stop_celery_beat, 
                                        stop_celery_worker
                                    )

@receiver(post_save, sender=BotControl)
def manage_bot_task(sender, instance, **kwargs):
    # Check if the bot should start running
    if instance.is_running:
        # If there's no active task, start the bot task
        if not instance.task_id:
            result = run_bot_task.apply_async()  # Run bot asynchronously
            instance.task_id = result.id
            instance.save(update_fields=['task_id'])
            start_celery_beat()  # Start Celery Beat
            start_celery_worker()  # Start Celery Worker
            print(f"Bot started with task ID: {result.id}")

    # If `is_running` is set to False, stop the task and Celery processes
    else:
        if instance.task_id:
            app.control.revoke(instance.task_id, terminate=True)  # Terminate running task
            instance.task_id = None  # Clear the task ID
            instance.save(update_fields=['task_id'])
            stop_celery_beat()  # Stop Celery Beat
            stop_celery_worker()  # Stop Celery Worker
            print("Bot task has been revoked and Celery has been stopped.")
