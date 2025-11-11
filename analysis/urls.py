
from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path('conversations/', views.upload_conversation, name='upload_conversation'),
    path('analyse/', views.analyse_conversation_endpoint, name='analyse_conversation'),
    path('reports/', views.list_reports, name='list_reports'),
]
