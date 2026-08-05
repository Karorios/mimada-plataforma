from datetime import date, timedelta

from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):

    class Meta:
        model = Pedido

        fields = [
            "tipo_entrega",
            "es_regalo",
            "entrega_anonima",
            "nombre_destinatario",
            "telefono_destinatario",
            "mensaje",
            "direccion",
            "barrio",
            "ciudad",
            "referencia",
            "fecha_entrega",
            "hora_entrega",
        ]

        widgets = {
            "tipo_entrega": forms.Select(),

            "nombre_destinatario": forms.TextInput(),

            "telefono_destinatario": forms.TextInput(),

            "mensaje": forms.Textarea(attrs={
                "rows": 3
            }),

            "direccion": forms.TextInput(),

            "barrio": forms.TextInput(),

            "ciudad": forms.TextInput(),

            "referencia": forms.Textarea(attrs={
                "rows": 2
            }),

            "fecha_entrega": forms.DateInput(attrs={
                "type": "date"
            }),

            "hora_entrega": forms.Select(
    choices=[
        ("08:00 - 10:00", "8:00 AM - 10:00 AM"),
        ("10:00 - 12:00", "10:00 AM - 12:00 PM"),
        ("12:00 - 02:00", "12:00 PM - 2:00 PM"),
        ("02:00 - 04:00", "2:00 PM - 4:00 PM"),
        ("04:00 - 06:00", "4:00 PM - 6:00 PM"),
    ]
),

        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        fecha_minima = date.today() + timedelta(days=2)

        self.fields["fecha_entrega"].widget.attrs["min"] = (
            fecha_minima.isoformat()
        )

    def clean_fecha_entrega(self):
        fecha = self.cleaned_data["fecha_entrega"]
        fecha_minima = date.today() + timedelta(days=2)
        if fecha < fecha_minima:
            raise forms.ValidationError(
                "Los pedidos deben realizarse con mínimo 2 días de anticipación."
            )
        return fecha

    def clean(self):
        datos = super().clean()
        tipo_entrega = datos.get("tipo_entrega")
        if tipo_entrega == "DOMICILIO":
            if not datos.get("direccion"):
                self.add_error("direccion", "La dirección es obligatoria para domicilio.")
            if not datos.get("barrio"):
                self.add_error("barrio", "El barrio es obligatorio para domicilio.")
        return datos