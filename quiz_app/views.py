from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, UserResult
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
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST' or request.method == 'GET':
        auth_logout(request)
    return redirect('login')

@login_required(login_url='login')
def student_dashboard(request):
    # Fetch results belonging strictly to the logged-in student
    past_results = UserResult.objects.filter(user=request.user)
    
    # Fetch all available quizzes for them to take
    available_quizzes = Quiz.objects.all()
    
    context = {
        'past_results': past_results,
        'available_quizzes': available_quizzes
    }
    return render(request, 'quiz_app/dashboard.html', context)


import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import StudentProfile

# Razorpay Client Initialization
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required(login_url='login')
def checkout_view(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if profile.is_premium:
        return redirect('student_dashboard')
        
    amount = 5900  # ₹59 = 5900 Paise
    currency = "INR"
    
    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        payment_capture='1'
    ))
    
    context = {
        'order_id': razorpay_order['id'],
        'amount': amount,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'user': request.user
    }
    return render(request, 'quiz_app/checkout.html', context)

@csrf_exempt
def payment_success_view(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        
        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            profile = StudentProfile.objects.get(user=request.user)
            profile.is_premium = True
            profile.payment_id = payment_id
            profile.save()
            
            return render(request, 'quiz_app/payment_status.html', {'status': 'success'})
        except Exception as e:
            return render(request, 'quiz_app/payment_status.html', {'status': 'failed'})
            
    return HttpResponseBadRequest()