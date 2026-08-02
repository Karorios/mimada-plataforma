from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('logout/', views.logout_view, name='logout'),
    path('login-admin/', views.login_admin_view, name='login_admin'),
    path('favoritos/', views.favoritos_view, name='favoritos'),
    path('favoritos/<int:producto_id>/toggle/', views.toggle_favorito, name='toggle_favorito'),
]