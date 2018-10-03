from typing import List
from datetime import datetime
from mongoengine import Q

from data.cliente import Cliente

from data.contrato import Contrato
from services import contrato_service, producto_service


def crear_cliente(organizacion_id: str, correo_vendedor: str, nombre: str, apellidos: str, direccion: str,
                  fecha_nacimiento: datetime, telefono: str, email: str) -> Cliente:

    cliente = Cliente()
    cliente.organizacionId = organizacion_id
    cliente.correoVendedor = correo_vendedor
    cliente.nombre = nombre
    cliente.apellidos = apellidos
    cliente.direccion = direccion
    cliente.fechaNacimiento = fecha_nacimiento
    cliente.telefono = telefono
    cliente.email = email

    cliente.save()

    return cliente


def editar_cliente(cliente_id: str, email: str, nombre: str, apellidos: str, fecha_nacimiento: datetime,
                   direccion: str, telefono: str) -> Cliente:

    cliente = obtener_cliente_por_id(cliente_id=cliente_id)
    cliente.email = email
    cliente.nombre = nombre
    cliente.apellidos = apellidos
    cliente.fechaNacimiento = fecha_nacimiento
    cliente.direccion = direccion
    cliente.telefono = telefono

    cliente.save()

    return cliente


def obtener_todos_los_clientes() -> List[Cliente]:
    clientes = [
        cliente.to_dict() for cliente in Cliente.objects().all()
    ]
    return clientes


def obtener_clientes_por_correo_vendedor(correo_vendedor: str) -> List[Cliente]:
    clientes = Cliente.objects(correoVendedor=correo_vendedor)
    return clientes


def obtener_clientes_por_organizacion_id(organizacion_id: str) -> List[Cliente]:
    clientes = [
        cliente.to_dict() for cliente in Cliente.objects(organizacionId=organizacion_id)
    ]
    return clientes


def obtener_cliente_por_id(cliente_id: str) -> Cliente:
    cliente = Cliente.objects().get(id=cliente_id)
    return cliente


def borrar_cliente_por_id(cliente_id: str) -> bool:
    cliente = Cliente.objects().get(id=cliente_id)
    cliente.delete()
    return True


def cliente_le_pertenece_a_vendedor(vendedor_email: str, cliente_id: str) -> bool:
    cliente = Cliente.objects(
        Q(correoVendedor=vendedor_email) &
        Q(id=cliente_id)
    )
    if cliente:
        return True
    return False


def obtener_contratos_por_cliente(cliente_id: str) -> List[Contrato]:
    contratos = contrato_service.find_all_for_cliente_id(cliente_id=cliente_id)
    return contratos


def resumen_contratos_por_cliente(cliente_id: str) -> dict:

    cliente = obtener_cliente_por_id(cliente_id=cliente_id)
    contratos = contrato_service.find_all_for_cliente_id(cliente_id=cliente_id)

    resultado_dict = dict()
    resultado_dict['cliente'] = cliente.to_dict()
    resumen_contratos = []
    for contrato in contratos:
        resumen_contrato = dict()
        producto = producto_service.get_producto_by_id(producto_id=contrato.productoId)
        resumen_contrato['producto'] = producto.to_dict()
        resumen_contrato['contrato'] = contrato.to_dict()

        resumen_contratos.append(resumen_contrato)

    resultado_dict['resumen_contratos'] = resumen_contratos

    return resultado_dict

