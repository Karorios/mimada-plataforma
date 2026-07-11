from django import forms
from .models import ItemInventario, CategoriaInventario


class ItemInventarioForm(forms.ModelForm):
    tiene_color = forms.BooleanField(
        required=False,
        label='Este producto tiene color',
        widget=forms.CheckboxInput(attrs={'id': 'id_tiene_color'})
    )

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
            'color': forms.TextInput(attrs={
                'type': 'color',
                'id': 'id_color',
                'style': 'width:50px; height:36px; padding:2px; border-radius:8px; border:1px solid #f0c0d4; cursor:pointer;'
            }),
            'precio': forms.NumberInput(attrs={'class': 'form-input'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-input'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si el item ya existe y tiene color guardado, marca el checkbox de entrada
        if self.instance and self.instance.pk and self.instance.color:
            self.fields['tiene_color'].initial = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not self.cleaned_data.get('tiene_color'):
            instance.color = None
        if commit:
            instance.save()
        return instance

class CategoriaInventarioForm(forms.ModelForm):
    class Meta:
        model = CategoriaInventario
        fields = ['nombre', 'tipo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input'}),
            'tipo': forms.Select(attrs={'class': 'form-input'}),
        }