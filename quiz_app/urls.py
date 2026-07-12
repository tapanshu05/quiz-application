from django.urls import path
from . import views

urlpatterns = [
    # मुख्य खाली रास्ता अब सीधे लॉगिन पेज पर ले जाएगा
    path('', views.login_view, name='home'),  
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
    path('solutions/', views.solutions_view, name='solutions'),
    path('notes/', views.notes_view, name='notes'),
]