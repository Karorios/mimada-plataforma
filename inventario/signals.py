from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.db import models
from decimal import Decimal
from .models import ItemInventario, CategoriaInventario, RecetaCinta


@receiver(pre_save, sender=ItemInventario)
def guardar_stock_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            anterior = ItemInventario.objects.get(pk=instance.pk)
            instance._stock_anterior = anterior.stock_actual
        except ItemInventario.DoesNotExist:
            instance._stock_anterior = None
    else:
        instance._stock_anterior = None


@receiver(post_save, sender=ItemInventario)
def crear_rosa_automatica(sender, instance, created, **kwargs):
    """Cada Cinta nueva crea SU PROPIA Rosa, aunque comparta color con otra cinta."""
    if not created:
        return
    if instance.categoria.tipo != 'INSUMO':
        return
    if instance.categoria.nombre.strip().lower() != 'cintas':
        return
    if not instance.color:
        return

    categoria_rosas, _ = CategoriaInventario.objects.get_or_create(
        nombre='Rosas', defaults={'tipo': 'PRODUCTO_TERMINADO'}
    )

    rosa = ItemInventario.objects.create(
        categoria=categoria_rosas,
        nombre=f"Rosa {instance.nombre}",
        unidad_medida='UNIDAD',
        color=instance.color,
        stock_actual=0,
        stock_minimo=0,
    )
    RecetaCinta.objects.create(
        producto_terminado=rosa,
        cinta=instance,
        metros_por_unidad=Decimal('1.10'),
    )


@receiver(post_save, sender=ItemInventario)
def descontar_cinta_por_produccion(sender, instance, created, **kwargs):
    if created:
        return
    anterior = getattr(instance, '_stock_anterior', None)
    if anterior is None:
        return
    incremento = instance.stock_actual - anterior
    if incremento <= 0:
        return
    receta = getattr(instance, 'receta_cinta', None)
    if receta is None:
        return
    metros_a_descontar = receta.metros_por_unidad * incremento
    ItemInventario.objects.filter(pk=receta.cinta_id).update(
        stock_actual=models.F('stock_actual') - metros_a_descontar
    )