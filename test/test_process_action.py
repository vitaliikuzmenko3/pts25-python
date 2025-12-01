# pylint: disable=too-many-instance-attributes, too-many-public-methods, duplicate-code, invalid-name
import unittest
from collections import Counter
from typing import List, Tuple, Dict, Optional

from terra_futura.process_action import ProcessAction
from terra_futura.interfaces import InterfaceCard, InterfaceGrid, InterfaceEffect
from terra_futura.simple_types import Resource, GridPosition

class FakeEffect(InterfaceEffect):
    def __init__(self,
                 valid_inputs: List[Resource],
                 valid_outputs: List[Resource],
                 valid_pollution: int):
        self._inputs = Counter(valid_inputs)
        self._outputs = Counter(valid_outputs)
        self._pollution = valid_pollution

    def check(
        self,
        inputs: List[Resource],
        output: List[Resource],
        pollution: int
    ) -> bool:
        return (Counter(inputs) == self._inputs and
                Counter(output) == self._outputs and
                pollution == self._pollution)

    def has_assistance(self) -> bool:
        return False

    def state(self) -> str:
        return "{}"

class FakeCard(InterfaceCard):
    def __init__(self,
                 pos: GridPosition,
                 upper_effect: Optional[InterfaceEffect],
                 lower_effect: Optional[InterfaceEffect],
                 initial_resources: List[Resource]):
        self._pos = pos
        self._upper_effect = upper_effect
        self._lower_effect = lower_effect
        self._resources = Counter(initial_resources)
        self._is_active = True
        self._current_pollution = 0

    def get_position(self) -> GridPosition:
        return self._pos

    def is_active(self) -> bool:
        return self._is_active

    def set_active(self, status: bool) -> None:
        self._is_active = status

    def can_get_resources(self, resources: List[Resource]) -> bool:
        needed = Counter(resources)
        for res, count in needed.items():
            if self._resources[res] < count:
                return False
        return True

    def get_resources(self, resources: List[Resource]) -> None:
        for res in resources:
            if self._resources[res] <= 0:
                raise ValueError("Attempt to delete non-existent resource")
            self._resources[res] -= 1

    def can_put_resources(self, resources: List[Resource]) -> bool:
        return True

    def put_resources(self, resources: List[Resource]) -> None:
        for r in resources:
            if r == Resource.POLLUTION:
                self._current_pollution += 1
            else:
                self._resources[r] += 1

    def check(self, inputs: List[Resource], output: List[Resource], pollution: int) -> bool:
        if self._upper_effect is None:
            return False
        return self._upper_effect.check(inputs, output, pollution)

    def check_lower(self, inputs: List[Resource], output: List[Resource], pollution: int) -> bool:
        if self._lower_effect is None:
            return False
        return self._lower_effect.check(inputs, output, pollution)

    def has_assistance(self) -> bool:
        return False

    def state(self) -> str:
        return "{}"

    def get_resource_count(self, resource: Resource) -> int:
        return self._resources[resource]

    def get_pollution_count(self) -> int:
        return self._current_pollution

class FakeGrid(InterfaceGrid):
    def __init__(self) -> None:
        self._cards: Dict[Tuple[int, int], FakeCard] = {}

    def get_card(self, coordinate: GridPosition) -> Optional[InterfaceCard]:
        return self._cards.get((coordinate.x, coordinate.y))

    def can_be_activated(self, coordinate: GridPosition) -> bool:
        card = self.get_card(coordinate)
        return card is not None and card.is_active()

    def add_card(self, card: FakeCard) -> None:
        self._cards[(card.get_position().x, card.get_position().y)] = card

