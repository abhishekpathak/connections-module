# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Set


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


class Connection(object):
    """ a connection links two users. It is an undirected link.

    """

    def __init__(self, connection_id: str, users: Set[str]):

        self.id = connection_id

        self.users = users


class Recommendation(object):
    """ a recommendation provided to a user to create connections with more users.

    """

    def __init__(self, recommendation_id: str, user: str, recommended_user: str):

        self.id = recommendation_id

        self.user = user

        self.recommended_user = recommended_user
