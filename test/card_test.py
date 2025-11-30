import unittest
import json

from terra_futura.card import Card
from terra_futura.simple_types import Resource
from terra_futura.effects import (
    EffectTransformationFixed,
    EffectArbitraryBasic,
    EffectOr
)


class TestCardBasics(unittest.TestCase):

    def test_can_get_resources_valid(self)-> None:
        card = Card([Resource.RED, Resource.GREEN], 5)
        self.assertTrue(card.can_get_resources([Resource.RED]))

    def test_can_get_resources_invalid(self)-> None:
        card = Card([Resource.RED], 5)
        self.assertFalse(card.can_get_resources([Resource.GREEN]))

    def test_get_resources(self)-> None:
        card = Card([Resource.RED, Resource.GREEN], 5)
        card.get_resources([Resource.RED])
        self.assertEqual(card.resources, [Resource.GREEN])

    def test_get_resources_error(self)-> None:
        card = Card([Resource.GREEN], 5)
        with self.assertRaises(ValueError):
            card.get_resources([Resource.RED])

    def test_can_put_resources_respects_pollution_limit(self)-> None:
        card = Card([Resource.GREEN], pollutionSpacesL=1)
        self.assertTrue(card.can_put_resources([Resource.GREEN]))
        self.assertFalse(card.can_put_resources([Resource.POLLUTION, Resource.POLLUTION]))

    def test_put_resources(self)-> None:
        card = Card([Resource.GREEN], pollutionSpacesL=2)
        card.put_resources([Resource.POLLUTION])
        self.assertIn(Resource.POLLUTION, card.resources)


class TestCardWithEffects(unittest.TestCase):

    def test_check_upper_transformation_fixed_valid(self)-> None:
        effect = EffectTransformationFixed(
            [Resource.RED], [Resource.MONEY], pollution=0
        )
        card = Card([Resource.RED], 5, upperEffect=effect)
        self.assertTrue(card.check(
            inputs=[Resource.RED],
            output=[Resource.MONEY],
            pollution=0
        ))

    def test_check_upper_transformation_fixed_invalid(self)-> None:
        effect = EffectTransformationFixed(
            [Resource.RED], [Resource.MONEY], pollution=0
        )
        card = Card([Resource.RED], 5, upperEffect=effect)

        self.assertFalse(card.check(
            inputs=[Resource.GREEN],
            output=[Resource.MONEY],
            pollution=0
        ))

    def test_check_lower_arbitrary_basic_valid(self)-> None:
        effect = EffectArbitraryBasic(
            2, [Resource.MONEY], pollution=0
        )
        card = Card([Resource.RED, Resource.GREEN], 5, lowerEffect=effect)
        self.assertTrue(card.check_lower(
            inputs=[Resource.RED, Resource.GREEN],
            output=[Resource.MONEY],
            pollution=0
        ))

    def test_check_lower_arbitrary_basic_invalid(self)-> None:
        effect = EffectArbitraryBasic(
            2, [Resource.MONEY], pollution=0
        )
        card = Card([Resource.RED, Resource.GREEN], 5, lowerEffect=effect)
        self.assertFalse(card.check_lower(
            inputs=[Resource.RED],
            output=[Resource.MONEY],
            pollution=0
        ))

class TestCardOrEffect(unittest.TestCase):

    def test_or_effect(self)-> None:
        e1 = EffectTransformationFixed([Resource.RED], [Resource.GREEN], pollution=0)
        e2 = EffectArbitraryBasic(1, [Resource.MONEY], pollution=0)
        effect_or = EffectOr([e1, e2])
        card = Card([Resource.RED], 5, upperEffect=effect_or)
        self.assertTrue(card.check(
            inputs=[Resource.RED],
            output=[Resource.GREEN],
            pollution=0
        ))
        self.assertTrue(card.check(
            inputs=[Resource.YELLOW],
            output=[Resource.MONEY],
            pollution=0
        ))
        self.assertFalse(card.check(
            inputs=[Resource.GREEN],
            output=[Resource.YELLOW],
            pollution=0
        ))

class TestCardState(unittest.TestCase):

    def test_state_serialization(self)-> None:
        effect = EffectTransformationFixed([Resource.RED], [Resource.GREEN], pollution=0)
        card = Card([Resource.RED, Resource.GREEN], 3, True, effect, None)
        state = json.loads(card.state())
        self.assertEqual(state["resources"], ["Red", "Green"])
        self.assertEqual(state["pollution_limit"], 3)
        self.assertTrue(state["assistance"])
        self.assertEqual(state["upper_effect"]["type"], "fixed")
        self.assertIsNone(state["lower_effect"])
