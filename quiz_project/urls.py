# quiz_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),          # एडमिन पैनल का रास्ता
    path('', include('quiz_app.urls')),       # बाकी सारे पेजेस का रास्ता quiz_app संभालेगा
]

from django.contrib.auth.models import User
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser 'admin' created successfully!")
except Exception:
    pass