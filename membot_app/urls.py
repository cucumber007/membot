from django.urls import path

from membot_app import views

urlpatterns = [
    path('message_hook/', views.on_message_received),
    path('password/', views.set_password),
    path('trigger_notifications/', views.trigger_notifications),
    path('mark/', views.mark),
]