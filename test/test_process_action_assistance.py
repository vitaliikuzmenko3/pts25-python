"""Unit tests for ProcessActionAssistance using fake cards and grid."""

import unittest
from typing import List, Optional, Dict, Tuple
from terra_futura.process_action_assistance import ProcessActionAssistance
from terra_futura.simple_types import GridPosition, Resource
from terra_futura.interfaces import ICard, IGrid, InterfaceSelectReward


class FakeCard(ICard):
    """Fake card implementing ICard for testing."""

    def __init__(self, has_assistance: bool = True, can_activate: bool = True) -> None:
        self.resources: Dict[Resource, int] = {}
        self._has_assistance = has_assistance
        self._can_activate = can_activate
        self.get_calls: List[List[Resource]] = []
        self.put_calls: List[List[Resource]] = []

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

    def check(self, inputs: List[Resource], outputs: List[Resource], pollution: int) -> bool:
        return self._can_activate

    def check_lower(self, inputs: List[Resource], outputs: List[Resource], pollution: int) -> bool:
        return self._can_activate

    def has_assistance(self) -> bool:
        return self._has_assistance

    def state(self) -> str:
        return "FakeCard"

    def add(self, resource: Resource, count: int = 1) -> None:
        self.resources[resource] = self.resources.get(resource, 0) + count


class FakeGrid(IGrid):
    """Fake grid implementing IGrid for testing."""

    def __init__(self) -> None:
        self.cards: Dict[Tuple[int, int], ICard] = {}
        self.activatable: Dict[Tuple[int, int], bool] = {}

    def get_card(self, coordinate: GridPosition) -> Optional[ICard]:
        return self.cards.get((coordinate.x, coordinate.y))

    def can_put_card(self, coordinate: GridPosition) -> bool:
        _ = coordinate
        return True

    def put_card(self, coordinate: GridPosition, card: ICard) -> None:
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

    def place(self, x: int, y: int, card: ICard, active: bool = True) -> None:
        self.cards[(x, y)] = card
        self.activatable[(x, y)] = active


class FakeReward(InterfaceSelectReward):
    """Fake reward interface for testing."""

    def __init__(self) -> None:
        self.calls: List[Dict[str, object]] = []

    def set_reward(
        self,
        player: int,
        card: ICard,
        reward: List[Resource],
        mode: str = "assistance"
    ) -> None:
        self.calls.append({
            "player": player,
            "card": card,
            "reward": reward.copy(),
            "mode": mode
        })

    def can_select_reward(self, resource: Resource) -> bool:
        _ = resource
        return True

    def select_reward(self, resource: Resource) -> None:
        _ = resource

    def state(self) -> str:
        return "FakeReward"


class TestProcessActionAssistance(unittest.TestCase):
    """Unit tests for ProcessActionAssistance."""

    def setUp(self) -> None:
        """Initialize test environment with grid, cards, and reward."""
        self.reward: FakeReward = FakeReward()
        self.action: ProcessActionAssistance = ProcessActionAssistance(self.reward)
        self.grid: FakeGrid = FakeGrid()
        self.card: FakeCard = FakeCard()
        self.assist: FakeCard = FakeCard()
        self.grid.place(0, 0, self.card)

    def _add_card(self, x: int, y: int, res: Dict[Resource, int]) -> FakeCard:
        """Add a card with resources to the grid at (x, y)."""
        c: FakeCard = FakeCard()
        for r, n in res.items():
            c.add(r, n)
        self.grid.place(x, y, c)
        return c

    def test_basic_assistance(self) -> None:
        """Test simple assistance activation."""
        _inp: FakeCard = self._add_card(1, 1, {Resource.GREEN: 1})

        ok: bool = self.action.activate_card(
            self.card,
            self.grid,
            2,
            self.assist,
            [(Resource.GREEN, GridPosition(1, 1))],
            [(Resource.BULB, GridPosition(0, 0))],
            []
        )

        self.assertTrue(ok)
        self.assertEqual(len(_inp.get_calls), 1)
        self.assertEqual(len(self.card.put_calls), 1)
        self.assertEqual(len(self.reward.calls), 1)

    def test_with_pollution_production(self) -> None:
        """Test assistance activation that produces pollution."""
        self._add_card(1, 0, {Resource.RED: 1})
        pol: FakeCard = self._add_card(0, 1, {})

        ok: bool = self.action.activate_card(
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

    def test_pollution_transfer(self) -> None:
        """Test transfer of pollution between cards."""
        src: FakeCard = self._add_card(1, 1, {Resource.POLUTION: 1})
        start: FakeCard = self._add_card(0, 0, {})
        card_to_activate: ICard = FakeCard()
        self.grid.place(1, 0, card_to_activate)

        ok: bool = self.action.activate_card(
            card_to_activate,
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

    def test_multiple_resources(self) -> None:
        """Test activation using multiple resources from different cards."""
        c1: FakeCard = self._add_card(1, 0, {Resource.GREEN: 1, Resource.RED: 1})
        c2: FakeCard = self._add_card(0, 1, {Resource.YELLOW: 1})

        ok: bool = self.action.activate_card(
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

    def test_no_assistance_effect_fails(self) -> None:
        """Activation fails if card has no assistance effect."""
        self.card = FakeCard(has_assistance=False)
        self.grid.place(0, 0, self.card)

        ok: bool = self.action.activate_card(
            self.card, self.grid, 2, self.assist, [], [], []
        )
        self.assertFalse(ok)

    def test_card_not_in_grid_fails(self) -> None:
        """Activation fails if card is not in the grid."""
        orphan: FakeCard = FakeCard()
        ok: bool = self.action.activate_card(
            orphan, self.grid, 2, self.assist, [], [], []
        )
        self.assertFalse(ok)

    def test_blocked_card_fails(self) -> None:
        """Activation fails if the card is blocked."""
        self.grid.activatable[(0, 0)] = False
        ok: bool = self.action.activate_card(
            self.card, self.grid, 2, self.assist, [], [], []
        )
        self.assertFalse(ok)

    def test_insufficient_resources_fails(self) -> None:
        """Activation fails if input resources are insufficient."""
        self._add_card(1, 1, {})

        ok: bool = self.action.activate_card(
            self.card,
            self.grid,
            2,
            self.assist,
            [(Resource.GREEN, GridPosition(1, 1))],
            [(Resource.BULB, GridPosition(0, 0))],
            []
        )
        self.assertFalse(ok)

    def test_pollution_transfer_multiple_fails(self) -> None:
        """Activation fails if pollution transfer is attempted from multiple cards."""
        self._add_card(1, 1, {Resource.POLUTION: 2})
        ok: bool = self.action.activate_card(
            self.card,
            self.grid,
            2,
            self.assist,
            [],
            [],
            [GridPosition(1, 1), GridPosition(2, 2)]
        )
        self.assertFalse(ok)

if __name__ == "__main__":
    unittest.main()
