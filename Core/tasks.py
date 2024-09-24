# tasks.py
from celery import shared_task
from Bot.main import Bot
from Bot.config import *
from .models import BotControl

@shared_task(bind=True)
def run_bot_task(self):
    control = BotControl.objects.first()

    if control and control.is_running:
        bot = Bot(control.medimops_account_email, control.medimops_account_password, GOLOGIN_TOKEN, PROFILE_ID)
        bot.run()
        print("Bot task completed successfully.")
    else:
        print("Bot is paused, no action taken.")
