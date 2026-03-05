# widgets/gui.py
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, DirectoryTree, Static, Log
from textual.containers import Container, VerticalScroll, Horizontal
from textual.screen import Screen
from textual.message import Message
from pathlib import Path
import re
import logging

# --- 配置日志 ---
logging.basicConfig(
    filename=".cache/process_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w" # 每次运行重写日志
)

# --- 数字转单词核心逻辑 ---
UNITS = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
TEENS = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
THOUSANDS = ["", "thousand", "million", "billion"]

def _convert_chunk(n: int) -> str:
    if n == 0: return ""
    words = ""
    hundreds = n // 100
    remainder = n % 100
    if hundreds > 0:
        words += UNITS[hundreds] + " hundred"
        if remainder > 0: words += " "
    if remainder >= 20:
        words += TENS[remainder // 10]
        if remainder % 10 > 0: words += "-" + UNITS[remainder % 10]
    elif remainder > 9:
        words += TEENS[remainder - 10]
    elif remainder > 0:
        words += UNITS[remainder]
    return words.strip()

def number_to_words(n: int) -> str:
    if n == 0: return "zero"
    if n < 0: return "minus " + number_to_words(abs(n))
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

# --- 处理增强：百分比与日期 ---
def smart_replace(match):
    text = match.group(0)
    # 处理百分比: 9% -> nine percent
    if text.endswith('%'):
        num = int(text[:-1])
        res = f"{number_to_words(num)} percent"
        logging.info(f"MATCH [Percent]: {text} -> {res}")
        return res
    
    # 处理纯数字
    if text.isdigit():
        res = number_to_words(int(text))
        logging.info(f"MATCH [Number]: {text} -> {res}")
        return res
    
    return text

# --- Textual UI 组件 ---

class FileSelected(Message):
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__()

class FileProcessorScreen(Screen):
    BINDINGS = [
        ("n", "next_line", "Next"),
        ("p", "prev_line", "Prev"),
        ("s", "save_file", "Save File"),
        ("escape", "pop_screen", "Back"),
    ]

    def __init__(self, original_lines: list[str], processed_lines: list[str], filename: str):
        super().__init__()
        self.original_lines = original_lines
        self.processed_lines = processed_lines
        self.filename = filename
        self.current_line_index = 0

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Container(
            Static(f"File: {self.filename} (Line {self.current_line_index + 1}/{len(self.original_lines)})", id="file-info"),
            Horizontal(
                VerticalScroll(Static("", id="original-line"), classes="content-box"),
                VerticalScroll(Static("", id="processed-line"), classes="content-box"),
                id="lines-container"
            ),
            # 增加一个实时日志查看窗口
            Log(id="mini-log"),
            Horizontal(
                Button("Prev", id="prev-line-button"),
                Button("Next", id="next-line-button", variant="primary"),
                Button("Save New File", id="save-button", variant="success"),
                id="nav-buttons-container"
            ),
            id="processor-container"
        )

    def on_mount(self) -> None:
        self.update_line_display()
        self.query_one("#mini-log").write_line("Processing started...")

    def update_line_display(self) -> None:
        idx = self.current_line_index
        self.query_one("#original-line", Static).update(self.original_lines[idx])
        self.query_one("#processed-line", Static).update(self.processed_lines[idx])
        self.query_one("#file-info", Static).update(f"Line {idx + 1} of {len(self.original_lines)}")
        
        # 更新按钮状态
        self.query_one("#prev-line-button").disabled = (idx == 0)
        self.query_one("#next-line-button").disabled = (idx >= len(self.original_lines) - 1)

    def action_next_line(self) -> None:
        if self.current_line_index < len(self.original_lines) - 1:
            self.current_line_index += 1
            self.update_line_display()

    def action_prev_line(self) -> None:
        if self.current_line_index > 0:
            self.current_line_index -= 1
            self.update_line_display()

    def action_save_file(self) -> None:
        new_path = Path(f"processed_{self.filename}")
        try:
            with open(new_path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.processed_lines))
            self.notify(f"Saved to {new_path}")
            logging.info(f"FILE SAVED: {new_path}")
        except Exception as e:
            self.notify(f"Save failed: {e}", severity="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next-line-button": self.action_next_line()
        elif event.button.id == "prev-line-button": self.action_prev_line()
        elif event.button.id == "save-button": self.action_save_file()

class FileSelectorScreen(Screen):
    def compose(self) -> ComposeResult:
        yield DirectoryTree(".")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.post_message(FileSelected(Path(event.path)))

class MainApp(App):
    CSS = """
    #lines-container { height: 40%; margin: 1; border: double $accent; }
    .content-box { background: $surface; padding: 1; border: thick $primary; margin: 1; }
    #mini-log { height: 20%; background: black; color: lightgreen; margin: 1; }
    #nav-buttons-container { align: center middle; height: auto; }
    Button { margin: 0 1; }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Welcome to Number-to-Word Processor", id="file-info"),
            Button("Select File to Start", id="open_file_button", variant="primary"),
            id="main-container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open_file_button":
            self.push_screen(FileSelectorScreen())

    def on_file_selected(self, event: FileSelected) -> None:
        self.original_lines = []
        self.processed_lines = []
        
        try:
            with open(event.path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    clean_line = line.rstrip('\n')
                    self.original_lines.append(clean_line)
                    
                    # 使用正则匹配：数字 或者 数字+%
                    processed = re.sub(r'\d+%', smart_replace, clean_line) # 先匹配百分比
                    processed = re.sub(r'\d+', smart_replace, processed)   # 再匹配剩余数字
                    self.processed_lines.append(processed)

            self.push_screen(FileProcessorScreen(self.original_lines, self.processed_lines, event.path.name))
        except Exception as e:
            self.notify(f"Error: {e}")

if __name__ == "__main__":
    app = MainApp()
    app.run()