# -*- coding: utf-8 -*-


class DataIntegrityException(Exception):
    """ Thrown by a repository.

     Thrown when some data integrity constraint is violated

    """

    def __init__(self, message=None, exception=None):

        self.message = message

        self.exception = exception
