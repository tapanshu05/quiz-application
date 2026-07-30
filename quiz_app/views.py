import random
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import StudentRegistrationForm
from .models import StudentProfile, Quiz, Question

# 1. Teachoo Style Dark Landing Page
def landing_page_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'quiz_app/home.html')


# Send OTP API
@csrf_exempt
def send_otp_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone')
            
            if not phone or len(phone) != 10:
                return JsonResponse({'status': 'error', 'message': '10 अंकों का मान्य मोबाइल नंबर डालें!'}, status=400)
                
            generated_otp = str(random.randint(1000, 9999))
            request.session['register_otp'] = generated_otp
            request.session['register_phone'] = phone
            
            return JsonResponse({
                'status': 'success', 
                'message': f'OTP आपके नंबर पर भेज दिया गया है! (Testing OTP: {generated_otp})'
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid Request'}, status=400)


# Registration View
from django.core.mail import send_mail
from django.conf import settings

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile, created = StudentProfile.objects.get_or_create(user=user)
            profile.save()
            
            # 📩 Send Welcome Email Automatically (100% FREE)
            try:
                subject = "🎉 Welcome to FormulaFly! Registration Successful"
                message = f"Hello {user.first_name or user.username},\n\nCongratulations! Your registration on FormulaFly has been completed successfully.\n\nThank you for choosing us to power your learning journey!\n\nBest regards,\nTeam FormulaFly"
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [user.email]
                
                send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            except Exception as e:
                print(f"Email Error: {e}")
            
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
        
    return render(request, 'quiz_app/register.html', {'form': form})
# 4. Student Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'quiz_app/login.html', {'form': form})

# 5. Logout View
def logout_view(request):
    logout(request)
    return redirect('landing')

# 6. Dashboard View
@login_required
def student_dashboard(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    student_class = getattr(profile, 'student_class', '10') or '10'
    
    subject_price = 149 if student_class in ['9', '10'] else 199

    context = {
        'profile': profile,
        'student_class': student_class,
        'subject_price': subject_price,
    }
    return render(request, 'quiz_app/dashboard.html', context)

# 7. Start Quiz
@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    return render(request, 'quiz_app/start_quiz.html', {'quiz': quiz, 'questions': questions})

# 8. Submit Quiz
@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'quiz_app/quiz_result.html', {'quiz': quiz})

# 9. Performance History
@login_required
def performance_history_view(request):
    return render(request, 'quiz_app/performance.html')

# 10. Solutions View
@login_required
def solutions_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    if not getattr(profile, 'is_premium', False):
        return redirect('checkout')
    return render(request, 'quiz_app/solutions.html')

# 11. Notes View
@login_required
def notes_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    if not getattr(profile, 'is_premium', False):
        return redirect('checkout')
    return render(request, 'quiz_app/notes.html')

# 12. Checkout
@login_required
def checkout_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    student_class = getattr(profile, 'student_class', '10') or '10'
    price = 149 if student_class in ['9', '10'] else 199
    
    return render(request, 'quiz_app/checkout.html', {'price': price, 'student_class': student_class})

# 13. Payment Success
@login_required
def payment_success_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    profile.is_premium = True
    profile.save()
    return render(request, 'quiz_app/payment_success.html')