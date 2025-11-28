# pylint: disable=unused-argument, duplicate-code
from typing import List, Tuple, Protocol
from .simple_types import Resource

class InterfaceActivateGrid:
    def set_activation_pattern(self, pattern: List[Tuple[int, int]]) -> None:
        assert False
class InterfaceEffect(Protocol):
    def check(
        self,
        inputs: List[Resource],
        output: List[Resource],
        pollution: int
    ) -> bool:
        ...
    def hasAssistance(self) -> bool:
        ...
    def state(self) -> str:
        ...