from .utils import BaseWindow


class SizeWarningWindow(BaseWindow):
    framed = False

    def __init__(self, min_width: int, min_height: int, **kwargs):
        super().__init__(**kwargs)
        self.min_width = min_width
        self.min_height = min_height

    def draw(self) -> list[str]:
        return [
            f"Terminal too small — need at least {self.min_width}x{self.min_height}",
        ]

    def handle_input(self, key: str) -> None:
        if key == "q":
            self.stop_process()
