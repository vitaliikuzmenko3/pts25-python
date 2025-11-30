import unittest
from typing import Optional, Dict

from terra_futura.move_card import MoveCard
from terra_futura.simple_types import GridPosition
from terra_futura.interfaces import InterfaceCard, InterfacePile, InterfaceGrid

class MockCard(InterfaceCard):
    def state(self) -> str:
        return "{}"

class MockPile(InterfacePile):
    def __init__(self) -> None:
        self.cards: Dict[int, InterfaceCard] = {}

    def add_card(self, index: int) -> None:
        self.cards[index] = MockCard()

    def get_card(self, index: int) -> Optional[InterfaceCard]:
        return self.cards.get(index)

    def take_card(self, index: int) -> Optional[InterfaceCard]:
        return self.cards.pop(index, None)

class MockGrid(InterfaceGrid):
    def __init__(self) -> None:
        self.occupied: set[tuple[int, int]] = set()

    def can_put_card(self, coordinate: GridPosition) -> bool:
        return (coordinate.x, coordinate.y) not in self.occupied

    def put_card(self, coordinate: GridPosition, card: InterfaceCard) -> None:
        self.occupied.add((coordinate.x, coordinate.y))

class TestMoveCard(unittest.TestCase):
    def setUp(self) -> None:
        self.move_card_action = MoveCard()
        self.pile = MockPile()
        self.grid = MockGrid()
        self.pos = GridPosition(0, 0)

    def test_move_success(self) -> None:
        self.pile.add_card(1)
        
        success = self.move_card_action.move_card(self.pile, 1, self.pos, self.grid)
        
        self.assertTrue(success)
        self.assertIsNone(self.pile.get_card(1))
        self.assertFalse(self.grid.can_put_card(self.pos))

    def test_move_fail_no_card(self) -> None:
        success = self.move_card_action.move_card(self.pile, 1, self.pos, self.grid)
        self.assertFalse(success)

    def test_move_fail_grid_occupied(self) -> None:
        self.pile.add_card(1)
        self.grid.put_card(self.pos, MockCard())
        
        success = self.move_card_action.move_card(self.pile, 1, self.pos, self.grid)
        
        self.assertFalse(success)
        self.assertIsNotNone(self.pile.get_card(1))

if __name__ == "__main__":
    unittest.main()