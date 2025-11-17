import unittest
from terra_futura.card import Card
from terra_futura.card import Resource, CardEffects


class TestCard(unittest.TestCase):

    def test_can_get_resources_success(self) -> None:
        card = Card([Resource.GREEN, Resource.RED], pollutionSpacesL=2)
        self.assertTrue(card.can_get_resources([Resource.GREEN]))

    def test_can_get_resources_fail(self) -> None:
        card = Card([Resource.GREEN], pollutionSpacesL=2)
        self.assertFalse(card.can_get_resources([Resource.RED]))

    def test_get_resources_removes_them(self)-> None:
        card = Card([Resource.GREEN, Resource.RED], pollutionSpacesL=2)
        card.get_resources([Resource.GREEN])
        self.assertEqual(card.resources, [Resource.RED])

    def test_put_resources_limited_by_pollution(self)-> None:
        card = Card([Resource.POLLUTION], pollutionSpacesL=1)
        with self.assertRaises(ValueError):
            card.put_resources([Resource.POLLUTION])

    def test_check_with_pollution(self)-> None:
        effect = CardEffects(pollution=1)
        card = Card([Resource.GREEN, Resource.POLLUTION], pollutionSpacesL=3, upperEffect=effect)
        self.assertTrue(card.check_lower([Resource.GREEN], [], 0))

    def test_check_lower_always_ignores_pollution(self)-> None:
        card = Card([Resource.GREEN], pollutionSpacesL=0)
        self.assertTrue(card.check_lower([Resource.GREEN], [], 999))
