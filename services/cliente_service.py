from typing import List
from data.cliente import Cliente
from datetime import datetime


def crear_cliente(organizacion_id: str, correo_vendedor: str, nombre: str, apellidos: str, direccion: str,
                  fechaNacimiento: str, telefono: str, email: str) -> Cliente:

    if fechaNacimiento:
        fecha_nacimiento = datetime.strptime(fechaNacimiento, '%Y-%m-%d')
    else:
        fecha_nacimiento = None

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


def editar_cliente(cliente_id: str, email: str, nombre: str, apellidos: str, fecha_nacimiento: str,
                   direccion: str, telefono: str) -> Cliente:

    if fecha_nacimiento:
        fecha = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
    else:
        fecha = None

    cliente = get_cliente_by_id(cliente_id=cliente_id)
    cliente.email = email
    cliente.nombre = nombre
    cliente.apellidos = apellidos
    cliente.fechaNacimiento = fecha
    cliente.direccion = direccion
    cliente.telefono = telefono

    cliente.save()

    return cliente


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


def get_cliente_by_id(cliente_id: str) -> Cliente:
    cliente = Cliente.objects().get(id=cliente_id)
    return cliente
