from django import forms
from .models import Abono


class AbonoForm(forms.ModelForm):
    class Meta:
        model = Abono
        fields = ['pedido', 'monto', 'metodo_pago', 'nota']
        widgets = {
            'pedido': forms.Select(attrs={'class': 'form-input'}),
            'monto': forms.NumberInput(attrs={'class': 'form-input'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-input'}),
            'nota': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Opcional'}),
        }