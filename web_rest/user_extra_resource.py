from flask_restful import Resource, reqparse
from data.user_extra import UserExtra
from flask_jwt_extended import (jwt_required, get_jwt_identity)
from services import user_extra_service

import datetime

pictures_update_parser = reqparse.RequestParser(bundle_errors=True)
pictures_update_parser.add_argument('picturesUrls', action='append')

profile_pic_parser = reqparse.RequestParser(bundle_errors=True)
profile_pic_parser.add_argument('profilePictureUrl')


class GetUserExtra(Resource):
    @jwt_required
    def get(self):
        user_login = get_jwt_identity()

        try:
            extra = user_extra_service.get_user_extra_by_login(user_login)
        except Exception as ex:
            extra = user_extra_service.create_user_extra(user_login)

        return extra.to_dict()


class UpdateUserPictures(Resource):
    @jwt_required
    def put(self):
        user_login = get_jwt_identity()

        try:
            extra = user_extra_service.get_user_extra_by_login(user_login)
        except Exception as ex:
            extra = user_extra_service.create_user_extra(user_login)

        data = pictures_update_parser.parse_args()

        if data['picturesUrls'] is None or len(data['picturesUrls']) == 0:
            extra.profilePictureUrl = ''

        all_pictures_urls = list(extra.picturesUrls)
        for pictureUrl in data['picturesUrls']:
            if pictureUrl not in all_pictures_urls:
                all_pictures_urls.append(pictureUrl)

        extra.picturesUrls = all_pictures_urls

        extra.save()

        return extra.to_dict()


class UpdateUserProfilePic(Resource):
    @jwt_required
    def put(self):
        user_login = get_jwt_identity()

        try:
            extra = user_extra_service.get_user_extra_by_login(user_login)
        except Exception as ex:
            extra = user_extra_service.create_user_extra(user_login)

        data = profile_pic_parser.parse_args()

        extra.profilePictureUrl = data['profilePictureUrl']

        extra.save()

        return extra.to_dict()
