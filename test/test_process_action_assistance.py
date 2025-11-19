import unittest
from typing import List, Optional, Dict
from terra_futura.process_action_assistance import ProcessActionAssistance
from terra_futura.simple_types import GridPosition, Resource
from terra_futura.interfaces import ICard, IGrid, InterfaceSelectReward


class FakeCard(ICard):
    def __init__(self, has_assistance=True, can_activate=True):
        self.resources: Dict[Resource, int] = {}
        self._has_assistance = has_assistance
        self._can_activate = can_activate
        self.get_calls = []
        self.put_calls = []

    def can_get_resources(self, resources: List[Resource]) -> bool:
        return all(self.resources.get(r, 0) > 0 for r in resources)

    def get_resources(self, resources: List[Resource]) -> None:
        self.get_calls.append(resources.copy())
        for r in resources:
            self.resources[r] = self.resources.get(r, 0) - 1

    def can_put_resources(self, resources: List[Resource]) -> bool:
        return True

    def put_resources(self, resources: List[Resource]) -> None:
        self.put_calls.append(resources.copy())
        for r in resources:
            self.resources[r] = self.resources.get(r, 0) + 1

    def check(self, i: List[Resource], o: List[Resource], p: int) -> bool:
        return self._can_activate

    def check_lower(
        self, i: List[Resource], o: List[Resource], p: int
    ) -> bool:
        return self._can_activate

    def has_assistance(self) -> bool:
        return self._has_assistance

    def state(self) -> str:
        return "FakeCard"

    def add(self, resource: Resource, count: int = 1):
        self.resources[resource] = self.resources.get(resource, 0) + count


class FakeGrid(IGrid):
    def __init__(self):
        self.cards: Dict[tuple, ICard] = {}
        self.activatable: Dict[tuple, bool] = {}

    def get_card(self, pos: GridPosition) -> Optional[ICard]:
        return self.cards.get((pos.x, pos.y))

    def can_put_card(self, pos: GridPosition) -> bool:
        return True

    def put_card(self, pos: GridPosition, card: ICard) -> None:
        self.cards[(pos.x, pos.y)] = card

    def can_be_activated(self, pos: GridPosition) -> bool:
        return self.activatable.get((pos.x, pos.y), True)

    def set_activated(self, pos: GridPosition) -> None:
        pass

    def set_activation_pattern(self, pattern: List[GridPosition]) -> None:
        pass

    def end_turn(self) -> None:
        pass

    def state(self) -> str:
        return "FakeGrid"

    def place(self, x: int, y: int, card: ICard, active=True):
        self.cards[(x, y)] = card
        self.activatable[(x, y)] = active


class FakeReward(InterfaceSelectReward):
    def __init__(self):
        self.calls = []

    def set_reward(
        self,
        player_id: int,
        card: ICard,
        reward: List[Resource],
        mode="assistance"
    ):
        self.calls.append({
            "player": player_id,
            "card": card,
            "reward": reward.copy(),
            "mode": mode
        })

    def can_select_reward(self, resource: Resource) -> bool:
        return True

    def select_reward(self, resource: Resource):
        pass

    def state(self) -> str:
        return "FakeReward"


