import mongoengine
import datetime

import data.mongo_digiall_utils as mongo_utils


class Proyecto(mongoengine.Document):
    fecha_creacion = mongoengine.DateTimeField(default=datetime.datetime.now())

    nombre = mongoengine.StringField(required=True)
    descripcion = mongoengine.StringField()
    correoCreador = mongoengine.StringField()
    idSeccion = mongoengine.StringField()
    svgId = mongoengine.StringField()
    organizacionId = mongoengine.StringField()
    padreId = mongoengine.StringField()

    def to_dict(self):
        return mongo_utils.mongo_to_dict(self)

    meta = {
        'db_alias': 'core',
        'collection': 'proyecto'
    }
