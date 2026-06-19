import time
import math
from dataclasses import dataclass

from .utils import BaseWindow
from ..utils import get_card_ascii, join_cards
from ..game_logic import BlackjackGame, GameResult, GameState, Hand, Modes
from ..config import config

result_text_mapping = {
    GameResult.WIN: "YOU WIN",
    GameResult.BLACKJACK: "BLACKJACK! You win",
    GameResult.LOSE: "Dealer wins. You lose",
    GameResult.PUSH: "PUSH! Bet returned",
}

result_color_mapping = {
    GameResult.WIN: "green",
    GameResult.BLACKJACK: "bold_yellow",
    GameResult.LOSE: "red",
    GameResult.PUSH: "yellow",
}


@dataclass
class _RevealAnimation:
    frames: list[str]
    frame_duration: float
    frame_index: int = 0
    _next_frame_at: float = 0.0

    def __post_init__(self) -> None:
        self._next_frame_at = time.monotonic() + self.frame_duration

    def current_frame(self) -> str:
        return self.frames[self.frame_index]

    def advance(self, now: float) -> bool:
        """Move to the next frame if due. Returns False once the animation is finished."""
        if self.frame_index >= len(self.frames) - 1:
            return False

        if now >= self._next_frame_at:
            self.frame_index += 1
            self._next_frame_at = now + self.frame_duration

        return True


