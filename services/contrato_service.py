from typing import List
from data.contrato import Contrato, PagoProgramado, PagoReal

from services import cliente_service, producto_service
from data_auth.models import UserModel


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
        cliente = cliente_service.get_cliente_by_id(cliente_id)
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
    contratos = [
        contrato.to_dict() for contrato in Contrato.objects()
    ]
    return contratos


def get_last_contrato_for_producto_id(producto_id: str) -> Contrato:
    contrato = Contrato.objects(producto_id=producto_id)[0]
    return contrato


def find_all_contratos_for_producto_id(producto_id: str) -> List[Contrato]:
    contratos = [
        contrato.to_dict() for contrato in Contrato.objects(productoId=producto_id)
    ]
    return contratos


def get_contrato_by_id(contrato_id: str) -> Contrato:
    contrato = Contrato.objects().get(id=contrato_id)
    return contrato
