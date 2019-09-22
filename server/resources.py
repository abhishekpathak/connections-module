# -*- coding: utf-8 -*-
import logging
from typing import List, Dict

from flask import request
from flask_restful import Resource

from server import utils
from server.controller import Controller
from server.exceptions import DataIntegrityException
from server.models import User
from server.app import config, api

logger = logging.getLogger(__name__)

controller = Controller(users_repository=config.usersRepository,
                        connections_repository=config.connectionsRepository,
                        recommendations_repository=config.recommendationsRepository)


class User(Resource):
    """ Exposes a User as a RESTful resource.

    """

    @staticmethod
    def user_repr(user: User) -> Dict:
        """ gets the json mapping for a user object.

        The json API representation of a user need not be coupled to the domain model of a user.
        This method provides the object-API mapping for a user.

        Args:
            user: the user object

        Returns:
            the json representation de-serialized as a dict

        """

        return {
            'id': user.id,
            'name': user.profile.name,
            'email': user.email,
            'college': user.profile.college
        }

    @staticmethod
    def hateoas_repr(user_id: str) -> List[Dict]:
        """  This method collects and returns all related resources as links.

        A link is the description of a resource. Each link contains sufficient information for a client
        to be able to fully navigate to the resource.

        This enables HATEOAS for our REST API.

        Args:
            user_id: the user id defining the resource

        Returns:
            a list of the links

        """

        return [
            {
                'rel': 'self',
                'href': api.url_for(User, user_id=user_id),
                'action': 'GET',
                'types': ['application/json']
            }
        ]

    def get(self, user_id: str):
        """ fetches the details of a user.

        Args:
            user_id: id of the user.

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        user = controller.get_user(user_id)
        if user is None:
            return utils.format_error("the user ID was not found"), 404

        resp_dict = {
            '_data': self.user_repr(user),
            '_description': None,
            '_links': self.hateoas_repr(user_id)
        }

        return resp_dict

    def patch(self, user_id: str):
        """ updates the details of a user.

        Args:
            user_id: id of the user.

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        patch = request.get_json()

        logger.debug('update user: details recieved: {}'.format(patch))

        try:
            user = controller.update_user_details(user_id, **patch)
        except KeyError:
            message = "no record found for user: {}".format(user_id)
            logger.error(message)
            return utils.format_error(message), 404

        resp_dict = {
            '_data': self.user_repr(user),
            '_description': None,
            '_links': self.hateoas_repr(user_id)
        }

        status = 200

        headers = {'Location': api.url_for(User, user_id=user.id)}

        return resp_dict, status, headers


