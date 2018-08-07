from flask import send_from_directory
from flask_restful import Resource, reqparse
from flask_jwt_extended import (jwt_required)

from app import app

import base64
import os

upload_parser = reqparse.RequestParser()
upload_parser.add_argument('folder', help='folder must be provided', required=True, type=str)
upload_parser.add_argument('files', action='append', type=dict, required=True)


@app.route('/archivo/<string:request_folder>/<string:file_name>')
def dispatch_file(request_folder, file_name):
    return send_from_directory('static/{}'.format(request_folder), file_name)


class UploadFiles(Resource):
    @jwt_required
    def post(self):
        data = upload_parser.parse_args()

        folder = data['folder'].replace(" ", "_")
        files = list(data['files'])

        if len(files) <= 0:
            return {'message', 'No files in request'}, 400

        added_files = [];

        for current_file in files:
            os.makedirs('static/{}'.format(folder), exist_ok=True)

            base64_data = str(current_file['value'])

            filename = current_file['filename'].replace(" ", "_")

            saving_file = open('static/{}/{}'.format(folder, filename), 'wb')
            saving_file.write(base64.decodebytes(base64_data.encode()))
            saving_file.close()

            saved_file_name = '{}/{}'.format(folder, filename)

            added_files.append(saved_file_name)

        return added_files
