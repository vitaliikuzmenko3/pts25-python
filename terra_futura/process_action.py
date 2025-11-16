# pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals, too-many-return-statements, too-many-branches, invalid-name
from typing import List, Tuple, Dict
from .simple_types import Resource, GridPosition
from .interfaces import InterfaceCard, InterfaceGrid

class ProcessAction:
    def __init__(self) -> None:
        pass
    def activateCard(
        self,
        card: InterfaceCard,
        grid: InterfaceGrid,
        inputs: List[Tuple[Resource, GridPosition]],
        outputs: List[Tuple[Resource, GridPosition]],
        pollution: List[GridPosition]
    ) -> bool:
        involved_cards: Dict[GridPosition, InterfaceCard] = {}
        if not self._validate_action(card, grid, inputs, outputs, pollution, involved_cards):
            return False
        self._execute_action(card, inputs, outputs, pollution, involved_cards)
        return True
    def _validate_action(
        self,
        card_to_activate: InterfaceCard,
        grid: InterfaceGrid,
        inputs: List[Tuple[Resource, GridPosition]],
        outputs: List[Tuple[Resource, GridPosition]],
        pollution: List[GridPosition],
        out_involved_cards: Dict[GridPosition, InterfaceCard]
    ) -> bool:
        card_pos = card_to_activate.get_position()
        if not grid.canBeActivated(card_pos):
            return False
        out_involved_cards[card_pos] = card_to_activate
        input_resources = [res for res, _ in inputs]
        output_resources = [res for res, _ in outputs]
        pollution_count = len(pollution)
        is_valid_effect = card_to_activate.checkInput(
            input_resources, output_resources, pollution_count
        ) or card_to_activate.checkLower(
            input_resources, output_resources, pollution_count
        )
        if not is_valid_effect:
            return False
        for _, pos in outputs:
            if pos.x != card_pos.x or pos.y != card_pos.y:
                return False
        inputs_by_card: Dict[GridPosition, List[Resource]] = {}
        for res, pos in inputs:
            if pos not in inputs_by_card:
                inputs_by_card[pos] = []
            inputs_by_card[pos].append(res)
        for pos, resources_needed in inputs_by_card.items():
            input_card = grid.getCard(pos)
            if input_card is None:
                return False
            if not grid.canBeActivated(pos):
                return False
            if not input_card.canGetResources(resources_needed):
                return False
            out_involved_cards[pos] = input_card
        for pos in pollution:
            pollution_card = grid.getCard(pos)
            if pollution_card is None:
                return False
            if not grid.canBeActivated(pos):
                return False
            out_involved_cards[pos] = pollution_card
        return True
    def _execute_action(
        self,
        card_to_activate: InterfaceCard,
        inputs: List[Tuple[Resource, GridPosition]],
        outputs: List[Tuple[Resource, GridPosition]],
        pollution: List[GridPosition],
        involved_cards: Dict[GridPosition, InterfaceCard]
    ) -> None:
        inputs_by_card: Dict[GridPosition, List[Resource]] = {}
        for res, pos in inputs:
            if pos not in inputs_by_card:
                inputs_by_card[pos] = []
            inputs_by_card[pos].append(res)
        for pos, resources_to_spend in inputs_by_card.items():
            involved_cards[pos].getResources(resources_to_spend)
        output_resources = [res for res, _ in outputs]
        if output_resources:
            card_to_activate.putResources(output_resources)
        for pos in pollution:
            involved_cards[pos].add_pollution()
