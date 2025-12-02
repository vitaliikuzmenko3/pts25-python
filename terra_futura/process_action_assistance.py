# pylint: disable=too-many-arguments,too-many-positional-arguments
"""Handles processing card actions and assistance in Terra Futura (Assistance Mode Only)."""
from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Any
from terra_futura.interfaces import (
    InterfaceProcessActionAssistance,
    InterfaceSelectReward,
    InterfaceGrid,
    InterfaceCard
)
from terra_futura.simple_types import GridPosition, Resource

class ProcessActionAssistance(InterfaceProcessActionAssistance):
    """Manages card activation and standard assistance rewards."""

    _select_reward_manager: InterfaceSelectReward
    _current_card: Optional[InterfaceCard]

    def __init__(self, select_reward_manager: InterfaceSelectReward):
        """Initialize with a reward manager."""
        self._select_reward_manager = select_reward_manager
        self._current_card = None

    def current_card(self) -> Optional[InterfaceCard]:
        """Return the current card being processed."""
        return self._current_card

    def _validate_and_setup(
        self,
        card: InterfaceCard,
        grid: InterfaceGrid,
        assisting_card: Optional[InterfaceCard],
        paid_resources: List[Resource],
        gained_resources: List[Resource],
        pollution_count: int
    ) -> Tuple[bool, Optional[GridPosition]]:
        """Check if card activation is valid and find its position."""
        card_coordinate: Optional[GridPosition] = None

        for row in range(-2, 3):
            for col in range(-2, 3):
                pos = GridPosition(row, col)
                if grid.get_card(pos) is card:
                    card_coordinate = pos
                    break
            if card_coordinate is not None:
                break

        if card_coordinate is None or not card.has_assistance():
            return False, None
        if not grid.can_be_activated(card_coordinate):
            return False, None
        if assisting_card is None or not assisting_card.check_lower(
            paid_resources, gained_resources, pollution_count
        ):
            return False, None
        return True, card_coordinate

    def _validate_inputs(
        self,
        grid: InterfaceGrid,
        inputs: List[Tuple[Resource, GridPosition]]
    ) -> Optional[Dict[str, Any]]:
        """Validate that inputs can be used for the activation."""
        involved_cards: Dict[GridPosition, InterfaceCard] = {}
        inputs_by_card: Dict[GridPosition, List[Resource]] = {}

        for res, pos in inputs:
            inputs_by_card.setdefault(pos, []).append(res)

        for pos, resources_needed in inputs_by_card.items():
            card = grid.get_card(pos)
            if card is None or not card.can_get_resources(resources_needed):
                return None
            involved_cards[pos] = card

        return {"involved_cards": involved_cards,
                "inputs_by_card": inputs_by_card}

    def _handle_standard_assistance_reward(
        self,
        player: int,
        card: InterfaceCard,
        pollution: List[GridPosition],
        involved_cards: Dict[GridPosition, InterfaceCard],
        paid_resources: List[Resource]
    ) -> bool:
        """Handle normal assistance reward (reward from paid resources)."""
        for pos in pollution:
            c = involved_cards.get(pos)
            if c:
                c.put_resources([Resource.POLLUTION])
        self._select_reward_manager.set_reward(
            player=player,
            card=card,
            reward=paid_resources
        )
        return True

    def activate_card(
        self,
        card: InterfaceCard,
        grid: InterfaceGrid,
        assisting_player: int,
        assisting_card: InterfaceCard,
        inputs: List[Tuple[Resource, GridPosition]],
        outputs: List[Tuple[Resource, GridPosition]],
        pollution: List[GridPosition]
    ) -> bool:
        """Activate a card and process assistance rewards."""
        if not self._start_activation(card, assisting_card, assisting_player):
            return False
        paid_resources = [r for r, _ in inputs]
        gained_resources = [r for r, _ in outputs]
        pollution_count = len(pollution)
        if not self._validate_card_activation(
            card,
            grid,
            assisting_card,
            paid_resources,
            gained_resources,
            pollution_count
        ):
            self._current_card = None
            return False
        input_data = self._validate_inputs(grid, inputs)
        if input_data is None:
            self._current_card = None
            return False

        involved_cards = input_data["involved_cards"]
        inputs_by_card = input_data["inputs_by_card"]

        if not self._process_pollution_cards(grid,
                                              pollution,
                                              involved_cards):
            self._current_card = None
            return False
        self._distribute_resources(
            inputs_by_card,
            involved_cards,
            gained_resources,
            card
        )
        success = self._handle_standard_assistance_reward(
            assisting_player,
            assisting_card,
            pollution,
            involved_cards,
            paid_resources
        )

        self._current_card = None
        return success
    def _start_activation(
        self,
        card: InterfaceCard,
        assisting_card: Optional[InterfaceCard],
        assisting_player: int
    ) -> bool:
        """Check basic conditions and set current card."""
        if assisting_card is None or assisting_player == 0:
            self._current_card = None
            return False
        self._current_card = card
        return True

    def _validate_card_activation(
        self,
        card: InterfaceCard,
        grid: InterfaceGrid,
        assisting_card: InterfaceCard,
        paid_resources: List[Resource],
        gained_resources: List[Resource],
        pollution_count: int
    ) -> bool:
        """Validate card and assistance eligibility."""
        valid, _ = self._validate_and_setup(
            card,
            grid,
            assisting_card,
            paid_resources,
            gained_resources,
            pollution_count
        )
        return valid

    def _process_pollution_cards(
        self,
        grid: InterfaceGrid,
        pollution: List[GridPosition],
        involved_cards: Dict[GridPosition, InterfaceCard]
    ) -> bool:
        """Add pollution cards to involved_cards and check validity."""
        for pos in pollution:
            c = grid.get_card(pos)
            if c is None:
                return False
            involved_cards[pos] = c
        return True

    def _distribute_resources(
        self,
        inputs_by_card: Dict[GridPosition, List[Resource]],
        involved_cards: Dict[GridPosition, InterfaceCard],
        gained_resources: List[Resource],
        card: InterfaceCard
    ) -> None:
        """Distribute resources to involved cards and the main card."""
        for pos, resources in inputs_by_card.items():
            involved_cards[pos].get_resources(resources)
        card.put_resources(gained_resources)
