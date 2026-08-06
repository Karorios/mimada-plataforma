from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from catalogo import views as catalogo_views

urlpatterns = [
    path('', catalogo_views.inicio, name='home'),
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('catalogo/', include('catalogo.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('finanzas/', include('finanzas.urls')),
    path('inventario/', include('inventario.urls')),
    path('pedidosadmin/', include('pedidosadmin.urls')),
    path('panelprincipaladmin/', include('panelprincipaladmin.urls')),
    path('asistente-ia/', include('asistente_ia.urls')),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='usuarios/password_reset.html'
         ), name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='usuarios/password_reset_done.html'
         ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='usuarios/password_reset_confirm.html'
         ), name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='usuarios/password_reset_complete.html'
         ), name='password_reset_complete'),
]
