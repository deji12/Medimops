# tasks.py
from celery import shared_task
from Bot.main import Bot
from .models import BotControl

@shared_task(bind=True)
def run_bot_task(self):
    control = BotControl.objects.first()

    if control and control.is_running:
        bot = Bot()
        bot.run()
        print("Bot task started successfully.")
    else:
        print("Bot is paused, no action taken.")
