"""Unit tests for ProcessActionAssistance using fake cards and grid (Assistance Only)."""
import unittest
from typing import List, Optional, Dict, Tuple
from terra_futura.process_action_assistance import ProcessActionAssistance
from terra_futura.simple_types import GridPosition, Resource
from terra_futura.interfaces import InterfaceCard, InterfaceGrid, InterfaceSelectReward


class FakeCard(InterfaceCard):
    """Fake card implementing InterfaceCard for testing."""

    def __init__(self, has_assistance: bool = True, can_activate: bool = True) -> None:
        self.resources: List[Resource] = []
        self._has_assistance = has_assistance
        self._can_activate = can_activate
        self.get_calls: List[List[Resource]] = []
        self.put_calls: List[List[Resource]] = []

    def can_get_resources(self, resources: List[Resource]) -> bool:
        return all(self.resources.count(r) > 0 for r in resources)


    def get_resources(self, resources: List[Resource]) -> None:
        self.get_calls.append(resources.copy())
        for r in resources:
            self.resources.remove(r)

    def can_put_resources(self, resources: List[Resource]) -> bool:
        return True

    def put_resources(self, resources: List[Resource]) -> None:
        self.put_calls.append(resources.copy())
        self.resources.extend(resources)

    def check(self, inputs: List[Resource], outputs: List[Resource], pollution: int) -> bool:
        return self._can_activate

    def check_lower(self, inputs: List[Resource], outputs: List[Resource], pollution: int) -> bool:
        return self._can_activate

    def has_assistance(self) -> bool:
        return self._has_assistance

    def state(self) -> str:
        return "FakeCard"

    def add(self, resource: Resource, count: int = 1) -> None:
        for _ in range(count):
            self.resources.append(resource)


class FakeGrid(InterfaceGrid):
    """Fake grid implementing InterfaceGrid for testing."""

    def __init__(self) -> None:
        self.cards: Dict[Tuple[int, int], InterfaceCard] = {}
        self.activatable: Dict[Tuple[int, int], bool] = {}

    def get_card(self, coordinate: GridPosition) -> Optional[InterfaceCard]:
        return self.cards.get((coordinate.x, coordinate.y))

    def can_put_card(self, coordinate: GridPosition) -> bool:
        _ = coordinate
        return True

    def put_card(self, coordinate: GridPosition, card: InterfaceCard) -> None:
        self.cards[(coordinate.x, coordinate.y)] = card

    def can_be_activated(self, coordinate: GridPosition) -> bool:
        return self.activatable.get((coordinate.x, coordinate.y), True)

    def set_activated(self, coordinate: GridPosition) -> None:
        _ = coordinate

    def set_activation_pattern(self, pattern: List[GridPosition]) -> None:
        _ = pattern

    def end_turn(self) -> None:
        pass

    def state(self) -> str:
        return "FakeGrid"

    def place(self, x: int, y: int, card: InterfaceCard, active: bool = True) -> None:
        self.cards[(x, y)] = card
        self.activatable[(x, y)] = active


