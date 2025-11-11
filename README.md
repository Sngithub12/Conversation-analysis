Conversation Analysis System

A Django-based analytics platform that evaluates AI–user chat conversations using multiple NLP metrics such as clarity, accuracy, empathy, and sentiment. The system supports:

✅ API endpoints for uploading and analyzing conversations

⚙️ Automated daily cron job to re-analyze new conversations

🗃️ Database storage for conversation data and analysis reports

💡 Optional frontend for easy visualization and upload

🚀 Features

Upload chat conversations dynamically (text or JSON)

Auto-analyzes conversations for:

Clarity

Relevance

Accuracy

Completeness

Empathy

Sentiment

Response timing

Stores analysis results in the database

HOW TO RUN:
1.Clone The Repository
git clone https://github.com/Sngithub12/Conversation-analysis.git

cd Conversation-analysis
2.Install Dependencies(i used anaconda prompt)
3.Python manage.py makemigrations
4.python manage.py runserver

Automated daily cron job for pending analyses
Cron-job:
python daily_analysis_runner.py

REST API endpoints (usable via Postman or frontend)
--#Endpoints --
http://127.0.0.1:8000/api/conversations/
http://127.0.0.1:8000/api/analyse/
http://127.0.0.1:8000/api/reports/
