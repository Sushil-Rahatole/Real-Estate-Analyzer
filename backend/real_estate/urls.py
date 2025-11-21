from django.urls import path
from . import views

urlpatterns = [
    path('api/analyze/', views.analyze_real_estate, name='analyze_real_estate'),
    path('api/upload/', views.upload_excel, name='upload_excel'),
]