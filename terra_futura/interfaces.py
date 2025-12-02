# pylint: disable=unused-argument, duplicate-code, redefined-builtin, too-many-arguments, too-many-positional-arguments
"""Interfaces for Terra Futura game entities and actions."""
from __future__ import annotations
from typing import List, Tuple, Optional, Protocol, TYPE_CHECKING
from terra_futura.simple_types import GridPosition, Resource

if TYPE_CHECKING:
    from terra_futura.card import Card

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


class InterfaceSelectReward:
    """Interface for selecting and setting rewards."""

    def set_reward(
        self,
        player: int,
        card: InterfaceCard,
        reward: List[Resource]
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
        card: InterfaceCard,
        grid: InterfaceGrid,
        assisting_player: int,
        assisting_card: InterfaceCard,
        inputs: List[Tuple[Resource, GridPosition]],
        outputs: List[Tuple[Resource, GridPosition]],
        pollution: List[GridPosition]
    ) -> bool:
        """Activate a card with assistance applied."""
        assert False

class RandomProviderInterface:
    """Interface for random operations on the pile."""
    def shuffle(self, _cards: List[InterfaceCard]) -> None:
        """Shuffle the given cards in place."""
        assert False

    def pop_card(self, _cards: List[InterfaceCard]) -> Optional[InterfaceCard]:
        """Pop a card from the given list."""
        assert False


class InterfaceCard:
    # pylint: disable=redefined-builtin

    resources: List["Resource"]
    upper_effect: Optional["InterfaceEffect"]
    lower_effect: Optional["InterfaceEffect"]
    pollution_limit: int

    def can_get_resources(self, resources: List["Resource"]) -> bool:
        raise NotImplementedError

    def get_resources(self, resources: List["Resource"]) -> None:
        raise NotImplementedError

    def can_put_resources(self, resources: List["Resource"]) -> bool:
        raise NotImplementedError

    def put_resources(self, resources: List["Resource"]) -> None:
        raise NotImplementedError

    def check(
            self,
            inputs: List["Resource"],
            output: List["Resource"],
            pollution: int
    ) -> bool:
        raise NotImplementedError

    def check_lower(
            self,
            inputs: List["Resource"],
            output: List["Resource"],
            pollution: int
    ) -> bool:
        raise NotImplementedError

    def has_assistance(self) -> bool:
        raise NotImplementedError

    def state(self) -> str:
        raise NotImplementedError

    def is_active(self) -> bool:
        raise NotImplementedError

    def get_position(self) -> GridPosition:
        raise NotImplementedError


class ObserverInterface:
    def notify(self, game_state: str) -> None:
        assert False

class InterfaceEffect(Protocol):
    def check(
        self,
        inputs: List["Resource"],
        output: List["Resource"],
        pollution: int,
    ) -> bool:
        raise NotImplementedError

    def has_assistance(self) -> bool:
        raise NotImplementedError

    def state(self) -> str:
        raise NotImplementedError

class InterfaceGrid:
    """Interface for the game grid."""

    def get_card(self, coordinate: GridPosition) -> Optional[InterfaceCard]:
        """Get a card at the given coordinate."""
        assert False

    def can_put_card(self, coordinate: GridPosition) -> bool:
        """Check if a card can be placed at the coordinate."""
        assert False

    def put_card(self, coordinate: GridPosition, card: InterfaceCard) -> None:
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

class InterfacePile:
    """Interface for a pile of cards."""

    def get_card(self, index: int) -> Optional[InterfaceCard]:
        """Get a card at the specified index."""
        assert False

    def take_card(self, index: int) -> Optional[InterfaceCard]:
        """Take a card from the specified index."""
        assert False

    def remove_last_card(self) -> Optional[InterfaceCard]:
        """Remove the last visible card and move it to the discard pile."""
        assert False

    def state(self) -> str:
        """Return the pile state as a JSON-serializable string."""
        assert False
