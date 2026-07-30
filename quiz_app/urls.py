from django.urls import path
from . import views

urlpatterns = [
    # 1. Landing Page (Teachoo Style Dark Page for exampreparation.online)
    path('', views.landing_page_view, name='landing'),
    
    # 2. Auth Routes
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # 3. Student Dashboard & Quiz Portal
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('quizzes/', views.home_view, name='home'),  # 💡 Quizzes की लिस्ट देखने के लिए 'home' या 'quizzes'
    
    # 4. Quiz Taking & Results
    path('quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('dashboard/performance/', views.performance_history_view, name='performance_history'),
    
    # 5. Premium Learning Modules
    path('solutions/', views.solutions_view, name='solutions'),
    path('notes/', views.notes_view, name='notes'),
    
    # 6. Payment Routes
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
]