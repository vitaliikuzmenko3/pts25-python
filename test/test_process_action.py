import unittest
from collections import Counter
from typing import List, Tuple, Dict, Any, Optional

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

    def hasAssistance(self) -> bool:
        return False
    
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
        self.pollution_added_count = 0

    def get_position(self) -> GridPosition:
        return self._pos

    def is_active(self) -> bool:
        return self._is_active
        
    def set_active(self, status: bool) -> None:
        self._is_active = status

    def canGetResources(self, resources: List[Resource]) -> bool:
        needed = Counter(resources)
        for res, count in needed.items():
            if self._resources[res] < count:
                return False
        return True
        
    def getResources(self, resources: List[Resource]) -> None:
        for res in resources:
            if self._resources[res] <= 0:
                raise ValueError("Attempt to delete non-existent resource")
            self._resources[res] -= 1

    def canPutResources(self, resources: List[Resource]) -> bool:
        return True

    def putResources(self, resources: List[Resource]) -> None:
        self._resources.update(resources) 

    def checkInput(self, i: List[Resource], o: List[Resource], p: int) -> bool:
        if self._upper_effect is None:
            return False
        return self._upper_effect.check(i, o, p)

    def checkLower(self, i: List[Resource], o: List[Resource], p: int) -> bool:
        if self._lower_effect is None:
            return False
        return self._lower_effect.check(i, o, p) 

    def add_pollution(self) -> None:
        self.pollution_added_count += 1
        
    def get_resource_count(self, resource: Resource) -> int:
        return self._resources[resource]
    
class FakeGrid(InterfaceGrid):
    def __init__(self):
        self._cards: Dict[Tuple[int, int], FakeCard] = {}

    def getCard(self, coordinate: GridPosition) -> Optional[InterfaceCard]:
        return self._cards.get((coordinate.x, coordinate.y)) 
        
    def canBeActivated(self, coordinate: GridPosition) -> bool:
        card = self.getCard(coordinate)
        return card is not None and card.is_active() 

    def add_card(self, card: FakeCard) -> None:
        self._cards[(card.get_position().x, card.get_position().y)] = card
        
