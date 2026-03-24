import re
from pathlib import Path
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, Label, RadioSet, RadioButton
from textual.containers import Container, ScrollableContainer, VerticalScroll, Horizontal, Vertical
from ..engine import number_to_words
from ..models import FileSelected

class FileProcessorScreen(Screen):
    BINDINGS = [
        ("n", "next_line", "Next Line"),
        ("p", "prev_line", "Prev Line"),
        ("s", "save_file", "Save All"),
        ("escape", "pop_screen", "Back"),
    ]

    def __init__(self, lines: list[str], filename: str):
        super().__init__()
        self.lines = lines
        self.processed_lines = list(lines)
        self.filename = filename
        self.current_idx = 0
        self.log_entries = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Container(id="processor-wrapper"):
            yield Static(f"File: {self.filename}", id="file-title")
            with Horizontal(id="main-area"):
                with VerticalScroll(id="left-pane"):
                    yield Label("Original Line:", classes="section-title")
                    yield Static("", id="current-line-text", classes="display-box")
                    yield Label("Final Processed Preview:", classes="section-title")
                    yield Static("", id="processed-preview", classes="display-box")
                with Vertical(id="right-pane"):
                    yield Label("Found Numbers (Manual Mode):", classes="section-title")
                    yield VerticalScroll(id="match-list")
            with Horizontal(id="action-bar"):
                yield Button("Previous", id="btn-prev")
                yield Button("Next / Confirm", id="btn-next", variant="primary")
                yield Button("Save Result", id="btn-save", variant="success")

    def on_mount(self) -> None:
        self.load_line()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """选项变动时实时预览"""
        self.apply_conversions(preview_only=True)

    def load_line(self) -> None:
        line = self.lines[self.current_idx]
        self.query_one("#current-line-text", Static).update(line)
        self.query_one("#processed-preview", Static).update(self.processed_lines[self.current_idx])
        
        match_list = self.query_one("#match-list")
        for child in match_list.children:
            child.remove()

        matches = list(re.finditer(r'\d+', line))
        if not matches:
            match_list.mount(Static("No numbers found.", classes="info-msg"))
        else:
            for m in matches:
                val, offset = m.group(), m.start()
                cont = ScrollableContainer(classes="match-item")
                match_list.mount(cont)
                cont.mount(
                    Label(f"Value: [b]{val}[/b]"),
                    RadioSet(
                        RadioButton("Number", value=True),
                        RadioButton("Percent"),
                        RadioButton("Year"),
                        id=f"rs-{offset}"
                    )
                )

    def apply_conversions(self, preview_only=False):
        line = self.lines[self.current_idx]
        matches = list(re.finditer(r'\d+', line))
        new_line = line
        
        for m in reversed(matches):
            offset = m.start()
            val_int = int(m.group())
            try:
                rs = self.query_one(f"#rs-{offset}", RadioSet)
                choice = rs.pressed_index
                if choice == 0: replacement = number_to_words(val_int)
                elif choice == 1: replacement = f"{number_to_words(val_int)} percent"
                elif choice == 2:
                    replacement = f"{number_to_words(val_int//100)} {number_to_words(val_int%100)}" if 1000 <= val_int <= 2999 else number_to_words(val_int)
                else: replacement = str(val_int)
                
                new_line = new_line[:m.start()] + replacement + new_line[m.end():]
                if not preview_only:
                    self.log_entries.append(f"Line {self.current_idx+1}: {val_int} -> {replacement}")
            except: continue
        
        if not preview_only:
            self.processed_lines[self.current_idx] = new_line
        self.query_one("#processed-preview", Static).update(new_line)

    def action_next_line(self):
        self.apply_conversions()
        if self.current_idx < len(self.lines) - 1:
            self.current_idx += 1
            self.load_line()

    def action_prev_line(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.load_line()

    def action_save_file(self):
        self.apply_conversions()
        # 确保目录存在
        Path(".cache").mkdir(exist_ok=True)
        Path(f".cache/processed_{self.filename}").write_text("\n".join(self.processed_lines), encoding="utf-8")
        Path(".cache/process_log.txt").write_text("\n".join(self.log_entries), encoding="utf-8")
        self.notify("Saved to .cache/ folder")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-next": self.action_next_line()
        elif event.button.id == "btn-prev": self.action_prev_line()
        elif event.button.id == "btn-save": self.action_save_file()