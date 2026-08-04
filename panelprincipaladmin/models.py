from django.db import models

imagen = models.ImageField(
    upload_to='catalogo/productos/',
    blank=True,
    null=True
)
