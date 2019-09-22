# -*- coding: utf-8 -*-


class DataIntegrityException(Exception):
    """ Thrown by a repository.

     Thrown when some data integrity constraint is violated

    """

    def __init__(self, message=None, exception=None):

        self.message = message

        self.exception = exception


class HttpError(Exception):
    """ Thrown by a resource.

    Thrown when a application exception corresponds to a specific HTTP error for the client.

    """

    def __init__(self, status_code, message=None):

        Exception.__init__(self)

        self.message = message

        self.status_code = status_code

    def to_dict(self):

        return {
            '_description': self.message
        }
