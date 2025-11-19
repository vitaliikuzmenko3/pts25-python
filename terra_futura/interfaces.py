# pylint: disable=unused-argument,too-few-public-methods,too-many-arguments,too-many-positional-arguments
"""Interfaces for Terra Futura game entities and actions."""
from __future__ import annotations
from typing import List, Optional, Tuple
from terra_futura.simple_types import GridPosition, Resource


class InterfaceActivateGrid:
    """Interface for activating a grid pattern."""

    def set_activation_pattern(self, pattern: List[Tuple[int, int]]) -> None:
        """Set the activation pattern for the grid."""
        assert False


class TerraFuturaObserverInterface:
    """Observer interface to notify game state changes."""

    def notify(self, game_state: str) -> None:
        """Notify observer of the current game state."""
        assert False


class ICard:
    """Interface for a game card."""

    def can_get_resources(self, resources: List[Resource]) -> bool:
        """Check if the card can give the specified resources."""
        assert False

    def get_resources(self, resources: List[Resource]) -> None:
        """Obtain the specified resources from the card."""
        assert False

    def can_put_resources(self, resources: List[Resource]) -> bool:
        """Check if the specified resources can be placed on the card."""
        assert False

    def put_resources(self, resources: List[Resource]) -> None:
        """Place the specified resources on the card."""
        assert False

    def check(
        self,
        inputs: List[Resource],
        outputs: List[Resource],
        pollution: int
    ) -> bool:
        """Check if the card operation is valid."""
        assert False

    def check_lower(
        self,
        inputs: List[Resource],
        outputs: List[Resource],
        pollution: int
    ) -> bool:
        """Check a lower-level card operation."""
        assert False

    def has_assistance(self) -> bool:
        """Return True if the card has assistance applied."""
        assert False

    def state(self) -> str:
        """Return the card state as a JSON-serializable string."""
        assert False


class InterfaceSelectReward:
    """Interface for selecting and setting rewards."""

    def set_reward(
        self,
        player: int,
        card: ICard,
        reward: List[Resource],
        mode: str
    ) -> None:
        """Set a reward for a player and card."""
        assert False

    def can_select_reward(self, resource: Resource) -> bool:
        """Check if the reward can be re-selected."""
        assert False

    def select_reward(self, resource: Resource) -> None:
        """Select a reward."""
        assert False

    def state(self) -> str:
        """Return the state of reward selection."""
        assert False


class InterfaceProcessActionAssistance:
    """Interface for processing assistance actions on cards."""

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
        """Activate a card with assistance applied."""
        assert False


class IGrid:
    """Interface for the game grid."""

    def get_card(self, coordinate: GridPosition) -> Optional[ICard]:
        """Get a card at the given coordinate."""
        assert False

    def can_put_card(self, coordinate: GridPosition) -> bool:
        """Check if a card can be placed at the coordinate."""
        assert False

    def put_card(self, coordinate: GridPosition, card: ICard) -> None:
        """Place a card at the given coordinate."""
        assert False

    def can_be_activated(self, coordinate: GridPosition) -> bool:
        """Check if a card at the coordinate can be activated."""
        assert False

    def set_activated(self, coordinate: GridPosition) -> None:
        """Mark the card at the coordinate as activated."""
        assert False

    def set_activation_pattern(
        self,
        pattern: List[GridPosition]
    ) -> None:
        """Set an activation pattern on the grid."""
        assert False

    def end_turn(self) -> None:
        """End the current turn."""
        assert False

    def state(self) -> str:
        """Return the grid state as a JSON-serializable string."""
        assert False


class IPile:
    """Interface for a pile of cards."""

    def get_card(self, index: int) -> Optional[ICard]:
        """Get a card at the specified index."""
        assert False

    def take_card(self, index: int) -> Optional[ICard]:
        """Take a card from the specified index."""
        assert False

    def remove_last_card(self) -> Optional[ICard]:
        """Remove the last visible card and move it to the discard pile."""
        assert False

    def state(self) -> str:
        """Return the pile state as a JSON-serializable string."""
        assert False