class TestProcessAction(unittest.TestCase):

    def setUp(self) -> None:
        self.process_action = ProcessAction()
        self.grid = FakeGrid()

        self.pos_a = GridPosition(0, 0)
        self.card_a_resources = [Resource.RED, Resource.RED, Resource.GREEN]
        self.card_a = FakeCard(self.pos_a, None, None, self.card_a_resources)

        self.pos_b = GridPosition(0, 1)

        self.effect_b_inputs = [Resource.RED, Resource.RED]
        self.effect_b_outputs = [Resource.CAR]
        self.effect_b_pollution = 1

        self.effect_b_lower = FakeEffect(
            self.effect_b_inputs, self.effect_b_outputs, self.effect_b_pollution
        )

        self.player_inputs = [
            (Resource.RED, self.pos_a),
            (Resource.RED, self.pos_a)
        ]
        self.player_outputs = [(Resource.CAR, self.pos_b)]
        self.player_pollution = [self.pos_a]

        self.card_b = FakeCard(self.pos_b, None, self.effect_b_lower, [])

        self.grid.add_card(self.card_a)
        self.grid.add_card(self.card_b)

    def test_success_simple_action(self) -> None:
        result = self.process_action.activate_card(
            self.card_b, self.grid,
            self.player_inputs, self.player_outputs, self.player_pollution
        )

        self.assertTrue(result)
        self.assertEqual(self.card_a.get_resource_count(Resource.RED), 0)
        self.assertEqual(self.card_a.get_resource_count(Resource.GREEN), 1)
        self.assertEqual(self.card_a.get_pollution_count(), 1)
        self.assertEqual(self.card_b.get_resource_count(Resource.CAR), 1)

    def test_fail_if_card_to_activate_is_inactive(self) -> None:
        self.card_b.set_active(False)

        result = self.process_action.activate_card(
            self.card_b, self.grid,
            self.player_inputs, self.player_outputs, self.player_pollution
        )

        self.assertFalse(result)
        self.assertEqual(self.card_a.get_resource_count(Resource.RED), 2)
        self.assertEqual(self.card_b.get_resource_count(Resource.CAR), 0)

    def test_fail_if_input_card_is_inactive(self) -> None:
        self.card_a.set_active(False)

        result = self.process_action.activate_card(
            self.card_b, self.grid,
            self.player_inputs, self.player_outputs, self.player_pollution
        )

        self.assertFalse(result)
        self.assertEqual(self.card_a.get_resource_count(Resource.RED), 2)
        self.assertEqual(self.card_b.get_resource_count(Resource.CAR), 0)

    def test_fail_if_pollution_target_is_inactive(self) -> None:
        self.card_a.set_active(False)

        result = self.process_action.activate_card(
            self.card_b, self.grid,
            self.player_inputs, self.player_outputs, self.player_pollution
        )

        self.assertFalse(result)
        self.assertEqual(self.card_a.get_resource_count(Resource.RED), 2)

    def test_fail_not_enough_resources(self) -> None:
        player_inputs_expensive = [
            (Resource.RED, self.pos_a),
            (Resource.RED, self.pos_a),
            (Resource.GREEN, self.pos_a)
        ]

        result = self.process_action.activate_card(
            self.card_b, self.grid,
            player_inputs_expensive, self.player_outputs, self.player_pollution
        )
        self.assertFalse(result)

        effect_b_expensive = FakeEffect([Resource.RED]*3, self.effect_b_outputs, 1)
        self.card_b = FakeCard(self.pos_b, None, effect_b_expensive, [])
        self.grid.add_card(self.card_b)

        player_inputs_3red = [
            (Resource.RED, self.pos_a),
            (Resource.RED, self.pos_a),
            (Resource.RED, self.pos_a)
        ]

        result2 = self.process_action.activate_card(
            self.card_b, self.grid,
            player_inputs_3red, self.player_outputs, self.player_pollution
        )
        self.assertFalse(result2)
        self.assertEqual(self.card_a.get_resource_count(Resource.RED), 2)

    def test_fail_invalid_effect_transaction(self) -> None:
        invalid_inputs = [(Resource.RED, self.pos_a), (Resource.GREEN, self.pos_a)]

        result = self.process_action.activate_card(
            self.card_b, self.grid, invalid_inputs, self.player_outputs, self.player_pollution
        )
        self.assertFalse(result)
        self.assertEqual(self.card_a.get_resource_count(Resource.RED), 2)

    def test_fail_output_to_wrong_card(self) -> None:
        invalid_outputs = [(Resource.CAR, self.pos_a)]

        result = self.process_action.activate_card(
            self.card_b, self.grid,
            self.player_inputs, invalid_outputs, self.player_pollution
        )

        self.assertFalse(result)
        self.assertEqual(self.card_a.get_resource_count(Resource.RED), 2)
        self.assertEqual(self.card_a.get_resource_count(Resource.CAR), 0)

    def test_success_upper_effect_gain(self) -> None:
        effect_b_upper = FakeEffect([], [Resource.GREEN], 0)
        self.card_b = FakeCard(self.pos_b, effect_b_upper, self.effect_b_lower, [])
        self.grid.add_card(self.card_b)

        player_inputs_gain: List[Tuple[Resource, GridPosition]] = []
        player_outputs_gain: List[Tuple[Resource, GridPosition]] = [(Resource.GREEN, self.pos_b)]
        player_pollution_gain: List[GridPosition] = []

        result = self.process_action.activate_card(
            self.card_b, self.grid,
            player_inputs_gain, player_outputs_gain, player_pollution_gain
        )

        self.assertTrue(result)
        self.assertEqual(self.card_b.get_resource_count(Resource.GREEN), 1)
        self.assertEqual(self.card_a.get_pollution_count(), 0)

if __name__ == "__main__":
    unittest.main()
