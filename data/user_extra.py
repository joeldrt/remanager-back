import mongoengine
import datetime

import data.mongo_digiall_utils as mongo_utils


class UserExtra(mongoengine.Document):
    fechaAlta = mongoengine.DateTimeField(default=datetime.datetime.now())

    login = mongoengine.StringField(unique=True)

    profilePictureUrl = mongoengine.StringField()

    picturesUrls = mongoengine.ListField(mongoengine.StringField(), default=[])

    def to_dict(self):
        return mongo_utils.mongo_to_dict(self)

    meta = {
        'db_alias': 'core',
        'collection': 'user_extra'
    }
