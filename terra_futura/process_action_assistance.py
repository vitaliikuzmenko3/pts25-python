from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Any
from terra_futura.interfaces import (
    InterfaceProcessActionAssistance,
    InterfaceSelectReward,
    IGrid,
    ICard
)
from terra_futura.simple_types import GridPosition, Resource


class ProcessActionAssistance(InterfaceProcessActionAssistance):

    _select_reward_manager: InterfaceSelectReward
    _current_card: Optional[ICard]

    def __init__(self, select_reward_manager: InterfaceSelectReward):
        self._select_reward_manager = select_reward_manager
        self._current_card = None

    def _validate_and_setup(
        self,
        card: ICard,
        grid: IGrid,
        assisting_card: Optional[ICard],
        paid_resources: List[Resource],
        gained_resources: List[Resource],
        pollution_count: int
    ) -> Tuple[bool, Optional[GridPosition]]:

        card_coordinate: Optional[GridPosition] = None

        for row in range(-2, 3):
            for col in range(-2, 3):
                position = GridPosition(row, col)
                card_at_position = grid.get_card(position)
                if card_at_position is card:
                    card_coordinate = position
                    break
            if card_coordinate is not None:
                break

        if card_coordinate is None or not card.has_assistance():
            return False, None

        if not grid.can_be_activated(card_coordinate):
            return False, None

        if assisting_card is None or not assisting_card.check_lower(
            paid_resources,
            gained_resources,
            pollution_count
        ):
            return False, None

        return True, card_coordinate

    def _validate_inputs(
        self,
        grid: IGrid,
        inputs: List[Tuple[Resource, GridPosition]]
    ) -> Optional[Dict[str, Any]]:

        involved_cards: Dict[GridPosition, ICard] = {}
        inputs_by_card: Dict[GridPosition, List[Resource]] = {}

        for res, pos in inputs:
            inputs_by_card.setdefault(pos, []).append(res)

        for pos, resources_needed in inputs_by_card.items():
            input_card = grid.get_card(pos)
            if (input_card is None or
                    not input_card.can_get_resources(resources_needed)):
                return None
            involved_cards[pos] = input_card

        return {
            'involved_cards': involved_cards,
            'inputs_by_card': inputs_by_card
        }

    def _handle_pollution_transfer_reward(
        self,
        assisting_player: int,
        assisting_card: ICard,
        grid: IGrid,
        pollution: List[GridPosition],
        involved_cards: Dict[GridPosition, ICard]
    ) -> bool:

        if len(pollution) != 1:
            return False

        for pos in pollution:
            involved_cards[pos].get_resources([Resource.POLUTION])

        start_card = grid.get_card(GridPosition(0, 0))
        if start_card is None:
            return False

        start_card.put_resources([Resource.POLUTION])

        self._select_reward_manager.set_reward(
            player_id=assisting_player,
            card=assisting_card,
            reward=[Resource.POLUTION],
            mode="pollution"
        )
        return True

    def _handle_standard_assistance_reward(
        self,
        assisting_player: int,
        assisting_card: ICard,
        pollution: List[GridPosition],
        involved_cards: Dict[GridPosition, ICard],
        paid_resources: List[Resource]
    ) -> bool:

        if len(pollution) > 0:
            for pos in pollution:
                pollution_card = involved_cards.get(pos)
                if pollution_card is None:
                    return False
                pollution_card.put_resources([Resource.POLUTION])

        self._select_reward_manager.set_reward(
            player_id=assisting_player,
            card=assisting_card,
            reward=paid_resources,
            mode="assistance"
        )
        return True

    def activate_card(
        self,
        card: ICard,
        grid: IGrid,
        assisting_player: int,
        assisting_card: ICard,
        inputs: List[Tuple[Resource, GridPosition]],
        outputs: List[Tuple[Resource, GridPosition]],
        pollution: List[GridPosition]
    ) -> bool:

        is_assistance = assisting_card is not None and assisting_player != 0
        if not is_assistance:
            self._current_card = None
            return False

        self._current_card = card

        paid_resources = [r for r, _ in inputs]
        gained_resources = [r for r, _ in outputs]
        pollution_count = len(pollution)

        success, card_coordinate = self._validate_and_setup(
            card, grid, assisting_card, paid_resources,
            gained_resources, pollution_count
        )
        if not success:
            self._current_card = None
            return False

        input_validation_data = self._validate_inputs(grid, inputs)
        if input_validation_data is None:
            self._current_card = None
            return False

        involved_cards = input_validation_data['involved_cards']
        inputs_by_card = input_validation_data['inputs_by_card']

        for pos in pollution:
            pollution_card = grid.get_card(pos)
            if pollution_card is None:
                self._current_card = None
                return False
            involved_cards[pos] = pollution_card

        for pos, resources_to_spend in inputs_by_card.items():
            involved_cards[pos].get_resources(resources_to_spend)

        card.put_resources(gained_resources)

        is_pollution_transfer = (pollution_count > 0 and not paid_resources)

        if is_pollution_transfer:
            success = self._handle_pollution_transfer_reward(
                assisting_player, assisting_card, grid, pollution,
                involved_cards
            )
        else:
            success = self._handle_standard_assistance_reward(
                assisting_player, assisting_card, pollution, involved_cards,
                paid_resources
            )

        self._current_card = None
        return success

