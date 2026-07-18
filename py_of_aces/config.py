import os
from pathlib import Path
import tomllib


def _config_dir() -> Path:
    """$XDG_CONFIG_HOME/pyaces, ~/.config/pyaces when it is unset or relative."""
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", ""))
    base = xdg if xdg.is_absolute() else Path.home() / ".config"
    return base / "pyaces"


def default_path() -> Path:
    """The config file read when no other is given."""
    return _config_dir() / "config.toml"


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
dealer_hits_soft_17 = true
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
    """The settings of a config file's data, each left out taking its default."""

    def __init__(self, data: dict | None = None):
        data = data or {}
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
            "bet_options",
            {"1": 10, "2": 25, "3": 50, "4": 100},
        )
        self.num_decks: int = game.get("num_decks", 1)
        self.num_cards_reshuffle: int = game.get("num_cards_reshuffle", 15)
        self.dealer_stand_value: int = game.get("dealer_stand_value", 17)
        self.dealer_hits_soft_17: bool = game.get("dealer_hits_soft_17", True)
        self.dealer_action_delay: float = game.get("dealer_action_delay", 0.6)
        self.max_splits: int = game.get("max_splits", 3)

        self.animations_enabled: bool = animation.get("enabled", True)
        self.reveal_steps: int = animation.get("reveal_steps", 7)
        self.reveal_frame_duration: float = animation.get(
            "reveal_frame_duration",
            0.12,
        )


def load_config(path: Path | None = None) -> Config:
    """Reads the config at path, or the default one, created from the defaults
    when missing."""
    if path is None:
        path = default_path()
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_DEFAULT_CONFIG)

    with path.open("rb") as config_file:
        return Config(tomllib.load(config_file))
