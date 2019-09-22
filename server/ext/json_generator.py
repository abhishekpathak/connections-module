# -*- coding: utf-8 -*-

import json
import os
import random
import uuid
from pathlib import Path
from typing import List

from faker import Faker
import sys

sys.path.append(str(Path(os.getcwd()).parents[0]))

from server.ORM.json_connections_repository import JsonConnectionsRepository
from server.controller import Controller
from server.ORM.json_recommendations_repository import JsonRecommendationsRepository
from server.ORM.json_users_repository import JsonUsersRepository
from faker.providers import internet

fake = Faker()
fake.add_provider(internet)


def random_from_list(some_list: List):
    return some_list[random.randint(0, len(some_list) - 1)]


college_list = ['college1', 'college2']

data = {
    'users': [],
    'connections': [],
    'recommendations': []
}

# generate users
for _ in range(7):
    user_dict = {
        'id': fake.user_name(),
        'email': fake.email(),
        'name': fake.name(),
        'college': random_from_list(college_list)
    }
    data['users'].append(user_dict)

# generate connections
user_ids = [user['id'] for user in data['users']]

for _ in range(4):
    connection_dict = {
        'id': str(uuid.uuid4()),
        'users': [random_from_list(user_ids), random_from_list(user_ids)]
    }
    data['connections'].append(connection_dict)

connected_user_ids = [connection['users'][0] for connection in data['connections']]

# generate recommendations
for user_id in user_ids:
    for _ in range(2):
        recommendation_dict = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'recommended_user_id': random_from_list(user_ids)
        }
        data['recommendations'].append(recommendation_dict)

with open('data.json', 'w') as f:
    f.write(json.dumps(data))


users_repo = JsonUsersRepository('data.json')
conn_repo = JsonConnectionsRepository('data.json')
reco_repo = JsonRecommendationsRepository('data.json')
controller = Controller(users_repo, conn_repo, reco_repo)
akshay = controller.get_user(random_from_list(connected_user_ids))
srk = controller.add_user(name='Shah Rukh Khan', email='srk@gmail.com', college='St. Stephens')
controller.update_user_details(akshay.id, name='Akshay Kumar', email='akki@gmail.com')

print("name: ", akshay.profile.name)
print("connections:", [user.profile.name for user in controller.get_connections(akshay.id)])
print("recommendations:", [user.profile.name for user in controller.get_recommendations(akshay.id)])

print("name: ", srk.profile.name)
print("connections:", [user.profile.name for user in controller.get_connections(srk.id)])
print("recommendations:", [user.profile.name for user in controller.get_recommendations(srk.id)])

print("adding connection...")
controller.add_connection(srk.id, akshay.id)
print("connection exists?", controller.check_connection_exists(srk.id, akshay.id))

print("name: ", akshay.profile.name)
print("connections:", [user.profile.name for user in controller.get_connections(akshay.id)])
print("recommendations:", [user.profile.name for user in controller.get_recommendations(akshay.id)])

print("name: ", srk.profile.name)
print("connections:", [user.profile.name for user in controller.get_connections(srk.id)])
print("recommendations:", [user.profile.name for user in controller.get_recommendations(srk.id)])

print("removing connection...")
controller.remove_connection(akshay.id, srk.id)
print("connection exists?", controller.check_connection_exists(srk.id, akshay.id))

print("name: ", akshay.profile.name)
print("connections:", [user.profile.name for user in controller.get_connections(akshay.id)])
print("recommendations:", [user.profile.name for user in controller.get_recommendations(akshay.id)])

print("name: ", srk.profile.name)
print("connections:", [user.profile.name for user in controller.get_connections(srk.id)])
print("recommendations:", [user.profile.name for user in controller.get_recommendations(srk.id)])

print("removing user...", akshay.profile.name)
controller.remove_user(akshay.id)