class TestProcessAction(unittest.TestCase):

    def setUp(self) -> None:
        self.process_action = ProcessAction()
        self.grid = FakeGrid()
        
        self.pos_A = GridPosition(0, 0)
        self.card_A_resources = [Resource.RED, Resource.RED, Resource.GREEN]
        self.card_A = FakeCard(self.pos_A, None, None, self.card_A_resources)
        
        self.pos_B = GridPosition(0, 1)
        
        self.effect_B_inputs = [Resource.RED, Resource.RED]
        self.effect_B_outputs = [Resource.CAR]
        self.effect_B_pollution = 1
        
        self.effect_B_lower = FakeEffect(
            self.effect_B_inputs, self.effect_B_outputs, self.effect_B_pollution
        )
        
        self.player_inputs = [
            (Resource.RED, self.pos_A), 
            (Resource.RED, self.pos_A)
        ]
        self.player_outputs = [(Resource.CAR, self.pos_B)]
        self.player_pollution = [self.pos_A]

        self.card_B = FakeCard(self.pos_B, None, self.effect_B_lower, [])
        
        self.grid.add_card(self.card_A)
        self.grid.add_card(self.card_B)

    def test_success_simple_action(self) -> None:
        result = self.process_action.activateCard(
            self.card_B, self.grid, 
            self.player_inputs, self.player_outputs, self.player_pollution
        )
        
        self.assertTrue(result)
        self.assertEqual(self.card_A.get_resource_count(Resource.RED), 0)
        self.assertEqual(self.card_A.get_resource_count(Resource.GREEN), 1)
        self.assertEqual(self.card_A.pollution_added_count, 1)
        self.assertEqual(self.card_B.get_resource_count(Resource.CAR), 1)
        
    def test_fail_if_card_to_activate_is_inactive(self) -> None:
        self.card_B.set_active(False)
        
        result = self.process_action.activateCard(
            self.card_B, self.grid, 
            self.player_inputs, self.player_outputs, self.player_pollution
        )
        
        self.assertFalse(result)
        self.assertEqual(self.card_A.get_resource_count(Resource.RED), 2)
        self.assertEqual(self.card_B.get_resource_count(Resource.CAR), 0)
        
    def test_fail_if_input_card_is_inactive(self) -> None:
        self.card_A.set_active(False)
        
        result = self.process_action.activateCard(
            self.card_B, self.grid, 
            self.player_inputs, self.player_outputs, self.player_pollution
        )
        
        self.assertFalse(result)
        self.assertEqual(self.card_A.get_resource_count(Resource.RED), 2)
        self.assertEqual(self.card_B.get_resource_count(Resource.CAR), 0)
        
    def test_fail_if_pollution_target_is_inactive(self) -> None:
        self.card_A.set_active(False) 
        
        result = self.process_action.activateCard(
            self.card_B, self.grid, 
            self.player_inputs, self.player_outputs, self.player_pollution
        )
        
        self.assertFalse(result)
        self.assertEqual(self.card_A.get_resource_count(Resource.RED), 2)
        
    def test_fail_not_enough_resources(self) -> None:
        player_inputs_expensive = [
            (Resource.RED, self.pos_A), 
            (Resource.RED, self.pos_A),
            (Resource.GREEN, self.pos_A)
        ]
        
        result = self.process_action.activateCard(
            self.card_B, self.grid, 
            player_inputs_expensive, self.player_outputs, self.player_pollution
        )
        self.assertFalse(result)
        
        effect_B_expensive = FakeEffect([Resource.RED]*3, self.effect_B_outputs, 1)
        self.card_B = FakeCard(self.pos_B, None, effect_B_expensive, [])
        self.grid.add_card(self.card_B)
        
        player_inputs_3red = [
            (Resource.RED, self.pos_A), 
            (Resource.RED, self.pos_A),
            (Resource.RED, self.pos_A)
        ]
        
        result2 = self.process_action.activateCard(
            self.card_B, self.grid, 
            player_inputs_3red, self.player_outputs, self.player_pollution
        )
        self.assertFalse(result2)
        self.assertEqual(self.card_A.get_resource_count(Resource.RED), 2)

    def test_fail_invalid_effect_transaction(self) -> None:
        invalid_inputs = [(Resource.RED, self.pos_A), (Resource.GREEN, self.pos_A)]
        
        result = self.process_action.activateCard(
            self.card_B, self.grid, invalid_inputs, self.player_outputs, self.player_pollution
        )
        self.assertFalse(result)
        self.assertEqual(self.card_A.get_resource_count(Resource.RED), 2)
        
    def test_fail_output_to_wrong_card(self) -> None:
        invalid_outputs = [(Resource.CAR, self.pos_A)]
        
        result = self.process_action.activateCard(
            self.card_B, self.grid, 
            self.player_inputs, invalid_outputs, self.player_pollution
        )
        
        self.assertFalse(result) 
        self.assertEqual(self.card_A.get_resource_count(Resource.RED), 2)
        self.assertEqual(self.card_A.get_resource_count(Resource.CAR), 0)
        
    def test_success_upper_effect_gain(self) -> None:
        effect_B_upper = FakeEffect([], [Resource.GREEN], 0)
        self.card_B = FakeCard(self.pos_B, effect_B_upper, self.effect_B_lower, [])
        self.grid.add_card(self.card_B)
        
        player_inputs_gain = []
        player_outputs_gain = [(Resource.GREEN, self.pos_B)]
        player_pollution_gain = []
        
        result = self.process_action.activateCard(
            self.card_B, self.grid, 
            player_inputs_gain, player_outputs_gain, player_pollution_gain
        )
        
        self.assertTrue(result)
        self.assertEqual(self.card_B.get_resource_count(Resource.GREEN), 1)
        self.assertEqual(self.card_A.pollution_added_count, 0)
        
if __name__ == "__main__":
    unittest.main()