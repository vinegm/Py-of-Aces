from typing import Callable
from blessed import Terminal
from ..config import Config


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

        height = getattr(self.term, "height", None) or 24
        pad = max((int(height) - len(lines)) // 2, 0)

        print(self.term.clear)
        for _ in range(pad):
            print()

        for line in lines:
            print(self.term.center(line))
