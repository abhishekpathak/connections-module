# -*- coding: utf-8 -*-

from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Set, Iterable


class Profile(object):
    """ models the profile of a user.

    """

    def __init__(self, name: str, college: str):

        self.name = name

        self.college = college


class User(object):
    """ models a user in the app.

    """

    def __init__(self, user_id: str, email: str, profile: Profile):

        self.id = user_id

        self.email = email

        self.profile = profile

    def __str__(self):
        return "User: [id: {}, name: {}, email: {}, college: {}]"\
            .format(self.id, self.profile.name, self.email, self.profile.college)


class UsersRepository(ABC):

    @abstractmethod
    def get(self, user_id: str) -> User:
        """ gets a user object from the repo.

        Args:
            user_id: id of the user

        Returns:
             the user object linked to the id

        """

        pass

    @abstractmethod
    def create(self, email: str, profile: Profile) -> User:
        """ creates and persists a new user object in the repo.

        Args:
            email
            profile

        Returns:
             the user object that was created

        """

        pass

    @abstractmethod
    def update(self, user_id: str, profile: Profile) -> User:
        """ updates and persists a user object in the repo.

        Args:
            user_id: id of the user
            profile: the profile (details to update)

        Returns:
             the user object that was updated

        """

        pass

    @abstractmethod
    def delete(self, user_id: str) -> None:
        """ deletes a user object from the repo.

        Args:
            user_id: id of the user

        Returns:
            None

        """

        pass


class Connection(object):
    """ a connection links two users. It is an undirected link.

    """

    def __init__(self, connection_id: str, users: Set[str]):

        self.id = connection_id

        self.users = users


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
            offset: the starting index from where to retrieve the results
            limit: the maximum number of results to retrieve in one go

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


class Recommendation(object):
    """ a recommendation provided to a user to create connections with more users.

    """

    def __init__(self, recommendation_id: str, user: str, recommended_user: str):

        self.id = recommendation_id

        self.user = user

        self.recommended_user = recommended_user


class RecommendationsRepository(ABC):

    @abstractmethod
    def get(self, user: str, offset: int, limit: int) -> Iterable[Recommendation]:
        """ gets all recommendations from the repo for a given user.

        Args:
            user: the user id for which recommendations are to be fetched
            offset: the starting index from where to retrieve the results
            limit: the maximum number of results to retrieve in one go

        Returns:
             the recommendations for the user

        """

        pass

    @abstractmethod
    def save(self, user: str, recommended_user: str) -> Recommendation:
        """ create and persist a recommendation in the repo.

        Args:
            user: the user id to which the recommendation is linked
            recommended_user

        Returns:
             the created recommendation

        """

        pass

    @abstractmethod
    def delete(self, recommendation_id: str) -> None:
        """ deletes a recommendation from the repo.

        Args:
            recommendation_id: id of the recommendation

        Returns:
             None

        """

        pass
