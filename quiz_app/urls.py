from django.urls import path
from . import views

urlpatterns = [
    # 1. मुख्य होमपेज का रास्ता जो गायब हो गया था (इसे सबसे ऊपर रखें)
    path('', views.home, name='home'),
    
    # 2. क्विज़ स्टार्ट और सबमिट करने के पुराने रास्ते
    path('quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
    
    # 3. नए लॉगिन और रजिस्ट्रेशन के रास्ते
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]