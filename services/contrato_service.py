from typing import List
from data.contrato import Contrato, PagoProgramado, PagoReal
from datetime import datetime

from services import cliente_service, producto_service


def crear_contrato(tipo: str, cliente_id: str, producto_id: str, correo_vendedor: str, dias_validez: int) -> Contrato:
    contrato = Contrato()
    contrato.tipo = tipo
    contrato.clienteId = cliente_id
    contrato.productoId = producto_id
    contrato.correoVendedor = correo_vendedor
    contrato.diasValidez = -1 if not dias_validez else dias_validez

    contrato.save()

    producto = producto_service.get_producto_by_id(producto_id=producto_id)

    if not producto:
        contrato.delete()
        raise Exception('No se encontró el producto - se destruye el contrato')

    producto.estatus = map_estatus_tipo_de_contrato(contrato.tipo)

    producto.save()

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
    pago_real.validado = False
    pago_real.correoQueValida = None

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
    contrato = Contrato.objects(producto_id=producto_id)[0]
    return contrato


def find_all_contratos_for_producto_id(producto_id: str) -> List[Contrato]:
    contratos = Contrato.objects(productoId=producto_id)
    return contratos


def get_contrato_by_id(contrato_id: str) -> Contrato:
    contrato = Contrato.objects().get(id=contrato_id)
    return contrato


def find_all_for_cliente_id(cliente_id: str) -> List[Contrato]:
    contratos = Contrato.objects(clienteId=cliente_id)
    return contratos
