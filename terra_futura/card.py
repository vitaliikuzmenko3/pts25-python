# pylint: disable=invalid-name, too-many-arguments, too-many-positional-arguments
from __future__ import annotations
import json
from typing import List, Optional
from terra_futura.interfaces import InterfaceCard, InterfaceEffect
from terra_futura.simple_types import Resource


class Card(InterfaceCard):
    def __init__(
        self,
        resources: List[Resource],
        pollutionSpacesL: int,
        assistance: bool = False,
        upperEffect: Optional[InterfaceEffect] = None,
        lowerEffect: Optional[InterfaceEffect] = None,
    ):
        self.resources = resources.copy()
        self.pollution_limit = pollutionSpacesL
        self.assistance = assistance
        self.upper_effect = upperEffect
        self.lower_effect = lowerEffect

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
            raise ValueError("Not enough resources")
        for r in resources:
            self.resources.remove(r)

    def can_put_resources(self, resources: List[Resource]) -> bool:
        pol_new = sum(r == Resource.POLLUTION for r in resources)
        pol_old = sum(r == Resource.POLLUTION for r in self.resources)
        return pol_new + pol_old <= self.pollution_limit

    def put_resources(self, resources: List[Resource]) -> None:
        if not self.can_put_resources(resources):
            raise ValueError("Too much pollution")
        self.resources.extend(resources)

    def check(self,
    inputs: List[Resource],
    output: List[Resource],
    pollution: int) -> bool:
        return (
            self.upper_effect is not None and
            self.upper_effect.check(inputs, output, pollution)
        )

    def check_lower(self,
    inputs: List[Resource],
    output: List[Resource],
    pollution: int) -> bool:
        return (
            self.lower_effect is not None and
            self.lower_effect.check(inputs, output, pollution)
        )

    def has_assistance(self) -> bool:
        return self.assistance

    def state(self) -> str:
        return json.dumps({
            "resources": [r.value for r in self.resources],
            "pollution": sum(r == Resource.POLLUTION for r in self.resources),
            "pollution_limit": self.pollution_limit,
            "assistance": self.assistance,
            "upper_effect": json.loads(self.upper_effect.state())
            if self.upper_effect else None,
            "lower_effect": json.loads(self.lower_effect.state())
            if self.lower_effect else None,
        })
