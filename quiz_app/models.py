from django.db import models
from django.contrib.auth.models import User

# 1. Quiz Table
class Quiz(models.Model):
    title = models.CharField(max_length=200)       # Name of the quiz (e.g., Python Basics)
    time_limit = models.IntegerField()             # Time allowed in minutes (e.g., 5)

    def __str__(self):
        return self.title


# 2. Table to store Questions and their 4 multiple-choice options
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE) # Links this question to a specific quiz
    question_text = models.TextField()                       # The actual question
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1)          # Stores 'A', 'B', 'C', or 'D'
    solution = models.TextField(blank=True, null=True, help_text="Write step-by-step LaTeX solution here")

    def __str__(self):
        return self.question_text[:50]


# 3. Table to store User Performance/Results
class UserResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Which user took the test
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE) # Which quiz they took
    score = models.IntegerField()                            # Marks obtained
    total_questions = models.IntegerField()                  # Total questions present

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score}/{self.total_questions})"


# 4. Student Profile Table (All-in-one merged)
class StudentProfile(models.Model):
    CLASS_CHOICES = [
        ('9', 'Class 9th'),
        ('10', 'Class 10th'),
        ('11', 'Class 11th'),
        ('12', 'Class 12th'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    student_class = models.CharField(max_length=2, choices=CLASS_CHOICES, default='10')
    is_premium = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Class {self.student_class}"