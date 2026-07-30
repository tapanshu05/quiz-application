from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm
from .models import StudentProfile, Quiz, Question, UserResponse, Payment

# 1. Teachoo Style Dark Landing Page (Without Login Requirement)
def landing_page_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'quiz_app/home.html')

# 2. Student Registration View
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'quiz_app/register.html', {'form': form})

# 3. Student Login View
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

# 4. Logout View
def logout_view(request):
    logout(request)
    return redirect('landing')

# 5. Student Dashboard View (Dynamic Pricing based on Class)
@login_required
def student_dashboard(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    student_class = profile.student_class or "10"
    
    # 💡 Class 9th & 10th = ₹149 | Class 11th & 12th = ₹199
    if student_class in ['9', '10']:
        subject_price = 149
    else:
        subject_price = 199

    context = {
        'profile': profile,
        'student_class': student_class,
        'subject_price': subject_price,
    }
    return render(request, 'quiz_app/dashboard.html', context)

# 6. Quiz Starting View
@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    return render(request, 'quiz_app/start_quiz.html', {'quiz': quiz, 'questions': questions})

# 7. Quiz Submission View
@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        score = 0
        total = quiz.questions.count()
        
        for question in quiz.questions.all():
            selected_choice_id = request.POST.get(f'question_{question.id}')
            if selected_choice_id:
                choice = Choice.objects.filter(id=selected_choice_id).first()
                if choice and choice.is_correct:
                    score += 1
                UserResponse.objects.create(
                    user=request.user,
                    quiz=quiz,
                    question=question,
                    selected_choice=choice
                )
        return render(request, 'quiz_app/quiz_result.html', {'score': score, 'total': total, 'quiz': quiz})
    return redirect('dashboard')

# 8. Performance History
@login_required
def performance_history_view(request):
    responses = UserResponse.objects.filter(user=request.user)
    return render(request, 'quiz_app/performance.html', {'responses': responses})

# 9. Handwritten Solutions View (Protected)
@login_required
def solutions_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    if not profile.is_premium:
        return redirect('checkout')
    return render(request, 'quiz_app/solutions.html')

# 10. PDF Notes View (Protected)
@login_required
def notes_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    if not profile.is_premium:
        return redirect('checkout')
    return render(request, 'quiz_app/notes.html')

# 11. Checkout / Payment Page View
@login_required
def checkout_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    student_class = profile.student_class or "10"
    price = 149 if student_class in ['9', '10'] else 199
    
    return render(request, 'quiz_app/checkout.html', {'price': price, 'student_class': student_class})

# 12. Payment Success View
@login_required
def payment_success_view(request):
    profile = get_object_or_404(StudentProfile, user=request.user)
    profile.is_premium = True
    profile.save()
    return render(request, 'quiz_app/payment_success.html')