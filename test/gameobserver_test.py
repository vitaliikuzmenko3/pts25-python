import unittest
from terra_futura.gameobserver import GameObserver
from terra_futura.interfaces import ObserverInterface


class FakeObserver(ObserverInterface):
    def __init__(self) -> None:
        self.received: str | None = None

    def notify(self, game_state: str) -> None:
        self.received = game_state


class TestGameObserver(unittest.TestCase):

    def test_register_and_notify(self) -> None:
        observer = GameObserver()
        fake1 = FakeObserver()
        fake2 = FakeObserver()
        observer.register(1, fake1)
        observer.register(2, fake2)
        state = {1: "state1", 2: "state2"}
        observer.notifyAll(state)
        assert fake1.received == "state1"
        assert fake2.received == "state2"

    def test_notify_only_registered(self) -> None:
        observer = GameObserver()
        fake = FakeObserver()
        observer.register(1, fake)
        state = {1: "hello", 99: "should_not_send"}
        observer.notifyAll(state)
        assert fake.received == "hello"
