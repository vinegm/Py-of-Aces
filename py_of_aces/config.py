import tomllib
from pathlib import Path

_CONFIG_DIR = Path.home() / ".config" / "pyaces"
_CONFIG_FILE = _CONFIG_DIR / "config.toml"

_DEFAULT_CONFIG = """\
[keys]
up = ["key_up", "k"]
down = ["key_down", "j"]
enter = ["key_enter", " "]
quit = ["key_escape", "q"]

[game]
starting_money = 1000
default_bet = 100
num_decks = 1
num_cards_reshuffle = 15
dealer_stand_value = 17
dealer_action_delay = 0.6
max_splits = 3

[animation]
enabled = true
reveal_steps = 7
reveal_frame_duration = 0.12

[bet_options]
"1" = 10
"2" = 25
"3" = 50
"4" = 100
"""


class Config:
    """Loads ~/.config/pyaces/config.toml (creating it from defaults if missing)
    and exposes its values as attributes."""

    def __init__(self):
        data = self.__load()
        keys = data.get("keys", {})
        game = data.get("game", {})
        animation = data.get("animation", {})

        self.up_keys: list[str] = keys.get("up", ["key_up", "k"])
        self.down_keys: list[str] = keys.get("down", ["key_down", "j"])
        self.enter_keys: list[str] = keys.get("enter", ["key_enter", " "])
        self.quit_keys: list[str] = keys.get("quit", ["key_escape", "q"])

        self.starting_money: int = game.get("starting_money", 1_000)
        self.default_bet: int = game.get("default_bet", 100)
        self.bet_options: dict[str, int] = data.get(
            "bet_options", {"1": 10, "2": 25, "3": 50, "4": 100}
        )
        self.num_decks: int = game.get("num_decks", 1)
        self.num_cards_reshuffle: int = game.get("num_cards_reshuffle", 15)
        self.dealer_stand_value: int = game.get("dealer_stand_value", 17)
        self.dealer_action_delay: float = game.get("dealer_action_delay", 0.6)
        self.max_splits: int = game.get("max_splits", 3)

        self.animations_enabled: bool = animation.get("enabled", True)
        self.reveal_steps: int = animation.get("reveal_steps", 7)
        self.reveal_frame_duration: float = animation.get(
            "reveal_frame_duration", 0.12
        )

    @staticmethod
    def __load() -> dict:
        if not _CONFIG_FILE.exists():
            _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            _CONFIG_FILE.write_text(_DEFAULT_CONFIG)

        with _CONFIG_FILE.open("rb") as config_file:
            return tomllib.load(config_file)


config = Config()
