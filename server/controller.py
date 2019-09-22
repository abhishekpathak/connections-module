# -*- coding: utf-8 -*-

import logging
from typing import Set

from server.app import config
from server.models import User, Profile, UsersRepository, ConnectionsRepository, RecommendationsRepository

logger = logging.getLogger(__name__)


class Controller(object):
    """ Responsible for managing data flows. All business logic should be encapsulated here.

    The controller sits between the data requester (client) and the data store (models).
    Clients talk to the controller to get a view on the data. The controller in turn has a handle to all of the
    data stores, and delegates data CRUD operations to them. It can also transform the data it recieves.

    Clients view data through the lens that the controller chooses. The controller exposes many common
    business operations for the clients to use. If the controller does not support an operation, it should be assumed
    that it is not a "feature" for business.

    """

    def __init__(self, users_repository: UsersRepository,
                 connections_repository: ConnectionsRepository,
                 recommendations_repository: RecommendationsRepository):

        self.usersRepository = users_repository

        self.connectionsRepository = connections_repository

        self.recommendationsRepository = recommendations_repository

    def get_user(self, user_id: str) -> User:
        """ gets a user given the id.

        Args:
            user_id: id of the user to get

        Returns:
            the User object

        """

        return self.usersRepository.get(user_id)

    def update_user_details(self, user_id: str, **kwargs) -> User:
        """ updates a user.

        Args:
            user_id: id of the user to update
            kwargs: field to update: new value

        Returns:
            the updated User object

        """

        updatable_fields = [
            'name',
            'college'
        ]

        profile = self.get_user(user_id).profile

        for item in kwargs:
            if item in updatable_fields:
                logger.debug('field {} will be updated for user {}'.format(item, user_id))
                setattr(profile, item, kwargs[item])

        return self.usersRepository.update(user_id, profile)

    def add_user(self, email: str, name: str, college: str) -> User:
        """ adds a user to the system.

        Usually will be called after a successful sign-up.

        Args:
            email
            name
            college

        Returns:
            the created User object

        """

        profile = Profile(name=name, college=college)

        logger.info('a new user signed up with email: {}'.format(email))

        return self.usersRepository.create(email, profile)

    def remove_user(self, user_id: str) -> None:
        """ removes a user from the system.

        Args:
            user_id: id of the user to remove

        Returns:
            None

        """

        logger.info('deleting user {}'.format(user_id))

        self.usersRepository.delete(user_id)

    def get_connections(self, user_id: str, offset: int = 0, limit: int = 50) -> Set[User]:
        """ gets all the connections/friends of a user.

        Paginated for predictable performance across users.

        Args:
            user_id: id of the user
            offset: the starting index from where to retrieve the results
            limit: the maximum number of results to retrieve in one go

        Returns:
            an unordered set of all the connected users.

        """

        limit = limit if limit < config.CONNECTIONS_MAX_PAGE_SIZE else config.CONNECTIONS_MAX_PAGE_SIZE

        connections_iterator = self.connectionsRepository.get_all(user_id, offset, limit)

        users = set()

        for connection in connections_iterator:
            connected_user = connection.users.difference({user_id}).pop()
            logger.debug('found connection with id: {} and users: {}. Connected user deduced is {}'
                         .format(connection.id, connection.users, connected_user))
            users.add(self.get_user(connected_user))
            # fail-safe in case the repository does not honor the limit
            if len(users) >= limit:
                logger.warning('the data repository returned more than the limit: {}'.format(limit))
                break

        return users

    def add_connection(self, user1: str, user2: str) -> None:
        """ adds a connection between two users.

        In other words, this method makes two users friends.

        Args:
            user1: the first user
            user2: the second user

            note that a connection is undirected. The prefixes (first, second) of the users are mere notations and do
            not imply any kind of inherent order.

        Returns:
            None
            An exception might be thrown if such a connection already exists.

        """

        logger.info('adding a new connection between {} and {}'.format(user1, user2))

        self.connectionsRepository.create({user1, user2})

    def batch_add_connections(self, user: str, user_ids_to_connect: str) -> None:
        """ adds a connection between two users (batch mode).

        offloads the batch processing to a task queue. Should ideally return a job status to track.

        Args:
            user: the first user
            user_ids_to_connect: a list of users to connect the first user to.

            note that a connection is undirected. The prefixes (first, second) of the users are mere notations and do
            not imply any kind of inherent order.

        Returns:
            None

        """

        #raise NotImplementedError() # commented out to allow the API to demonstrate its functionality.
        pass

    def remove_connection(self, user1: str, user2: str) -> None:
        """ removes an (existing) connection between two users.

        In other words, this method "un-friends" two users.

        Args:
            user1: the first user
            user2: the second user

            note that a connection is undirected. The prefixes (first, second) of the users are mere notations and do
            not imply any kind of inherent order.

        Returns:
            None
            An exception might be thrown if such a connection does not exist.

        """

        logger.info('removing the connection between {} and {}'.format(user1, user2))

        self.connectionsRepository.delete({user1, user2})

    def check_connection_exists(self, user1: str, user2: str) -> bool:
        """ checks if two users are connected.

        More rigorously, checks for the existence of a connection between two users.

        Args:
            user1: the first user
            user2: the second user

            note that a connection is undirected. The prefixes (first, second) of the users are mere notations and do
            not imply any kind of inherent order.

        Returns:
            True if a such a connection exists, False otherwise.

        """

        connection = self.connectionsRepository.get({user1, user2})

        return connection is not None

    def get_recommendations(self, user_id: str, offset: int = 0, limit: int = 50) -> Set[User]:
        """ fetches the friend/connection recommendations for a user.

        Paginated for predictable performance across users.

        Args:
            user_id: id of the user
            offset: the starting index from where to retrieve the results
            limit: the maximum number of results to retrieve in one go

        Returns:
            an unordered set of all the recommended users.

        """

        limit = limit if limit < config.RECOMMENDATIONS_MAX_PAGE_SIZE else config.RECOMMENDATIONS_MAX_PAGE_SIZE

        recommendations_iterator = self.recommendationsRepository.get(user_id, offset, limit)

        users = set()

        for recommendation in recommendations_iterator:
            logger.debug('found recommendation with id: {}, user: {} and recommended user: {}'
                         .format(recommendation.id, recommendation.user, recommendation.recommended_user))
            users.add(self.get_user(recommendation.recommended_user))
            # fail-safe in case the repository does not honor the limit
            if len(users) >= limit:
                logger.warning('the data repository returned more than the limit: {}'.format(limit))
                break

        return users

    def add_recommendations(self, user_id: str, recommended_users: Set[str]) -> None:
        """ adds the (newly generated) recommendations for a user to the system.

        The recommendations will usually be generated by a (separate long-running) job.
        A transporter will periodically call this method to dump fresh recommendations to the data repositories
        so that they can be served.

        Args:
            user_id: id of the user
            recommended_users: an unordered set of the user ids of the recommended users

        Returns:
            None

        """

        for recommended_user in recommended_users:
            logger.info('adding a new recommendation for {}: {}'.format(user_id, recommended_user))
            self.recommendationsRepository.save(user_id, recommended_user)

    def delete_recommendations(self, user_id: str) -> None:
        """ deletes the (stale) recommendations for a user.

        Since recommendations depend on a variety of signals which are constantly changing, we need to purge the
        existing recommendations for a user periodically and add fresh recommendations {@see add_recommendations)

        Args:
            user_id: id of the user

        Returns:
            None

        """

        recommendations = self.recommendationsRepository.get(user_id, offset=0, limit=50)

        for recommendation in recommendations:
            logger.info('removing the recommendation for {}: {}'.format(user_id, recommendation.recommended_user))
            self.recommendationsRepository.delete(recommendation.id)
