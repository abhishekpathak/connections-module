# -*- coding: utf-8 -*-

import json
import logging
import uuid

from faker import Faker
from faker.providers import internet

from server.exceptions import DataIntegrityException
from server.models import Profile, User, UsersRepository

logger = logging.getLogger(__name__)

fake = Faker()
fake.add_provider(internet)

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

        message = "user not found: {}".format(user_id)

        logger.error(message)

    def create(self, email: str, profile: Profile) -> User:

        user = User(fake.user_name(), email, profile)

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

        message = "user not found: {}".format(user_id)

        logger.error(message)

        raise KeyError(message)