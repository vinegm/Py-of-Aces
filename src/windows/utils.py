from blessed import Terminal


class BaseWindow:
    def __init__(self, terminal_instance: Terminal, switch_win: callable):
        self.term = terminal_instance
        self.switch_win = switch_win

    def draw(self):
        raise NotImplementedError

    def handle_input(self, key):
        raise NotImplementedError
