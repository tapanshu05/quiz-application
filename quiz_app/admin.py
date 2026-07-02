# quiz_app/admin.py
from django.contrib import admin
from .models import Quiz, Question, UserResult

# Registering models so they appear in the Admin Panel
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(UserResult)