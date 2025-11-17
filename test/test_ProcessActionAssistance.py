import unittest
from unittest.mock import Mock, call
from terra_futura.interfaces import ICard, IGrid, InterfaceSelectReward
from terra_futura.ProcessActionAssistance import ProcessActionAssistance
from terra_futura.simple_types import GridPosition, Resource
from terra_futura.Card import Card

class ProcessActionAssistanceTest(unittest.TestCase):

    def setUp(self):
        self.mock_reward_manager = Mock(spec=InterfaceSelectReward)
        self.processor = ProcessActionAssistance(self.mock_reward_manager)

        self.player_id = 1
        self.assisting_player_id = 2

        self.mock_card = Mock(spec=ICard, player_id=self.player_id, name="MainCard")
        self.mock_card.hasAssistance.return_value = True
        self.mock_assisting_card = Mock(spec=ICard, name="AssistingCard")

        self.mock_input_card_b = Mock(spec=ICard, name="InputCardB")
        self.mock_pollution_card = Mock(spec=ICard, name="PollutionTargetCard")

        self.mock_grid = Mock(spec=IGrid)
        self.mock_grid.getCard.side_effect = lambda pos: {
            GridPosition(0, 0): self.mock_card,
            GridPosition(1, 0): self.mock_input_card_b,
            GridPosition(2, 2): self.mock_pollution_card,
        }.get(pos)

        self.inputs = [
            (Resource.RED, GridPosition(0, 0)),
            (Resource.YELLOW, GridPosition(1, 0))
        ]
        self.outputs = [(Resource.BULB, GridPosition(0, 0))]
        self.pollution_targets = [GridPosition(2, 2)]

        self.paid_resources = [Resource.RED, Resource.YELLOW]
        self.gained_resources = [Resource.BULB]
        self.pollution_count = 1

        self.mock_grid.canBeActivated.return_value = True
        self.mock_assisting_card.checkLower.return_value = True
        self.mock_card.canGetResources.return_value = True
        self.mock_input_card_b.canGetResources.return_value = True

    def test_activate_card_failure_no_assistance_ability(self):
        self.mock_card.hasAssistance.return_value = False
        result = self.processor.activateCard(
            card=self.mock_card,
            grid=self.mock_grid,
            assisting_player=self.assisting_player_id,
            assisting_card=self.mock_assisting_card,
            inputs=self.inputs,
            outputs=self.outputs,
            pollution=self.pollution_targets
        )
        self.assertFalse(result)

    def test_activate_card_failure_cannot_be_activated(self):
        self.mock_grid.canBeActivated.return_value = False
        result = self.processor.activateCard(
            card=self.mock_card,
            grid=self.mock_grid,
            assisting_player=self.assisting_player_id,
            assisting_card=self.mock_assisting_card,
            inputs=self.inputs,
            outputs=self.outputs,
            pollution=self.pollution_targets
        )
        self.assertFalse(result)

    def test_activate_card_failure_assisting_card_check_lower_fails(self):
        self.mock_assisting_card.checkLower.return_value = False
        result = self.processor.activateCard(
            card=self.mock_card,
            grid=self.mock_grid,
            assisting_player=self.assisting_player_id,
            assisting_card=self.mock_assisting_card,
            inputs=self.inputs,
            outputs=self.outputs,
            pollution=self.pollution_targets
        )
        self.assertFalse(result)

    def test_activate_card_failure_input_card_cannot_pay(self):
        self.mock_input_card_b.canGetResources.return_value = False

        result = self.processor.activateCard(
            card=self.mock_card,
            grid=self.mock_grid,
            assisting_player=self.assisting_player_id,
            assisting_card=self.mock_assisting_card,
            inputs=self.inputs,
            outputs=self.outputs,
            pollution=self.pollution_targets
        )
        self.assertFalse(result)
        self.mock_card.getResources.assert_not_called()

    def test_activate_card_failure_pollution_card_is_none(self):
        self.mock_grid.getCard.side_effect = lambda pos: {
            GridPosition(0, 0): self.mock_card,
            GridPosition(1, 0): self.mock_input_card_b,
            GridPosition(2, 2): None,
        }.get(pos)

        result = self.processor.activateCard(
            card=self.mock_card,
            grid=self.mock_grid,
            assisting_player=self.assisting_player_id,
            assisting_card=self.mock_assisting_card,
            inputs=self.inputs,
            outputs=self.outputs,
            pollution=self.pollution_targets
        )
        self.assertFalse(result)

    def test_activate_card_normal_assistance_success(self):
        result = self.processor.activateCard(
            card=self.mock_card,
            grid=self.mock_grid,
            assisting_player=self.assisting_player_id,
            assisting_card=self.mock_assisting_card,
            inputs=self.inputs,
            outputs=self.outputs,
            pollution=self.pollution_targets
        )

        self.assertTrue(result)

        self.mock_card.getResources.assert_called_once_with([Resource.RED])
        self.mock_input_card_b.getResources.assert_called_once_with([Resource.YELLOW])
        self.mock_card.putResources.assert_called_once_with(self.gained_resources)
        self.mock_pollution_card.putResources.assert_called_once_with([Resource.POLUTION])

        self.mock_reward_manager.setReward.assert_called_once_with(
            player_id=self.assisting_player_id,
            card=self.mock_assisting_card,
            reward=self.paid_resources,
            mode="assistance"
        )
        self.assertIsNone(self.processor._current_card)

    def test_activate_card_pollution_transfer_copy_failure_count(self):
        two_pollution_targets = [GridPosition(2, 2), GridPosition(1, 1)]

        result = self.processor.activateCard(
            card=self.mock_card,
            grid=self.mock_grid,
            assisting_player=self.assisting_player_id,
            assisting_card=self.mock_assisting_card,
            inputs=[],
            outputs=[],
            pollution=two_pollution_targets
        )

        self.assertFalse(result)
        self.mock_pollution_card.getResources.assert_not_called()
        self.mock_reward_manager.setReward.assert_not_called()

    def test_activate_card_pollution_transfer_copy_success(self):
        one_pollution_targets = [GridPosition(2, 2)]

        result = self.processor.activateCard(
            card=self.mock_card,
            grid=self.mock_grid,
            assisting_player=self.assisting_player_id,
            assisting_card=self.mock_assisting_card,
            inputs=[],
            outputs=[],
            pollution=one_pollution_targets
        )

        self.assertTrue(result)

        self.mock_pollution_card.getResources.assert_called_once_with([Resource.POLUTION])

        self.assertIn(
            call([Resource.POLUTION]),
            self.mock_card.putResources.mock_calls
        )

        self.mock_reward_manager.setReward.assert_called_once_with(
            player_id=self.assisting_player_id,
            card=self.mock_assisting_card,
            reward=[Resource.POLUTION],
            mode="pollution"
        )
        self.assertIsNone(self.processor._current_card)

    def test_activate_card_failure_cannot_assist_self(self):
        with self.assertRaisesRegex(AssertionError, "Cannot assist yourself"):
            self.processor.activateCard(
                card=self.mock_card,
                grid=self.mock_grid,
                assisting_player=self.player_id,
                assisting_card=self.mock_assisting_card,
                inputs=self.inputs,
                outputs=self.outputs,
                pollution=self.pollution_targets
            )
        self.mock_reward_manager.setReward.assert_not_called()


if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ProcessActionAssistanceTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

