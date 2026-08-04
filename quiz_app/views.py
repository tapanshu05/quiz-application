import random
import json
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings

from .forms import StudentRegistrationForm
from .models import StudentProfile, Quiz, Question


# 📚 Class Wise Dynamic Subjects Mapping
CLASS_SUBJECTS = {
    '9': [
        {'name': 'Mathematics', 'icon': '📐', 'desc': 'NCERT step-by-step solutions & practice tests.'},
        {'name': 'Science', 'icon': '🧪', 'desc': 'Physics, Chemistry & Biology concepts.'},
        {'name': 'English', 'icon': '📚', 'desc': 'Grammar, prose & poetry notes.'},
        {'name': 'SST', 'icon': '🌍', 'desc': 'History, Geography, Civics & Economics.'},
        {'name': 'Hindi', 'icon': '✍️', 'desc': 'Kritika & Kshitij chapter notes.'},
        {'name': 'Physical Education', 'icon': '⚽', 'desc': 'Physical education study guides.'},
    ],
    '10': [
        {'name': 'Mathematics', 'icon': '📐', 'desc': 'Board exam targeted solutions & formulas.'},
        {'name': 'Science', 'icon': '🧪', 'desc': 'Physics, Chemistry & Biology board prep.'},
        {'name': 'English', 'icon': '📚', 'desc': 'First Flight & Footprints solved notes.'},
        {'name': 'SST', 'icon': '🌍', 'desc': 'History, Geography, Civics & Economics.'},
        {'name': 'Hindi', 'icon': '✍️', 'desc': 'Complete Hindi syllabus & solutions.'},
        {'name': 'Physical Education', 'icon': '⚽', 'desc': 'Physical education study guides.'},
    ],
    '11': [
        {'name': 'Mathematics', 'icon': '📐', 'desc': 'Algebra, Calculus & Coordinate Geometry.'},
        {'name': 'Physics', 'icon': '⚡', 'desc': 'Mechanics, Thermodynamics & Waves.'},
        {'name': 'Chemistry', 'icon': '🧪', 'desc': 'Organic, Inorganic & Physical Chemistry.'},
        {'name': 'Biology', 'icon': '🧬', 'desc': 'Botany, Zoology & Key Diagrams.'},
        {'name': 'English', 'icon': '📚', 'desc': 'Hornbill & Snapshots core literature.'},
        {'name': 'Physical Education', 'icon': '⚽', 'desc': 'Theory & Practical study material.'},
    ],
    '12': [
        {'name': 'Mathematics', 'icon': '📐', 'desc': 'Calculus, Vectors & 3D Geometry.'},
        {'name': 'Physics', 'icon': '⚡', 'desc': 'Electrostatics, Optics & Modern Physics.'},
        {'name': 'Chemistry', 'icon': '🧪', 'desc': 'Complete Board exam revision notes.'},
        {'name': 'Biology', 'icon': '🧬', 'desc': 'Genetics, Biotechnology & Ecology.'},
        {'name': 'English', 'icon': '📚', 'desc': 'Flamingo & Vistas solved notes.'},
        {'name': 'Physical Education', 'icon': '⚽', 'desc': 'Theory & Practical study material.'},
    ]
}


# 1. Landing Page
def landing_page_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'quiz_app/home.html')


# 2. Send OTP API
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


# 📩 Background Email Sending Function
def send_welcome_email_async(user_email, username):
    try:
        subject = "🎉 Welcome to FormulaFly! Registration Successful"
        message = (
            f"Hello {username},\n\n"
            f"Congratulations! Your registration on FormulaFly has been completed successfully.\n\n"
            f"Thank you for choosing us to power your learning journey!\n\n"
            f"Best regards,\n"
            f"Team FormulaFly"
        )
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'formulafly.online@gmail.com')
        
        # Send Email
        sent_count = send_mail(subject, message, from_email, [user_email], fail_silently=False)
        print(f"✅ EMAIL SUCCESS: Sent {sent_count} email to {user_email}")
    except Exception as e:
        print(f"❌ EMAIL ERROR: Failed to send to {user_email}. Reason: {e}")


# 3. Registration View
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile, created = StudentProfile.objects.get_or_create(user=user)
            
            # अगर URL query में class आयी थी तो उसे भी सेव कर लो
            selected_class = request.GET.get('class')
            if selected_class and hasattr(profile, 'student_class'):
                profile.student_class = selected_class
            profile.save()
            
            # 🚀 Threading Call
            if user.email:
                email_thread = threading.Thread(
                    target=send_welcome_email_async, 
                    args=(user.email, user.first_name or user.username)
                )
                email_thread.start()
            
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
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


# 6. Dynamic Student Dashboard View
@login_required
def student_dashboard(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    student_class = str(getattr(profile, 'student_class', '10') or '10')
    
    # स्टूडेंट की क्लास के हिसाब से ऑटोमैटिक सब्जेक्ट्स लोड होंगे
    subjects = CLASS_SUBJECTS.get(student_class, CLASS_SUBJECTS['10'])

    context = {
        'profile': profile,
        'student_class': student_class,
        'subjects': subjects,
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

# 14. Subject Detail Page (Notes & Solutions)
@login_required
def subject_detail_view(request, subject_name):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    student_class = str(getattr(profile, 'student_class', '10') or '10')

    context = {
        'subject_name': subject_name,
        'student_class': student_class,
    }
    return render(request, 'quiz_app/subject_detail.html', context)