class UserList(Resource):
    """ Exposes a group of User objects as a RESTful resource and lets you POST to add a new user.

    """

    def post(self):
        """ adds a user to the system.

        Args:
            None

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        payload = request.get_json()

        logger.debug('create user: details recieved: {}'.format(payload))

        try:
            user = controller.add_user(email=payload['email'], name=payload['name'], college=payload['college'])
        except KeyError:
            message = "unable to parse one of the following: email, name, college"
            logger.error(message)
            return utils.format_error(message), 400

        resp_dict = {
            '_data': User.user_repr(user),
            '_description': None,
            '_links': User.hateoas_repr(user.id)
        }

        status = 201

        headers = {'Location': api.url_for(User, user_id=user.id)}

        return resp_dict, status, headers


class Connection(Resource):
    """ Exposes a collection of Connection objects as a RESTful resource.

    """

    @staticmethod
    def connection_repr(user: User) -> Dict:
        """ gets the json mapping for a user object.

        The json API representation of a connection need not be coupled to its domain model.
        This method provides the object-API mapping for a connection.

        Args:
            user: the connection (a user object)

        Returns:
            the json representation de-serialized as a dict

        """

        return {
            'id': user.id,
            'name': user.profile.name,
        }

    @staticmethod
    def hateoas_repr(user_id: str):
        """  This method collects and returns all related resources as links.

        A link is the description of a resource. Each link contains sufficient information for a client
        to be able to fully navigate to the resource.

        This enables HATEOAS for our REST API.

        Args:
            user_id: the user id defining the resource

        Returns:
            a list of the links

        """

        return [
            {
                'rel': 'self',
                'href': api.url_for(User, user_id=user_id),
                'action': 'GET',
                'types': ['application/json']
            }
        ]

    def get(self, user_id: str):
        """ fetches the connections/friends of a user.

        Paginated for optimum performance across users.

        Args:
            user_id: id of the user.

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        user = controller.get_user(user_id)
        if user is None:
            return utils.format_error("the user ID was not found"), 404

        offset = int(request.args.get('offset', 0))

        limit = int(request.args.get('limit', 50))

        logger.debug('received a request to get the connnections for user {} with offset {} and limit {}'
                     .format(user_id, offset, limit))

        connected_users = controller.get_connections(user_id, offset, limit)

        link_for_next_page = {
            'rel': 'next',
            'href': api.url_for(Connection, user_id=user_id, offset=offset + len(connected_users), limit=limit),
            'action': 'GET',
            'types': ['application/json']
        }

        resp_dict = {
            '_data': [self.connection_repr(user) for user in connected_users],
            '_description': None,
            '_links': [link_for_next_page] + self.hateoas_repr(user_id)
        }

        return resp_dict

    def post(self, user_id: str):
        """ creates a new connection for the current user.

        Args:
            user_id: id of the current user.

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        user = controller.get_user(user_id)
        if user is None:
            return utils.format_error("the user ID was not found"), 404

        try:
            user_id_to_connect = request.get_json()['id']
        except KeyError:
            message = "add connection: expecting id in payload"
            logger.error(message)
            return utils.format_error(message), 400

        resp_dict = {
            '_data': None,
            '_description': None,
            '_links': self.hateoas_repr(user_id)
        }

        try:
            controller.add_connection(user_id, user_id_to_connect)
            return resp_dict, 201,
        except DataIntegrityException:
            return resp_dict, 409

    def delete(self, user_id: str):
        """ deletes a connection for the current user

        Args:
            user_id: id of the current user.

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        try:
            user_id_to_disconnect = request.args['user']
        except KeyError:
            message = 'can only delete connections one at a time. Please specify user=<user_id> in query params.'
            logger.error(message)
            return utils.format_error(message), 404

        controller.remove_connection(user_id, user_id_to_disconnect)

        return {}, 204


class BatchConnection(Resource):

    def post(self, user_id: str):
        """ creates multiple new connections for the current user.

        Args:
            user_id: id of the current user.

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        user_ids_to_connect = request.get_json()['ids']
        controller.batch_add_connections(user_id, user_ids_to_connect)

        resp_dict = {
            '_data': None,
            '_description': None,
            '_links': Connection.hateoas_repr(user_id)
        }

        return resp_dict, 202


class Recommendation(Resource):
    """ Exposes a collection of Recommendation objects as a RESTful resource.

    """

    @staticmethod
    def recommendation_repr(user: User):
        """ gets the json mapping for a recommendation.

        The json API representation of a recommendation need not be coupled to its domain model.
        This method provides the object-API mapping for a recommendation.

        Args:
            user: the recommendation (a user object)

        Returns:
            the json representation de-serialized as a dict

        """

        return {
            'id': user.id,
            'name': user.profile.name,
        }

    @staticmethod
    def hateoas_repr(user_id: str):
        """  This method collects and returns all related resources as links.

        A link is the description of a resource. Each link contains sufficient information for a client
        to be able to fully navigate to the resource.

        This enables HATEOAS for our REST API.

        Args:
            user_id: the user id defining the resource

        Returns:
            a list of the links

        """

        return [
            {
                'rel': 'self',
                'href': api.url_for(User, user_id=user_id),
                'action': 'GET',
                'types': ['application/json']
            }
        ]

    def get(self, user_id: str):
        """ fetches the recommendations of a user.

        Paginated for optimum performance across users.

        Args:
            user_id: id of the user.

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        user = controller.get_user(user_id)
        if user is None:
            return utils.format_error("the user ID was not found"), 404

        offset = int(request.args.get('offset', 0))

        limit = int(request.args.get('limit', 50))

        logger.debug('recieved a request to get the recommendations for user {} with offset {} and limit {}'
                     .format(user_id, offset, limit))

        recommended_users = controller.get_recommendations(user_id, offset, limit)

        link_for_next_page = {
            'rel': 'next',
            'href': api.url_for(Recommendation, user_id=user_id, offset=offset + len(recommended_users), limit=limit),
            'action': 'GET',
            'types': ['application/json']
        }

        resp_dict = {
            '_data': [self.recommendation_repr(user) for user in recommended_users],
            '_description': None,
            '_links': [link_for_next_page] + self.hateoas_repr(user_id)
        }

        return resp_dict