class FakeReward(InterfaceSelectReward):
    """Fake reward interface for testing (Assistance Mode Only)."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, object]] = []

    def set_reward(
        self,
        player: int,
        card: InterfaceCard,
        reward: List[Resource]
    ) -> None:
        """Зберігає виклик set_reward для перевірки."""
        self.calls.append({
            "player": player,
            "card": card,
            "reward": reward.copy(),
        })

    def can_select_reward(self, resource: Resource) -> bool:
        _ = resource
        return True

    def select_reward(self, resource: Resource) -> None:
        _ = resource

    def state(self) -> str:
        return "FakeReward"
class TestProcessActionAssistance(unittest.TestCase):

    def setUp(self) -> None:
        self.reward: FakeReward = FakeReward()
        self.action: ProcessActionAssistance = ProcessActionAssistance(self.reward)
        self.grid: FakeGrid = FakeGrid()
        self.card: FakeCard = FakeCard()
        self.assist: FakeCard = FakeCard()
        self.grid.place(0, 0, self.card)

    def _add_card(self, x: int, y: int, res: Dict[Resource, int]) -> FakeCard:
        c: FakeCard = FakeCard()
        for r, n in res.items():
            c.add(r, n)
        self.grid.place(x, y, c)
        return c

    def test_basic_assistance_success(self) -> None:
        paid_res = {Resource.GREEN: 1, Resource.RED: 1}
        input_card: FakeCard = self._add_card(1, 1, paid_res)

        paid_inputs = [(Resource.GREEN, GridPosition(1, 1)), (Resource.RED, GridPosition(1, 1))]
        gained_outputs = [(Resource.BULB, GridPosition(0, 0))]

        ok: bool = self.action.activate_card(
            card=self.card,
            grid=self.grid,
            assisting_player=2,
            assisting_card=self.assist,
            inputs=paid_inputs,
            outputs=gained_outputs,
            pollution=[]
        )

        self.assertTrue(ok)

        self.assertEqual(len(input_card.get_calls), 1)
        self.assertIn(Resource.GREEN, input_card.get_calls[0])
        self.assertIn(Resource.RED, input_card.get_calls[0])

        self.assertEqual(len(self.card.put_calls), 1)
        self.assertIn(Resource.BULB, self.card.put_calls[0])

        self.assertEqual(len(self.reward.calls), 1)
        reward_call = self.reward.calls[0]
        self.assertEqual(reward_call["player"], 2)
        self.assertEqual(reward_call["card"], self.assist)


    def test_assistance_with_pollution_production(self) -> None:
        paid_res = {Resource.RED: 1}
        self._add_card(1, 0, paid_res)
        pollution_target: FakeCard = self._add_card(0, 1, {})

        ok: bool = self.action.activate_card(
            card=self.card,
            grid=self.grid,
            assisting_player=2,
            assisting_card=self.assist,
            inputs=[(Resource.RED, GridPosition(1, 0))],
            outputs=[(Resource.GEAR, GridPosition(0, 0))],
            pollution=[GridPosition(0, 1)]
        )

        self.assertTrue(ok)

        self.assertEqual(len(pollution_target.put_calls), 1)
        self.assertIn(Resource.POLLUTION, pollution_target.put_calls[0])

        self.assertEqual(len(self.reward.calls), 1)


    def test_multiple_resources_from_different_cards(self) -> None:
        c1: FakeCard = self._add_card(1, 0, {Resource.GREEN: 1, Resource.RED: 1})
        c2: FakeCard = self._add_card(0, 1, {Resource.YELLOW: 1})
        paid_inputs = [
            (Resource.GREEN, GridPosition(1, 0)),
            (Resource.RED, GridPosition(1, 0)),
            (Resource.YELLOW, GridPosition(0, 1))
        ]

        ok: bool = self.action.activate_card(
            card=self.card,
            grid=self.grid,
            assisting_player=2,
            assisting_card=self.assist,
            inputs=paid_inputs,
            outputs=[(Resource.CAR, GridPosition(0, 0))],
            pollution=[]
        )

        self.assertTrue(ok)

        self.assertEqual(len(c1.get_calls), 1)
        self.assertEqual(len(c2.get_calls), 1)

        self.assertEqual(len(self.reward.calls), 1)

    def test_no_assistance_effect_fails(self) -> None:
        self.card = FakeCard(has_assistance=False)
        self.grid.place(0, 0, self.card)
        ok: bool = self.action.activate_card(
            card=self.card,
            grid=self.grid,
            assisting_player=2,
            assisting_card=self.assist,
            inputs=[],
            outputs=[],
            pollution=[]
        )
        self.assertFalse(ok)
        self.assertEqual(len(self.reward.calls), 0)

    def test_card_not_in_grid_fails(self) -> None:
        orphan: FakeCard = FakeCard()
        ok: bool = self.action.activate_card(
            card=orphan,
            grid=self.grid,
            assisting_player=2,
            assisting_card=self.assist,
            inputs=[],
            outputs=[],
            pollution=[]
        )
        self.assertFalse(ok)
        self.assertEqual(len(self.reward.calls), 0)

    def test_blocked_card_fails(self) -> None:
        self.grid.activatable[(0, 0)] = False
        ok: bool = self.action.activate_card(
            card=self.card,
            grid=self.grid,
            assisting_player=2,
            assisting_card=self.assist,
            inputs=[],
            outputs=[],
            pollution=[]
        )
        self.assertFalse(ok)
        self.assertEqual(len(self.reward.calls), 0)

    def test_insufficient_resources_fails(self) -> None:
        self._add_card(1, 1, {})
        ok: bool = self.action.activate_card(
            card=self.card,
            grid=self.grid,
            assisting_player=2,
            assisting_card=self.assist,
            inputs=[(Resource.GREEN, GridPosition(1, 1))],
            outputs=[(Resource.BULB, GridPosition(0, 0))],
            pollution=[]
        )
        self.assertFalse(ok)
        self.assertEqual(len(self.reward.calls), 0)

    def test_assisting_card_effect_check_fails(self) -> None:
        self.assist = FakeCard(can_activate=False)
        ok: bool = self.action.activate_card(
            card=self.card,
            grid=self.grid,
            assisting_player=2,
            assisting_card=self.assist,
            inputs=[],
            outputs=[],
            pollution=[]
        )
        self.assertFalse(ok)
        self.assertEqual(len(self.reward.calls), 0)


if __name__ == "__main__":
    unittest.main()
