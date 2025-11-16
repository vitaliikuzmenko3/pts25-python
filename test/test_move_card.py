import unittest
from typing import Optional

from terra_futura.move_card import MoveCard
from terra_futura.interfaces import InterfaceGrid, InterfacePile, Card
from terra_futura.simple_types import GridPosition

class FakePile(InterfacePile):
    def __init__(self, card_to_return: Optional[Card]):
        self._card_to_return = card_to_return
        self.take_card_called_with_index = -1

    def take_card(self, index: int) -> Optional[Card]:
        self.take_card_called_with_index = index
        return self._card_to_return

class FakeGrid(InterfaceGrid):
    def __init__(self, can_put: bool):
        self._can_put = can_put
        self.put_card_called = False

    def can_put_card(self, coordinate: GridPosition) -> bool:
        return self._can_put

    def put_card(self, coordinate: GridPosition, card: Card) -> None:
        self.put_card_called = True

class TestMoveCard(unittest.TestCase):

    def setUp(self) -> None:
        self.move_card_action = MoveCard()
        self.sample_card = Card()
        self.destination = GridPosition(0, 1)

    def test_move_card_successful(self):
        fake_pile = FakePile(card_to_return=self.sample_card)
        fake_grid = FakeGrid(can_put=True)
        card_index_to_take = 1

        result = self.move_card_action.execute(fake_pile, fake_grid, card_index_to_take, self.destination)

        self.assertTrue(result)
        self.assertEqual(fake_pile.take_card_called_with_index, card_index_to_take)
        self.assertTrue(fake_grid.put_card_called)

    def test_move_card_fails_if_grid_cannot_put(self):
        fake_pile = FakePile(card_to_return=self.sample_card)
        fake_grid = FakeGrid(can_put=False)

        result = self.move_card_action.execute(fake_pile, fake_grid, 1, self.destination)

        self.assertFalse(result)
        self.assertFalse(fake_grid.put_card_called)

    def test_move_card_fails_if_pile_has_no_card(self):
        fake_pile = FakePile(card_to_return=None)
        fake_grid = FakeGrid(can_put=True)

        result = self.move_card_action.execute(fake_pile, fake_grid, 1, self.destination)

        self.assertFalse(result)
        self.assertFalse(fake_grid.put_card_called)