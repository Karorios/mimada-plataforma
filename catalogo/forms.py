from django import forms
from .models import Producto, ItemCarrusel
from .models import Producto, ItemCarrusel, ProductoDelMes


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


class ItemCarruselForm(forms.ModelForm):
    class Meta:
        model = ItemCarrusel
        fields = [
            'tipo', 'producto', 'imagen', 'ajuste_imagen',
            'titulo', 'subtitulo', 'texto_boton', 'url_destino', 'orden', 'activo',
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'campo-input', 'id': 'id_tipo'}),
            'producto': forms.Select(attrs={'class': 'campo-input'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'campo-file'}),
            'ajuste_imagen': forms.Select(attrs={'class': 'campo-input', 'id': 'id_ajuste_imagen'}),
            'titulo': forms.TextInput(attrs={'class': 'campo-input', 'placeholder': "Ej: Mes del amor y la amistad"}),
            'subtitulo': forms.TextInput(attrs={'class': 'campo-input', 'placeholder': "Ej: El mes perfecto para tu pedido"}),
            'texto_boton': forms.TextInput(attrs={'class': 'campo-input', 'placeholder': "Ver más"}),
            'url_destino': forms.TextInput(attrs={'class': 'campo-input', 'placeholder': "/catalogo/lista/"}),
            'orden': forms.NumberInput(attrs={'class': 'campo-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'campo-check'}),
        }
class ProductoDelMesForm(forms.ModelForm):
    class Meta:

                model = ProductoDelMes
                fields = [
                    'tipo', 'producto', 'imagen',
                    'titulo', 'descripcion', 'texto_boton', 'url_destino', 'orden', 'activo',
                ]

                def clean(self):
                    datos = super().clean()
                    tipo = datos.get('tipo')
                    producto = datos.get('producto')
                    if tipo == 'PRODUCTO' and not producto:
                        self.add_error('producto', 'Selecciona un producto del catálogo.')
                    return datos

                widgets = {
                    'tipo': forms.Select(attrs={'class': 'campo-input', 'id': 'id_tipo'}),
                    'producto': forms.Select(attrs={'class': 'campo-input'}),
                    'imagen': forms.ClearableFileInput(attrs={'class': 'campo-file'}),
                    'titulo': forms.TextInput(attrs={'class': 'campo-input', 'placeholder': "Ej: Ramo de rosas rojas"}),
                    'descripcion': forms.TextInput(
                        attrs={'class': 'campo-input', 'placeholder': "Descripción corta para la card"}),
                    'texto_boton': forms.TextInput(attrs={'class': 'campo-input', 'placeholder': "Ver producto"}),
                    'url_destino': forms.TextInput(
                        attrs={'class': 'campo-input', 'placeholder': "/catalogo/producto/5/"}),
                    'orden': forms.NumberInput(attrs={'class': 'campo-input'}),
                    'activo': forms.CheckboxInput(attrs={'class': 'campo-check'}),

                }
