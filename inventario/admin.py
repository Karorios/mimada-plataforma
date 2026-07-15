from django.contrib import admin

# Register your models here.
from .models import CategoriaInventario, ItemInventario

admin.site.register(CategoriaInventario)
admin.site.register(ItemInventario)