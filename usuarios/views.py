from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import LoginForm, RegistroForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('catalogo:inicio')
        else:
            messages.error(request, 'Correo o contraseña incorrectos')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.save()
            login(request, user)
            return redirect('catalogo:inicio')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('usuarios:login')