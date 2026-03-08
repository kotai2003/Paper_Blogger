"""論文要約タブ - 落合式1枚スライド要約を表示"""

from pathlib import Path
from tkinter import ttk

from widgets.markdown_viewer import MarkdownViewer


class TabSummary(ttk.Frame):
    """落合式論文要約の表示タブ"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.viewer = MarkdownViewer(self)
        self.viewer.pack(fill="both", expand=True, padx=8, pady=8)

    def load(self, markdown_text: str, base_dir: str | Path | None = None):
        self.viewer.load(markdown_text, base_dir=base_dir)

    def clear(self):
        self.viewer.load("")
