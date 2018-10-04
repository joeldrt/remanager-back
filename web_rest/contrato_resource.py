from flask_restful import Resource, reqparse, request
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from data_auth.models import UserModel

from services import contrato_service

from data.contrato import Contrato, PagoProgramado

from datetime import datetime

contrato_parser = reqparse.RequestParser(bundle_errors=True)
contrato_parser.add_argument('tipo', required=True, help='tipo is required')
contrato_parser.add_argument('clienteId', required=True, help='clienteId is required')
contrato_parser.add_argument('productoId', required=True, help='productoId is required')
contrato_parser.add_argument('diasValidez', type=int, help='value cannot be converted to integer')


class CrearContrato(Resource):
    @jwt_required
    def post(self):
        vendedor_login = get_jwt_identity()

        current_vendedor = UserModel.find_by_login(vendedor_login)

        if not current_vendedor:
            return {'message': 'No user with login {}'.format(vendedor_login)}, 401

        data = request.data.decode('utf-8')

        try:
            contrato = Contrato.from_json(data)
        except Exception as exception:
            return {'message', 'El objeto enviado no cumple con el formato correcto'}, 400

        if not contrato_service.verify_cliente_exists(contrato.clienteId):
            return {'message': 'No cliente with id {} found'.format(contrato.clienteId)}, 404

        if not contrato_service.verify_producto_exists(contrato.productoId):
            return {'message': 'No producto with id {} found'.format(contrato.productoId)}, 404

        try:
            contrato = contrato_service.crear_contrato(tipo=contrato.tipo,
                                                       cliente_id=contrato.clienteId,
                                                       producto_id=contrato.productoId,
                                                       correo_vendedor=current_vendedor.email,
                                                       dias_validez=contrato.diasValidez,
                                                       pagos_programados=contrato.pagosProgramados)
        except Exception as ex:
            return {'message': str(ex)}, 500

        return contrato.to_dict()


pago_programado_parser = reqparse.RequestParser(bundle_errors=True)
pago_programado_parser.add_argument('fechaCompromisoPago',
                                    required=True,
                                    type=lambda x: datetime.strptime(x, '%Y-%m-%dT%H:%M:%S'),
                                    help='Fecha Compromiso Pago is required')
pago_programado_parser.add_argument('monto', required=True, type=float, help='monto is required')


class AgregarPagoProgramado(Resource):
    @jwt_required
    def post(self, contrato_id):

        data = pago_programado_parser.parse_args()

        fecha_compromiso_pago = data['fecha_compromiso_pago']
        monto = data['monto']

        try:
            pago_programado = contrato_service.generar_objeto_pago_programado(fecha_compromiso_pago=fecha_compromiso_pago,
                                                                              monto=monto)
            contrato = contrato_service.agregar_pago_programado(contrato_id=contrato_id,
                                                                pago_programado=pago_programado)
        except Exception as ex:
            return {'message': str(ex)}, 500

        return contrato.to_dict()


pago_real_parser = reqparse.RequestParser(bundle_errors=True)
pago_real_parser.add_argument('monto', required=True, type=float, help='monto is required')
pago_real_parser.add_argument('archivos', action='append')


class AgregarPagoReal(Resource):
    @jwt_required
    def post(self, contrato_id):

        data = pago_real_parser.parse_args()

        monto = data['monto']
        archivos = data['archivos']

        try:
            pago_real = contrato_service.generar_objeto_pago_real(monto=monto,
                                                                  archivos=archivos)
            contrato = contrato_service.agregar_pago_real(contrato_id=contrato_id,
                                                          pago_real=pago_real)
        except Exception as ex:
            return {'message': str(ex)}, 500

        return contrato.to_dict()


class FindAllContratos(Resource):
    @jwt_required
    def get(self):
        requester_login = get_jwt_identity()

        current_requester = UserModel.find_by_login(requester_login)

        if 'ROLE_ADMIN' not in [authority.authority_name for authority in current_requester.authorities]:
            return {'message': 'You dont have access to this resource'}, 403

        contratos = contrato_service.find_all_contratos()
        return contratos


class GetLastContratoForProductoId(Resource):
    @jwt_required
    def get(self, producto_id):
        try:
            contrato = contrato_service.get_last_contrato_for_producto_id(producto_id=producto_id)
        except Exception as ex:
            return {'message': str(ex)}, 500
        return contrato.to_dict()


class FindAllContratosForProductoId(Resource):
    @jwt_required
    def get(self, producto_id):
        contratos = contrato_service.find_all_contratos_for_producto_id(producto_id=producto_id)
        return contratos


class FindContratosForClienteId(Resource):
    @jwt_required
    def get(self, cliente_id):
        contratos = contrato_service.find_all_for_cliente_id(cliente_id=cliente_id)
        return contratos


class GetContratoByContratoId(Resource):
    @jwt_required
    def get(self, contrato_id):
        try:
            contrato = contrato_service.get_contrato_by_id(contrato_id=contrato_id)
        except Exception as ex:
            return {'message': str(ex)}, 500
        return contrato.to_dict()
