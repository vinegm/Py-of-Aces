from blessed import Terminal
from py_of_aces.config import Config
import sys
from typing import Callable

_SYNC_START = "\x1b[?2026h"
_SYNC_END = "\x1b[?2026l"


class BaseWindow:
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

    def tick(self) -> bool:
        """Advance window state without input. Return True to trigger a render."""
        return False

    def render(self) -> None:
        """Renders the lines from draw() centered vertically and horizontally."""
        lines = self.draw() or []

        if not isinstance(lines, (list, tuple)):
            lines = [str(lines)]

        height = int(getattr(self.term, "height", None) or 24)
        pad = max((height - len(lines)) // 2, 0)
        rows = [""] * pad + [self.term.center(line) for line in lines]

        # Overwrites the last frame row by row in one write, never blanking
        # the screen, so fast input does not flash. Terminals supporting it
        # show the frame only once complete (synchronized output).
        frame = [_SYNC_START]
        for y, row in enumerate(rows[:height]):
            frame.append(self.term.move_yx(y, 0) + row + self.term.clear_eol)
        if len(rows) < height:
            frame.append(self.term.move_yx(len(rows), 0) + self.term.clear_eos)
        frame.append(_SYNC_END)

        sys.stdout.write("".join(frame))
        sys.stdout.flush()
