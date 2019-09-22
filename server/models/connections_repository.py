# -*- coding: utf-8 -*-

import json
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Set, Iterable

from server.exceptions import DataIntegrityException
from server.models.entities import Connection

logger = logging.getLogger(__name__)


class ConnectionsRepository(ABC):

    @abstractmethod
    def get_by_id(self, connection_id) -> Connection:
        """ gets a connection from the repo on the basis of id.

        Args:
            connection_id: id of the connection

        Returns:
             the connection object linked to the id

        """

        pass

    @abstractmethod
    def get(self, users: Set[str]) -> Connection:
        """ gets a connection from the repo on the basis of connected users.

        Args:
            users: the user ids present in the connection

        Returns:
             the connection object linked to the users

        """

        pass

    @abstractmethod
    def get_all(self, user: str, offset: int, limit: int) -> Iterable[Connection]:
        """ gets all connections from the repo for a user.

        Prefer pagination for optimum performance across users.
        Use offset and limit to create pages.

        Args:
            user: the user id for which all linked connections are to be fetched

        Returns:
             all the connection objects linked to the user

        """

        pass

    @abstractmethod
    def create(self, users: Set[str]) -> Connection:
        """ creates and persists a connection in the repo.

        Args:
            users: the user ids present in the connection

        Returns:
             the created connection object

        """

        pass

    @abstractmethod
    def delete(self, users: Set[str]) -> None:
        """ deletes a connection from the repo on the basis of connected users.

        Args:
            users: the user ids present in the connection

        Returns:
             None

        """

        pass


class JsonConnectionsRepository(ConnectionsRepository):

    def __init__(self, json_file: str):

        super().__init__()

        self.connections = []

        for connection_dict in json.load(open(json_file)).get('connections', []):
            connection = self._object_mapper(connection_dict)
            self.connections.append(connection)

    @staticmethod
    def _object_mapper(connection_dict: dict) -> Connection:

        try:
            user1_id, user2_id = connection_dict['users'][0], connection_dict['users'][1]
            return Connection(connection_id=connection_dict['id'], users={user1_id, user2_id})
        except KeyError or IndexError as e:
            message = "malformed data in json file"
            logger.error(message)
            raise DataIntegrityException(message, e)

    def get_by_id(self, connection_id) -> Connection:

        for connection in self.connections:
            if connection.id == connection_id:
                return connection

        message = "connection not found: {}", connection_id

        logger.error(message)

        raise KeyError(message)

    def get(self, users: Set[str]) -> Connection:

        for connection in self.connections:
            if connection.users == users:
                return connection

        message = "connection not found: {}", users

        logger.error(message)

        raise KeyError(message)

    def get_all(self, user: str, offset: int, limit: int) -> Iterable[Connection]:

        connections = []

        for connection in self.connections:
            if user in connection.users:
                connections.append(connection)

        return connections

    def create(self, users: Set[str]) -> Connection:

        if self.get(users) is None:
            connection = Connection(str(uuid.uuid4()), users)
            self.connections.append(connection)
            return connection
        else:
            message = "connection already exists: {}", users
            logger.error(message)
            raise DataIntegrityException(message)

    def delete(self, users: Set[str]) -> None:

        for connection in self.connections:
            if connection.users == users:
                self.connections.remove(connection)
                return

        message = "connection not found: {}", users

        logger.error(message)

        raise KeyError(message)
