import random


class Card:
    """
    Represents a single playing card.
    """

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def value(self):
        """Return Blackjack value of the card."""
        if self.rank in ["J", "Q", "K"]:
            return 10

        if self.rank == "A":
            return [1, 11]

        return int(self.rank)

    def __str__(self):
        return f"{self.rank}{self.suit}"


class BlackjackDeck:
    """
    A deck of cards for Blackjack.
    - Supports shuffling
    - Dealing cards
    - Resetting to a new shuffled deck
    """

    suits = ["s", "h", "d", "c"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(self, shuffle=True):
        self._cards = []
        self.reset_deck(shuffle=shuffle)

    def __build_deck(self):
        """Create the deck with the given number of decks."""
        for suit in self.suits:
            for rank in self.ranks:
                self._cards.append(Card(rank, suit))

    def shuffle(self):
        """Shuffle the deck in place."""
        random.shuffle(self._cards)

    def deal(self, n: int = 1) -> list[Card]:
        """
        Deal n cards from the deck.

        Returns:
            List of Card objects.
        """
        if n > len(self._cards):
            raise ValueError("Too many cards requested to deal.")

        dealt, self._cards = self._cards[:n], self._cards[n:]
        return dealt

    def get_all_cards(self):
        """Return a list of all remaining cards in the deck."""
        return self._cards[:]

    def reset_deck(self, shuffle=True):
        """Reset to a full deck again."""
        self.__build_deck()
        if shuffle:
            self.shuffle()

    def __len__(self):
        return len(self._cards)
