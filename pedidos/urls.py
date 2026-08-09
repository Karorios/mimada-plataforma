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
        "guardar-detalle-personalizado/",
        views.guardar_detalle_personalizado,
        name="guardar_detalle_personalizado"
    ),

    path(
        "crear-pedido-personalizado/",
        views.crear_pedido_personalizado,
        name="crear_pedido_personalizado"
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
        "nuevo-detalle/",
        views.nuevo_detalle,
        name="nuevo_detalle"
    ),

    path(
        "confirmar/",
        views.confirmar_pedido,
        name="confirmar_pedido"
    ),
path("editar/<int:pedido_id>/", views.editar_pedido, name="editar_pedido"),
    path("cancelar/<int:pedido_id>/", views.cancelar_pedido, name="cancelar_pedido"),

]