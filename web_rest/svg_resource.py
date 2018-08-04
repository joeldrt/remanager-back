from flask_restful import Resource, reqparse, request
from data.svg import Svg, Poligono, Punto
from flask_jwt_extended import (jwt_required, get_jwt_identity)

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('id')
parser.add_argument('nombre')
parser.add_argument('imagenContentType')
parser.add_argument('imagen')
parser.add_argument('width', type=float)
parser.add_argument('height', type=float)
parser.add_argument('codigoContentType')
parser.add_argument('codigo')
parser.add_argument('proyectoId')
parser.add_argument('poligonos', type=dict, action='append')


class AddSvg(Resource):
    @jwt_required
    def post(self):
        data = request.data

        svg = Svg.from_json(data)

        try:
            svg.save()
        except Exception as ex:
            return {'message', ex.message}, 500

        return svg.to_dict()


class GetSvgById(Resource):
    @jwt_required
    def get(self, svg_id):
        svg = Svg.objects().get(id=svg_id)
        return svg.to_dict()
