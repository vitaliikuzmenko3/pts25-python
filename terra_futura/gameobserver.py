# pylint: disable=invalid-name, too-many-arguments, too-many-positional-arguments
from __future__ import annotations
from typing import List
from terra_futura.interfaces import InterfaceGameObserver, InterfaceCard
from terra_futura.card import Resource


class GameObserver(InterfaceGameObserver):

    def __init__(self, cards: List[InterfaceCard]):
        self.cards = cards
        self.activated_effects_log: List[str] = []

    def activate_effect(self, card_index: int, effect_type: str = "upper") -> None:
        card = self.cards[card_index]

        effect = card.upper_effect if effect_type == "upper" else card.lower_effect

        if effect.add_resources:
            card.put_resources(effect.add_resources)

        for old, new in effect.transform_resources_into.items():
            while old in card.resources:
                card.resources.remove(old)
                card.resources.append(new)

        for _ in range(effect.pollution):
            card.put_resources([Resource.POLLUTION])

        self.activated_effects_log.append(
            f"Card {card_index} activated {effect_type}: {effect.describe()}"
        )

    def game_state(self) -> str:
        out = []
        for i, c in enumerate(self.cards):
            out.append(f"Card {i}: {c.state()}")
        return "\n".join(out)

    def get_total_pollution(self) -> int:
        total = 0
        for card in self.cards:
            total += sum(r == Resource.POLLUTION for r in card.resources)
        return total
