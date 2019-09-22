# -*- coding: utf-8 -*-

from server.app import api

from server.resources import User, UserList, Connection, BatchConnection, Recommendation

api.add_resource(UserList, '/users')

api.add_resource(User, '/users/<string:user_id>')

api.add_resource(Connection, '/users/<string:user_id>/connections')

api.add_resource(BatchConnection, '/users/<string:user_id>/connections/batch')

api.add_resource(Recommendation, '/users/<string:user_id>/recommendations')
