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