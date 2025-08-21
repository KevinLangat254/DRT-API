from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()  # ✅ This gives you the actual User model class

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"placeholder": "Enter username", "class": "form-control"})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password", "class": "form-control"})
    )

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User   # ✅ now this is the real model, not a string
        fields = ["username", "email", "password1", "password2"]
