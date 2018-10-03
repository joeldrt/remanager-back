from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from services import cliente_service
from data_auth.models import UserModel
from datetime import datetime


agregar_cliente_parser = reqparse.RequestParser(bundle_errors=True)
agregar_cliente_parser.add_argument('email', required=True)
agregar_cliente_parser.add_argument('nombre', required=True)
agregar_cliente_parser.add_argument('apellidos')
agregar_cliente_parser.add_argument('direccion')
agregar_cliente_parser.add_argument('fechaNacimiento', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'))
agregar_cliente_parser.add_argument('telefono', required=True)


class AgregarCliente(Resource):
    @jwt_required
    def post(self):
        vendedor_login = get_jwt_identity()

        vendedor = UserModel.find_by_login(vendedor_login)
        if not vendedor:
            return {'message': 'Vendedor {} doesnt exists'.format(vendedor_login)}, 401

        data = agregar_cliente_parser.parse_args()

        organizacionId = vendedor.organizationId
        correoVendedor = vendedor.email
        nombre = data['nombre']
        apellidos = data['apellidos']
        direccion = data['direccion']
        fechaNacimiento = data['fechaNacimiento']
        telefono = data['telefono']
        email = data['email']

        try:
            cliente = cliente_service.crear_cliente(organizacion_id=organizacionId,
                                                    correo_vendedor=correoVendedor,
                                                    nombre=nombre,
                                                    apellidos=apellidos,
                                                    direccion=direccion,
                                                    fecha_nacimiento=fechaNacimiento,
                                                    telefono=telefono,
                                                    email=email)
        except Exception as ex:
            return {'message', 'Error del servidor al guardar el cliente'}, 500

        return cliente.to_dict()


class ObtenerClientePorId(Resource):
    @jwt_required
    def get(self, cliente_id):
        vendedor_login = get_jwt_identity()

        vendedor = UserModel.find_by_login(vendedor_login)
        if not vendedor:
            return {'message': 'Vendedor {} doesnt exists'.format(vendedor_login)}, 401

        if not cliente_service.cliente_le_pertenece_a_vendedor(vendedor_email=vendedor.email, cliente_id=cliente_id):
            return {'message': 'El cliente no le pertenece al vendedor'}, 403

        cliente = cliente_service.obtener_cliente_por_id(cliente_id)

        return cliente.to_dict()


editar_cliente_parser = reqparse.RequestParser(bundle_errors=True)
editar_cliente_parser.add_argument('id', required=True)
editar_cliente_parser.add_argument('email', required=True)
editar_cliente_parser.add_argument('nombre', required=True)
editar_cliente_parser.add_argument('apellidos')
editar_cliente_parser.add_argument('direccion')
editar_cliente_parser.add_argument('fechaNacimiento', type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'))
editar_cliente_parser.add_argument('telefono', required=True)


class EditarCliente(Resource):
    @jwt_required
    def put(self, cliente_id):
        vendedor_login = get_jwt_identity()

        vendedor = UserModel.find_by_login(vendedor_login)
        if not vendedor:
            return {'message': 'Vendedor {} doesnt exists'.format(vendedor_login)}, 401

        if not cliente_service.cliente_le_pertenece_a_vendedor(vendedor_email=vendedor.email, cliente_id=cliente_id):
            return {'message': 'El cliente no le pertenece al vendedor'}, 403

        data = editar_cliente_parser.parse_args()

        if data['id'] != cliente_id:
            return {'message': 'Tratando de editar un cliente con diferente id'}, 400


        email = data['email']
        nombre = data['nombre']
        apellidos = data['apellidos']
        direccion = data['direccion']
        fecha_nacimiento = data['fechaNacimiento']
        telefono = data['telefono']

        try:
            cliente = cliente_service.editar_cliente(cliente_id=cliente_id,
                                                     email=email,
                                                     nombre=nombre,
                                                     apellidos=apellidos,
                                                     fecha_nacimiento=fecha_nacimiento,
                                                     direccion=direccion,
                                                     telefono=telefono)
        except Exception as exception:
            return {'message': 'Error del servidor al editar el cliente'}, 500

        return cliente.to_dict()


class BorrarCliente(Resource):
    @jwt_required
    def delete(self, cliente_id):
        vendedor_login = get_jwt_identity()

        vendedor = UserModel.find_by_login(vendedor_login)
        if not vendedor:
            return {'message': 'Vendedor {} doesnt exists'.format(vendedor_login)}, 401

        if not cliente_service.cliente_le_pertenece_a_vendedor(vendedor_email=vendedor.email, cliente_id=cliente_id):
            return {'message': 'El cliente no le pertenece al vendedor'}, 403

        if not cliente_service.borrar_cliente_por_id(cliente_id=cliente_id):
            return {'message': 'Error del servidor al borrar el cliente'}, 500

        return {'message': 'El cliente fue borrado exitosamente'}, 200


class ObtenerClientesPorVendedor(Resource):
    @jwt_required
    def get(self):
        vendedor_login = get_jwt_identity()

        vendedor = UserModel.find_by_login(vendedor_login)
        if not vendedor:
            return {'message': 'Vendedor {} doesnt exists'.format(vendedor_login)}, 401

        try:
            clientes_objs = cliente_service.obtener_clientes_por_correo_vendedor(vendedor.email)

            clientes = [
                cliente.to_dict() for cliente in clientes_objs
            ]
        except Exception as exception:
            return {'message': 'error del servidor al obtener los clientes por vendedor'}

        return clientes


class ObtenerResumenContratosPorCliente(Resource):
    @jwt_required
    def get(self, cliente_id):
        vendedor_login = get_jwt_identity()

        vendedor = UserModel.find_by_login(vendedor_login)
        if not vendedor:
            return {'message': 'Vendedor {} doesnt exists'.format(vendedor_login)}, 401

        if not cliente_service.cliente_le_pertenece_a_vendedor(vendedor_email=vendedor.email, cliente_id=cliente_id):
            return {'message': 'El cliente no le pertenece al vendedor'}, 403

        try:
            resumen_contratos = cliente_service.resumen_contratos_por_cliente(cliente_id=cliente_id)
        except Exception as exception:
            return {'message': 'Error del servidor al recuperar los contratos por cliente'}, 500

        return resumen_contratos