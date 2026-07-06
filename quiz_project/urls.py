# quiz_project/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),          # एडमिन पैनल का रास्ता
    path('', include('quiz_app.urls')),       # बाकी सारे पेजेस का रास्ता quiz_app संभालेगा
]

