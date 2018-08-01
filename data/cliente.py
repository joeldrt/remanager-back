import mongoengine
import datetime

import data.mongo_digiall_utils as mongo_utils


class HistoricoEstatusProducto(mongoengine.Document):
    productoId = mongoengine.StringField()
    fechaInicio = mongoengine.DateTimeField()
    tipoEstatus = mongoengine.StringField(required=True)
    estatus = mongoengine.DateTimeField()
    tiempoDeVidaDias = mongoengine.IntField()


class PagoProgramado(mongoengine.Document):
    clienteId = mongoengine.StringField()
    productoId = mongoengine.StringField()
    fechaCreacion = mongoengine.DateTimeField(default=datetime.datetime.now())
    fechaPago = mongoengine.DateTimeField()
    monto = mongoengine.FloatField()


class PagoReal(mongoengine.Document):
    clienteId = mongoengine.StringField()
    productoId = mongoengine.StringField()
    estatusPago = mongoengine.StringField()
    fechaRecepcion = mongoengine.DateTimeField()
    fechaConfirmacion = mongoengine.DateTimeField()
    monto = mongoengine.FloatField()
    notas = mongoengine.StringField()
    comprobantesUrls = mongoengine.ListField(mongoengine.StringField(), default=[])


class Cliente(mongoengine.Document):
    fechaAlta = mongoengine.DateTimeField(default=datetime.datetime.now())

    nombre = mongoengine.StringField(required=True)
    apellidos = mongoengine.StringField()
    correoVendedor = mongoengine.StringField()
    direccion = mongoengine.StringField()
    fechaNacimiento = mongoengine.DateTimeField()
    organizacionId = mongoengine.StringField()
    telefono = mongoengine.StringField()
    email = mongoengine.StringField()
    historicoProductos = mongoengine.ListField(mongoengine.EmbeddedDocumentField(HistoricoEstatusProducto))
    pagosProgramados = mongoengine.ListField(mongoengine.EmbeddedDocumentField(PagoProgramado))
    pagosReales = mongoengine.ListField(mongoengine.EmbeddedDocumentField(PagoReal))

    def to_dict(self):
        return mongo_utils.mongo_to_dict(self)

    meta = {
        'db_alias': 'core',
        'collection': 'cliente'
    }