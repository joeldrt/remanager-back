import mongoengine
from datetime import datetime

import data.mongo_digiall_utils as mongo_utils


class PagoReal(mongoengine.EmbeddedDocument):
    fechaCreacion = mongoengine.DateTimeField(default=datetime.now)
    monto = mongoengine.FloatField()
    archivos = mongoengine.ListField(mongoengine.StringField())
    validado = mongoengine.BooleanField(default=False)
    correoQueValida = mongoengine.StringField()


class PagoProgramado(mongoengine.EmbeddedDocument):
    fechaCompromisoPago = mongoengine.DateTimeField()
    monto = mongoengine.FloatField()


class Contrato(mongoengine.Document):
    fechaCreacion = mongoengine.DateTimeField(default=datetime.now)

    activo = mongoengine.BooleanField(default=True)

    tipo = mongoengine.StringField()

    clienteId = mongoengine.StringField()
    productoId = mongoengine.StringField()

    correoVendedor = mongoengine.StringField()
    diasValidez = mongoengine.IntField()

    observaciones = mongoengine.StringField()

    pagosProgramados = mongoengine.ListField(mongoengine.EmbeddedDocumentField(PagoProgramado))
    pagosReales = mongoengine.ListField(mongoengine.EmbeddedDocumentField(PagoReal))

    def to_dict(self):
        return mongo_utils.mongo_to_dict_1(self)

    @mongoengine.queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('-fechaCreacion')

    meta = {
        'db_alias': 'core',
        'collection': 'contrato'
    }
