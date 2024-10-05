from django.db import models
from cryptography.fernet import Fernet

class BotControl(models.Model):
    is_running = models.BooleanField(default=False)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    card_type = models.CharField(max_length=50, null=True, blank=True)
    card_holder_name = models.CharField(max_length=255, null=True, blank=True)
    card_number = models.CharField(max_length=20, null=True, blank=True)
    expiration_month = models.CharField(max_length=5, null=True, blank=True)
    expiration_year = models.CharField(max_length=5, null=True, blank=True)
    cvv = models.CharField(max_length=3, null=True, blank=True)
    key = models.CharField(max_length=255, null=True, blank=True, default=Fernet.generate_key())
    task_id = models.CharField(max_length=255, null=True, blank=True)  # Stores Celery task ID

    medimops_account_email = models.EmailField(max_length=255, null=True, blank=True)
    medimops_account_password = models.CharField(max_length=255, null=True, blank=True)

class ProductMaxPrice(models.Model):
    item_name = models.CharField(max_length=255)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)