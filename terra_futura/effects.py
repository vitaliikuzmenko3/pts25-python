# pylint: disable=invalid-name, too-few-public-methods, disable=unused-argument
import json
from collections import Counter
from typing import List, Set
from terra_futura.simple_types import Resource
from terra_futura.interfaces import InterfaceEffect

RAW_RESOURCES: Set[Resource] = {
    Resource.GREEN,
    Resource.RED,
    Resource.YELLOW,
}

class EffectTransformationFixed(InterfaceEffect):
    def __init__(self, input_res: List[Resource], output_res: List[Resource], pollution: int):
        self._inputs = Counter(input_res)
        self._outputs = Counter(output_res)
        self._pollution = pollution
        self._input_list = [str(r) for r in input_res]
        self._output_list = [str(r) for r in output_res]

    def check(self, inputs: List[Resource], output: List[Resource], pollution: int) -> bool:
        return (Counter(inputs) == self._inputs and
                Counter(output) == self._outputs and
                pollution == self._pollution)

    def has_assistance(self) -> bool:
        return False

    def state(self) -> str:
        return json.dumps({
            "type": "fixed",
            "inputs": self._input_list,
            "outputs": self._output_list,
            "pollution": self._pollution
        })


class EffectArbitraryBasic(InterfaceEffect):
    def __init__(self, from_count: int, output_res: List[Resource], pollution: int):
        self._from_count = from_count
        self._outputs = Counter(output_res)
        self._pollution = pollution
        self._output_list = [str(r) for r in output_res]

    def check(self, inputs: List[Resource], output: List[Resource], pollution: int) -> bool:
        if len(inputs) != self._from_count:
            return False
        for res in inputs:
            if res not in RAW_RESOURCES:
                return False
        return (Counter(output) == self._outputs and
                pollution == self._pollution)

    def has_assistance(self) -> bool:
        return False

    def state(self) -> str:
        return json.dumps({
            "type": "arbitrary",
            "count_needed": self._from_count,
            "outputs": self._output_list,
            "pollution": self._pollution
        })

class EffectOr(InterfaceEffect):
    def __init__(self, effects: List[InterfaceEffect]):
        self._effects = effects

    def check(self, inputs: List[Resource], output: List[Resource], pollution: int) -> bool:
        for effect in self._effects:
            if effect.check(inputs, output, pollution):
                return True
        return False

    def has_assistance(self) -> bool:
        for effect in self._effects:
            if effect.has_assistance():
                return True
        return False

    def state(self) -> str:
        children_states = [json.loads(e.state()) for e in self._effects]
        return json.dumps({
            "type": "or",
            "options": children_states
        })

class EffectAssistance(InterfaceEffect):
    def __init__(self) -> None:
        pass

    def check(self, inputs: List[Resource], output: List[Resource], pollution: int) -> bool:
        return False

    def has_assistance(self) -> bool:
        return True

    def state(self) -> str:
        return json.dumps({"type": "assistance"})

class EffectPollutionTransfer(InterfaceEffect):
    def __init__(self) -> None:
        pass

    def check(self, inputs: List[Resource], output: List[Resource], pollution: int) -> bool:
        return len(inputs) == 0 and len(output) == 0

    def has_assistance(self) -> bool:
        return False

    def state(self) -> str:
        return json.dumps({"type": "pollution_transfer"})
