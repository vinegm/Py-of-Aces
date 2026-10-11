from dataclasses import Field, dataclass, field, fields
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
    starting_money: int = field(default=1_000, metadata={"min": 1})
    default_bet: int = field(default=100, metadata={"min": 1})
    num_decks: int = field(default=1, metadata={"min": 1})
    num_cards_reshuffle: int = field(default=15, metadata={"min": 0})
    dealer_stand_value: int = field(default=17, metadata={"min": 2, "max": 21})
    dealer_hits_soft_17: bool = True
    dealer_action_delay: float = field(default=0.6, metadata={"min": 0})
    max_splits: int = field(default=3, metadata={"min": 0})


@dataclass(frozen=True)
class Animation:
    enabled: bool = True
    reveal_steps: int = field(default=7, metadata={"min": 1})
    reveal_frame_duration: float = field(default=0.12, metadata={"min": 0})


@dataclass(frozen=True)
class Config:
    """The settings of a config file, each left out or invalid taking its
    default. The warnings say what was wrong with the file."""

    keys: Keys = Keys()
    game: Game = Game()
    animation: Animation = Animation()
    bet_options: dict[str, int] = field(default_factory=_default_bet_options)
    warnings: list[str] = field(default_factory=list)


_SECTIONS = {
    "keys",
    "game",
    "animation",
    "bet_options",
}


def _keys_problem(value: Any) -> str | None:
    if not isinstance(value, list) or not value:
        return "must be a list of keys"

    for key in value:
        if not isinstance(key, str) or not key:
            return "must be a list of keys"

    return None


def _number_problem(setting: Field, value: Any) -> str | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "must be a number"

    if isinstance(setting.default, int) and not isinstance(value, int):
        return "must be a whole number"

    low = setting.metadata.get("min")
    if low is not None and value < low:
        return f"must be at least {low}"

    high = setting.metadata.get("max")
    if high is not None and value > high:
        return f"must be at most {high}"

    return None


def _problem_with(setting: Field, value: Any) -> str | None:
    """Why the value can't be used for the setting, if it can't."""
    if isinstance(setting.default, tuple):
        return _keys_problem(value)

    if isinstance(setting.default, bool):
        return None if isinstance(value, bool) else "must be true or false"

    return _number_problem(setting, value)


def _usable(value: Any) -> Any:
    """The value as the game wants it: keys are lowercase, as input is."""
    if not isinstance(value, list):
        return value

    keys = []
    for key in value:
        keys.append(key.lower())

    return tuple(keys)


def _warn_unknown(
    data: dict,
    known: set[str],
    prefix: str,
    warnings: list[str],
) -> None:
    for key in data:
        if key not in known:
            warnings.append(f"{prefix}{key}: unknown setting, ignored")


def _read_section(section: Any, name: str, data: Any, warnings: list[str]) -> Any:
    """The section with the values data has for it, warning of those invalid."""
    if not isinstance(data, dict):
        warnings.append(f"{name}: must be a table, using its defaults")
        return section()

    known = set()
    values = {}
    for setting in fields(section):
        known.add(setting.name)
        if setting.name not in data:
            continue

        value = data[setting.name]
        problem = _problem_with(setting, value)
        if problem:
            warnings.append(f"{name}.{setting.name}: {problem}, using the default")
            continue

        values[setting.name] = _usable(value)

    _warn_unknown(data, known, f"{name}.", warnings)

    return section(**values)


def _bet_option_problem(key: str, bet: Any) -> str | None:
    if len(key) != 1:
        return f"{key!r} must be a single key"

    if isinstance(bet, bool) or not isinstance(bet, int) or bet < 1:
        return f"the bet of {key!r} must be a whole number of at least 1"

    return None


def _read_bet_options(data: Any, warnings: list[str]) -> dict[str, int]:
    """The quick bets, or the default ones if any of them is invalid."""
    if not isinstance(data, dict):
        warnings.append("bet_options: must be a table, using the defaults")
        return _default_bet_options()

    options = {}
    for key, bet in data.items():
        problem = _bet_option_problem(key, bet)
        if problem:
            warnings.append(f"bet_options: {problem}, using the defaults")
            return _default_bet_options()

        options[key.lower()] = bet

    return options


def _config_from(data: dict) -> Config:
    warnings: list[str] = []
    _warn_unknown(data, _SECTIONS, "", warnings)

    return Config(
        keys=_read_section(Keys, "keys", data.get("keys", {}), warnings),
        game=_read_section(Game, "game", data.get("game", {}), warnings),
        animation=_read_section(
            Animation,
            "animation",
            data.get("animation", {}),
            warnings,
        ),
        bet_options=_read_bet_options(
            data.get("bet_options", _default_bet_options()),
            warnings,
        ),
        warnings=warnings,
    )


def load_config(path: Path | None = None) -> Config:
    """Reads the config at path, or the default one."""
    file = path or default_path()
    try:
        with file.open("rb") as config_file:
            return _config_from(tomllib.load(config_file))
    except FileNotFoundError as err:
        if path is None:
            return Config()

        return Config(warnings=[f"could not load the config: {err}"])
    except (OSError, tomllib.TOMLDecodeError) as err:
        return Config(warnings=[f"could not load the config: {err}"])
