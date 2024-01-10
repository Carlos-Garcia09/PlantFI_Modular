from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Planta  # Cambia la importación aquí
from .models import Bitacora

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Planta  # Cambia la referencia al modelo Planta
        fields = []  # Agrega campos adicionales si los tienes en Planta

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class BitacoraForm(forms.ModelForm):
    class Meta:
        model = Bitacora
        fields = ['imagen', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
# from .models import Planta  # Cambia la importación aquí

# class SignUpForm(UserCreationForm):
#     class Meta:
#         model = User
#         fields = ['username', 'password1', 'password2']

# class UserProfileForm(forms.ModelForm):
#     class Meta:
#         model = Planta  # Cambia la referencia al modelo Planta
#         fields = []  # Agrega campos adicionales si los tienes en Planta

# class LoginForm(forms.Form):
#     username = forms.CharField(label='Username', max_length=100)
#     password = forms.CharField(label='Password', widget=forms.PasswordInput)