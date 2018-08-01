from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

import data.mongo_setup as mongo_setup
import logging
import datetime

app = Flask(__name__, static_url_path='/static')
handler = logging.FileHandler('remanager.log')
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

CORS(app)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Th15157h33nD'

db = SQLAlchemy(app)

app.config['JWT_SECRET_KEY'] = 'Th15157h33nD'
app.config['JWT_BLACKLIST_ENABLES'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
app.config['JWT_EXPIRES'] = datetime.timedelta(days=30)

jwt = JWTManager(app)

from web_rest import user_auth_resource, proyecto_resource, cliente_resource
from data_auth import models
from data.organizacion import Organizacion


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    authorities = [authority.authority_name for authority in user.authorities]
    return {'authorities': authorities}


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.login


api.add_resource(user_auth_resource.UserLogin, '/api/authenticate')
api.add_resource(user_auth_resource.Account, '/api/account')
api.add_resource(user_auth_resource.Organization, '/api/account_organizacion')

api.add_resource(proyecto_resource.FindRootProyectos, '/api/_search_root/proyectos')
api.add_resource(proyecto_resource.FindAllByPadreId, '/api/_search_by_padreid/proyectos/<string:padre_id>')

api.add_resource(cliente_resource.AddCliente, '/api/clientes')
api.add_resource(cliente_resource.FindAllByCorreoVendedor, '/api/_search_by_cv/clientes/<string:correo_vendedor>')
api.add_resource(cliente_resource.GetClienteById, '/api/clientes/<string:cliente_id>')


def init_database_values():
    authority1 = models.AuthorityModel(authority_name='ROLE_ADMIN')
    authority2 = models.AuthorityModel(authority_name='ROLE_USER')

    db.session.add(authority1)
    db.session.add(authority2)
    db.session.commit()

    admin = models.UserModel(
        login='admin',
        password=models.UserModel.generate_hash('admin'),
        firstName='Administrator',
        lastName='Administrator',
        email='admin@localhost'
    )

    admin.authorities.append(authority1)
    admin.authorities.append(authority2)

    admin.save_to_db()

    organizacion = Organizacion()
    organizacion.nombre = 'Organización Principal'
    organizacion.descripcion = 'Organización Principal'
    organizacion.correo_creador = 'admin@localhost'

    organizacion.save()

    admin.organizationId = str(organizacion.id)

    admin.save_to_db()


@app.before_first_request
def create_tables():
    db.create_all()
    mongo_setup.global_init()

    if not models.UserModel.find_by_login('admin'):
        init_database_values()
