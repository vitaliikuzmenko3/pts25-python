from __future__ import annotations
from typing import List, Optional, Tuple, Dict
from terra_futura.interfaces import (
    InterfaceProcessActionAssistance,
    InterfaceSelectReward,
    IGrid
)
from terra_futura.Card import Card 
from terra_futura.simple_types import GridPosition, Resource

class ProcessActionAssistance(InterfaceProcessActionAssistance):
    
    _select_reward_manager: InterfaceSelectReward
    _current_card: Optional[Card]
    
    def __init__(self, select_reward_manager: InterfaceSelectReward):
        self._select_reward_manager = select_reward_manager
        self._current_card = None

    def _finalize_activation(self, success: bool = True) -> bool:
        self._current_card = None
        return success

    def activateCard(
        self,
        card: Card,
        grid: IGrid,
        assisting_player: int,
        assisting_card: Card,
        inputs: List[Tuple[Resource, GridPosition]],
        outputs: List[Tuple[Resource, GridPosition]],
        pollution: List[GridPosition]
    ) -> bool:
        
        is_assistance = assisting_card is not None and assisting_player != 0
        if not is_assistance:
            return self._finalize_activation(False)

        assert assisting_player != card.player_id, "Cannot assist yourself."
        self._current_card = card

        card_coordinate: Optional[GridPosition] = None

        for row in range(-2, 3):
            for col in range(-2, 3):
                position = GridPosition(row, col)
                card_at_position = grid.getCard(position)
                if card_at_position is not None and card_at_position is card:
                    card_coordinate = position
                    break
            if card_coordinate is not None:
                break

        paid_resources = [r for r, _ in inputs]
        gained_resources = [r for r, _ in outputs]
        pollution_count = len(pollution)

        if not card.hasAssistance():
            return self._finalize_activation(False)

        if card_coordinate is None:
            return self._finalize_activation(False)

        if not grid.canBeActivated(card_coordinate):
            return self._finalize_activation(False)

        if assisting_card is None:
            return self._finalize_activation(False)

        if not assisting_card.checkLower(
            paid_resources,
            gained_resources,
            pollution_count
        ):
            return self._finalize_activation(False)

        involved_cards: Dict[GridPosition, Card] = {}
        inputs_by_card: Dict[GridPosition, List[Resource]] = {}

        for res, pos in inputs:
            if pos not in inputs_by_card:
                inputs_by_card[pos] = []
            inputs_by_card[pos].append(res)

        for pos, resources_needed in inputs_by_card.items():
            input_card = grid.getCard(pos)
            if input_card is None:
                return self._finalize_activation(False)
            if not input_card.canGetResources(resources_needed):
                return self._finalize_activation(False)
            involved_cards[pos] = input_card

        for pos in pollution:
            pollution_card = grid.getCard(pos)
            if pollution_card is None:
                return self._finalize_activation(False)
            involved_cards[pos] = pollution_card

        for pos, resources_to_spend in inputs_by_card.items():
            involved_cards[pos].getResources(resources_to_spend)

        card.putResources(gained_resources)

        is_pollution_transfer = (
            pollution_count > 0 and not paid_resources
        )

        if is_pollution_transfer:
            if pollution_count == 1:
                for pos in pollution:
                    involved_cards[pos].getResources([Resource.POLUTION])
            else:
                return self._finalize_activation(False)

            start_card = grid.getCard(GridPosition(0, 0))
            start_card.putResources([Resource.POLUTION])

            self._select_reward_manager.setReward(
                player_id=assisting_player,
                card=assisting_card,
                reward=[Resource.POLUTION],
                mode="pollution"
            )
            return self._finalize_activation(True)

        else:
            if pollution_count > 0:
                for pos in pollution:
                    involved_cards[pos].putResources([Resource.POLUTION])

            self._select_reward_manager.setReward(
                player_id=assisting_player,
                card=assisting_card,
                reward=paid_resources,
                mode="assistance"
            )
            return self._finalize_activation(True)
