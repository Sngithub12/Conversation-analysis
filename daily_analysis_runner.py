import os
import django
import time

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conversation_analysis.settings")
django.setup()

from analysis.models import Conversation, ConversationAnalysis
from analysis.analysis_utils import analyze_conversation  # your Part 1 logic

def run_daily_analysis():
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
    print(f"✅ Daily analysis complete. {unanalysed_convos.count()} processed.")

if __name__ == "__main__":
    while True:
        print("Running daily analysis...")
        run_daily_analysis()
        print("Sleeping for 24 hours...")
        time.sleep(86400)  # 24 hours in seconds
