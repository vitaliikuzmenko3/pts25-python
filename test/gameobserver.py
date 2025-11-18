import unittest
from terra_futura.gameobserver import GameObserver
from terra_futura.interfaces import ObserverInterface


class FakeObserver(ObserverInterface):
    def __init__(self):
        self.last_notification = None

    def notify(self, game_state: str) -> None:
        self.last_notification = game_state


class TestGameObserver(unittest.TestCase):

    def test_notify_single_player(self) -> None:
        observer = GameObserver()
        fake = FakeObserver()

        observer.register(1, fake)
        observer.notifyAll({1: "state_for_player_1"})

        self.assertEqual(fake.last_notification, "state_for_player_1")

    def test_notify_multiple_players(self)-> None:
        observer = GameObserver()
        p1 = FakeObserver()
        p2 = FakeObserver()
        observer.register(1, p1)
        observer.register(2, p2)
        observer.notifyAll({
            1: "state1",
            2: "state2"
        })
        self.assertEqual(p1.last_notification, "state1")
        self.assertEqual(p2.last_notification, "state2")

    def test_does_not_crash_if_player_missing(self)-> None:
        observer = GameObserver()
        p1 = FakeObserver()
        observer.register(1, p1)
        observer.notifyAll({
            1: "s1",
            2: "s2"
        })
        self.assertEqual(p1.last_notification, "s1")
