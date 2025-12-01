from __future__ import annotations
from typing import List
from enum import Enum

class Points:

    def __init__(self, value: int):
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    @staticmethod
    def sum(points_list: List["Points"]) -> "Points":
        return Points(sum(x.value for x in points_list))

    @staticmethod
    def sum_nonnegative(points_list: List["Points"]) -> "Points":
        total = Points.sum(points_list)
        return total if total.value >= 0 else Points(0)

    def __str__(self) -> str:
        return str(self._value)


class Resource(Enum):
    GREEN = 1
    RED = 2
    YELLOW = 3
    BULB = 4
    GEAR = 5
    CAR = 6
    MONEY = 7
    POLLUTION = 8


class Deck(Enum):
    I = 1
    II = 2


class CardSource:

    def __init__(self, deck: Deck, index: int):
        assert index >= 0, "Index CardSource init less 0"
        self._deck = deck
        self._index = index

    @property
    def deck(self) -> Deck:
        return self._deck

    @deck.setter
    def deck(self, value: Deck) -> None:
        self._deck = value

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int) -> None:
        assert value >= 0, "Index CardSource less 0 setter"
        self._index = value


class GameState(Enum):
    TAKE_CARD_NO_CARD_DISCARDED = 1
    TAKE_CARD_CARD_DISCARDED = 2
    ACTIVATE_CARD = 3
    SELECT_REWARD = 4
    SELECT_ACTIVATION_PATTERN = 5
    SELECT_SCORING_METHOD = 6
    FINISH = 7


class GridPosition:

    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def __str__(self) -> str:
        return f"({self._x},{self._y})"

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GridPosition):
            return NotImplemented
        return self.x == other.x and self.y == other.y
