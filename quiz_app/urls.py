# quiz_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),                                     # 1. होम पेज (क्विज़ लिस्ट)
    path('quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),       # 2. क्विज़ खेलने वाला पेज
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'), # 3. रिजल्ट सबमिट करने के लिए
]