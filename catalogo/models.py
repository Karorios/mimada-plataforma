from django.db import models


class Categoria(models.Model):
    NOMBRE_CHOICES = [
        ('FLORES', 'Flores'),
        ('CAJAS_SORPRESA', 'Cajas sorpresa'),
        ('LLAVEROS', 'Llaveros'),
        ('MONAS', 'Moñas'),
        ('DETALLES_HOMBRES', 'Detalles hombres'),
    ]
    nombre = models.CharField(max_length=30, choices=NOMBRE_CHOICES, unique=True)
    descripcion = models.CharField(max_length=200, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.get_nombre_display()


class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='catalogo/productos/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)  # para "trabajos anteriormente hechos" / hero

    unidades_listas = models.PositiveIntegerField(
        default=0,
        help_text="Unidades ya armadas y listas para entrega inmediata. Solo informativo, no bloquea la venta."
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-destacado', 'nombre']

    def __str__(self):
        return self.nombre