# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Iterable

from server.models.entities import Recommendation

logger = logging.getLogger(__name__)


class RecommendationsRepository(ABC):

    @abstractmethod
    def get(self, user: str, offset: int, limit: int) -> Iterable[Recommendation]:
        """ gets all recommendations from the repo for a given user.

        Args:
            user: the user id for which recommendations are to be fetched

        Returns:
             the recommendations for the user

        """

        pass

    @abstractmethod
    def save(self, user: str, recommended_user: str) -> Recommendation:
        """ create and persist a recommendation in the repo.

        Args:
            user: the user id to which the recommendation is linked
            recommended_user

        Returns:
             the created recommendation

        """

        pass

    @abstractmethod
    def delete(self, recommendation_id: str) -> None:
        """ deletes a recommendation from the repo.

        Args:
            recommended_id: id of the recommendation

        Returns:
             None

        """

        pass
