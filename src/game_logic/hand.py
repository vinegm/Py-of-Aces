from typing import List
from src.game_logic.deck import Card

class Hand:
    def __init__(self, cards: List[Card] = [], hidden_card_default: bool = False):
        self.cards: List[Card] = cards
        self.has_hidden_card = hidden_card_default
        self.hidden_card_default = hidden_card_default

    @property
    def is_bust(self) -> bool:
        return self.get_value() > 21

    @property
    def can_split(self) -> bool:
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.get_value() == 21

    @property
    def can_double_down(self) -> bool:
        return len(self.cards) == 2

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def get_value(self) -> int:
        return self.__count_cards(self.cards)

    def get_showing_value(self) -> int:
        if not self.has_hidden_card:
            return self.get_value()
        
        return self.__count_cards(self.cards[:-1])
    
    def get_cards(self) -> List[Card]:
        return self.cards

    def get_showing_cards(self) -> List[Card]:
        if not self.has_hidden_card:
            return self.cards
        
        return self.cards[:-1]

    def __count_cards(self, cards) -> int:
        total = 0
        aces = 0

        for card in cards:
            value = card.value()
            if isinstance(value, list):
                aces += 1
                total += 11
            else:
                total += value

        # Adjust for aces
        while total > 21 and aces:
            total -= 10
            aces -= 1

        return total

    def reset(self):
        self.cards = []
        self.has_hidden_card = self.hidden_card_default