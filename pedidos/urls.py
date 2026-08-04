from django.urls import path
from . import views

app_name = "pedidos"

urlpatterns = [
    path("", views.inicio, name="inicio"),

    path(
        "crear-detalle/",
        views.crear_detalle,
        name="crear_detalle"
    ),

    path(
        "crear-pedido/<int:producto_id>/",
        views.crear_pedido,
        name="crear_pedido"
    ),

    path(
        "resumen/",
        views.resumen,
        name="resumen"
    ),

    path(
        "confirmar/",
        views.confirmar_pedido,
        name="confirmar_pedido"
    ),
]