from textual.message import Message
from pathlib import Path

class FileSelected(Message):
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__()