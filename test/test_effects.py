# pylint: disable=missing-docstring, too-many-public-methods
import unittest
import json
from terra_futura.simple_types import Resource
from terra_futura.effects import (
    EffectTransformationFixed,
    EffectArbitraryBasic,
    EffectOr,
    EffectAssistance,
    EffectPollutionTransfer
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

    def test_effect_or_logic(self) -> None:
        eff_a = EffectTransformationFixed([Resource.RED], [Resource.MONEY], 0)
        eff_b = EffectTransformationFixed([Resource.GREEN], [Resource.MONEY], 0)
        effect_or = EffectOr([eff_a, eff_b])
        self.assertTrue(effect_or.check([Resource.RED], [Resource.MONEY], 0))
        self.assertTrue(effect_or.check([Resource.GREEN], [Resource.MONEY], 0))
        self.assertFalse(effect_or.check([Resource.YELLOW], [Resource.MONEY], 0))

    def test_effect_or_has_assistance(self) -> None:
        effect = EffectOr([
            EffectTransformationFixed([], [], 0),
            EffectAssistance()
        ])
        self.assertTrue(effect.has_assistance())

        effect_clean = EffectOr([
            EffectTransformationFixed([], [], 0)
        ])
        self.assertFalse(effect_clean.has_assistance())

    def test_state_json(self) -> None:
        eff = EffectTransformationFixed([Resource.RED], [Resource.CAR], 1)
        state = json.loads(eff.state())
        self.assertEqual(state["type"], "fixed")
        self.assertEqual(state["pollution"], 1)

    def test_pollution_transfer(self) -> None:
        effect = EffectPollutionTransfer()
        self.assertTrue(effect.check([], [], 0))
        self.assertFalse(effect.check([Resource.RED], [], 0))
        self.assertFalse(effect.check([], [Resource.MONEY], 0))

    def test_starting_card_logic(self) -> None:
        gain_red = EffectTransformationFixed([], [Resource.RED], 0)
        gain_green = EffectTransformationFixed([], [Resource.GREEN], 0)
        gain_yellow = EffectTransformationFixed([], [Resource.YELLOW], 0)
        gain_money = EffectTransformationFixed([], [Resource.MONEY], 0)
        gain_any = EffectOr([gain_red, gain_green, gain_yellow, gain_money])
        assistance = EffectAssistance()
        start_card_effect = EffectOr([gain_any, assistance])
        self.assertTrue(start_card_effect.check([], [Resource.RED], 0))
        self.assertTrue(start_card_effect.check([], [Resource.MONEY], 0))
        self.assertTrue(start_card_effect.has_assistance())

if __name__ == "__main__":
    unittest.main()
