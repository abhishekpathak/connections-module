import unittest
from unittest.mock import MagicMock

from server.controller import Controller
from server.ORM.json_connections_repository import ConnectionsRepository
from server.models import User, Profile
from server.ORM.json_recommendations_repository import RecommendationsRepository
from server.ORM.json_users_repository import UsersRepository


class TestController(unittest.TestCase):

    def setUp(self) -> None:
        michael = User(user_id='mscott', email='mscott@dunder-mifflin.com', profile=Profile(name='Michael Scott', college='Scranton University'))
        users_repository: UsersRepository = MagicMock()
        users_repository.get = MagicMock(return_value=michael)
        users_repository.create = MagicMock(return_value=michael)
        users_repository.update = MagicMock(return_value=michael)
        connections_repository: ConnectionsRepository = MagicMock()
        recommendations_repository: RecommendationsRepository = MagicMock()
        self.controller = Controller(users_repository, connections_repository, recommendations_repository)

    def test_get_user(self) -> None:
        user = self.controller.get_user('foo')
        self.controller.usersRepository.get.assert_called_once_with('foo')
        assert isinstance(user, User)

    def test_update_user_details(self) -> None:
        user = self.controller.update_user_details('mscott', college='University of New York')
        self.controller.usersRepository.update.assert_called_once()
        assert isinstance(user, User)

    def test_add_user(self) -> None:
        user = self.controller.add_user(name='Michael Scott', email='mscott@dunder-mifflin.com', college='Scranton University')
        self.controller.usersRepository.create.assert_called_once()
        assert isinstance(user, User)

    def test_remove_user(self) -> None:
        user = self.controller.add_user(name='Michael Scott', email='mscott@dunder-mifflin.com', college='Scranton University')
        assert isinstance(user, User)
        self.controller.remove_user(user.id)
        assert self.controller.usersRepository.delete.called_once_with(user.id)

    def test_get_connections(self) -> None:
        pass

    def test_add_connection(self) -> None:
        pass

    def test_remove_connection(self) -> None:
        pass

    def test_get_recommendations(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()