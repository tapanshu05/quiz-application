from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 1. Student Profile Model
class StudentProfile(models.Model):
    CLASS_CHOICES = (
        ('9', 'Class 9th'),
        ('10', 'Class 10th'),
        ('11', 'Class 11th'),
        ('12', 'Class 12th'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_class = models.CharField(max_length=10, choices=CLASS_CHOICES, default='10')
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - Class {self.student_class}"


# 2. Quiz Model
class Quiz(models.Model):
    title = models.CharField(max_length=200, default="Quiz")
    subject = models.CharField(max_length=100, default="Mathematics")
    student_class = models.CharField(max_length=10, default='10')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.subject} - Class {self.student_class})"


# 3. Question Model
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    subject = models.CharField(max_length=100, default="Mathematics")
    student_class = models.CharField(max_length=10, default='10')
    chapter_name = models.CharField(max_length=200, blank=True, null=True)
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(
        max_length=1, 
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.subject} (Class {self.student_class}) - {self.question_text[:50]}"


# 4. User Result Model
class UserResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, default="Mathematics")
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField(default=0.0)
    date_attempted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.subject}: {self.score}/{self.total_questions}"


# 5. Payment Order Model
class PaymentOrder(models.Model):
    PLAN_CHOICES = (
        ('single', 'Single Subject'),
        ('maths_science', 'Maths + Science Combo'),
        ('all_subjects', 'All Subjects Super Combo'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=20, choices=PLAN_CHOICES)
    subject_name = models.CharField(max_length=100, blank=True, null=True)
    student_class = models.CharField(max_length=10)
    amount = models.IntegerField()
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.get_plan_type_display()} - Class {self.student_class} (Paid: {self.is_paid})"