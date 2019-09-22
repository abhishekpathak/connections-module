# -*- coding: utf-8 -*-


from server.app import api

from server.resources import UserResource, UserListResource, ConnectionResource, BatchConnectionResource, \
    RecommendationResource

api.add_resource(UserListResource, '/users')

api.add_resource(UserResource, '/users/<string:user_id>')

api.add_resource(ConnectionResource, '/users/<string:user_id>/connections')

api.add_resource(BatchConnectionResource, '/users/<string:user_id>/connections/batch')

api.add_resource(RecommendationResource, '/users/<string:user_id>/recommendations')
