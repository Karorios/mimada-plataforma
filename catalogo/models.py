from django.db import models


class Categoria(models.Model):
    NOMBRE_CHOICES = [
        ('FLORES', 'Flores'),
        ('CAJAS_SORPRESA', 'Cajas sorpresa'),
        ('LLAVEROS', 'Llaveros'),
        ('MONAS', 'Moñas'),
        ('DETALLES_HOMBRES', 'Detalles hombres'),
        ('BOMBAS_CHOCOLATE', 'Bombas de chocolate'),
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
class ItemCarrusel(models.Model):
    TIPO_CHOICES = [
        ('PRODUCTO', 'Producto destacado'),
        ('BANNER', 'Banner promocional'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='BANNER')
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, blank=True, null=True,
        related_name='items_carrusel',
        help_text="Solo si el tipo es 'Producto destacado'."
    )
    imagen = models.ImageField(
        upload_to='catalogo/carrusel/', blank=True, null=True,
        help_text="Solo si el tipo es 'Banner promocional'. Si es Producto, se usa la imagen del producto."
    )
    AJUSTE_CHOICES = [
        ('CONTENER', 'Mostrar imagen completa (con fondo difuminado)'),
        ('RECORTAR', 'Recortar imagen a la medida del banner'),
    ]
    ajuste_imagen = models.CharField(
        max_length=10, choices=AJUSTE_CHOICES, default='CONTENER',
        help_text="Cómo se muestra la imagen dentro del banner."
    )

    titulo = models.CharField(max_length=100, blank=True, help_text="Solo para banners. Ej: 'Mes del amor y la amistad'")
    subtitulo = models.CharField(max_length=200, blank=True, help_text="Solo para banners. Ej: 'El mes perfecto para hacer tu pedido'")
    texto_boton = models.CharField(max_length=40, blank=True, default="Ver más")
    url_destino = models.CharField(
        max_length=300, blank=True,
        help_text="A dónde lleva el botón, ej: /catalogo/lista/. Vacío = sin botón."
    )
    orden = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True, help_text="Desactívalo para ocultarlo sin borrarlo.")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Item del carrusel"
        verbose_name_plural = "Items del carrusel"
        ordering = ['orden', '-fecha_creacion']

    def __str__(self):
        if self.tipo == 'PRODUCTO' and self.producto:
            return f"Producto: {self.producto.nombre}"
        return f"Banner: {self.titulo or '(sin título)'}"

    def imagen_url(self):
        if self.tipo == 'PRODUCTO' and self.producto and self.producto.imagen:
            return self.producto.imagen.url
        if self.imagen:
            return self.imagen.url
        return None

class ProductoDelMes(models.Model):
    TIPO_CHOICES = [
        ('PRODUCTO', 'Producto del catálogo'),
        ('PERSONALIZADO', 'Contenido personalizado'),
    ]
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES, default='PRODUCTO')
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, blank=True, null=True,
        related_name='destacados_mes',
        help_text="Solo si el tipo es 'Producto del catálogo'."
    )
    imagen = models.ImageField(
        upload_to='catalogo/destacados_mes/', blank=True, null=True,
        help_text="Solo si el tipo es 'Contenido personalizado'. Si es Producto, se usa la imagen del producto."
    )
    titulo = models.CharField(max_length=100, blank=True, help_text="Se usa el nombre del producto si está vacío.")
    descripcion = models.CharField(max_length=200, blank=True, help_text="Descripción corta para la card.")
    texto_boton = models.CharField(max_length=40, blank=True, default="Ver producto")
    url_destino = models.CharField(
        max_length=300, blank=True,
        help_text="A dónde lleva el botón. Si está vacío y hay producto, va al detalle del producto."
    )
    orden = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True, help_text="Desactívalo para ocultarlo sin borrarlo.")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Producto del mes"
        verbose_name_plural = "Productos del mes"
        ordering = ['orden', '-fecha_creacion']

    def __str__(self):
        if self.tipo == 'PRODUCTO' and self.producto:
            return f"Producto del mes: {self.producto.nombre}"
        return f"Producto del mes: {self.titulo or '(sin título)'}"

    def imagen_url(self):
        if self.tipo == 'PRODUCTO' and self.producto and self.producto.imagen:
            return self.producto.imagen.url
        if self.imagen:
            return self.imagen.url
        return None

    def titulo_mostrar(self):
        if self.titulo:
            return self.titulo
        if self.tipo == 'PRODUCTO' and self.producto:
            return self.producto.nombre
        return ''

    def url_mostrar(self):
        if self.tipo == 'PRODUCTO' and self.producto:
            return f"/catalogo/producto/{self.producto.id}/"
        if self.url_destino:
            return self.url_destino
        return ''