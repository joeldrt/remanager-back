from flask_restful import Resource, reqparse
from data.cliente import Cliente, HistoricoEstatusProducto, PagoProgramado, PagoReal
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from services import cliente_service as service
from data_auth.models import UserModel

import datetime

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('nombre')
parser.add_argument('apellidos')
parser.add_argument('correoVendedor')
parser.add_argument('direccion')
parser.add_argument('fechaNacimiento')
parser.add_argument('organizacionId')
parser.add_argument('telefono')
parser.add_argument('email')


class AddCliente(Resource):
    @jwt_required
    def post(self):
        vendedor_login = get_jwt_identity()

        vendedor = UserModel.find_by_login(vendedor_login)
        if not vendedor:
            return {'message': 'Vendedor {} doesnt exists'.format(vendedor_login)}, 401

        data = parser.parse_args()

        cliente = Cliente()
        cliente.organizacionId = vendedor.organizationId
        cliente.correoVendedor = vendedor.email
        cliente.nombre = data['nombre']
        cliente.apellidos = data['apellidos']
        cliente.direccion = data['direccion']
        cliente.fechaNacimiento = datetime.datetime.strptime(data['fechaNacimiento'], '%Y-%m-%dT%H:%M:%S.%fZ')
        cliente.telefono = data['telefono']
        cliente.email = data['email']

        try:
            cliente.save()
        except Exception as ex:
            return {'message', ex.message}, 500

        return cliente.to_dict()


class FindAllClientesByCorreoVendedor(Resource):
    @jwt_required
    def get(self, correo_vendedor):
        clientes = service.find_clientes_by_correo_vendedor(correo_vendedor)
        return clientes


class GetClienteById(Resource):
    @jwt_required
    def get(self, cliente_id):
        cliente = service.get_cliente_by_id(cliente_id)
        return cliente
