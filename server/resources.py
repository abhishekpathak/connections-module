# -*- coding: utf-8 -*-
import logging
from typing import List, Dict

from flask import request
from flask_restful import Resource

from server.controller import Controller
from server.exceptions import HttpError, DataIntegrityException
from server.models.entities import User
from . import config, api

logger = logging.getLogger(__name__)

controller = Controller(users_repository=config.usersRepository,
                        connections_repository=config.connectionsRepository,
                        recommendations_repository=config.recommendationsRepository)


def _check_user(user_id: str) -> User:
    """ cross-checks if a user exists in the system.

    Args:
        user_id: id of the user to cross-check

    Returns:
        the user object if the user id exists in the system.
        raises an exception if it does not.

    """

    try:
        user = controller.get_user(user_id)
        logger.info('verified that user id {} exists.', user_id)
        return user
    except KeyError:
        message = "no record found for user: {}", user_id
        logger.error(message)
        raise HttpError(404, message)


class Users(Resource):
    """ Exposes the users as a RESTful resource.

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
                'href': api.url_for(Users, user_id=user_id),
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

        user = _check_user(user_id)

        resp_dict = {
            '_data': self.user_repr(user),
            '_description': None,
            '_links': self.hateoas_repr(user_id)
        }

        return resp_dict

    def post(self):
        """ adds a user to the system.

        Args:
            None

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        payload = request.get_json()

        logger.debug('create user: details recieved: {}', payload)

        try:
            user = controller.add_user(email=payload['email'], name=payload['name'], college=payload['college'])
        except KeyError:
            message = "unable to parse one of the following: email, name, college"
            logger.error(message)
            raise HttpError(400, message)

        resp_dict = {
            '_data': self.user_repr(user),
            '_description': None,
            '_links': self.hateoas_repr(user.id)
        }

        status = 201

        headers = {'Location': api.url_for(Users, user_id=user.id)}

        return resp_dict, status, headers

    def patch(self, user_id: str):
        """ updates the details of a user.

        Args:
            user_id: id of the user.

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        patch = request.get_json()

        logger.debug('update user: details recieved: {}', patch)

        try:
            user = controller.update_user_details(user_id, **patch)
        except KeyError:
            message = "no record found for user: {}", user_id
            logger.error(message)
            raise HttpError(404, message)

        resp_dict = {
            '_data': self.user_repr(user),
            '_description': None,
            '_links': self.hateoas_repr(user_id)
        }

        status = 200

        headers = {'Location': api.url_for(Users, user_id=user.id)}

        return resp_dict, status, headers


class Connections(Resource):

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
                'href': api.url_for(Users, user_id=user_id),
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

        _check_user(user_id)

        offset = int(request.args.get('offset', 0))

        limit = int(request.args.get('limit', 50))

        logger.debug('recieved a request to get the connnections for user {} with offset {} and limit {}',
                     user_id, offset, limit)

        connected_users = controller.get_connections(user_id, offset, limit)

        link_for_next_page = {
            'rel': 'next',
            'href': api.url_for(Connections, user_id=user_id, offset=offset + len(connected_users), limit=limit),
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

        _check_user(user_id)

        try:
            user_id_to_connect = request.get_json()['id']
        except KeyError:
            message = "add connection: expecting id in payload"
            logger.error(message)
            raise HttpError(400, message)

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
            raise HttpError(400, message)

        controller.remove_connection(user_id, user_id_to_disconnect)

        return {}, 204


class BatchConnections(Resource):

    def post(self, user_id: str):
        """ creates multiple new connections for the current user.

        Args:
            user_id: id of the current user.

        Returns:
            a response object (either directly or implicitly by the framework)

        """

        status = {}

        user_ids_to_connect = request.get_json()['ids']

        for user_id_to_connect in user_ids_to_connect:
            try:
                controller.add_connection(user_id, user_id_to_connect)
                status = 200
            except DataIntegrityException:
                status = 409
            finally:
                logger.debug('batch add connections to {}: status for {} is {}', user_id, user_id_to_connect, status)
                status[user_id_to_connect] = status

        resp_dict = {
            '_data': status,
            '_description': None,
            '_links': Connections.hateoas_repr(user_id)
        }

        return resp_dict


class Recommendations(Resource):

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
                'href': api.url_for(Users, user_id=user_id),
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

        _check_user(user_id)

        offset = int(request.args.get('offset', 0))

        limit = int(request.args.get('limit', 50))

        logger.debug('recieved a request to get the recommendations for user {} with offset {} and limit {}',
                     user_id, offset, limit)

        recommended_users = controller.get_recommendations(user_id, offset, limit)

        link_for_next_page = {
            'rel': 'next',
            'href': api.url_for(Recommendations, user_id=user_id, offset=offset + len(recommended_users), limit=limit),
            'action': 'GET',
            'types': ['application/json']
        }

        resp_dict = {
            '_data': [self.recommendation_repr(user) for user in recommended_users],
            '_description': None,
            '_links': [link_for_next_page] + self.hateoas_repr(user_id)
        }

        return resp_dict
