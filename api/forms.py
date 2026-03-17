from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # We define the fields we want to show upon creation.
        # UserCreationForm automatically handles generating the 2 password confirmation fields!
        fields = ('email', 'role', 'is_staff', 'is_active')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'role', 'is_staff', 'is_active')