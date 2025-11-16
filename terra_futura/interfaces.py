# pylint: disable=unused-argument, duplicate-code
from typing import List, Tuple, Protocol, Optional
from .simple_types import GridPosition, Resource

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

class InterfaceCard(Protocol):
    
    def get_position(self) -> GridPosition:
        ...

    def canGetResources(self, resources: List[Resource]) -> bool:
        ...
        
    def getResources(self, resources: List[Resource]) -> None:
        ...

    def canPutResources(self, resources: List[Resource]) -> bool:
        ...

    def putResources(self, resources: List[Resource]) -> None:
        ...

    def checkInput(
        self, 
        inputs: List[Resource], 
        output: List[Resource], 
        polution: int
    ) -> bool:
        ...

    def checkLower(
        self, 
        inputs: List[Resource], 
        output: List[Resource], 
        polution: int
    ) -> bool:
        ...

    def add_pollution(self) -> None:
        ...
class InterfaceGrid(Protocol):
    def getCard(self, coordinate: GridPosition) -> Optional[InterfaceCard]:
        ...
    def canBeActivated(self, coordinate: GridPosition) -> bool:
        ...