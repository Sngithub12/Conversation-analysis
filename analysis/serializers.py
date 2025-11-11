from rest_framework import serializers
from .models import Conversation, Message, ConversationAnalysis

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Conversation
        fields = '__all__'

class ConversationAnalysisSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    class Meta:
        model = ConversationAnalysis
        fields = '__all__'
