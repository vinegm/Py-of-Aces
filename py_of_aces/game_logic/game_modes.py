from enum import Enum


class Modes(Enum):
    BASE = 0
    NORMAL = 1
    PRACTICE = 2


class BaseGameMode:
    mode_type = Modes.BASE

    def place_bet(self, amount: int) -> bool:
        """Place a bet. Returns True if successful."""
        raise NotImplementedError

    def double_down_bet(self, current_bet: int) -> bool:
        """Handle doubling down a bet. Returns True if successful."""
        raise NotImplementedError

    def split_bet(self, current_bet: int) -> bool:
        """Handle splitting bet. Returns True if successful."""
        raise NotImplementedError

    def finish_round(self, winnings: int, total_bet: int):
        """Process round completion with winnings and total bet."""
        raise NotImplementedError

    def get_money_display(self) -> str:
        """Get the money display string for this mode."""
        raise NotImplementedError

    def get_available_money(self) -> int:
        """Get available money for betting."""
        raise NotImplementedError

    @property
    def is_game_over(self) -> bool:
        """Check if the game should end (e.g., out of money)."""
        raise NotImplementedError

    def can_afford_bet(self, amount: int) -> bool:
        """Check if player can afford a specific bet amount."""
        raise NotImplementedError


class NormalMode(BaseGameMode):
    mode_type = Modes.NORMAL

    def __init__(self, starting_money: int = 1000):
        self.player_money = starting_money

    def place_bet(self, amount: int) -> bool:
        if amount <= 0 or amount > self.player_money:
            return False

        self.player_money -= amount
        return True

    def double_down_bet(self, current_bet: int) -> bool:
        if current_bet > self.player_money:
            return False

        self.player_money -= current_bet
        return True

    def split_bet(self, current_bet: int) -> bool:
        if current_bet > self.player_money:
            return False

        self.player_money -= current_bet
        return True

    def finish_round(self, winnings: int, total_bet: int):
        self.player_money += winnings

    def get_money_display(self) -> str:
        return f"Money: ${self.player_money}"

    def get_available_money(self) -> int:
        return self.player_money

    @property
    def is_game_over(self) -> bool:
        return self.player_money <= 0

    def can_afford_bet(self, amount: int) -> bool:
        return amount <= self.player_money


class PracticeMode(BaseGameMode):
    mode_type = Modes.PRACTICE

    def __init__(self):
        self.practice_pot = 0

    def place_bet(self, amount: int) -> bool:
        return amount > 0

    def double_down_bet(self, current_bet: int) -> bool:
        return True

    def split_bet(self, current_bet: int) -> bool:
        return True

    def finish_round(self, winnings: int, total_bet: int):
        self.practice_pot += winnings - total_bet

    def get_money_display(self) -> str:
        return f"Practice Pot: {self.practice_pot:+}$"

    def get_available_money(self) -> int:
        return float("inf")

    @property
    def is_game_over(self) -> bool:
        return False

    def can_afford_bet(self, amount: int) -> bool:
        return True
