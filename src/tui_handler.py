import signal
from blessed import Terminal
from src.windows.utils import BaseWindow


class TuiHandler:
    """
    A class to handle the TUI application.

    args:
        min_height: The minimum height of the terminal.
        min_width: The minimum width of the terminal.
        windows: A dictionary of windows to add to the TUI.
        terminal_instance: An instance of blessed.Terminal to use.
    """

    def __init__(
        self,
        min_height: int = None,
        min_width: int = None,
        windows: dict = None,
        terminal_instance: Terminal = None,
    ):
        self.min_height = min_height
        self.min_width = min_width
        self.windows = windows or {}
        self.term = terminal_instance or Terminal()
        self.running = True

        # Hook for easier resize
        signal.signal(signal.SIGWINCH, self.__on_resize)

    def add_window(self, name: str, window_class: BaseWindow, *args, **kwargs):
        """
        args:
            name: The name of the window, used to call the window.
            window_class: The class of the window to add.
            *args: Positional arguments to pass to the window class.
            **kwargs: Keyword arguments to pass to the window class.
            ps: terminal_instance, switch_win and stop_process are
            automatically passed, overwrite with caution.
        """
        kwargs.setdefault("terminal_instance", self.term)
        kwargs.setdefault("switch_win", self.switch_win)
        kwargs.setdefault("stop_process", self.stop_process)
        self.windows[name] = window_class(*args, **kwargs)

    def switch_win(self, name: str):
        """
        args:
            name: The name of the window to switch to.
        """
        self.__check_window_exists(name)
        self.active_window = self.windows[name]
        self.active_window.draw()

    def stop_process(self):
        """Stop the main execution loop."""
        self.running = False

    def __check_window_exists(self, name: str):
        """
        args:
            name: The name of the window to check.
        """
        if name not in self.windows:
            raise ValueError(f"No window named '{name}' exists")

    def __on_resize(self, signum, frame):
        """
        args:
            signum: The signal number.
            frame: The current stack frame.
        """
        if self.active_window:
            self.active_window.draw()

    def __execution_loop(self):
        while self.running:
            key = self.term.inkey()
            self.active_window.handle_input(key.name or key)
            self.active_window.draw()

    def start(self, start_window: str):
        """
        args:
            start_window: The name of the window to start with.
        """
        with self.term.cbreak(), self.term.hidden_cursor():
            self.__check_window_exists(start_window)
            self.switch_win(start_window)

            try:
                self.__execution_loop()
            except KeyboardInterrupt:
                pass
