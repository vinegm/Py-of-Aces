from .utils import BaseWindow


class SizeWarningWindow(BaseWindow):
    def __init__(self, min_width: int, min_height: int, **kwargs):
        super().__init__(**kwargs)
        self.min_width = min_width
        self.min_height = min_height

    def draw(self) -> list[str]:
        lines: list[str] = []

        lines.append(self.term.reverse + "TERMINAL SIZE WARNING" + self.term.normal)
        lines.append("Your terminal is too small to display Py of Aces properly.")
        lines.append("")
        lines.append(f"Current size: {self.term.width}x{self.term.height}")
        lines.append(f"Required size: {self.min_width}x{self.min_height} (minimum)")
        lines.append("")
        lines.append("Please resize your terminal or use a smaller font.")
        lines.append("Press any key to continue or 'q' to quit...")

        return lines

    def handle_input(self, key: str) -> None:
        if key == "q":
            self.stop_process()
