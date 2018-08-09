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

jwt = JWTManager(app)

from web_rest import user_auth_resource, proyecto_resource, cliente_resource,\
    svg_resource, producto_resource, contrato_resource
from web_static import static_file_server
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
api.add_resource(proyecto_resource.FindAllProyectosByPadreId, '/api/_search_by_padreid/proyectos/<string:padre_id>')

api.add_resource(cliente_resource.AddCliente, '/api/clientes')
api.add_resource(cliente_resource.FindAllClientesByCorreoVendedor, '/api/_search_by_cv/clientes/<string:correo_vendedor>')
api.add_resource(cliente_resource.GetClienteById, '/api/clientes/<string:cliente_id>')

api.add_resource(svg_resource.AddSvg, '/api/svgs')
api.add_resource(svg_resource.GetSvgById, '/api/svgs/<string:svg_id>')

api.add_resource(producto_resource.FindAllProductosByProyectoId, '/api/_search_by_proyectoid/productos/<string:proyecto_id>')
api.add_resource(producto_resource.GetProductoById, '/api/productos/<string:producto_id>')
api.add_resource(producto_resource.FindAllProductos, '/api/productos/')

api.add_resource(contrato_resource.AddContrato, '/api/contratos')
api.add_resource(contrato_resource.FindAllContratos, '/api/contratos/all/')
api.add_resource(contrato_resource.GetLastContratoForProductoId, '/api/contratos/_by_producto_id/recent/<string:producto_id>')
api.add_resource(contrato_resource.FindAllContratosForProductoId, '/api/contratos/_by_producto_id/all/<string:producto_id>')
api.add_resource(contrato_resource.AddPagoReal, '/api/contratos/_add_pago_real/<string:contrato_id>')
api.add_resource(contrato_resource.AddPagoProgramado, '/api/contratos/_add_pago_programado/<string:contrato_id>')
api.add_resource(contrato_resource.FindContratosForClienteId, '/api/contratos/_by_cliente_id/<string:cliente_id>')

api.add_resource(static_file_server.UploadFiles, '/api/file/upload')


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
