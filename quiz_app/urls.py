from django.urls import path
from . import views

urlpatterns = [
    # 1. Your original landing pages (Make sure these point to your views correctly)
    path('', views.student_dashboard, name='home'),  # Setting dashboard as your main home view!
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # 2. Your Quiz specific pages
    path('quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    
    # 3. Dedicated Dashboard path
    path('dashboard/', views.student_dashboard, name='dashboard'),
]