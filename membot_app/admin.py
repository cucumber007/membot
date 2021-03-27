from django.contrib import admin

# Register your models here.
from membot_app import models

admin.site.register(models.User)
admin.site.register(models.Lexem)
admin.site.register(models.Memorization)

class EditQueueAdmin(admin.ModelAdmin):
    list_display = ('raw', 'lexems')

    def lexems(self, queueItem):
        return list(models.Lexem.objects.filter(user=queueItem.user))


admin.site.register(models.EditQueueItem, EditQueueAdmin)
