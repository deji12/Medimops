from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from datetime import datetime
from .models import BotControl
from decimal import Decimal
from cryptography.fernet import Fernet

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

        if is_running and is_running == "False":
            bot_controller.is_running = False
            messages.success(request, f"Bot has been stopped")
         
        bot_controller.save()
        return redirect('home')

    context = {
        "bot": bot_controller
    }
    return render(request, 'index.html', context)

@login_required
def CardDetails(request):

    bot_controller = BotControl.objects.last()

    if request.method == "POST":
        card_number = request.POST.get('card_number')
        card_holder_name = request.POST.get('card_holder_name')
        expiry_month = request.POST.get('expiration_month')
        expiry_year = request.POST.get('expiration_year')
        cvv = request.POST.get('cvv')

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
        return redirect('card')
        

    months = list(range(1, 13))  # Months 1 through 12
    current_year = datetime.now().year
    years = list(range(current_year, current_year + 7))  # Next 7 years
    
    # Pass these variables to the template
    context = {
        'months': months,
        'years': years,
        'bot': bot_controller
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

        if password and not bot_controller.medimops_account_password:
            bot_controller.medimops_account_password = password
            bot_controller.save()
            messages.success(request, 'Password set successfully')

        return redirect('account')
    
    context = {
        "bot": bot_controller
    }
    
    return render(request, 'account.html', context)