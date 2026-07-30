from django import forms
from django.contrib.auth.models import User
from .models import StudentProfile

class StudentRegistrationForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    mobile_number = forms.CharField(
        max_length=15, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'})
    )
    student_class = forms.ChoiceField(
        choices=StudentProfile.CLASS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create Password'})
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    # 💡 1. डुप्लीकेट ईमेल और यूजरनेम रोकने का वैलीडेशन
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please login instead!")
        return email

    # 💡 2. सेफ सेव मेथड (ताकि प्रोफाइल क्रिएट होते वक्त IntegrityError न आए)
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # ईमेल को ही यूजरनेम बना रहे हैं
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['name']
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            # get_or_create सेफ तरीका है ताकि अगर प्रोफाइल सिग्नल से बन भी गई हो तो क्रैश न हो
            profile, created = StudentProfile.objects.get_or_create(user=user)
            profile.mobile_number = self.cleaned_data['mobile_number']
            profile.student_class = self.cleaned_data['student_class']
            profile.save()
            
        return user