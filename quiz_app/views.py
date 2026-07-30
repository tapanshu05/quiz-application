from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.conf import settings
import razorpay

# मॉडल और फॉर्म इम्पोर्ट्स
from .models import Quiz, Question, UserResult, StudentProfile
from .forms import StudentRegistrationForm  # कस्टम फॉर्म जो हमने बनाया था

# Razorpay Client Initialization
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def register_view(request):
    """
    1. Custom Registration View:
    नाम, क्लास (9-12), मोबाइल नंबर, ईमेल और पासवर्ड लेता है और स्टूडेंट प्रोफाइल सेव करता है।
    """
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """2. Login View"""
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
    """3. Logout View"""
    if request.method == 'POST' or request.method == 'GET':
        auth_logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    """4. Homepage: Fetches all available quizzes"""
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_app/home.html', {'quizzes': quizzes})


@login_required(login_url='login')
def student_dashboard(request):
    """
    5. Student Dashboard:
    छात्र की क्लास के हिसाब से ऑटोमैटिक ₹149 या ₹199 का प्राइस तय करता है।
    """
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    past_results = UserResult.objects.filter(user=request.user)
    available_quizzes = Quiz.objects.all()
    
    # 💡 डायनामिक प्राइसिंग लॉजिक (Class Based)
    # Class 9 और 10 के लिए ₹149, Class 11 और 12 के लिए ₹199
    if profile.student_class in ['9', '10']:
        subject_price = 149
    else:
        subject_price = 199

    context = {
        'profile': profile,
        'student_class': profile.student_class,
        'subject_price': subject_price,
        'past_results': past_results,
        'available_quizzes': available_quizzes
    }
    return render(request, 'quiz_app/dashboard.html', context)


@login_required(login_url='login')
def checkout_view(request):
    """
    6. Dynamic Checkout View:
    अगर यूजर Class 9/10 का है तो Razorpay पर ₹149 (14900 Paise) का आर्डर बनेगा।
    अगर Class 11/12 का है तो ₹199 (19900 Paise) का आर्डर बनेगा।
    """
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # अगर छात्र पहले से ही प्रीमियम है, तो सीधे डैशबोर्ड पर भेज दो
    if profile.is_premium:
        return redirect('dashboard')
        
    # 💡 डायनामिक रेज़रपे अमाउंट लॉजिक
    if profile.student_class in ['9', '10']:
        amount_in_rupees = 149
        amount = 14900  # ₹149 = 14900 Paise
    else:
        amount_in_rupees = 199
        amount = 19900  # ₹199 = 19900 Paise
    
    currency = "INR"
    
    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        payment_capture='1'
    ))
    
    context = {
        'order_id': razorpay_order['id'],
        'amount': amount,
        'display_amount': amount_in_rupees,
        'student_class': profile.student_class,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'user': request.user
    }
    return render(request, 'quiz_app/checkout.html', context)


@csrf_exempt
def payment_success_view(request):
    """7. Auto Payment Handler: रेज़रपे से पेमेंट कंफर्म होते ही प्रीमियम एक्टिव होगा।"""
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
            # सिग्नेचर वेरीफाई करें
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # ऑटोमैटिक प्रीमियम एक्टिव कर दो
            if request.user.is_authenticated:
                profile, created = StudentProfile.objects.get_or_create(user=request.user)
                profile.is_premium = True
                profile.payment_id = payment_id
                profile.save()
            
            return redirect('dashboard')
            
        except razorpay.errors.SignatureVerificationError:
            return HttpResponseBadRequest("Security Check Failed: Invalid Signature.")
        except Exception as e:
            return HttpResponseBadRequest(f"An unexpected error occurred: {str(e)}")
            
    return redirect('dashboard')


@login_required(login_url='login')
def start_quiz(request, quiz_id):
    """8. Quiz Page"""
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    return render(request, 'quiz_app/start_quiz.html', {'quiz': quiz, 'questions': questions})


@login_required(login_url='login')
def submit_quiz(request, quiz_id):
    """9. Submission Logic & Detailed Analysis"""
    if request.method == "POST":
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        score = 0
        total_questions = questions.count()
        
        detailed_analysis = []

        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}', '')
            is_correct = (user_answer == question.correct_option)
            
            if is_correct:
                score += 1
                
            detailed_analysis.append({
                'question_text': question.question_text,
                'option_a': question.option_a,
                'option_b': question.option_b,
                'option_c': question.option_c,
                'option_d': question.option_d,
                'user_answer': user_answer,
                'correct_option': question.correct_option,
                'is_correct': is_correct,
                'solution': getattr(question, 'solution', 'No solution provided.'),
            })

        UserResult.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            total_questions=total_questions
        )

        return render(request, 'quiz_app/result.html', {
            'quiz': quiz,
            'score': score,
            'total_questions': total_questions,
            'analysis': detailed_analysis
        })

    return redirect('home')


@login_required(login_url='login')
def solutions_view(request):
    """10. Solutions View (Premium Locked)"""
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if not profile.is_premium:
        return redirect('checkout')
    return render(request, 'quiz_app/solutions.html')


@login_required(login_url='login')
def notes_view(request):
    """11. Notes View (Premium Locked)"""
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if not profile.is_premium:
        return redirect('checkout')
    return render(request, 'quiz_app/notes.html')


@login_required(login_url='login')
def performance_history_view(request):
    """12. Performance History Page (Premium Locked)"""
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if not profile.is_premium:
        return redirect('checkout')
        
    past_results = UserResult.objects.filter(user=request.user).order_by('-id')
    return render(request, 'quiz_app/performance.html', {'past_results': past_results})
