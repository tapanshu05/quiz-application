# quiz_project/urls.py
from django.contrib import admin
from django.urls import path, include

from quiz_app import views

urlpatterns = [
    path('admin/', admin.site.urls),          # एडमिन पैनल का रास्ता
    path('', include('quiz_app.urls')),  
    path('accounts/', include('allauth.urls')),     # बाकी सारे पेजेस का रास्ता quiz_app संभालेगा
    path('solutions/', views.solutions_view, name='solutions'),
]

