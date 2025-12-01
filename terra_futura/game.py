from typing import Dict, List, Optional, Tuple
from enum import Enum

from interfaces import TerraFuturaInterface
from simple_types import Resource, GridPosition, CardSource, Deck, GameState
from grid import Grid
from select_reward import SelectReward
from activation_pattern import ActivationPattern
from scoring_method import ScoringMethod
from process_action import ProcessAction
from process_action_assistance import ProcessActionAssistance
from pile import Pile


class Player:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.grid = Grid()
        self.activation_patterns: List[ActivationPattern] = []
        self.scoring_methods: List[ScoringMethod] = []
        self.selected_pattern: Optional[ActivationPattern] = None
        self.selected_scoring: Optional[ScoringMethod] = None


class Game(TerraFuturaInterface):
    def __init__(self, player_ids: List[int]):

        if len(player_ids) < 2 or len(player_ids) > 5:
            raise ValueError("Game requires 2-5 players")

        self.state = GameState.TAKE_CARD_NO_CARD_DISCARDED

        self.players: Dict[int, Player] = {}
        for player_id in player_ids:
            self.players[player_id] = Player(player_id)

        self.player_order = player_ids.copy()
        self.starting_player = player_ids[0]
        self.on_turn = self.starting_player
        self.turn_number = 1

        self.piles: Dict[Deck, Pile] = {
            Deck.I: Pile(),
            Deck.II: Pile()
        }

        self.select_reward = SelectReward()
        self.process_action = ProcessAction()
        self.process_action_assistance = ProcessActionAssistance(self.select_reward)

        self._cards_to_activate: List[GridPosition] = []
        self._activation_complete = False

        self._final_activation_phase: bool = False
        self._final_activated_players: set[int] = set()

    def take_card(
        self,
        player_id: int,
        source: CardSource,
        destination: GridPosition
    ) -> bool:
        if not self._validate_player_turn(player_id):
            return False

        if self.state not in [
            GameState.TAKE_CARD_NO_CARD_DISCARDED,
            GameState.TAKE_CARD_CARD_DISCARDED
        ]:
            return False

        if self._final_activation_phase:
            return False

        player = self.players[player_id]

        if not player.grid.can_put_card(destination):
            return False

        pile = self.piles[source.deck]
        card = pile.get_card(source.index)
        if card is None:
            return False

        pile.take_card(source.index)
        player.grid.put_card(destination, card)

        row_cards, col_cards = player.grid.get_row_and_column(destination)
        unique_positions = list({(pos.x, pos.y): pos for pos in row_cards + col_cards}.values())
        self._cards_to_activate = unique_positions
        self._activation_complete = False
        self.state = GameState.ACTIVATE_CARD
        return True

    def discard_last_card_from_deck(self, player_id: int, deck: Deck) -> bool:
        if not self._validate_player_turn(player_id):
            return False
        if self.state != GameState.TAKE_CARD_NO_CARD_DISCARDED:
            return False
        if self._final_activation_phase:
            return False

        pile = self.piles[deck]
        pile.remove_last_card()

        self.state = GameState.TAKE_CARD_CARD_DISCARDED
        return True

    def activate_card(
        self,
        player_id: int,
        card: GridPosition,
        inputs: List[Tuple[Resource, GridPosition]],
        outputs: List[Tuple[Resource, GridPosition]],
        pollution: List[GridPosition],
        other_player_id: Optional[int],
        other_card: Optional[GridPosition]
    ) -> bool:
        if not self._validate_player_turn(player_id):
            return False

        if self.state != GameState.ACTIVATE_CARD:
            return False

        player = self.players[player_id]
        card_obj = player.grid.get_card(card)
        if card_obj is None:
            return False
        if not player.grid.can_be_activated(card):
            return False

        is_assistance = other_player_id is not None and other_card is not None

        if is_assistance:
            if other_player_id not in self.players:
                return False
            other_player = self.players[other_player_id]
            other_card_obj = other_player.grid.get_card(other_card)
            if other_card_obj is None:
                return False

            success = self.process_action_assistance.activate_card(
                card=card_obj,
                grid=player.grid,
                assisting_player=other_player_id,
                assisting_card=other_card_obj,
                inputs=inputs,
                outputs=outputs,
                pollution=pollution
            )
            if not success:
                return False

            reward_resources = [resource for resource, _ in outputs]
            self.select_reward.set_reward(
                player=other_player_id,
                card=other_card_obj,
                reward=reward_resources
            )

            self.state = GameState.SELECT_REWARD

        else:
            success = self.process_action.activate_card(
                card=card_obj,
                grid=player.grid,
                inputs=inputs,
                outputs=outputs,
                pollution=pollution
            )
            if not success:
                return False

        player.grid.set_activated(card)

        if card in self._cards_to_activate:
            self._cards_to_activate.remove(card)

        if len(self._cards_to_activate) == 0 and not is_assistance:
            self._activation_complete = True

        return True

    def select_reward(self, player_id: int, resource: Resource) -> bool:
        if self.state != GameState.SELECT_REWARD:
            return False
        if self.select_reward.get_pending_player() != player_id:
            return False

        try:
            self.select_reward.select_reward(resource)
        except ValueError:
            return False

        self.select_reward.clear()
        self.state = GameState.ACTIVATE_CARD
        return True

    def turn_finished(self, player_id: int) -> bool:
        if not self._validate_player_turn(player_id):
            return False
        if self.state != GameState.ACTIVATE_CARD:
            return False
        if not self._activation_complete:
            return False

        player = self.players[player_id]
        player.grid.end_turn()
        self._cards_to_activate = []
        self._activation_complete = False

        total_turns = len(self.player_order) * 9

        if not self._final_activation_phase:

            self.turn_number += 1

            if self.turn_number > total_turns:
                self._final_activation_phase = True
                self.state = GameState.SELECT_ACTIVATION_PATTERN
                self.on_turn = self.starting_player
                self._final_activated_players.clear()
                return True

            current_index = self.player_order.index(self.on_turn)
            next_index = (current_index + 1) % len(self.player_order)
            self.on_turn = self.player_order[next_index]

            self.state = GameState.TAKE_CARD_NO_CARD_DISCARDED
            return True

        self._final_activated_players.add(player_id)

        if len(self._final_activated_players) == len(self.player_order):
            self.state = GameState.SELECT_SCORING_METHOD
            self.on_turn = self.starting_player
            return True

        current_index = self.player_order.index(self.on_turn)
        next_index = (current_index + 1) % len(self.player_order)
        self.on_turn = self.player_order[next_index]
        self.state = GameState.SELECT_ACTIVATION_PATTERN
        return True

    def select_activation_pattern(self, player_id: int, card: int) -> bool:
        if self.state != GameState.SELECT_ACTIVATION_PATTERN:
            return False
        if player_id != self.on_turn:
            return False
        if not self._final_activation_phase:
            return False
        if player_id not in self.players:
            return False

        player = self.players[player_id]

        if card < 0 or card >= len(player.activation_patterns):
            return False
        if player.selected_pattern is not None:
            return False

        pattern_obj = player.activation_patterns[card]
        pattern_obj.select()
        player.selected_pattern = pattern_obj

        self._cards_to_activate = pattern_obj._pattern.copy()
        self._activation_complete = False
        self.state = GameState.ACTIVATE_CARD
        return True

    def select_scoring(self, player_id: int, card: int) -> bool:
        if self.state != GameState.SELECT_SCORING_METHOD:
            return False
        if player_id not in self.players:
            return False
        if self.on_turn != player_id:
            return False

        player = self.players[player_id]

        if card < 0 or card >= len(player.scoring_methods):
            return False
        if player.selected_scoring is not None:
            return False

        method = player.scoring_methods[card]
        player.selected_scoring = method

        player_resources = self._get_player_resources(player_id)
        method.select_this_method_and_calculate(player_resources)

        all_selected = all(
            p.selected_scoring is not None
            for p in self.players.values()
        )

        if all_selected:
            self.state = GameState.FINISH
            return True

        current_index = self.player_order.index(self.on_turn)
        next_index = (current_index + 1) % len(self.player_order)
        self.on_turn = self.player_order[next_index]

        return True

    def _validate_player_turn(self, player_id: int) -> bool:
        return self.on_turn == player_id

    def _get_player_resources(self, player_id: int) -> List[Resource]:
        player = self.players[player_id]
        total: List[Resource] = []

        for pos, card in player.grid._cards.items():
            for r in card.resources:
                if r != Resource.POLLUTION:
                    total.append(r)

        return total

    def get_state(self) -> GameState:
        return self.state

    def get_current_player(self) -> int:
        return self.on_turn

    def get_turn_number(self) -> int:
        return self.turn_number

    def get_winner(self) -> Optional[int]:
        if self.state != GameState.FINISH:
            return None

        best_player = None
        best_score = -1

        for pid, player in self.players.items():
            if player.selected_scoring is None:
                continue

            resources = self._get_player_resources(pid)
            points = player.selected_scoring.select_this_method_and_calculate(resources).value

            if points > best_score:
                best_score = points
                best_player = pid

        return best_player
