from django.contrib import admin
from .models import ItemCarrusel


@admin.register(ItemCarrusel)
class ItemCarruselAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tipo', 'orden', 'activo', 'fecha_creacion')
    list_editable = ('orden', 'activo')
    list_filter = ('tipo', 'activo')
    ordering = ('orden',)