# widgets/gui.py
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, DirectoryTree, Static
from textual.containers import Container, VerticalScroll, Horizontal
from textual.screen import Screen
from textual.message import Message
from pathlib import Path
import re

# --- Number to Words Conversion ---
# (Keep the number_to_words function as defined previously)
UNITS = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
TEENS = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
THOUSANDS = ["", "thousand", "million", "billion"] # Extend as needed for larger numbers

def _convert_chunk(n: int) -> str:
    """Converts a number less than 1000 into words."""
    if n == 0:
        return ""

    words = ""
    hundreds = n // 100
    remainder = n % 100

    if hundreds > 0:
        words += UNITS[hundreds] + " hundred"
        if remainder > 0:
            words += " "

    if remainder >= 20:
        words += TENS[remainder // 10]
        if remainder % 10 > 0:
            words += "-" + UNITS[remainder % 10]
    elif remainder > 9:
        words += TEENS[remainder - 10]
    elif remainder > 0:
        words += UNITS[remainder]
    return words.strip()

def number_to_words(n: int) -> str:
    """Converts an integer to its word representation."""
    if n == 0:
        return "zero"

    if n < 0:
        return "minus " + number_to_words(abs(n))

    parts = []
    chunk_index = 0
    while n > 0:
        if n % 1000 != 0:
            chunk_words = _convert_chunk(n % 1000)
            if chunk_index > 0:
                chunk_words += " " + THOUSANDS[chunk_index]
            parts.append(chunk_words)
        n //= 1000
        chunk_index += 1

    return " ".join(reversed(parts))

# --- Textual App ---

class FileSelected(Message):
    """Custom message emitted when a file is selected."""
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__()

class FileProcessorScreen(Screen):
    """Screen to display original and processed lines, with navigation."""

    BINDINGS = [
        ("n", "next_line", "Next Line"),
        ("p", "prev_line", "Previous Line"),
        ("escape", "pop_screen", "Back"),
    ]

    def __init__(self, original_lines: list[str], processed_lines: list[str], filename: str):
        super().__init__()
        self.original_lines = original_lines
        self.processed_lines = processed_lines
        self.filename = filename
        self.current_line_index = 0

    def compose(self) -> ComposeResult:
        """Compose the file processor screen layout."""
        yield Header(show_clock=True)
        yield Footer()

        yield Container(
            Static(f"Processing: {self.filename}", id="file-info"),
            Horizontal(
                Container(
                    Static("Original Line:", classes="label"),
                    Static(self.original_lines[self.current_line_index] if self.original_lines else "", id="original-line", classes="content-box"),
                    VerticalScroll(id="original-scroll"), # Placeholder for potential scrollbar
                    classes="line-container"
                ),
                Container(
                    Static("Processed Line:", classes="label"),
                    Static(self.processed_lines[self.current_line_index] if self.processed_lines else "", id="processed-line", classes="content-box"),
                    VerticalScroll(id="processed-scroll"), # Placeholder for potential scrollbar
                    classes="line-container"
                ),
                id="lines-container"
            ),
            Container(
                Button("Previous Line", id="prev-line-button", variant="default"),
                Button("Next Line", id="next-line-button", variant="primary"),
                id="nav-buttons-container"
            ),
            id="processor-container"
        )

    def on_mount(self) -> None:
        """Called when the screen is mounted."""
        self.update_line_display()

    def update_line_display(self) -> None:
        """Updates the displayed original and processed lines."""
        original_static = self.query_one("#original-line", Static)
        processed_static = self.query_one("#processed-line", Static)

        if self.original_lines and self.current_line_index < len(self.original_lines):
            original_static.update(self.original_lines[self.current_line_index])
        else:
            original_static.update("")

        if self.processed_lines and self.current_line_index < len(self.processed_lines):
            processed_static.update(self.processed_lines[self.current_line_index])
        else:
            processed_static.update("")
        
        # Update button states
        self.query_one("#prev-line-button").disabled = (self.current_line_index == 0)
        self.query_one("#next-line-button").disabled = (self.current_line_index >= len(self.original_lines) - 1)

    def action_next_line(self) -> None:
        """Action to move to the next line."""
        if self.current_line_index < len(self.original_lines) - 1:
            self.current_line_index += 1
            self.update_line_display()

    def action_prev_line(self) -> None:
        """Action to move to the previous line."""
        if self.current_line_index > 0:
            self.current_line_index -= 1
            self.update_line_display()

    def action_pop_screen(self) -> None:
        """Action to go back to the previous screen."""
        self.app.pop_screen()

class FileSelectorScreen(Screen):
    """A screen with a DirectoryTree to select a file."""

    def compose(self) -> ComposeResult:
        yield DirectoryTree(".")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle when a file is selected in the DirectoryTree."""
        self.post_message(FileSelected(Path(event.path) if not isinstance(event.path, Path) else event.path))

class MainApp(App):
    """Textual app with file selection and line-by-line processing display."""

    CSS = """
    Screen {
        background: #222222; /* Dark background for screens */
    }
    Header {
        height: 3;
        background: #333333;
    }
    Footer {
        height: 3;
        background: #333333;
    }
    #main-container {
        align: center middle;
        height: 100%;
        width: 100%;
    }
    Button {
        width: 20;
        height: 3;
        margin: 1 2;
    }
    #file-info {
        text-align: center;
        margin-bottom: 1;
        color: #cccccc;
    }
    #lines-container {
        height: 70%;
        width: 90%;
        margin: 1 5;
        layout: horizontal;
        align: center middle;
        background: #333333;
        border: thick $accent;
    }
    .line-container {
        height: 100%;
        width: 50%;
        margin: 0 1;
        layout: vertical;
        align: center top;
    }
    .label {
        color: #aaaaaa;
        margin-bottom: 1;
        padding: 0 1;
        text-align: left;
        width: 100%;
        height: 2;
    }
    .content-box {
        width: 100%;
        height: 1fr; /* Takes remaining height */
        background: #444444;
        color: #eeeeee;
        padding: 1 1;
        margin: 0 1;
        border: thick $primary;
        overflow-y: auto; /* Enable vertical scrolling if content exceeds height */
    }
    #nav-buttons-container {
        width: 100%;
        align: center middle;
        margin-top: 1;
    }
    #processor-container {
        align: center top;
        padding: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_file_path: Path | None = None
        self.original_lines: list[str] = []
        self.processed_lines: list[str] = []

    def compose(self) -> ComposeResult:
        """Compose the main app layout."""
        yield Header()
        yield Footer()
        yield Container(
            Button("Select File", id="open_file_button", variant="primary"),
            id="main-container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "open_file_button":
            self.push_screen(FileSelectorScreen())

    def on_file_selected(self, event: FileSelected) -> None:
        """Handle the custom FileSelected event from FileSelectorScreen."""
        self.selected_file_path = event.path
        
        self.original_lines = []
        self.processed_lines = []
        
        try:
            with open(self.selected_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    self.original_lines.append(line.rstrip('\n')) # Store original line
                    
                    # Process line to convert numbers to words
                    def replace_number_match(match):
                        num_str = match.group(0)
                        try:
                            num = int(num_str)
                            return number_to_words(num)
                        except ValueError:
                            return num_str
                    
                    processed_line = re.sub(r'\d+', replace_number_match, line)
                    self.processed_lines.append(processed_line.rstrip('\n')) # Store processed line

            if not self.original_lines:
                self.notify("Selected file is empty.")
                self.pop_screen() # Go back if file is empty
                return

            # Push the new screen for line-by-line processing
            self.push_screen(FileProcessorScreen(self.original_lines, self.processed_lines, self.selected_file_path.name))

        except FileNotFoundError:
            self.notify(f"Error: File not found at {self.selected_file_path}")
            self.pop_screen() # Go back if file not found
        except Exception as e:
            self.notify(f"Error processing file '{self.selected_file_path.name}': {e}")
            self.pop_screen() # Go back on other errors

if __name__ == "__main__":
    app = MainApp()
    app.run()
