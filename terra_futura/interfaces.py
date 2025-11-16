# pylint: disable=unused-argument, duplicate-code
from typing import List, Tuple, Optional
from .simple_types import GridPosition

class Card:
        pass

class InterfaceActivateGrid:
    def set_activation_pattern(self, pattern: List[Tuple[int, int]]) -> None:
        assert False

class InterfacePile:
        def take_card(self, index: int) -> Optional[Card]:
            assert False

class InterfaceGrid:
        def can_put_card(self, coordinate: GridPosition) -> bool:
            assert False

        def put_card(self, coordinate: GridPosition, card: Card) -> None:
            assert False