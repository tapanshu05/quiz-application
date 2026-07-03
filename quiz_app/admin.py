from django.contrib import admin
from .models import Quiz, Question, UserResult

# अगर admin.site.register(UserResult) पहले से लिखा है, तो उसे हटा दें

@admin.register(UserResult)
class UserResultAdmin(admin.ModelAdmin):
    # यह लाइन एडमिन पैनल में सुंदर कॉलम बना देगी
    list_display = ('user', 'quiz', 'score', 'total_questions')
    
    # यह लाइन आपको किसी भी स्टूडेंट के नाम से रिज़ल्ट सर्च करने का ऑप्शन देगी
    search_fields = ('user__username', 'quiz__title')