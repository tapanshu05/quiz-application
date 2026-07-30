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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # ईमेल को ही यूजरनेम बना रहे हैं
        user.first_name = self.cleaned_data['name']
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            user.save()
            StudentProfile.objects.create(
                user=user,
                mobile_number=self.cleaned_data['mobile_number'],
                student_class=self.cleaned_data['student_class']
            )
        return user


class StudentLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'})
    )