from flask_restful import Resource, reqparse
from data_auth.models import UserModel, AuthorityModel, RevokedTokenModel
from flask_jwt_extended import (create_access_token,
                                jwt_required,
                                get_jwt_identity, get_jwt_claims, get_raw_jwt)

from services import organizacion_service as organization_service

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('login')
parser.add_argument('password')
parser.add_argument('firstName')
parser.add_argument('lastName')
parser.add_argument('email')
parser.add_argument('authorities', action='append')
parser.add_argument('old_password')


class UserRegistration(Resource):
    @jwt_required
    def post(self):
        claims = get_jwt_claims()

        if 'admin' not in claims['authorities']:
            return {'message': 'You dont have permision to perform this operation'}, 401

        data = parser.parse_args()

        if UserModel.find_by_login(data['login']):
            return {'message': 'User {} already exists'.format(data['login'])}

        new_user = UserModel(
            login=data['login'],
            password=UserModel.generate_hash(data['password']),
            firstName=data['firstName'],
            lastName=data['lastName'],
            email=data['email']
        )

        for authority in data['authorities']:
            new_user_authority = AuthorityModel.find_by_authority_name(authority)
            if new_user_authority:
                new_user.authorities.append(new_user_authority)

        try:
            new_user.save_to_db()

            return {'message': 'User {} was create'.format(new_user.login)}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = UserModel.find_by_login(data['login'])
        if not current_user:
            return {'message': 'User {} doesnt exists'.format(data['login'])}, 401

        if UserModel.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=current_user)
            return {
                'id_token': access_token
            }
        else:
            return {'message', 'Wrong credentials'}, 401


class Account(Resource):
    @jwt_required
    def get(self):
        login = get_jwt_identity()
        current_user = UserModel.find_by_login(login)
        if not current_user:
            return {'message': 'User {} doesnt exists'.format(login)}, 401
        else:
            ret_user = {
                'login': current_user.login,
                'firstName': current_user.firstName,
                'lastName': current_user.lastName,
                'email': current_user.email,
                'authorities': [authority.authority_name for authority in current_user.authorities]
            }
            return ret_user

    @jwt_required
    def put(self):
        data = parser.parse_args()
        user_to_edit = UserModel.find_by_login(data['login'])
        if not user_to_edit:
            return {'message': 'User {} doesnt exists'.format(data['login'])}
        else:
            user_to_edit.firstName = data['firstName']
            user_to_edit.lastName = data['lastName']
            try:
                user_to_edit.save_to_db()

                return {'message': 'User {} was edited'.format(user_to_edit.login)}
            except:
                return {'message': 'Something went wrong'}, 500


class Organization(Resource):
    @jwt_required
    def get(self):
        login = get_jwt_identity()
        current_user = UserModel.find_by_login(login)
        if not current_user:
            return {'message': 'User {} doesnt exists'.format(login)}, 401
        else:
            organization = organization_service.get_organizacion_by_id(current_user.organizationId)

        if not organization:
            return {'message': 'Organization {} doesnt exists'.format(current_user.organizationId)}, 401

        return organization.to_dict()
