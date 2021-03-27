from django.contrib import admin

# Register your models here.
from membot_app import models

admin.site.register(models.User)
admin.site.register(models.Lexem)
admin.site.register(models.EditQueue)