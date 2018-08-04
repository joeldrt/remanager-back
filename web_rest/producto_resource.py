from flask_restful import Resource, reqparse
from data.producto import Producto, ValorCampo
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from data_auth.models import UserModel

import datetime


class FindAllProductosByProyectoId(Resource):
    @jwt_required
    def get(self, proyecto_id):
        productos = [
            producto.to_dict() for producto in Producto.objects(proyectoId=proyecto_id)
        ]
        return productos


class GetProductoById(Resource):
    @jwt_required
    def get(self, producto_id):
        producto = Producto.objects().get(id=producto_id)
        return producto.to_dict()


class FindAllProductos(Resource):
    @jwt_required
    def get(self):
        productos = [
            producto.to_dict() for producto in Producto.objects()
        ]
        return productos