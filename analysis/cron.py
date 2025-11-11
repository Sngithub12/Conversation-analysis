# analysis/cron.py
from .models import Conversation, ConversationAnalysis
from .analysis_utils import analyze_conversation

def run_daily_analysis():
    """
    Cron job: runs every night at 12 AM.
    Analyses all new conversations that don't have an analysis yet.
    """
    unanalysed_convos = Conversation.objects.filter(analysis__isnull=True)
    for convo in unanalysed_convos:
        messages = [{"sender": m.sender, "message": m.text} for m in convo.messages.all()]
        result = analyze_conversation(messages)

        ConversationAnalysis.objects.create(
            conversation=convo,
            clarity_score=result["clarity_score"],
            relevance_score=result["relevance_score"],
            sentiment=result["sentiment"],
            empathy_score=result["empathy_score"],
            resolution=result["resolution"],
            overall_score=result["overall_score"],
        )

    print(f"✅ Daily analysis complete. {unanalysed_convos.count()} conversations processed.")
