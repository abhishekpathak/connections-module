# -*- coding: utf-8 -*-

from server import api

from server.resources import Users, Connections, BatchConnections, Recommendations

api.add_resource(Users, '/api/v1/users/<string:user_id>')

api.add_resource(Connections, '/api/v1/users/<string:user_id>/connections')

api.add_resource(BatchConnections, '/api/v1/users/<string:user_id>/connections/batch')

api.add_resource(Recommendations, '/api/v1/users/<string:user_id>/recommendations')
