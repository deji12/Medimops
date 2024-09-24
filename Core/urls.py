from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('', views.Home, name='home'),
    path('card/', views.CardDetails, name='card'),
    path('profile/', views.Profile, name='profile'),
    path('medimops-account/', views.Account, name='account'),
]