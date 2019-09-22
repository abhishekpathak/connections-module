# -*- coding: utf-8 -*-

import os
from pathlib import Path

from server.models.connections_repository import JsonConnectionsRepository
from server.models.recommendations_repository import JsonRecommendationsRepository
from server.models.users_repository import JsonUsersRepository

PROJECT_ROOT = str(Path(os.getcwd()))

# logging
log_config_file = PROJECT_ROOT + os.sep + 'settings' + os.sep + 'log.yaml'
print(log_config_file)

usersRepository = JsonUsersRepository(PROJECT_ROOT + os.sep + 'ext' + os.sep + 'data.json')
connectionsRepository = JsonConnectionsRepository(PROJECT_ROOT + os.sep + 'ext' + os.sep + 'data.json')
recommendationsRepository = JsonRecommendationsRepository(PROJECT_ROOT + os.sep + 'ext' + os.sep + 'data.json')

CONNECTIONS_MAX_PAGE_SIZE = 50

RECOMMENDATIONS_MAX_PAGE_SIZE = 50
