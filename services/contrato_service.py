from typing import List
from datetime import datetime, timedelta

from mongoengine import Q

from data.contrato import Contrato, PagoProgramado, PagoReal
from services import cliente_service, producto_service


def crear_contrato(tipo: str, cliente_id: str, producto_id: str, correo_vendedor: str, dias_validez: int,
                   pagos_programados: List[PagoProgramado]) -> Contrato:
    contrato = Contrato()
    contrato.tipo = tipo
    contrato.clienteId = cliente_id
    contrato.productoId = producto_id
    contrato.correoVendedor = correo_vendedor
    contrato.pagosProgramados = pagos_programados
    contrato.diasValidez = -1 if not dias_validez else dias_validez

    if pagos_programados and len(pagos_programados) > 0:
        formatear_pagos_programados(pagos_programados=pagos_programados)

    contrato.save()

    producto = producto_service.get_producto_by_id(producto_id=producto_id)

    if not producto:
        contrato.delete()
        raise Exception('No se encontró el producto - se destruye el contrato')

    if not contrato.tipo == 'CORRIDA':
        producto.estatus = map_estatus_tipo_de_contrato(contrato.tipo)
        producto.save()

    return contrato


def formatear_pagos_programados(pagos_programados: List[PagoProgramado]):
    for pago_programado in pagos_programados:
        pago_programado.fechaCompromisoPago = datetime.strptime(pago_programado.fechaCompromisoPago,
                                                                '%Y-%m-%dT%H:%M:%S.%fZ')


def desactivar_contrato(correo_vendedor: str, contrato_id: str) -> Contrato:
    contrato = get_contrato_by_id(contrato_id=contrato_id)
    contrato_dict = contrato.to_dict()
    if not contrato_dict['correoVendedor'] == correo_vendedor:
        raise Exception('El contrato no fue creado por el vendedor')

    if int(contrato_dict['diasValidez']) > 0:
        fecha_creacion = datetime.strptime(contrato_dict['fechaCreacion'],'%Y-%m-%dT%H:%M:%S.%f')
        fecha_vencimiento = fecha_creacion + timedelta(days=int(contrato_dict['diasValidez']))
        if fecha_vencimiento > datetime.now(): # significa que sigue vigente el contrato
            producto = producto_service.get_producto_by_id(contrato.productoId)
            producto.estatus = 'DISPONIBLE'
            producto.save()

    contrato.activo = False
    contrato.save()
    return contrato


def generar_objeto_pago_programado(fecha_compromiso_pago: datetime, monto: float) -> PagoProgramado:
    pago_programado = PagoProgramado()
    pago_programado.fechaCompromisoPago = fecha_compromiso_pago
    pago_programado.monto = monto

    return pago_programado


def agregar_pago_programado(contrato_id: str, pago_programado: PagoProgramado) -> Contrato:
    contrato = get_contrato_by_id(contrato_id)

    if not contrato:
        raise Exception('El contrato no se encontró')

    contrato.update(push__pagosProgramados=pago_programado)
    contrato.save()

    return contrato


def generar_objeto_pago_real(monto: float, archivos: [str]) -> PagoReal:
    pago_real = PagoReal()
    pago_real.monto = monto
    pago_real.archivos = archivos

    return pago_real


def agregar_pago_real(contrato_id: str, pago_real: PagoReal) -> Contrato:
    contrato = get_contrato_by_id(contrato_id)

    if not contrato:
        raise Exception('El contrato no se encontró')

    contrato.update(push__pagosReales=pago_real)
    contrato.save()

    return contrato


def map_estatus_tipo_de_contrato(tipo_de_contrato: str) -> str:
    switcher = {
        'DEVOLUCION': 'DISPONIBLE',
        'BLOQUEO': 'BLOQUEADO',
        'APARTADO': 'APARTADO',
        'VENTA': 'VENDIDO'
    }
    return switcher.get(tipo_de_contrato)


def verify_cliente_exists(cliente_id: str) -> bool:
    if not cliente_id:
        return False
    try:
        cliente = cliente_service.obtener_cliente_por_id(cliente_id)
    except Exception:
        return False

    if not cliente:
        return False

    return True


def verify_producto_exists(producto_id: str) -> bool:
    if not producto_id:
        return False
    try:
        producto = producto_service.get_producto_by_id(producto_id)
    except Exception:
        return False

    if not producto:
        return False

    return True


def find_all_contratos() -> List[Contrato]:
    contratos = Contrato.objects()
    return contratos


def get_last_contrato_for_producto_id(producto_id: str) -> Contrato:
    contrato = Contrato.objects(Q(activo=True) &
                                Q(producto_id=producto_id))[0]
    return contrato


def find_all_contratos_for_producto_id(producto_id: str) -> List[Contrato]:
    contratos = Contrato.objects(productoId=producto_id)
    return contratos


def get_contrato_by_id(contrato_id: str) -> Contrato:
    contrato = Contrato.objects(Q(activo=True) &
                                Q(id=contrato_id))[0]
    return contrato


def find_all_for_cliente_id(cliente_id: str) -> List[Contrato]:
    contratos = Contrato.objects(Q(activo=True) &
                                 Q(clienteId=cliente_id))
    return contratos

