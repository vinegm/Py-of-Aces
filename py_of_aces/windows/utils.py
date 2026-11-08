from blessed import Terminal
from py_of_aces.config import Config
import sys
from typing import Callable

_SYNC_START = "\x1b[?2026h"
_SYNC_END = "\x1b[?2026l"

# The outer width a window is at least drawn at, border included,
# so going from one to another doesn't make the box jump.
WINDOW_WIDTH = 59

# Border and padding, on each side of a window.
_FRAME_SIDE = 2


def key_label(keys: tuple[str, ...]) -> str:
    """How a key hint names a binding: its plain character, or else its first key."""
    for key in keys:
        if len(key) == 1 and key != " ":
            return key

    if keys[0] == " ":
        return "space"

    return keys[0].lower().removeprefix("key_")


def move_label(up: tuple[str, ...], down: tuple[str, ...]) -> str:
    """How a key hint names a pair of up and down bindings, "jk" by default."""
    down_label = key_label(down)
    up_label = key_label(up)

    if len(down_label) == 1 and len(up_label) == 1:
        return down_label + up_label

    return f"{down_label}/{up_label}"


class BaseWindow:
    framed = True

    def __init__(
        self,
        terminal_instance: Terminal,
        switch_win: Callable[[str], None],
        stop_process: Callable[[], None],
        config: Config,
    ):
        self.term = terminal_instance
        self.config = config
        self.switch_win = switch_win
        self.stop_process = stop_process

    def draw(self):
        raise NotImplementedError

    def handle_input(self, _: str):
        raise NotImplementedError

    def hints(self) -> list[tuple[str, str]]:
        """What the key hints bar shows: pairs of what a key does, and the key."""
        return []

    def tick(self) -> bool:
        """Advance window state without input. Return True to trigger a render."""
        return False

    def __frame(self, lines: list[str]) -> list[str]:
        """The lines inside the window's rounded border, each centered."""
        inner = WINDOW_WIDTH - 2 * _FRAME_SIDE
        for line in lines:
            inner = max(inner, self.term.length(line))

        rule = "─" * (inner + 2)
        framed = [f"╭{rule}╮"]
        for line in lines:
            framed.append(f"│ {self.term.center(line, inner)} │")
        framed.append(f"╰{rule}╯")

        return framed

    def __hints_bar(self) -> str:
        """The key hints bar, cut to fit the terminal."""
        parts: list[str] = []
        for desc, key in self.hints():
            parts.append(f"{desc}: {key}")

        return self.term.truncate(" | ".join(parts), self.term.width)

    def render(self) -> None:
        """Renders the window from draw() centered on the
        screen, with the key hints bar on the row under it."""
        lines = self.draw() or []

        # A window that handed over to another during draw() has nothing to show.
        if not lines:
            return

        if not isinstance(lines, (list, tuple)):
            lines = [str(lines)]

        if self.framed:
            lines = self.__frame(list(lines))

        height = int(getattr(self.term, "height", None) or 24)
        space = height - 1
        pad = max((space - len(lines)) // 2, 0)

        rows = [""] * pad
        for line in lines:
            rows.append(self.term.center(line))

        # Overwrites the last frame row by row in one write, never blanking
        # the screen, so fast input does not flash. Terminals supporting it
        # show the frame only once complete (synchronized output).
        frame = [_SYNC_START]
        for y, row in enumerate(rows[:space]):
            frame.append(self.term.move_yx(y, 0) + row + self.term.clear_eol)
        if len(rows) < space:
            frame.append(self.term.move_yx(len(rows), 0) + self.term.clear_eos)
        frame.append(
            self.term.move_yx(space, 0) + self.__hints_bar() + self.term.clear_eol,
        )
        frame.append(_SYNC_END)

        sys.stdout.write("".join(frame))
        sys.stdout.flush()
