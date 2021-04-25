from django.contrib import admin

# Register your models here.
from membot_app import models

admin.site.register(models.User)


class LexemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'english', 'russian', 'context')


admin.site.register(models.Lexem, LexemAdmin)


class MemorizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lexem', 'interval_stage', 'notify_at')


admin.site.register(models.Memorization, MemorizationAdmin)


class EditQueueAdmin(admin.ModelAdmin):
    list_display = ('raw', 'lexems')

    def lexems(self, queueItem):
        return list(models.Lexem.objects.filter(user=queueItem.user))


admin.site.register(models.EditQueueItem, EditQueueAdmin)
