# pylint: disable=missing-docstring, too-many-public-methods
import unittest
import json
from terra_futura.simple_types import Resource
from terra_futura.effects import (
    EffectTransformationFixed,
    EffectArbitraryBasic
)

class TestEffects(unittest.TestCase):

    def test_transformation_fixed_success(self) -> None:
        effect = EffectTransformationFixed(
            [Resource.RED, Resource.RED],
            [Resource.CAR],
            1
        )
        self.assertTrue(effect.check(
            inputs=[Resource.RED, Resource.RED],
            output=[Resource.CAR],
            pollution=1
        ))

    def test_transformation_fixed_fail_wrong_input(self) -> None:
        effect = EffectTransformationFixed([Resource.RED], [Resource.CAR], 0)
        self.assertFalse(effect.check([Resource.GREEN], [Resource.CAR], 0))
        self.assertFalse(effect.check([Resource.RED, Resource.RED], [Resource.CAR], 0))

    def test_arbitrary_basic_success(self) -> None:
        effect = EffectArbitraryBasic(2, [Resource.MONEY], 0)
        self.assertTrue(effect.check(
            inputs=[Resource.RED, Resource.GREEN],
            output=[Resource.MONEY],
            pollution=0
        ))

    def test_arbitrary_basic_fail_not_raw(self) -> None:
        effect = EffectArbitraryBasic(1, [Resource.MONEY], 0)
        self.assertFalse(effect.check([Resource.CAR], [Resource.MONEY], 0))

    def test_state_json(self) -> None:
        eff = EffectTransformationFixed([Resource.RED], [Resource.CAR], 1)
        state = json.loads(eff.state())
        self.assertEqual(state["type"], "fixed")
        self.assertEqual(state["pollution"], 1)
