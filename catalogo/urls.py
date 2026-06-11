from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.inicio, name='inicio'),
]