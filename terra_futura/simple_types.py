from enum import Enum, auto

class GridPosition:
    _x: int
    _y: int

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
        return "("+str(self._x)+","+str(self._y)+")"
class Resource(Enum):
    GREEN = auto()
    RED = auto()
    YELLOW = auto()
    BULB = auto()
    GEAR = auto()
    CAR = auto()
    MONEY = auto()
    POLUTION = auto()

    def __str__(self) -> str:
        return self.name
