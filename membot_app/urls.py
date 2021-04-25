from django.urls import path

from membot_app import views
from django.contrib import admin

urlpatterns = [
    path('message_hook/', views.on_lexem_received),
    path('password/', views.set_password),
    path('trigger_notifications/', views.trigger_notifications),
    path('mark/', views.mark),
    path('stats/', views.stats),
    path('backup/', views.backup),
]