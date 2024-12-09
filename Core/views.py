from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime
from .models import BotControl, ProductMaxPrice
from decimal import Decimal
from .utils import send_email
from .serializers import BotControlSerializer, ProductMaxPriceSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from rest_framework import status

@login_required
def Home(request):

    bot_controller = BotControl.objects.last()

    if request.method == "POST":
        max_price = request.POST.get('max_price')
        is_running = request.POST.get('is_running')

        if max_price and Decimal(str(max_price)) != bot_controller.max_price:
            bot_controller.max_price = Decimal(str(max_price))
            messages.success(request, f"Max price has been updated to {max_price}")
        
        if is_running and is_running == "True":

            # make sure user has entered card details
            if not bot_controller.card_number:
                messages.error(request, "Card details are required to start the bot")
                return redirect('home')

            bot_controller.is_running = True
            messages.success(request, f"Bot is running successfully")
            send_email(changed_entity='Running status')

        if is_running and is_running == "False":
            bot_controller.is_running = False
            messages.success(request, f"Bot has been stopped")
            send_email(changed_entity='Running status')
         
        bot_controller.save()
        return redirect('home')

    context = {
        "bot": bot_controller
    }
    return render(request, 'index.html', context)

@login_required
def CardDetails(request):

    card_types = ["Visa", "Mastercard", "American Express"]

    bot_controller = BotControl.objects.last()

    if request.method == "POST":
        card_number = request.POST.get('card_number')
        card_holder_name = request.POST.get('card_holder_name')
        expiry_month = request.POST.get('expiration_month')
        expiry_year = request.POST.get('expiration_year')
        cvv = request.POST.get('cvv')
        card_type = request.POST.get('card_type')

        if card_type and bot_controller.card_type != card_type:
            bot_controller.card_type = card_type

        # f = Fernet(bot_controller.key)

        if card_number and bot_controller.card_number != card_number:
            bot_controller.card_number = card_number
        
        if card_holder_name and bot_controller.card_holder_name!= card_holder_name:
            bot_controller.card_holder_name = card_holder_name

        if expiry_month and bot_controller.expiration_month != expiry_month:
            bot_controller.expiration_month = expiry_month

        if expiry_year and bot_controller.expiration_year!= expiry_year:
            bot_controller.expiration_year = expiry_year

        if cvv and bot_controller.cvv!= cvv:
            bot_controller.cvv = cvv
        
        bot_controller.save()

        messages.success(request, "Card details updated")

        send_email(changed_entity='Card details')

        return redirect('card')
        

    months = list(range(1, 13))  # Months 1 through 12
    current_year = datetime.now().year
    years = list(range(current_year, current_year + 7))  # Next 7 years
    
    # Pass these variables to the template
    context = {
        'months': months,
        'years': years,
        'bot': bot_controller,
        "card_types": card_types
    }

    return render(request, 'card.html', context)

def Login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('pswd')

        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        
        messages.error(request, 'Invalid username or password')
        return redirect('login')
    
    return render(request, 'login.html')

def Logout(request):

    logout(request)
    return redirect('login')

@login_required
def Profile(request):

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password and confirm_password and password == confirm_password:
            user = request.user
            user.set_password(password)
            user.save()
            messages.success(request, 'Password updated successfully')
        
        else:
            messages.error(request, 'Passwords do not match')
        
        return redirect('profile')

    return render(request, 'profile.html')

@login_required
def Account(request):

    bot_controller = BotControl.objects.last()

    if request.method == 'POST':

        email = request.POST.get('email')
        password = request.POST.get('password')

        if not (email and password):
            messages.error(request, 'Email and password are required')
            return redirect('account')
        
        if email and bot_controller.medimops_account_email != email:
            bot_controller.medimops_account_email = email
            bot_controller.save()
            messages.success(request, 'Email updated successfully')

            send_email(changed_entity='Medimops account credentials')

        if password and not bot_controller.medimops_account_password:
            bot_controller.medimops_account_password = password
            bot_controller.save()
            messages.success(request, 'Password set successfully')

            send_email(changed_entity='Medimops account credentials')

        return redirect('account')
    
    context = {
        "bot": bot_controller
    }
    
    return render(request, 'account.html', context)

@login_required
def ProductsMaxPrice(request):
    
    product_max_prices = ProductMaxPrice.objects.all().order_by('-date')
    context = {
        "max_prices": product_max_prices
    }
    return render(request, 'max-prices.html', context)

@login_required
def AddMaxPriceItem(request):
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        status = request.POST.get('status')

        new_max_price = ProductMaxPrice(
            item_name = name,
            max_price = price, 
        )

        if status == 'on':
            new_max_price.status = True

        new_max_price.save()
        messages.success(request, 'Max price item added successfully')

        send_email(changed_entity='Product max price addition')

        return redirect('product-max-price')
    
    return render(request, 'add-max-price.html')

@login_required
def UpdateMaxPriceItem(request, item_id):

    try:
        max_price_item = ProductMaxPrice.objects.get(id=item_id)
    except ProductMaxPrice.DoesNotExist:
        messages.error(request, 'Max price item not found')
        return redirect('product-max-price')
    
    if request.method == 'POST':

        name = request.POST.get('name')
        price = request.POST.get('price')
        status = request.POST.get('status')

        max_price_item.item_name = name
        max_price_item.max_price = price
        
        if status == 'on':
            max_price_item.status = True
        else:
            max_price_item.status = False

        max_price_item.save()
        messages.success(request, 'Max price item updated successfully')
        
        send_email(changed_entity=f'Max price for product edit - Id: {item_id}')

        return redirect('product-max-price')
    
    context = {
        "max_price_item": max_price_item
    }
    
    return render(request, 'add-max-price.html', context)

@api_view(["POST"])
def get_bot_info(request):

    password = request.data.get("password")

    if password != settings.BOT_INFO_PASSWORD:
        return Response({"message": "Invalid password provided"}, status=status.HTTP_400_BAD_REQUEST)
    
    bot_controller = BotControl.objects.last()
    product_max_price = ProductMaxPrice.objects.all()

    bot_data = BotControlSerializer(bot_controller)
    product_max_price_data = ProductMaxPriceSerializer(product_max_price, many=True)

    return Response({
        "bot_data": bot_data.data,
        "max_price_data": product_max_price_data.data
    }, status=status.HTTP_200_OK)