# quiz_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # आपके पुराने पाथ पहले से यहाँ होंगे, उनके नीचे ये जोड़ें:
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]