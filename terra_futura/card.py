# pylint: disable=invalid-name, too-many-arguments, too-many-positional-arguments
from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict
from terra_futura.interfaces import InterfaceCard
import json


class Resource(Enum):
    GREEN = "Green"
    RED = "Red"
    YELLOW = "Yellow"
    BULB = "Bulb"
    GEAR = "Gear"
    CAR = "Car"
    MONEY = "Money"
    POLLUTION = "Pollution"


class CardEffects:
    def __init__(
        self,
        add_resources: Optional[List[Resource]] = None,
        transform_resources_into: Optional[Dict[Resource, Resource]] = None,
        pollution: int = 0,
    ):
        self.add_resources = add_resources if add_resources else []
        self.transform_resources_into = transform_resources_into if transform_resources_into else {}
        self.pollution = pollution

    def describe(self) -> str:
        add = [r.value for r in self.add_resources]
        transform = [f"{o.value}->{n.value}" for o, n in self.transform_resources_into.items()]
        return f"Add {add}, Transform {transform}, Pollution {self.pollution}"


class Card(InterfaceCard):
    def __init__(
        self,
        resources: List[Resource],
        pollutionSpacesL: int,
        assistance: bool = False,
        upperEffect: Optional[CardEffects] = None,
        lowerEffect: Optional[CardEffects] = None,
    ):
        self.resources = resources.copy()
        self.pollution_limit = pollutionSpacesL
        self.assistance = assistance
        self.upper_effect = upperEffect if upperEffect else CardEffects()
        self.lower_effect = lowerEffect if lowerEffect else CardEffects()

    def can_get_resources(self, resources: List[Resource]) -> bool:
        temp = self.resources.copy()
        for r in resources:
            if r in temp:
                temp.remove(r)
            else:
                return False
        return True

    def get_resources(self, resources: List[Resource]) -> None:
        if not self.can_get_resources(resources):
            raise ValueError("Resources not available")
        for r in resources:
            self.resources.remove(r)

    def can_put_resources(self, resources: List[Resource]) -> bool:
        p_new = sum(1 for r in resources if r == Resource.POLLUTION)
        p_old = sum(1 for r in self.resources if r == Resource.POLLUTION)
        return p_new + p_old <= self.pollution_limit

    def put_resources(self, resources: List[Resource]) -> None:
        if not self.can_put_resources(resources):
            raise ValueError("Too much pollution")
        self.resources.extend(resources)

    # pylint: disable=redefined-builtin
    def check(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        if not self.can_get_resources(input):
            return False
        return pollution + self.upper_effect.pollution <= self.pollution_limit

    # pylint: disable=redefined-builtin
    def check_lower(self, input: List[Resource], output: List[Resource], pollution: int) -> bool:
        return self.can_get_resources(input)

    def has_assistance(self) -> bool:
        return self.assistance

    def state(self) -> str:
        state = {
            "resources": [r.value for r in self.resources],
            "pollution": sum(r == Resource.POLLUTION for r in self.resources),
            "pollution_limit": self.pollution_limit,
            "assistance": self.assistance,
            "upper_effect": {
                "add": [r.value for r in self.upper_effect.add_resources],
                "transform": {old.value: new.value for old, new in self.upper_effect.transform_resources_into.items()},
                "pollution": self.upper_effect.pollution,
            },
            "lower_effect": {
                "add": [r.value for r in self.lower_effect.add_resources],
                "transform": {old.value: new.value for old, new in self.lower_effect.transform_resources_into.items()},
                "pollution": self.lower_effect.pollution,
            },
        }
        return json.dumps(state)
