from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from inventario.models import ItemInventario
from catalogo.models import Producto


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADO', 'Confirmado'),
        ('EN_PROCESO', 'En proceso'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pedidos')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PENDIENTE')
    direccion_entrega = models.CharField(max_length=255)
    telefono_contacto = models.CharField(max_length=20)
    notas = models.TextField(blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente}"


class DetallePedido(models.Model):
    """Una línea del pedido: puede ser un producto del catálogo TAL CUAL,
    o un ramo personalizado armado en 'Crea tu detalle'."""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, null=True, blank=True)
    es_personalizado = models.BooleanField(default=False)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle de pedido #{self.pedido_id}"


class ConfiguracionRamo(models.Model):
    """Solo existe si DetallePedido.es_personalizado = True"""
    detalle_pedido = models.OneToOneField(DetallePedido, on_delete=models.CASCADE, related_name='configuracion')
    cantidad_rosas = models.PositiveSmallIntegerField()
    color_rosa = models.ForeignKey(ItemInventario, on_delete=models.PROTECT, related_name='+')
    color_cinta = models.ForeignKey(ItemInventario, on_delete=models.PROTECT, related_name='+')
    papel_decorativo = models.ForeignKey(ItemInventario, on_delete=models.PROTECT, related_name='+', null=True, blank=True)
    adicionales = models.ManyToManyField(ItemInventario, blank=True, related_name='+')

    def __str__(self):
        return f"Config. ramo - detalle #{self.detalle_pedido_id}"