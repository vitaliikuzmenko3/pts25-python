# pylint: disable=invalid-name, too-many-arguments, too-many-positional-arguments
from __future__ import annotations
from typing import Dict
from .interfaces import ObserverInterface


class GameObserver(ObserverInterface):
    def __init__(self) -> None:
        self.observers: Dict[int, ObserverInterface] = {}

    def register(self, player_id: int, observer: ObserverInterface) -> None:
        self.observers[player_id] = observer

    def notifyAll(self, new_state: Dict[int, str]) -> None:
        for player_id, state_string in new_state.items():
            if player_id in self.observers:
                self.observers[player_id].notify(state_string)
