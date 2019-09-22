# -*- coding: utf-8 -*-

import json
import logging
import uuid
from abc import ABC, abstractmethod

from server.exceptions import DataIntegrityException
from server.models.entities import Profile, User

logger = logging.getLogger(__name__)


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


class JsonUsersRepository(UsersRepository):

    def __init__(self, json_file: str):

        super().__init__()

        self.users = []

        for user_dict in json.load(open(json_file)).get('users', []):
            user = self._object_mapper(user_dict)
            self.users.append(user)

    @staticmethod
    def _object_mapper(user_dict: dict) -> User:

        try:
            return User(user_id=user_dict['id'],
                        email=user_dict['email'],
                        profile=Profile(name=user_dict['name'], college=user_dict['college']))
        except KeyError as e:
            message = "malformed data in json file"
            logger.error(message)
            raise DataIntegrityException(message, e)

    def get(self, user_id: str) -> User:

        for user in self.users:
            if user.id == user_id:
                return user

        message = "user not found: {}", user_id

        logger.error(message)

        raise KeyError(message)

    def create(self, email: str, profile: Profile) -> User:

        # TODO consider adding email uniqueness check?
        user = User(str(uuid.uuid4()), email, profile)

        self.users.append(user)

        return self.get(user.id)

    def update(self, user_id: str, profile: Profile) -> User:

        for existing_user in self.users:
            if existing_user.id == user_id:
                existing_user.profile = profile
                break

        return self.get(user_id)

    def delete(self, user_id: str) -> None:

        for existing_user in self.users:
            if existing_user.id == user_id:
                self.users.remove(existing_user)
                break

        message = "user not found: {}", user_id

        logger.error(message)

        raise KeyError(message)
