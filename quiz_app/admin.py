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