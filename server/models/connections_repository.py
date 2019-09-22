# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Set, Iterable

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
