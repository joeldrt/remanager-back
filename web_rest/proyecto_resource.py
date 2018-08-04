from flask_restful import Resource, reqparse
from data.proyecto import Proyecto
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from services import proyecto_service as service
from data_auth.models import UserModel

from werkzeug.exceptions import BadRequest
import json

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('id')
parser.add_argument('nombre')
parser.add_argument('descripcion')
parser.add_argument('correoCreador')
parser.add_argument('idSeccion')
parser.add_argument('svgId')
parser.add_argument('organizacionId')
parser.add_argument('padreId')


class AddProyecto(Resource):
    @jwt_required
    def post(self):
        user_login = get_jwt_identity()

        current_user = UserModel.find_by_login(user_login)
        if not current_user:
            return {'message': 'User {} doesnt exists'.format(user_login)}, 401

        data = parser.parse_args()

        proyecto = Proyecto()
        proyecto.nombre = data['nombre']
        proyecto.descripcion = data['descripcion']
        proyecto.correoCreador = current_user.email
        proyecto.idSeccion = data['idSeccion']
        proyecto.svgId = data['svgId']
        proyecto.organizacionId = current_user.organizationId
        proyecto.padreId = data['padreId']

        try:
            proyecto.save()
        except Exception as ex:
            return {'message', ex.message}, 500

        return proyecto.to_dict()


class FindRootProyectos(Resource):
    def get(self):
        proyectos = service.find_root_proyectos()
        return proyectos


class DeleteProyecto(Resource):
    @jwt_required
    def delete(self, proyecto_id):
        try:
            proyecto = service.get_proyecto_by_id(proyecto_id)
            proyecto.delete()
        except Proyecto.DoesNotExist as e:
            return {'message', e.args[0]}, 404
        return {'message', 'Proyecto with id: {} successfully deleted'.format(proyecto_id)}


class EditProyecto(Resource):
    @jwt_required
    def put(self):
        try:
            data = parser.parse_args()
        except BadRequest as br:
            br_data = br.data
            br_message = br_data['message']
            return {'message': '{} - {}'.format(br.description, json.dumps(br_message))}, br.code

        proyecto = service.get_proyecto_by_id(data['id'])

        if proyecto is None:
            return {'message': 'Proyecto {} doesnt exist'.format(data['id'])}, 401

        proyecto.nombre = data['nombre']
        proyecto.descripcion = data['descripcion']
        proyecto.correo_creador = data['correo_creador']
        proyecto.id_seccion = data['id_seccion']
        proyecto.svg_id = data['svg_id']
        proyecto.organizacion_id = data['organizacion_id']
        proyecto.padre_id = data['padre_id']

        edited_proyecto = proyecto.save()

        if edited_proyecto:
            return edited_proyecto.to_dict()
        else:
            return {'message', 'Unable to edit Proyecto {}'.format(proyecto.id)}, 500


class FindAllProyectosByPadreId(Resource):
    @jwt_required
    def get(self, padre_id):
        proyectos = service.find_all_by_padre_id(padre_id)
        return proyectos
