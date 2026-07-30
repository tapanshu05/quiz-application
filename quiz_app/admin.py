from django.contrib import admin
from .models import StudentProfile, Quiz, Question, UserResult

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_class', 'mobile_number', 'is_premium', 'payment_id')
    list_filter = ('is_premium', 'student_class')
    search_fields = ('user__username', 'user__email', 'mobile_number', 'payment_id')

