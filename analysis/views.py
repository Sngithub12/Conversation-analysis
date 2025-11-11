from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message, ConversationAnalysis
from .serializers import ConversationSerializer, ConversationAnalysisSerializer
from .analysis_utils import analyze_conversation  # Updated Part 2 version

# --- Upload a conversation ---
@api_view(['POST'])
def upload_conversation(request):
    """Upload chat data — handles JSON dicts, lists, or text."""
    import json

    data = request.data

    # Case 1: Direct JSON array
    if isinstance(data, list):
        messages = data
    # Case 2: Dictionary with messages key
    elif isinstance(data, dict) and 'messages' in data:
        messages = data['messages']
    # Case 3: Raw text string
    elif isinstance(data, str):
        try:
            messages = json.loads(data)
        except Exception:
            return Response({'error': 'Invalid JSON text input'}, status=400)
    else:
        return Response({'error': 'Invalid input format'}, status=400)

    if not messages:
        return Response({'error': 'No chat messages found'}, status=400)

    # Save conversation
    conv = Conversation.objects.create(title="Chat Upload")

    for msg in messages:
        if isinstance(msg, dict) and 'sender' in msg and 'message' in msg:
            Message.objects.create(conversation=conv, sender=msg['sender'], text=msg['message'])
        else:
            return Response({'error': 'Each message must have sender and message'}, status=400)

    return Response({'conversation_id': conv.id}, status=201)



# --- Analyse a single conversation by ID ---
@api_view(['POST'])
def analyse_conversation(request):
    """Trigger analysis"""
    conv_id = request.data.get('conversation_id')
    try:
        conv = Conversation.objects.get(id=conv_id)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found'}, status=404)

    messages = [{"sender": m.sender, "message": m.text} for m in conv.messages.all()]
    analysis_data = analyze_conversation(messages)

    # Create the analysis object safely
    analysis_obj = ConversationAnalysis.objects.create(conversation=conv, **analysis_data)
    serializer = ConversationAnalysisSerializer(analysis_obj)
    return Response(serializer.data, status=201)


# --- List all conversation analyses ---
@api_view(['GET'])
def list_reports(request):
    """List all conversation analyses"""
    analyses = ConversationAnalysis.objects.all().order_by('-created_at')
    serializer = ConversationAnalysisSerializer(analyses, many=True)
    return Response(serializer.data)


# --- Endpoint to process all unanalysed conversations ---
@api_view(['POST'])
def analyse_conversation_endpoint(request):
    """
    Trigger analysis for all conversations without analysis yet.
    """
    unanalysed_convos = Conversation.objects.filter(analysis__isnull=True)
    processed_count = 0

    for convo in unanalysed_convos:
        messages = [{"sender": m.sender, "message": m.text} for m in convo.messages.all()]
        result = analyze_conversation(messages)

        # Safely create ConversationAnalysis with defaults for all required fields
        ConversationAnalysis.objects.create(
            conversation=convo,
            clarity_score=result.get("clarity_score", 0.0),
            relevance_score=result.get("relevance_score", 0.0),
            accuracy_score=result.get("accuracy_score", 0.0),
            completeness_score=result.get("completeness_score", 0.0),
            empathy_score=result.get("empathy_score", 0.0),
            fallback_count=result.get("fallback_count", 0),
            sentiment=result.get("sentiment", "neutral"),
            sentiment_score=result.get("sentiment_score", 0.5),
            resolution=result.get("resolution", False),
            escalation_needed=result.get("escalation_needed", False),
            avg_user_response_seconds=result.get("avg_user_response_seconds", 0.0),
            avg_ai_response_seconds=result.get("avg_ai_response_seconds", 0.0),
            overall_score=result.get("overall_score", 0.0),
            created_at=result.get("created_at")
        )
        processed_count += 1

    return Response({
        "status": "success",
        "processed_conversations": processed_count
    })
