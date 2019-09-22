# -*- coding: utf-8 -*-

import json
import logging
from abc import ABC, abstractmethod
from typing import Iterable

from server.exceptions import DataIntegrityException
from server.models.entities import Recommendation
from server.models.recommendations_repository import RecommendationsRepository

logger = logging.getLogger(__name__)


class JsonRecommendationsRepository(RecommendationsRepository):

    def __init__(self, json_file: str):

        super().__init__()

        self.recommendations = set()

        for user_dict in json.load(open(json_file)).get('recommendations', []):
            recommendation = self._object_mapper(user_dict)
            self.recommendations.add(recommendation)

    @staticmethod
    def _object_mapper(user_dict: dict) -> Recommendation:

        try:
            return Recommendation(recommendation_id=user_dict['id'],
                                  user=user_dict['user_id'],
                                  recommended_user=user_dict['recommended_user_id'])
        except KeyError as e:
            message = "malformed data in json file"
            logger.error(message)
            raise DataIntegrityException(message, e)

    def get(self, user: str, offset: int, limit: int) -> Iterable[Recommendation]:

        recommendations = set()

        for recommendation in self.recommendations:
            if recommendation.user == user:
                recommendations.add(recommendation)

        return recommendations

    def save(self, user: str, recommended_user: str) -> Recommendation:

        raise NotImplementedError()

    def delete(self, recommendation_id: str) -> None:

        raise NotImplementedError()

    def total(self) -> int:

        return len(self.recommendations)
