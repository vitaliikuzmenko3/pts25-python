from terra_futura.interfaces import InterfacePile, InterfaceGrid
from terra_futura.simple_types import GridPosition

class MoveCard:
    def move_card(self, pile: InterfacePile, index: int,
                  grid_coordinate: GridPosition, grid: InterfaceGrid) -> bool:
        if not grid.can_put_card(grid_coordinate):
            return False

        if pile.get_card(index) is None:
            return False

        taken_card = pile.take_card(index)

        if taken_card is None:
            return False

        grid.put_card(grid_coordinate, taken_card)

        return True