class TestProcessActionAssistance(unittest.TestCase):
    def setUp(self):
        self.reward = FakeReward()
        self.action = ProcessActionAssistance(self.reward)
        self.grid = FakeGrid()
        self.card = FakeCard()
        self.assist = FakeCard()
        self.grid.place(0, 0, self.card)

    def _add_card(self, x: int, y: int, res: Dict[Resource, int]) -> FakeCard:
        c = FakeCard()
        for r, n in res.items():
            c.add(r, n)
        self.grid.place(x, y, c)
        return c

    def test_basic_assistance(self):
        inp = self._add_card(1, 1, {Resource.GREEN: 1})

        ok = self.action.activate_card(
            self.card,
            self.grid,
            2,
            self.assist,
            [(Resource.GREEN, GridPosition(1, 1))],
            [(Resource.BULB, GridPosition(0, 0))],
            []
        )

        self.assertTrue(ok)
        self.assertEqual(len(inp.get_calls), 1)
        self.assertEqual(len(self.card.put_calls), 1)
        self.assertEqual(len(self.reward.calls), 1)

    def test_with_pollution_production(self):
        inp = self._add_card(1, 0, {Resource.RED: 1})
        pol = self._add_card(0, 1, {})

        ok = self.action.activate_card(
            self.card,
            self.grid,
            2,
            self.assist,
            [(Resource.RED, GridPosition(1, 0))],
            [(Resource.GEAR, GridPosition(0, 0))],
            [GridPosition(0, 1)]
        )

        self.assertTrue(ok)
        self.assertIn(Resource.POLUTION, pol.put_calls[0])

    def test_pollution_transfer(self):
        src = self._add_card(1, 1, {Resource.POLUTION: 1})
        start = self._add_card(0, 0, {})
        self.grid.place(1, 0, FakeCard())

        ok = self.action.activate_card(
            self.grid.get_card(GridPosition(1, 0)),
            self.grid,
            2,
            self.assist,
            [],
            [],
            [GridPosition(1, 1)]
        )

        self.assertTrue(ok)
        self.assertEqual(len(src.get_calls), 1)
        self.assertEqual(len(start.put_calls), 1)
        self.assertEqual(self.reward.calls[0]["mode"], "pollution")

    def test_multiple_resources(self):
        c1 = self._add_card(1, 0, {Resource.GREEN: 1, Resource.RED: 1})
        c2 = self._add_card(0, 1, {Resource.YELLOW: 1})

        ok = self.action.activate_card(
            self.card,
            self.grid,
            2,
            self.assist,
            [
                (Resource.GREEN, GridPosition(1, 0)),
                (Resource.RED, GridPosition(1, 0)),
                (Resource.YELLOW, GridPosition(0, 1))
            ],
            [(Resource.CAR, GridPosition(0, 0))],
            []
        )

        self.assertTrue(ok)
        self.assertEqual(len(c1.get_calls), 1)
        self.assertEqual(len(c2.get_calls), 1)

    def test_no_assistance_fails(self):
        ok = self.action.activate_card(
            self.card, self.grid, 0, None, [], [], []
        )
        self.assertFalse(ok)

    def test_no_assistance_effect_fails(self):
        self.card = FakeCard(has_assistance=False)
        self.grid.place(0, 0, self.card)

        ok = self.action.activate_card(
            self.card, self.grid, 2, self.assist, [], [], []
        )
        self.assertFalse(ok)

    def test_card_not_in_grid_fails(self):
        orphan = FakeCard()
        ok = self.action.activate_card(
            orphan, self.grid, 2, self.assist, [], [], []
        )
        self.assertFalse(ok)

    def test_blocked_card_fails(self):
        self.grid.activatable[(0, 0)] = False
        ok = self.action.activate_card(
            self.card, self.grid, 2, self.assist, [], [], []
        )
        self.assertFalse(ok)

    def test_insufficient_resources_fails(self):
        self._add_card(1, 1, {})

        ok = self.action.activate_card(
            self.card,
            self.grid,
            2,
            self.assist,
            [(Resource.GREEN, GridPosition(1, 1))],
            [(Resource.BULB, GridPosition(0, 0))],
            []
        )
        self.assertFalse(ok)

    def test_pollution_transfer_multiple_fails(self):
        self._add_card(1, 1, {Resource.POLUTION: 2})

        ok = self.action.activate_card(
            self.card,
            self.grid,
            2,
            self.assist,
            [],
            [],
            [GridPosition(1, 1), GridPosition(2, 2)]
        )
        self.assertFalse(ok)

    def test_current_card_resets(self):
        self._add_card(1, 1, {Resource.GREEN: 1})

        self.action.activate_card(
            self.card,
            self.grid,
            2,
            self.assist,
            [(Resource.GREEN, GridPosition(1, 1))],
            [(Resource.BULB, GridPosition(0, 0))],
            []
        )

        self.assertIsNone(self.action._current_card)


if __name__ == "__main__":
    unittest.main()
