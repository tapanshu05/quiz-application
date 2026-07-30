from django.urls import path
from . import views

urlpatterns = [
    # 1. Landing Page
    path('', views.landing_page_view, name='landing'),
    
    # 2. Authentication
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # 3. Dashboard
    path('dashboard/', views.student_dashboard, name='dashboard'),
    
    # 4. Quiz Operations (views.home_view की जगह जो व्यू बनी है उसे कनेक्ट किया है)
    path('quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('dashboard/performance/', views.performance_history_view, name='performance_history'),
    
    # 5. Premium Modules
    path('solutions/', views.solutions_view, name='solutions'),
    path('notes/', views.notes_view, name='notes'),
    
    # 6. Payment System
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
]