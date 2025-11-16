from .interfaces import InterfaceGrid, InterfacePile
from .simple_types import GridPosition

class MoveCard:
    def execute(
        self, pile: InterfacePile, grid: InterfaceGrid, card_index: int, destination: GridPosition
    ) -> bool:
        if not grid.can_put_card(destination):
            return False

        card_to_move = pile.take_card(card_index)
        if card_to_move is None:
            return False

        grid.put_card(destination, card_to_move)

        return True
