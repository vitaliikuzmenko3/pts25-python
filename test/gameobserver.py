import unittest
from terra_futura.card import Card, CardEffects, Resource
from terra_futura.gameobserver import GameObserver


class TestGameObserver(unittest.TestCase):

    def test_activate_upper_effect_adds_resources(self) -> None:
        card = Card(
            [Resource.GREEN],
            pollutionSpacesL=5,
            upperEffect=CardEffects(add_resources=[Resource.RED])
        )
        obs = GameObserver([card])

        obs.activate_effect(0, "upper")

        self.assertIn(Resource.RED, card.resources)

    def test_activate_lower_effect_transforms_resources(self) -> None:
        card = Card(
            [Resource.GREEN],
            pollutionSpacesL=5,
            lowerEffect=CardEffects(transform_resources_into={Resource.GREEN: Resource.YELLOW})
        )
        obs = GameObserver([card])

        obs.activate_effect(0, "lower")

        self.assertIn(Resource.YELLOW, card.resources)
        self.assertNotIn(Resource.GREEN, card.resources)

    def test_total_pollution(self) -> None:
        card1 = Card([Resource.POLLUTION, Resource.GREEN], pollutionSpacesL=5)
        card2 = Card([Resource.GREEN], pollutionSpacesL=5)
        obs = GameObserver([card1, card2])

        self.assertEqual(obs.get_total_pollution(), 1)

    def test_game_state_format(self) -> None:
        card = Card([Resource.GREEN], pollutionSpacesL=5)
        obs = GameObserver([card])

        state = obs.game_state()

        self.assertIn("Card 0", state)
        self.assertIn("Resources", state)
