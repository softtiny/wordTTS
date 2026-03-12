# widgets/gui.py
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, DirectoryTree, Static, Label, RadioSet, RadioButton
from textual.containers import Container,  ScrollableContainer, VerticalScroll, Horizontal, Vertical
from textual.screen import Screen
from textual.message import Message
from pathlib import Path
import re
import logging

# --- 基础转换逻辑 ---
UNITS = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
TEENS = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
THOUSANDS = ["", "thousand", "million", "billion"]

def number_to_words(n: int) -> str:
    if n == 0: return "zero"
    if n < 0: return "minus " + number_to_words(abs(n))
    
    def _chunk(num):
        words = ""
        h, r = divmod(num, 100)
        if h > 0: words += UNITS[h] + " hundred" + (" " if r > 0 else "")
        if r >= 20:
            t, u = divmod(r, 10)
            words += TENS[t] + (" " + UNITS[u] if u > 0 else "")
        elif r > 9: words += TEENS[r - 10]
        elif r > 0: words += UNITS[r]
        return words.strip()

    parts, idx = [], 0
    while n > 0:
        if n % 1000 != 0:
            parts.append(_chunk(n % 1000) + (" " + THOUSANDS[idx] if idx > 0 else ""))
        n //= 1000
        idx += 1
    return " ".join(reversed(parts)).strip()

# --- UI 消息定义 ---
class FileSelected(Message):
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__()

# --- 核心处理器屏幕 ---
class FileProcessorScreen(Screen):
    BINDINGS = [
        ("n", "next_line", "Next Line"),
        ("s", "save_file", "Save All"),
        ("escape", "pop_screen", "Back"),
    ]

    def __init__(self, lines: list[str], filename: str):
        super().__init__()
        self.lines = lines
        self.processed_lines = list(lines) # 初始拷贝
        self.filename = filename
        self.current_idx = 0
        self.log_entries = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Container(id="processor-wrapper"):
            yield Static(f"File: {self.filename}", id="file-title")
            
            with Horizontal(id="main-area"):
                # 左侧：行导航和原始显示
                with VerticalScroll(id="left-pane"):
                    yield Label("Original Line:", classes="section-title")
                    yield Static("", id="current-line-text", classes="display-box")
                    yield Label("Final Processed Preview:", classes="section-title")
                    yield Static("", id="processed-preview", classes="display-box")
                
                # 右侧：手动转换工作区
                with VerticalScroll(id="right-pane"):
                    yield Label("Found Numbers (Select Mode):", classes="section-title")
                    yield Vertical(id="match-list") # 动态生成匹配项

            with Horizontal(id="action-bar"):
                yield Button("Previous", id="btn-prev")
                yield Button("Next / Confirm", id="btn-next", variant="primary")
                yield Button("Save Result", id="btn-save", variant="success")

    def on_mount(self) -> None:
        self.load_line()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        self.query_one("#processed-preview", Static).update("hahah")

    def load_line(self) -> None:
        """加载当前行并扫描数字"""
        line = self.lines[self.current_idx]
        self.query_one("#current-line-text", Static).update(line)
        self.query_one("#processed-preview", Static).update(self.processed_lines[self.current_idx])
        #self.query_one("#processed-preview", Static).update("dsfds")
        
        match_list = self.query_one("#match-list")
        # 清空旧组件
        for child in match_list.children:
            child.remove()

        matches = list(re.finditer(r'\d+', line))
        if not matches:
            match_list.mount(Static("No numbers found in this line.", classes="info-msg"))
        else:
            for m in matches:
                val = m.group()
                offset = m.start()
                
                # 1. 先创建并挂载外层容器
                cont =  ScrollableContainer(classes="match-item")
                match_list.mount(cont)
                
                # 2. 在容器挂载后再添加内部组件
                cont.mount(
                    Label(f"Value: [b]{val}[/b] (at pos {offset})"),
                    RadioSet(
                        RadioButton("As Number", value=True),
                        RadioButton("As Percent"),
                        RadioButton("As Year"),
                        id=f"rs-{offset}"
                    )
                )


    def apply_conversions(self):
        """应用转换逻辑"""
        line = self.lines[self.current_idx]
        matches = list(re.finditer(r'\d+', line))
        new_line = line
        
        # 倒序替换以防索引偏移
        for m in reversed(matches):
            offset = m.start()
            val_int = int(m.group())
            
            try:
                # 定位到对应的 RadioSet
                rs = self.query_one(f"#rs-{offset}", RadioSet)
                choice = rs.pressed_index
                
                if choice == 0: # Number
                    replacement = number_to_words(val_int)
                elif choice == 1: # Percent
                    replacement = f"{number_to_words(val_int)} percent"
                elif choice == 2: # Year
                    if 1000 <= val_int <= 2999:
                        replacement = f"{number_to_words(val_int//100)} {number_to_words(val_int%100)}"
                    else:
                        replacement = number_to_words(val_int)
                else:
                    replacement = str(val_int)
                
                new_line = new_line[:m.start()] + replacement + new_line[m.end():]
                self.log_entries.append(f"Line {self.current_idx+1}: {val_int} -> {replacement}")
            except Exception:
                continue
        
        self.processed_lines[self.current_idx] = new_line
        self.query_one("#processed-preview", Static).update(new_line)

    def action_next_line(self):
        self.apply_conversions() # 离开前保存当前行的转换
        if self.current_idx < len(self.lines) - 1:
            self.current_idx += 1
            self.load_line()

    def action_save_file(self):
        self.apply_conversions()
        output = Path(f".cache/processed_{self.filename}")
        output.write_text("\n".join(self.processed_lines), encoding="utf-8")
        
        log_path = Path(".cache/process_log.txt")
        log_path.write_text("\n".join(self.log_entries), encoding="utf-8")
        
        self.notify(f"Saved to {output} & log created!")

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "btn-next": self.action_next_line()
        elif event.button.id == "btn-prev" and self.current_idx > 0:
            self.current_idx -= 1
            self.load_line()
        elif event.button.id == "btn-save": self.action_save_file()

# --- 主程序入口 ---
class FileSelectorScreen(Screen):
    def compose(self) -> ComposeResult:
        yield DirectoryTree(".")

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        self.post_message(FileSelected(Path(event.path)))

class ManualProcessorApp(App):
    CSS = """
    #processor-wrapper { padding: 1; }
    #file-title { text-align: center; background: $accent; color: white; }
    .section-title { color: $secondary; margin-top: 1; }
    .display-box { background: $surface; border: solid $primary; min-height: 2; margin-bottom: 1; }
    
    #main-area { height: 80%; }
    #left-pane { width: 60%;  }
    #right-pane { width: 40%; border-left: solid $primary; }
    
    .match-item { background: $boost; border: solid $primary-lighten-2;  }
    RadioSet { background: transparent; }
    
    #action-bar { height: 3; align: center middle; }
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
            self.notify(f"Error reading file: {e}", severity="error")

if __name__ == "__main__":
    ManualProcessorApp().run()