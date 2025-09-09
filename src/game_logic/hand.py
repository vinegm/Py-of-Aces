from typing import List
from src.game_logic.deck import Card

class Hand:
    def __init__(self, cards: List[Card] = None):
        self.cards: List[Card] = []
        self.is_bust = False
        if cards:
            self.cards = cards

    def add_card(self, card: Card):
        self.cards.append(card)
        if self.get_value() > 21:
            self.is_bust = True

    def get_value(self) -> int:
        total = 0
        aces = 0

        for card in self.cards:
            value = card.value()
            if not isinstance(value, list):
                total += value
                continue
            
            aces += 1
            total += 11
            

        # Adjust for aces if busted
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total

    def is_blackjack(self) -> bool:
        if len(self.cards) != 2:
            return False
        
        return self.get_value() == 21

    def can_split(self) -> bool:
        return True
        if len(self.cards) != 2:
            return False
        
        return self.cards[0].rank == self.cards[1].rank

    def can_double_down(self) -> bool:
        return len(self.cards) == 2

    def reset(self):
        self.cards = []
        self.is_bust = False