from flask_restful import Resource, reqparse
from data.proyecto import Proyecto
from flask_jwt_extended import (jwt_required)
from services import proyecto_service as service

from werkzeug.exceptions import BadRequest
import json

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('id')
parser.add_argument('nombre')
parser.add_argument('descripcion')
parser.add_argument('correo_creador')
parser.add_argument('id_seccion')
parser.add_argument('svg_id')
parser.add_argument('organizacion_id')
parser.add_argument('padre_id')


class AddProyecto(Resource):
    @jwt_required
    def post(self):
        try:
            data = parser.parse_args()
        except BadRequest as br:
            br_data = br.data
            br_message = br_data['message']
            return {'message': '{} - {}'.format(br.description, json.dumps(br_message))}, br.code

        new_proyecto = service.persist_proyecto(proyecto_id=None,
                                                nombre=data['nombre'],
                                                descripcion=data['descripcion'],
                                                correo_creador=data['correo_creador'],
                                                id_seccion=data['id_seccion'],
                                                svg_id=data['svg_id'],
                                                organizacion_id=data['organizacion_id'],
                                                padre_id=data['padre_id'])

        if new_proyecto:
            return new_proyecto.to_dict()
        else:
            return {'message': 'Error storing entity Proyecto'}, 500


class FindRootProyectos(Resource):
    def get(self):
        proyectos = service.get_all_proyectos()
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


class FindAllByPadreId(Resource):
    @jwt_required
    def get(self, padre_id):
        proyectos = service.get_all_by_padre_id(padre_id)
        return proyectos
