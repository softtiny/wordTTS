"""
span_tracker.py
用于记录目标（数字、词语等）在字符串中出现位置的数据结构。
支持手动修改开始/结束位置。
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
# 核心数据结构
# ─────────────────────────────────────────────

@dataclass
class Span:
    """
    记录一个目标在字符串中的位置区间。

    属性:
        start   : 起始下标（包含）
        end     : 结束下标（不包含，与 Python 切片一致）
        value   : 该区间截取到的原始文本
        label   : 可选标签，用于说明该目标的类型（如 "数字"、"日期"）
    """
    start: int
    end: int
    value: str
    label: Optional[str] = None

    # ── 修改位置 ──────────────────────────────
    def move_start(self, new_start: int, source: str) -> "Span":
        """手动修改起始位置，并同步更新 value。"""
        if new_start < 0:
            raise ValueError(f"start 不能为负数，收到: {new_start}")
        if new_start >= self.end:
            raise ValueError(f"start({new_start}) 必须小于 end({self.end})")
        self.start = new_start
        self.value = source[self.start:self.end]
        return self

    def move_end(self, new_end: int, source: str) -> "Span":
        """手动修改结束位置，并同步更新 value。"""
        if new_end > len(source):
            raise ValueError(f"end({new_end}) 超出字符串长度 {len(source)}")
        if new_end <= self.start:
            raise ValueError(f"end({new_end}) 必须大于 start({self.start})")
        self.end = new_end
        self.value = source[self.start:self.end]
        return self

    def resize(self, new_start: int, new_end: int, source: str) -> "Span":
        """同时修改起始和结束位置。"""
        if new_start < 0 or new_end > len(source) or new_start >= new_end:
            raise ValueError(
                f"无效区间 [{new_start}, {new_end})，"
                f"字符串长度为 {len(source)}"
            )
        self.start = new_start
        self.end = new_end
        self.value = source[new_start:new_end]
        return self

    # ── 工具方法 ──────────────────────────────
    def length(self) -> int:
        """区间长度。"""
        return self.end - self.start

    def overlaps(self, other: "Span") -> bool:
        """判断两个区间是否重叠。"""
        return self.start < other.end and other.start < self.end

    def context(self, source: str, window: int = 10) -> str:
        """返回该区间在原文中的上下文片段。"""
        lo = max(0, self.start - window)
        hi = min(len(source), self.end + window)
        prefix = ("..." if lo > 0 else "")
        suffix = ("..." if hi < len(source) else "")
        snippet = source[lo:self.start] + f"[{self.value}]" + source[self.end:hi]
        return prefix + snippet + suffix

    def __repr__(self) -> str:
        tag = f"<{self.label}>" if self.label else ""
        return f"Span{tag}({self.start}:{self.end} '{self.value}')"


# ─────────────────────────────────────────────
# 容器：管理同一段文本中的所有 Span
# ─────────────────────────────────────────────

@dataclass
class SpanRecord:
    """
    针对一段固定文本，管理其中全部目标区间。

    属性:
        source : 原始字符串（不可变）
        spans  : 已记录的区间列表
    """
    source: str
    spans: list[Span] = field(default_factory=list)

    # ── 自动提取 ──────────────────────────────
    def extract_pattern(
        self,
        pattern: str,
        label: Optional[str] = None,
        flags: int = 0
    ) -> "SpanRecord":
        """
        用正则表达式自动扫描 source，添加所有匹配项。

        参数:
            pattern : 正则表达式字符串
            label   : 可选标签
            flags   : re 模块的标志（如 re.IGNORECASE）
        """
        for m in re.finditer(pattern, self.source, flags):
            self.spans.append(
                Span(
                    start=m.start(),
                    end=m.end(),
                    value=m.group(),
                    label=label,
                )
            )
        return self

    def extract_numbers(self) -> "SpanRecord":
        """快捷方法：提取所有整数和小数。"""
        return self.extract_pattern(r"-?\d+(?:\.\d+)?", label="数字")

        # ── 手动添加 / 修改 ───────────────────────
    def add(
        self,
        start: int,
        end: int,
        label: Optional[str] = None
    ) -> Span:
        """手动添加一个区间，返回新建的 Span 对象。"""
        span = Span(
            start=start,
            end=end,
            value=self.source[start:end],
            label=label,
        )
        self.spans.append(span)
        return span


    def update_span(
        self,
        index: int,
        new_start: Optional[int] = None,
        new_end: Optional[int] = None,
    ) -> Span:
        """
        按索引修改已有 Span 的起止位置。
        只传入 new_start 或 new_end 时，只修改对应端点。
        """
        span = self.spans[index]
        if new_start is not None and new_end is not None:
            span.resize(new_start, new_end, self.source)
        elif new_start is not None:
            span.move_start(new_start, self.source)
        elif new_end is not None:
            span.move_end(new_end, self.source)
        return span

    # ── 查询 ──────────────────────────────────
    def by_label(self, label: str) -> list[Span]:
        """按标签筛选区间。"""
        return [s for s in self.spans if s.label == label]

    def at_position(self, pos: int) -> list[Span]:
        """返回覆盖指定位置的所有区间。"""
        return [s for s in self.spans if s.start <= pos < s.end]

    def sorted_spans(self) -> list[Span]:
        """按 start 升序排列。"""
        return sorted(self.spans, key=lambda s: s.start)

    # ── 展示 ──────────────────────────────────
    def display(self) -> None:
        """打印所有区间及其上下文。"""
        print(f"原文: {self.source!r}\n")
        for i, span in enumerate(self.sorted_spans()):
            ctx = span.context(self.source)
            print(
                f"  [{i:02d}] {span!r:35s}  上下文: {ctx}"
            )

    def highlight(self) -> str:
        """
        在原文下方输出一行标记，用 ^ 标出各区间位置。
        适合在终端中直观查看区间分布。
        """
        marker = [" "] * len(self.source)
        for span in self.spans:
            for i in range(span.start, span.end):
                marker[i] = "^"
        return self.source + "\n" + "".join(marker)

    def __len__(self) -> int:
        return len(self.spans)

    def __repr__(self) -> str:
        return (
            f"SpanRecord(source={self.source!r}, "
            f"spans={self.spans})"
        )
