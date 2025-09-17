from blessed import Terminal


class BaseWindow:
    def __init__(
        self, terminal_instance: Terminal, switch_win: callable, stop_process: callable
    ):
        self.term = terminal_instance
        self.switch_win = switch_win
        self.stop_process = stop_process

    def draw(self):
        raise NotImplementedError

    def handle_input(self, key: str):
        raise NotImplementedError
