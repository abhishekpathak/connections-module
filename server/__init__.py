# -*- coding: utf-8 -*-

import os
from importlib import import_module

from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from server.settings import log

app = Flask(__name__)

# enable CORS for this app
CORS(app)

api = Api(app)

# SOCIAL_APP_MODE can have values either 'prod' or 'dev'
mode = os.environ.get('SOCIAL_APP_MODE', 'dev').lower()

config = import_module('server.settings.' + mode)

log.configure_logging(config.log_config_file)

from server import views
