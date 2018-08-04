from flask import send_from_directory
from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required)

from app import app


@app.route('/archivo/<string:request_folder>/<string:file_name>')
def dispatch_file(request_folder, file_name):
    return send_from_directory('static/{}'.format(request_folder), file_name)
