from rest_framework.serializers import ModelSerializer
from .models import *

class BotControlSerializer(ModelSerializer):
    class Meta:
        model = BotControl
        fields = '__all__'

class ProductMaxPriceSerializer(ModelSerializer):
    class Meta:
        model = ProductMaxPrice
        fields = '__all__'