from django.db import models
from django.core.validators import MinValueValidator

class CategoriaInventario(models.Model):
    TIPO_CHOICES = [
        ('PRODUCTO_TERMINADO', 'Producto Terminado'),
        ('INSUMO', 'Insumo'),
    ]

    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=25, choices=TIPO_CHOICES)

    class Meta:
        verbose_name = "Categoría de Inventario"
        verbose_name_plural = "Categorías de Inventario"
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"


class ItemInventario(models.Model):
    UNIDAD_CHOICES = [
        ('UNIDAD', 'Unidad'),
        ('METRO', 'Metro'),
    ]

    categoria = models.ForeignKey(
        CategoriaInventario, on_delete=models.PROTECT, related_name='items'
    )
    nombre = models.CharField(max_length=150)
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_CHOICES, default='UNIDAD')
    color = models.CharField(max_length=50, blank=True, null=True)
    imagen = models.ImageField(upload_to='inventario/', blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    stock_actual = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)] )
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Item de Inventario"
        verbose_name_plural = "Items de Inventario"
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return self.nombre

    @property
    def estado(self):
        if self.stock_actual <= 0:
            return 'AGOTADO'
        elif self.stock_actual <= self.stock_minimo:
            return 'STOCK_BAJO'
        return 'DISPONIBLE'

    @property
    def estado_display(self):
        return {
            'AGOTADO': 'Agotado',
            'STOCK_BAJO': 'Stock Bajo',
            'DISPONIBLE': 'Disponible',
        }[self.estado]


class RecetaCinta(models.Model):
    producto_terminado = models.OneToOneField(
        ItemInventario, on_delete=models.CASCADE, related_name='receta_cinta'
    )
    cinta = models.ForeignKey(
        ItemInventario, on_delete=models.PROTECT, related_name='usado_en_recetas'
    )
    metros_por_unidad = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.producto_terminado.nombre} usa {self.metros_por_unidad}m de {self.cinta.nombre}"