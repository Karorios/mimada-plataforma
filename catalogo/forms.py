from django import forms
from .models import Producto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['categoria', 'nombre', 'descripcion', 'precio', 'imagen', 'disponible', 'destacado']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'campo-input'}),
            'nombre': forms.TextInput(attrs={'class': 'campo-input', 'placeholder': 'Ej: Ramo de rosas rojas'}),
            'descripcion': forms.Textarea(attrs={'class': 'campo-input', 'rows': 3, 'placeholder': 'Describe el detalle...'}),
            'precio': forms.NumberInput(attrs={'class': 'campo-input', 'placeholder': '0'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'campo-file'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'campo-check'}),
            'destacado': forms.CheckboxInput(attrs={'class': 'campo-check'}),
        }