from django.contrib import admin
from .models import StudentProfile, Quiz, Question, UserResult, PaymentOrder

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_class', 'phone', 'is_premium', 'created_at')
    list_filter = ('student_class', 'is_premium')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'student_class', 'created_at')
    list_filter = ('subject', 'student_class')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'student_class', 'question_text', 'correct_option')
    list_filter = ('subject', 'student_class')

@admin.register(UserResult)
class UserResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'score', 'total_questions', 'percentage', 'date_attempted')
    list_filter = ('subject', 'date_attempted')

@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_type', 'subject_name', 'student_class', 'amount', 'is_paid', 'created_at')
    list_filter = ('plan_type', 'student_class', 'is_paid')
    search_fields = ('user__username', 'razorpay_order_id', 'razorpay_payment_id')