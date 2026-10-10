from dataclasses import dataclass, field, fields
import os
from pathlib import Path
import tomllib
from typing import Any


def _config_dir() -> Path:
    """$XDG_CONFIG_HOME/pyaces, ~/.config/pyaces when it is unset or relative."""
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", ""))
    base = xdg if xdg.is_absolute() else Path.home() / ".config"
    return base / "pyaces"


def default_path() -> Path:
    """The config file read when no other is given."""
    return _config_dir() / "config.toml"


def _default_bet_options() -> dict[str, int]:
    return {
        "1": 10,
        "2": 25,
        "3": 50,
        "4": 100,
    }


@dataclass(frozen=True)
class Keys:
    up: tuple[str, ...] = ("key_up", "k")
    down: tuple[str, ...] = ("key_down", "j")
    enter: tuple[str, ...] = ("key_enter", " ")
    quit: tuple[str, ...] = ("key_escape", "q")


@dataclass(frozen=True)
class Game:
    starting_money: int = 1_000
    default_bet: int = 100
    num_decks: int = 1
    num_cards_reshuffle: int = 15
    dealer_stand_value: int = 17
    dealer_hits_soft_17: bool = True
    dealer_action_delay: float = 0.6
    max_splits: int = 3


@dataclass(frozen=True)
class Animation:
    enabled: bool = True
    reveal_steps: int = 7
    reveal_frame_duration: float = 0.12


@dataclass(frozen=True)
class Config:
    """The settings of a config file, each left out taking its default."""

    keys: Keys = Keys()
    game: Game = Game()
    animation: Animation = Animation()
    bet_options: dict[str, int] = field(default_factory=_default_bet_options)


def _read_section(section: Any, data: dict) -> Any:
    """The section with the values data has for it."""
    values = {}
    for setting in fields(section):
        if setting.name in data:
            values[setting.name] = data[setting.name]

    return section(**values)


def _config_from(data: dict) -> Config:
    return Config(
        keys=_read_section(Keys, data.get("keys", {})),
        game=_read_section(Game, data.get("game", {})),
        animation=_read_section(Animation, data.get("animation", {})),
        bet_options=data.get("bet_options", _default_bet_options()),
    )


def load_config(path: Path | None = None) -> Config:
    """Reads the config at path, or the default one."""
    if path is None:
        path = default_path()
        if not path.exists():
            return Config()

    with path.open("rb") as config_file:
        return _config_from(tomllib.load(config_file))