class GameWindow(BaseWindow):
    _REVEAL_RING_WIDTH = 0.8
    _REVEAL_RING_CHAR = "/"
    _REVEAL_ORIGIN_X = -0.75
    _REVEAL_ORIGIN_Y = -0.75
    _REVEAL_X_SCALE = 0.6
    _REVEAL_Y_SCALE = 1.0

    def __init__(
        self, game: BlackjackGame, menu_window: str, betting_window: str, **kwargs
    ):
        super().__init__(**kwargs)
        self.game = game
        self.message = ""
        self.menu_window = menu_window
        self.betting_window = betting_window
        self._last_state = self.game.state
        self._dealer_next_action_at = 0.0
        self._hand_states: dict[tuple[str, int], tuple[int, bool]] = {}
        self._reveal_animations: dict[tuple[str, int], _RevealAnimation] = {}

    def draw(self):
        lines: list[str] = []

        mode_text = ""
        is_practice_mode = self.game.mode == Modes.PRACTICE
        if is_practice_mode:
            mode_text = " (PRACTICE)"

        title = self.term.bold(
            f"{self.term.reverse}PY OF ACES{mode_text}{self.term.normal}"
        )
        lines.append(title)
        lines.append("")

        money_info = self.game.get_money_display
        money_info += f" | Total Bet: ${self.game.total_bet}"
        if is_practice_mode:
            money_info += f" | Shoe: {len(self.game.deck)} cards"

        lines.append(money_info)
        lines.append("")

        lines.extend(self.__draw_hands())
        lines.append("")

        if self.game.state == GameState.DEALER_TURN:
            lines.append(self.term.yellow("Dealer playing..."))
            lines.append("")

        if self.game.state == GameState.ROUND_FINISHED:
            lines.extend(self.__draw_game_result())
            lines.append("")

        if self.message:
            styled_message = self.term.red(self.message)
            lines.append(styled_message)
            lines.append("")

        if self.game.will_reshuffle:
            styled_message = self.term.yellow(
                "After this round, the deck will be reshuffled."
            )
            lines.append(styled_message)
            lines.append("")

        lines.extend(self.__draw_controls())

        return lines

    def tick(self) -> bool:
        render_needed = self.__advance_reveal_animations()
        current_state = self.game.state
        if current_state != self._last_state:
            self._last_state = current_state
            if current_state == GameState.DEALER_TURN:
                self._dealer_next_action_at = (
                    time.monotonic() + config.dealer_action_delay
                )
            return render_needed

        if current_state != GameState.DEALER_TURN:
            return render_needed

        now = time.monotonic()
        if ("dealer", 0) in self._reveal_animations:
            self._dealer_next_action_at = now + config.dealer_action_delay
            return render_needed

        if now < self._dealer_next_action_at:
            return render_needed

        if self.game.advance_dealer_turn():
            self._dealer_next_action_at = now + config.dealer_action_delay
            return True

        return render_needed

    def __draw_hands(self) -> list[str]:
        lines: list[str] = []
        lines.append("DEALER")

        dealer_hand = self.game.dealer_hand
        lines.extend(self.__draw_cards(dealer_hand, "dealer", 0))
        lines.append("")

        lines.append("PLAYER")

        has_multiple_hands = len(self.game.player_hands) > 1
        for hand_index, hand in enumerate(self.game.player_hands):
            if has_multiple_hands:
                hand_title = f"Hand {hand_index + 1} ({self.game.bets[hand_index]}$)"
                if hand_index == self.game.current_hand_index:
                    hand_title += " (ACTIVE)"

                lines.append(hand_title)

            lines.extend(self.__draw_cards(hand, "player", hand_index))

        self.__cleanup_hand_state()

        return lines

    def __draw_cards(self, hand: Hand, owner: str, hand_index: int) -> list[str]:
        lines: list[str] = []
        card_arts = []
        has_hidden = hand.has_hidden_card
        key = (owner, hand_index)
        self.__update_reveal_state(hand, key)
        animation = self._reveal_animations.get(key)

        showing_cards = hand.get_showing_cards()
        for card in showing_cards:
            card_art = get_card_ascii(card.rank, card.suit)
            card_arts.append(self.__colorize_card(card_art, card.suit))

        if animation and showing_cards:
            card_arts[-1] = self.__colorize_card(
                animation.current_frame(), showing_cards[-1].suit
            )

        if has_hidden:
            hidden_art = get_card_ascii("?", "?", face_down_text="HIDDEN")
            card_arts.append(self.__paint_card(hidden_art, self.term.bright_black))

        combined_cards = join_cards(*card_arts)
        for line in combined_cards.splitlines():
            lines.append(line)

        hand_info = ""
        if has_hidden:
            hand_info += f"Showing: {hand.get_showing_value()}"
            lines.append(hand_info)
            return lines

        hand_info += f"Total: {hand.get_showing_value()}"
        if hand.is_blackjack:
            hand_info += " (BLACKJACK!)"

        elif hand.is_bust:
            hand_info += " (BUST!)"

        lines.append(hand_info)
        return lines

    def __colorize_card(self, card_art: str, suit: str) -> str:
        """Paint hearts and diamonds red, leave black suits as-is."""
        if suit not in ("h", "d"):
            return card_art

        return self.__paint_card(card_art, self.term.red)

    def __paint_card(self, card_art: str, color) -> str:
        return "\n".join(color(line) for line in card_art.splitlines())

    def __update_reveal_state(self, hand: Hand, key: tuple[str, int]) -> None:
        showing_cards = hand.get_showing_cards()
        showing_count = len(showing_cards)
        has_hidden = hand.has_hidden_card

        if config.animations_enabled:
            prev = self._hand_states.get(key)
            if prev:
                prev_showing, prev_hidden = prev
                if prev_hidden and not has_hidden and hand.cards:
                    self.__start_reveal_animation(key, hand.cards[-1])
                elif showing_count > prev_showing:
                    self.__start_reveal_animation(key, showing_cards[-1])
            elif showing_count:
                self.__start_reveal_animation(key, showing_cards[-1])

        self._hand_states[key] = (showing_count, has_hidden)

    def __start_reveal_animation(self, key: tuple[str, int], card) -> None:
        frames = self.__build_reveal_frames(card)
        self._reveal_animations[key] = _RevealAnimation(
            frames, config.reveal_frame_duration
        )

    def __build_reveal_frames(self, card) -> list[str]:
        back = get_card_ascii("?", "?", face_down_text="REVEAL")
        face = get_card_ascii(card.rank, card.suit)
        back_lines = back.splitlines()
        face_lines = face.splitlines()
        width = len(back_lines[0]) if back_lines else 0
        height = len(back_lines)

        origin_x, origin_y = self._REVEAL_ORIGIN_X, self._REVEAL_ORIGIN_Y
        x_scale, y_scale = self._REVEAL_X_SCALE, self._REVEAL_Y_SCALE
        steps = max(config.reveal_steps, 1)

        max_dist = (
            math.hypot(
                max(width - 1 - origin_x, 0) * x_scale,
                max(height - 1 - origin_y, 0) * y_scale,
            )
            or 1.0
        )

        frames = [back]
        for step in range(1, steps + 1):
            radius = max_dist * step / steps
            frames.append(
                self.__blend_card_radial(
                    back_lines,
                    face_lines,
                    radius,
                    origin_x,
                    origin_y,
                    x_scale,
                    y_scale,
                )
            )

        return frames

    def __blend_card_radial(
        self,
        back_lines: list[str],
        face_lines: list[str],
        radius: float,
        origin_x: float,
        origin_y: float,
        x_scale: float,
        y_scale: float,
    ) -> str:
        ring_width = self._REVEAL_RING_WIDTH
        ring_char = self._REVEAL_RING_CHAR

        blended_lines: list[str] = []
        for row_index, (back_line, face_line) in enumerate(zip(back_lines, face_lines)):
            blended = []
            for col_index, back_char in enumerate(back_line):
                dist = math.hypot(
                    (col_index - origin_x) * x_scale,
                    (row_index - origin_y) * y_scale,
                )
                if dist <= radius and col_index < len(face_line):
                    blended.append(face_line[col_index])
                elif (
                    dist <= radius + ring_width
                    and back_char not in "+-|"
                    and col_index < len(face_line)
                ):
                    blended.append(ring_char)
                else:
                    blended.append(back_char)
            blended_lines.append("".join(blended))

        return "\n".join(blended_lines)

    def __advance_reveal_animations(self) -> bool:
        if not self._reveal_animations:
            return False

        now = time.monotonic()
        to_remove = [
            key
            for key, animation in self._reveal_animations.items()
            if not animation.advance(now)
        ]
        for key in to_remove:
            self._reveal_animations.pop(key, None)

        return True

    def __cleanup_hand_state(self) -> None:
        active_keys = {("dealer", 0)}
        active_keys.update(
            ("player", index) for index in range(len(self.game.player_hands))
        )

        for key in list(self._hand_states.keys()):
            if key not in active_keys:
                self._hand_states.pop(key, None)
                self._reveal_animations.pop(key, None)

    def __draw_game_result(self) -> list[str]:
        lines: list[str] = []
        results = self.game.results

        if len(results) > 1:
            for hand_index, result in enumerate(results):
                if result is None:
                    continue
                lines.append(f"Hand {hand_index + 1}: {self.__style_result(result)}")
        elif results[0] is not None:
            lines.append(self.__style_result(results[0]))

        net_result = self.game.get_winnings() - self.game.total_bet
        if net_result > 0:
            styled_result = self.term.bold_green(f"Result: +{net_result}$")
        elif net_result < 0:
            styled_result = self.term.bold_red(f"Result: {net_result}$")
        else:
            styled_result = self.term.bold_yellow("Result: ±0$")

        lines.append(styled_result)
        return lines

    def __style_result(self, result: GameResult) -> str:
        color = getattr(self.term, result_color_mapping[result])
        return color(result_text_mapping[result])

    def __draw_controls(self) -> list[str]:
        controls = ""
        match self.game.state:
            case GameState.PLAYER_TURN:
                controls += "[h] Hit  [SPACE] Stand"

                if self.game.can_double_down:
                    controls += "  [d] Double Down"

                if self.game.can_split:
                    controls += "  [p] Split"

                controls += "  [q] Quit"

            case GameState.ROUND_FINISHED:
                if self.game.available_money + self.game.get_winnings() > 0:
                    controls += "[ENTER] New Round  "
                controls += "[r] Restart money  "
                controls += "[q] Quit"

        return [controls]

    def handle_input(self, key: str) -> None:
        """Handle user input based on the current game state."""
        self.message = ""
        key = key.lower()

        if key in config.quit_keys:
            self.switch_win(self.menu_window)
            return

        if self.game.state == GameState.PLAYER_TURN:
            self.__handle_player_turn_input(key)
            return

        if self.game.state != GameState.ROUND_FINISHED:
            return

        if key == "r":
            self.game.reset_money()
            self.game.start_new_round()
            self.switch_win(self.betting_window)
            return

        if key not in config.enter_keys:
            return

        self.game.finish_round()
        if self.game.is_game_over:
            self.message = "Game Over! No money left."
            return

        self.game.start_new_round()
        self.switch_win(self.betting_window)

    def __handle_player_turn_input(self, key: str):
        """Handle input during the player's turn."""
        match key:
            case "h":
                if not self.game.hit():
                    self.message = "Cannot hit right now!"

            case " ":
                if not self.game.stand():
                    self.message = "Cannot stand right now!"

            case "d":
                if not self.game.double_down():
                    self.message = "Cannot double down!"

            case "p":
                if not self.game.split():
                    self.message = "Cannot split right now!"
