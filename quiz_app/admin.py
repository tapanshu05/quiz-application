from django.contrib import admin
from .models import Quiz, Question, UserResult

# 1. क्विज़ और क्वेश्चंस के ऑप्शन को एडमिन पैनल में वापस लाना
admin.site.register(Quiz)
admin.site.register(Question)

# 2. यूज़र रिज़ल्ट को सुंदर टेबल में दिखाने का आपका पुराना कोड
@admin.register(UserResult)
class UserResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score', 'total_questions')
    search_fields = ('user__username', 'quiz__title')

from django.contrib import admin
from .models import StudentProfile  # 💡 मॉडल को इम्पोर्ट करें

# StudentProfile को एडमिन पैनल में रजिस्टर करें
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_premium', 'payment_id']
    list_filter = ['is_premium']
    search_fields = ['user__username', 'payment_id']