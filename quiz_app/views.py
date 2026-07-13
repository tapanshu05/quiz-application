from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.conf import settings
import razorpay

# मॉडल इम्पोर्ट्स
from .models import Quiz, Question, UserResult, StudentProfile

# Razorpay Client Initialization
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

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

        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}')
            if user_answer == question.correct_option:
                score += 1

        UserResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions
        )
        
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
    past_results = UserResult.objects.filter(user=request.user)
    available_quizzes = Quiz.objects.all()
    
    context = {
        'past_results': past_results,
        'available_quizzes': available_quizzes
    }
    return render(request, 'quiz_app/dashboard.html', context)

@login_required(login_url='login')
def checkout_view(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # अगर छात्र पहले से ही प्रीमियम है, तो सीधे डैशबोर्ड पर भेज दो
    if profile.is_premium:
        return redirect('dashboard')
        
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
    """4. Auto Payment Handler: रेज़रपे से पेमेंट कंफर्म होते ही ताला अपने आप खुलेगा और यूज़र डैशबोर्ड पर आ जाएगा।"""
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
            # रेज़रपे के सिग्नेचर को 100% सिक्योर तरीके से वेरीफाई करें
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # अगर यूजर लॉगिन है तो उसकी प्रोफाइल ढूंढकर ऑटोमैटिक प्रीमियम एक्टिव कर दो
            if request.user.is_authenticated:
                profile, created = StudentProfile.objects.get_or_create(user=request.user)
                profile.is_premium = True
                profile.payment_id = payment_id
                profile.save()
            
            # 🚀 बिना किसी फालतू पेज पर रोके छात्र को सीधे प्रीमियम डैशबोर्ड पर रीडायरेक्ट करो
            return redirect('dashboard')
            
        except razorpay.errors.SignatureVerificationError:
            return HttpResponseBadRequest("Security Check Failed: Invalid Signature.")
        except Exception as e:
            return HttpResponseBadRequest(f"An unexpected error occurred: {str(e)}")
            
    return redirect('dashboard')

@login_required(login_url='login')
def solutions_view(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if not profile.is_premium:
        return redirect('checkout')
    return render(request, 'quiz_app/solutions.html')

@login_required(login_url='login')
def notes_view(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if not profile.is_premium:
        return redirect('checkout')
    return render(request, 'quiz_app/notes.html')

@login_required(login_url='login')
def performance_history_view(request):
    """4. Performance History Page: यूजर के सारे पुराने टेस्ट का रिजल्ट नए पेज पर दिखाएगा"""
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # सुरक्षा परत: अगर यूजर प्रीमियम नहीं है तो उसे सीधे पेमेंट पर भगाओ
    if not profile.is_premium:
        return redirect('checkout')
        
    # सिर्फ लॉगिन यूजर के पुराने रिजल्ट्स निकालो (ताजा रिजल्ट सबसे ऊपर - Ordered by latest)
    past_results = UserResult.objects.filter(user=request.user).order_by('-id')
    
    return render(request, 'quiz_app/performance.html', {'past_results': past_results})