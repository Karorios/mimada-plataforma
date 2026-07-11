from django import forms
from .models import ItemInventario, CategoriaInventario


class ItemInventarioForm(forms.ModelForm):
    class Meta:
        model = ItemInventario
        fields = [
            'categoria', 'nombre', 'unidad_medida', 'color',
            'imagen', 'precio', 'stock_actual', 'stock_minimo',
        ]
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-input'}),
            'nombre': forms.TextInput(attrs={'class': 'form-input'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-input'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-input', 'style': 'height:42px; padding:4px; cursor:pointer;'}),
            'precio': forms.NumberInput(attrs={'class': 'form-input'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-input'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-input'}),
        }


class CategoriaInventarioForm(forms.ModelForm):
    class Meta:
        model = CategoriaInventario
        fields = ['nombre', 'tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input'}),
            'tipo': forms.Select(attrs={'class': 'form-input'}),
        }