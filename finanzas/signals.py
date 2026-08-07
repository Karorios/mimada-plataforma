from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Abono


@receiver(post_save, sender=Abono)
def avanzar_pedido_al_recibir_abono(sender, instance, created, **kwargs):
    """Cuando se registra un abono, si el pedido sigue Pendiente/Confirmado,
    lo pasa automáticamente a En Proceso."""
    if not created:
        return

    pedido = instance.pedido
    if pedido.estado in ('PENDIENTE', 'CONFIRMADO'):
        pedido.estado = 'EN_PROCESO'
        pedido.save()