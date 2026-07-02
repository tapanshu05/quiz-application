# quiz_app/models.py
from django.db import models
from django.contrib.auth.models import User

# 1. Table to store Quiz Name and its Time Limit
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

    def __str__(self):
        return self.question_text

# 3. Table to store User Performance/Results
class UserResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Which user took the test
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE) # Which quiz they took
    score = models.IntegerField()                            # Marks obtained
    total_questions = models.IntegerField()                  # Total questions present