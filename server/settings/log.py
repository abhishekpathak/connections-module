# -*- coding: utf-8 -*-

from logging.config import dictConfig

import yaml

""" Logging configuration.
"""


def configure_logging(log_config_file):
    with open(log_config_file) as fl:
        dictConfig(yaml.load(fl))
