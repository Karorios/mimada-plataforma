import uuid


def _obtener_carrito(request):
    return request.session.setdefault("carrito", [])


def agregar_producto(request, producto_id, cantidad=1):
    carrito = _obtener_carrito(request)

    for item in carrito:
        if item["tipo"] == "producto" and item["producto_id"] == producto_id:
            item["cantidad"] += cantidad
            request.session.modified = True
            return

    carrito.append({
        "id": uuid.uuid4().hex,
        "tipo": "producto",
        "producto_id": producto_id,
        "cantidad": cantidad,
    })
    request.session.modified = True


def agregar_personalizado(request, detalle_personalizado):
    carrito = _obtener_carrito(request)
    carrito.append({
        "id": uuid.uuid4().hex,
        "tipo": "personalizado",
        "detalle": detalle_personalizado,
    })
    request.session.modified = True


def eliminar_item(request, item_id):
    carrito = _obtener_carrito(request)
    request.session["carrito"] = [item for item in carrito if item["id"] != item_id]
    request.session.modified = True


def actualizar_cantidad(request, item_id, cantidad):
    carrito = _obtener_carrito(request)
    for item in carrito:
        if item["id"] == item_id and item["tipo"] == "producto":
            item["cantidad"] = max(1, cantidad)
    request.session.modified = True


def vaciar_carrito(request):
    request.session["carrito"] = []
    request.session.modified = True


def cantidad_total(request):
    carrito = _obtener_carrito(request)
    total = 0
    for item in carrito:
        if item["tipo"] == "producto":
            total += item["cantidad"]
        else:
            total += 1
    return total