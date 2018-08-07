import mongoengine
import datetime

import data.mongo_digiall_utils as mongo_utils


class PagoReal(mongoengine.EmbeddedDocument):
    fechaCreacion = mongoengine.DateTimeField(default=datetime.datetime.now())
    monto = mongoengine.FloatField()
    correoQueValida = mongoengine.StringField()
    validado = mongoengine.BooleanField()
    archivos = mongoengine.ListField(mongoengine.StringField())


class PagoProgramado(mongoengine.EmbeddedDocument):
    fechaCompromisoPago = mongoengine.DateTimeField()
    monto = mongoengine.FloatField()


class Contrato(mongoengine.Document):
    fechaCreacion = mongoengine.DateTimeField(default=datetime.datetime.now())

    tipo = mongoengine.StringField()

    clienteId = mongoengine.StringField()
    productoId = mongoengine.StringField()

    vendedorId = mongoengine.IntField()
    diasValidez = mongoengine.IntField()

    observaciones = mongoengine.StringField()

    pagosProgramados = mongoengine.ListField(mongoengine.EmbeddedDocumentField(PagoProgramado))
    pagosReales = mongoengine.ListField(mongoengine.EmbeddedDocumentField(PagoReal))

    def to_dict(self):
        return mongo_utils.mongo_to_dict(self)

    @mongoengine.queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('-fechaCreacion')

    meta = {
        'db_alias': 'core',
        'collection': 'contrato'
    }
