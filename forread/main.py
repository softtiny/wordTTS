from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, DirectoryTree
from textual.containers import Container
from textual.screen import Screen
from pathlib import Path

from .models import FileSelected
from .screens.processor import FileProcessorScreen

class FileSelectorScreen(Screen):
    def compose(self) -> ComposeResult:
        yield DirectoryTree(".")
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.post_message(FileSelected(Path(event.path)))

class ManualProcessorApp(App):
    # 将 CSS 抽离或放在此处
    CSS = """
    #processor-wrapper { padding: 1; height: 100%; }
    #file-title { text-align: center; background: $accent; color: white; height: 3; content-align: center middle; }
    .section-title { color: $secondary; margin: 1 0; }
    .display-box { background: $surface; border: solid $primary; padding: 1; min-height: 5; margin-bottom: 1; }
    #main-area { height: 75%; }
    #left-pane { width: 55%; padding-right: 1; border-right: tall $primary; }
    #right-pane { width: 45%; padding-left: 1; }
    .match-item { background: $boost; border: solid $primary-lighten-2; margin-bottom: 1; padding: 1; height: auto; }
    #action-bar { height: 5; align: center middle; border-top: heavy $primary; }
    Button { margin: 0 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Manual Number-to-Word Converter", id="welcome"),
            Button("Open File", variant="primary", id="open-btn"),
            id="start-screen"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "open-btn":
            self.push_screen(FileSelectorScreen())

    def on_file_selected(self, event: FileSelected):
        try:
            content = event.path.read_text(encoding="utf-8").splitlines()
            self.push_screen(FileProcessorScreen(content, event.path.name))
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

def run():
    app = ManualProcessorApp()
    app.run()

if __name__ == "__main__":
    run()