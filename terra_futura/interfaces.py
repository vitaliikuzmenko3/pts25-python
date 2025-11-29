# pylint: disable=unused-argument, duplicate-code, redefined-builtin
from typing import Protocol
from typing import List, Tuple, TYPE_CHECKING, Optional
from terra_futura.simple_types import Resource
if TYPE_CHECKING:
    from terra_futura.card import Card


class InterfaceActivateGrid:
    def set_activation_pattern(self, pattern: List[Tuple[int, int]]) -> None:
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
