from data.producto import Producto, ValorCampo


def update_producto_estatus(producto_id: str, estatus: str):
    producto = Producto.objects.get(id=producto_id)
    producto.estatus = estatus
    producto.save()


def get_producto_by_id(producto_id: str):
    producto = Producto.objects().get(id=producto_id)
    return producto

