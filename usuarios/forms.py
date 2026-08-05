from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'tucorreo@ejemplo.com',
            'class': 'form-input'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'form-input'
        })
    )

class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'tucorreo@ejemplo.com',
            'class': 'form-input'
        })
    )
    first_name = forms.CharField(
        label='Nombre completo',
        widget=forms.TextInput(attrs={
            'placeholder': 'Tu nombre completo',
            'class': 'form-input'
        })
    )
    telefono = forms.CharField(
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'placeholder': '+57 300 000 0000',
            'class': 'form-input'
        })
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'email', 'telefono', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(username=email).exists():
            raise forms.ValidationError('Ese correo ya tiene una cuenta asociada. Intenta iniciar sesión.')
        return email