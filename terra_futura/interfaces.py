from __future__ import annotations
from typing import List, Optional, Tuple
from terra_futura.simple_types import GridPosition, Resource

class InterfaceActivateGrid:
    def set_activation_pattern(self, pattern: List[Tuple[int, int]]) -> None:
        assert False
        
class TerraFuturaObserverInterface:
    def notify(self, gameState: str) -> None:
        assert False
        
class ICard:
    def can_get_resources(self, resources: List[Resource]) -> bool:
        assert False

    def get_resources(self, resources: List[Resource]) -> None:
        assert False

    def can_put_resources(self, resources: List[Resource]) -> bool:
        assert False

    def put_resources(self, resources: List[Resource]) -> None:
        assert False

    def check(
        self,
        input: List[Resource],
        output: List[Resource],
        pollution: int
    ) -> bool:
        assert False

    def check_lower(
        self,
        input: List[Resource],
        output: List[Resource],
        pollution: int
    ) -> bool:
        assert False

    def has_assistance(self) -> bool:
        assert False

    def state(self) -> str:
        assert False


class InterfaceSelectReward:
    def set_reward(
        self,
        player: int,
        card: ICard,
        reward: List[Resource]
    ):
        assert False

    def can_relect_reward(self, resource: Resource) -> bool:
        assert False

    def select_reward(self, resource: Resource):
        assert False

    def state(self) -> str:
        assert False


class InterfaceProcessActionAssistance:
    def activate_card(
        self,
        card: ICard,
        grid: IGrid,
        inputs: List[Tuple[Resource, GridPosition]],
        outputs: List[Tuple[Resource, GridPosition]],
        pollution: List[GridPosition],
        otherPlayerId: Optional[int],
        otherCard: Optional[ICard]
    ) -> bool:
        assert False


class IGrid:
    def get_card(self, coordinate: GridPosition) -> Optional[ICard]:
        assert False

    def can_put_card(self, coordinate: GridPosition) -> bool:
        assert False

    def put_card(self, coordinate: GridPosition, card: ICard) -> None:
        assert False

    def can_be_activated(self, coordinate: GridPosition) -> bool:
        assert False

    def set_activated(self, coordinate: GridPosition) -> None:
        assert False

    def set_activation_pattern(
        self,
        pattern: List[GridPosition]
    ) -> None:
        assert False

    def end_turn(self) -> None:
        assert False

    def state(self) -> str:
        assert False


class IPile:
    def get_card(self, index: int) -> Optional[ICard]:
        assert False

    def take_card(self, index: int) -> Optional[ICard]:
        assert False

    def remove_last_card(self) -> Optional[ICard]:
        assert False

    def state(self) -> str:
        assert False
