from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from .models import Quiz, Question, UserResult

@login_required(login_url='login')
def home(request):
    """1. Homepage: Fetches all available quizzes from the database and displays them"""
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_app/home.html', {'quizzes': quizzes})

@login_required(login_url='login')
def start_quiz(request, quiz_id):
    """2. Quiz Page: Fetches a specific quiz and all its questions for the user"""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    return render(request, 'quiz_app/start_quiz.html', {'quiz': quiz, 'questions': questions})

@login_required(login_url='login')
def submit_quiz(request, quiz_id):
    """3. Submission Logic: Calculates scores and saves them to the UserResult table"""
    if request.method == "POST":
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        score = 0
        total_questions = questions.count()

        # Loop through each question to check if the submitted answer matches the correct one
        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}') # Gets selected radio option
            if user_answer == question.correct_option:
                score += 1

        # Save the finalized performance record into the database
        UserResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions
        )
        
        # Take the user to a summary dashboard or back home after submission
        return render(request, 'quiz_app/result.html', {
            'quiz': quiz,
            'score': score,
            'total_questions': total_questions
        })
        
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user) # रजिस्टर होते ही ऑटोमैटिक लॉगिन हो जाएगा
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'quiz_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'quiz_app/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST' or request.method == 'GET':
        auth_logout(request)
    return redirect('login')