from datetime import date

from django import forms
from catalogo.models import Producto


class VentaPresencialForm(forms.Form):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(disponible=True),
        required=False,
        label="Producto del catálogo",
        help_text="Elige uno si ya existe en el catálogo.",
    )
    producto_nombre_libre = forms.CharField(
        required=False,
        max_length=150,
        label="O escribe el nombre (si no está en el catálogo)",
        help_text="Ej: 'rosas unidad', para ventas sueltas que no son un producto del catálogo.",
    )
    cantidad = forms.IntegerField(min_value=1, initial=1, label="Cantidad")
    precio_unitario = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        label="Precio unitario",
        help_text="Se autocompleta si eliges un producto del catálogo; puedes ajustarlo.",
    )
    nombre_cliente = forms.CharField(required=False, max_length=120, label="Nombre del cliente (opcional)")
    telefono_cliente = forms.CharField(required=False, max_length=20, label="Teléfono (opcional)")
    fecha_venta = forms.DateField(
        initial=date.today, label="Fecha de la venta",
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def clean(self):
        cleaned = super().clean()
        producto = cleaned.get('producto')
        nombre_libre = (cleaned.get('producto_nombre_libre') or '').strip()

        if not producto and not nombre_libre:
            raise forms.ValidationError(
                "Elige un producto del catálogo o escribe el nombre manualmente."
            )

        precio = cleaned.get('precio_unitario')
        if not precio and producto:
            cleaned['precio_unitario'] = producto.precio

        if not cleaned.get('precio_unitario'):
            raise forms.ValidationError(
                "Indica un precio unitario (o elige un producto del catálogo que ya tenga precio)."
            )

        return cleaned

    def nombre_para_historial(self):
        """Nombre que se usará para HistorialVentas — coincide con las
        claves de CONTENIDO_ROSAS/GIRASOLES/LIRIOS en heuristica.py."""
        producto = self.cleaned_data.get('producto')
        if producto:
            return producto.nombre.strip().lower()
        return self.cleaned_data.get('producto_nombre_libre', '').strip().lower()