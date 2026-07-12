import argparse
from importlib.metadata import version
from pathlib import Path
import random
import sys
import tomllib

from .config import Config, load_config
from .tui_handler import TuiHandler
from .windows import MenuWindow, GameWindow, BettingWindow, SizeWarningWindow
from .game_logic.blackjack_game import BlackjackGame


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="pyaces", description="A blackjack TUI written in Python"
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {version('py-of-aces')}"
    )

    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--config",
        type=Path,
        metavar="PATH",
        help="load the config from PATH instead of the default location",
    )
    source.add_argument(
        "--no-config",
        action="store_true",
        help="ignore the config file and run with the built-in defaults",
    )

    parser.add_argument(
        "--seed",
        metavar="SEED",
        help="shuffle the same way every run, as for a recorded demo",
    )

    return parser.parse_args(argv)


def config_of(args: argparse.Namespace) -> Config:
    """The config the flags ask for, exiting with the reason it can not be read."""
    if args.no_config:
        return Config()

    try:
        return load_config(args.config)
    except (OSError, tomllib.TOMLDecodeError) as err:
        sys.exit(f"pyaces: could not read the config: {err}")


def run(argv: list[str] | None = None):
    """Start Py of Aces"""
    MIN_HEIGHT = 30
    MIN_WIDTH = 25

    args = parse_args(argv)
    config = config_of(args)

    if args.seed is not None:
        random.seed(args.seed)
    tui = TuiHandler(config, min_height=MIN_HEIGHT, min_width=MIN_WIDTH)
    game_instance = BlackjackGame(config)

    tui.add_window("menu", MenuWindow, betting_window="betting", game=game_instance)
    tui.add_window(
        "betting",
        BettingWindow,
        menu_window="menu",
        game_window="game",
        game=game_instance,
    )
    tui.add_window(
        "game",
        GameWindow,
        menu_window="menu",
        betting_window="betting",
        game=game_instance,
    )
    tui.add_window(
        "size_warning", SizeWarningWindow, min_width=MIN_WIDTH, min_height=MIN_HEIGHT
    )

    tui.start("menu")
