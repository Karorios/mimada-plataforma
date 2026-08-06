from django.db import models
from pedidos.models import Pedido


class Abono(models.Model):
    METODO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('TARJETA', 'Tarjeta'),
        ('OTRO', 'Otro'),
    ]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='abonos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES, default='EFECTIVO')
    nota = models.CharField(max_length=255, blank=True)
    fecha_abono = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_abono']

    def __str__(self):
        return f"Abono ${self.monto} - Pedido #{self.pedido_id}"