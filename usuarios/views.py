from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from catalogo.models import Producto
from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, RegistroForm, EditarPerfilForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
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
            user.username = form.cleaned_data['email']  # Usa el correo como username
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('usuarios:login')


def login_admin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('finanzas:dashboard')
        else:
            messages.error(
                request,
                'Credenciales incorrectas o no tienes permisos de administrador'
            )

    return render(request, 'usuarios/login_admin.html')


@login_required(login_url='usuarios:login')
def favoritos_view(request):
    favoritos = request.user.favoritos.all()
    return render(request, 'usuarios/favoritos.html', {'favoritos': favoritos})


@login_required(login_url='usuarios:login')
def toggle_favorito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if producto in request.user.favoritos.all():
        request.user.favoritos.remove(producto)
    else:
        request.user.favoritos.add(producto)
    return redirect(request.META.get('HTTP_REFERER', 'usuarios:favoritos'))

@login_required(login_url='usuarios:login')
def mi_cuenta_view(request):
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tus datos se actualizaron correctamente.')
            return redirect('usuarios:mi_cuenta')
    else:
        form = EditarPerfilForm(instance=request.user)

    return render(request, 'usuarios/mi_cuenta.html', {'form': form})
