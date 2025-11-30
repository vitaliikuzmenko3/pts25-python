import unittest

from terra_futura.scoring_method import ScoringMethod
from terra_futura.simple_types import Resource, Points


class TestScoringMethod(unittest.TestCase):

    def test_ignores_money_and_pollution_in_available_resources(self) -> None:
        method = ScoringMethod(
            resources=[Resource.GREEN, Resource.RED],
            points_per_combination=Points(5)
        )

        available = [
            Resource.GREEN,
            Resource.RED,
            Resource.MONEY,       # ignored
            Resource.POLLUTION    # ignored
        ]

        result = method.select_this_method_and_calculate(available)
        self.assertEqual(result.value, 5)

    def test_counts_only_complete_sets(self) -> None:
        method = ScoringMethod(
            resources=[Resource.GREEN, Resource.YELLOW],
            points_per_combination=Points(3)
        )

        available = [
            Resource.GREEN,
            Resource.GREEN,
            Resource.YELLOW
        ]

        result = method.select_this_method_and_calculate(available)
        self.assertEqual(result.value, 3)

    def test_multiple_sets(self) -> None:
        method = ScoringMethod(
            resources=[Resource.BULB, Resource.GEAR],
            points_per_combination=Points(4)
        )

        available = [
            Resource.BULB, Resource.BULB,
            Resource.GEAR, Resource.GEAR
        ]

        result = method.select_this_method_and_calculate(available)
        self.assertEqual(result.value, 8)

    def test_repeated_required_resources(self) -> None:
        method = ScoringMethod(
            resources=[Resource.GREEN, Resource.GREEN, Resource.RED],
            points_per_combination=Points(7)
        )

        available = [
            Resource.GREEN, Resource.GREEN, Resource.GREEN,
            Resource.RED, Resource.RED
        ]

        result = method.select_this_method_and_calculate(available)
        self.assertEqual(result.value, 7)

    def test_zero_sets_when_missing_resource(self) -> None:
        method = ScoringMethod(
            resources=[Resource.CAR, Resource.GEAR],
            points_per_combination=Points(10)
        )

        available = [
            Resource.CAR
        ]

        result = method.select_this_method_and_calculate(available)
        self.assertEqual(result.value, 0)

    def test_state_before_and_after(self) -> None:
        method = ScoringMethod(
            resources=[Resource.GREEN, Resource.RED],
            points_per_combination=Points(4)
        )

        before = method.state()
        self.assertIn("Not calculated", before)
        self.assertIn("selected=False", before)

        method.select_this_method_and_calculate([Resource.GREEN, Resource.RED])

        after = method.state()
        self.assertIn("selected=True", after)
        self.assertIn("total=", after)


if __name__ == '__main__':
    unittest.main()
