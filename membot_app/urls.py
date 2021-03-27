from django.urls import path

from membot_app import views

urlpatterns = [
    path('message_hook/', views.on_message_received),
]