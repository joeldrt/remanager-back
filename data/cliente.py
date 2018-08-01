import mongoengine
import datetime

import data.mongo_digiall_utils as mongo_utils


class Cliente(mongoengine.Document):
    fecha_creacion = mongoengine.DateTimeField(default=datetime.datetime.now())

