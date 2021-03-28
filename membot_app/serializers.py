from rest_framework import serializers

from membot_app import models


class LexemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lexem
        fields = ['id', 'english', 'russian', 'context', 'created_at', 'updated_at']


class MemorizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Memorization
        fields = ['lexem', 'interval_stage', 'notify_at']


class EditQueueItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EditQueueItem
        fields = ['raw', 'created_at']


class BackupSerializer(serializers.Serializer):
    lexems = LexemSerializer(many=True)
    edit_queue = EditQueueItemSerializer(many=True)
    memorizations = MemorizationSerializer(many=True)
