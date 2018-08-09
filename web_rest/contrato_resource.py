from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required, get_jwt_identity)

from mongoengine import Q

from data.contrato import Contrato, PagoProgramado, PagoReal
from data_auth.models import UserModel

from services import contrato_service
from services import producto_service

import datetime

contrato_parser = reqparse.RequestParser(bundle_errors=True)
contrato_parser.add_argument('tipo', required=True, help='tipo is required')
contrato_parser.add_argument('clienteId', required=True, help='clienteId is required')
contrato_parser.add_argument('productoId', required=True, help='productoId is required')
contrato_parser.add_argument('diasValidez', type=int, help='value cannot be converted to integer')
contrato_parser.add_argument('pagosProgramados', action='append', type=dict)
contrato_parser.add_argument('pagosReales', action='append', type=dict)

pago_programado_parser = reqparse.RequestParser(bundle_errors=True)
pago_programado_parser.add_argument('fechaCompromisoPago', required=True, help='fechaCompromisoPago is required')
pago_programado_parser.add_argument('monto', required=True, help='monto is required')

pago_real_parser = reqparse.RequestParser(bundle_errors=True)
pago_real_parser.add_argument('monto', required=True, help='monto is required')
pago_real_parser.add_argument('archivos', action='append')


class AddContrato(Resource):
    @jwt_required
    def post(self):
        vendedor_login = get_jwt_identity()

        current_venedor = UserModel.find_by_login(vendedor_login)

        if not current_venedor:
            return {'message': 'No user with login {}'.format(vendedor_login)}, 401

        data = contrato_parser.parse_args()

        if not contrato_service.verify_cliente_exists(data['clienteId']):
            return {'message': 'No cliente with id {} found'.format(data['clienteId'])}, 404

        if not contrato_service.verify_producto_exists(data['productoId']):
            return {'message': 'No producto with id {} found'.format(data['productoId'])}, 404

        contrato = Contrato()
        contrato.tipo = data['tipo']
        contrato.clienteId = data['clienteId']
        contrato.productoId = data['productoId']
        contrato.vendedorId = current_venedor.id
        contrato.diasValidez = -1 if not data['diasValidez'] else data['diasValidez']

        pagos_reales = []

        if data['pagosReales'] is not None:
            for current_pago_real in data['pagosReales']:
                pago_real = PagoReal()
                pago_real.monto = current_pago_real['monto']
                pago_real.validado = False
                pago_real.correoQueValida = None
                pagos_reales.append(pago_real)

            contrato.pagosReales = pagos_reales

        pagos_programados = []

        if data['pagosProgramados'] is not None:
            for current_pago_programado in data['pagosProgramados']:
                pago_programado = PagoProgramado()
                pago_programado.monto = current_pago_programado['monto']
                pago_programado.fechaCompromisoPago = datetime.datetime.strptime(
                    current_pago_programado['fechaCompromisoPago'],
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )
                pagos_programados.append(pago_programado)

            contrato.pagosProgramados = pagos_programados

        try:
            contrato.save()
            producto_service.update_producto_estatus(
                contrato.productoId,
                contrato_service.map_estatus_tipo_de_contrato(contrato.tipo))
        except Exception as ex:
            return {'message': ex.message}, 500

        return contrato.to_dict()


class AddPagoProgramado(Resource):
    @jwt_required
    def post(self, contrato_id):

        try:
            contrato = contrato_service.get_contrato_by_id(contrato_id)
        except Exception as ex:
            return {'message': ex.message}, 500

        data = pago_programado_parser.parse_args()

        pago_programado = PagoProgramado()
        pago_programado.fechaCompromisoPago = datetime.datetime.strptime(
            data['fechaCompromisoPago'],
            '%Y-%m-%dT%H:%M:%S.%fZ'
        )
        pago_programado.monto = data['monto']

        contrato.update(push__pagosProgramados=pago_programado)

        try:
            contrato.save()
        except Exception as ex:
            return {'message': ex.message}, 500

        return contrato.to_dict()


class AddPagoReal(Resource):
    @jwt_required
    def post(self, contrato_id):

        try:
            contrato = contrato_service.get_contrato_by_id(contrato_id)
        except Exception as ex:
            return {'message': ex.message}, 500

        data = pago_real_parser.parse_args()

        pago_real = PagoReal()
        pago_real.monto = data['monto']
        pago_real.archivos = data['archivos']
        pago_real.validado = False
        pago_real.correoQueValida = None

        contrato.update(push__pagosReales=pago_real)

        try:
            contrato.save()
        except Exception as ex:
            return {'message': ex.message}, 500

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
            contrato = contrato_service.get_last_contrato_for_producto_id(producto_id)
        except Exception as ex:
            return {'message': ex.message}, 500
        return contrato.to_dict()


class FindAllContratosForProductoId(Resource):
    @jwt_required
    def get(self, producto_id):
        contratos = contrato_service.find_all_contratos_for_producto_id(producto_id)
        return contratos


class FindContratosForClienteId(Resource):
    @jwt_required
    def get(self, cliente_id):
        contratos = contrato_service.find_all_for_cliente_id(cliente_id)
        return contratos
