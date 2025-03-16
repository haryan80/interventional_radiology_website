from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('speakers/', views.speakers, name='speakers'),
    path('schedule/', views.schedule, name='schedule'),
    path('registration/', views.registration, name='registration'),
    path('registration/success/', views.registration_success, name='registration_success'),
] 