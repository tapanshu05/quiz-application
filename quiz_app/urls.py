from django.urls import path
from . import views

urlpatterns = [
    # 💡 खाली URL ('') पर Teachoo स्टाइल Landing Page खुलेगा
    path('', views.landing_page_view, name='landing'),
    
    # बाकी सारे पेजों के URLs:
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    
    path('quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('dashboard/performance/', views.performance_history_view, name='performance_history'),
    
    path('solutions/', views.solutions_view, name='solutions'),
    path('notes/', views.notes_view, name='notes'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
    path('send-otp/', views.send_otp_view, name='send_otp'),
    path('subject/<str:subject_name>/', views.subject_detail_view, name='subject_detail'),
]