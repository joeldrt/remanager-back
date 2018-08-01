from typing import List

from data.cliente import Cliente, HistoricoEstatusProducto, PagoProgramado, PagoReal


def find_all_clientes() -> List[Cliente]:
    clientes = [
        cliente.to_dict() for cliente in Cliente.objects().all()
    ]
    return clientes


def find_clientes_by_correo_vendedor(correoVendedor: str) -> List[Cliente]:
    clientes = [
        cliente.to_dict() for cliente in Cliente.objects(correoVendedor=correoVendedor)
    ]
    return clientes


def find_clientes_by_organizacion_id(organizacionId: str) -> List[Cliente]:
    clientes = [
        cliente.to_dict() for cliente in Cliente.objects(organizacionId=organizacionId)
    ]
    return clientes


def get_cliente_by_id(cliente_id: str):
    cliente = Cliente.objects().get(id=cliente_id)
    return cliente.to_dict()
