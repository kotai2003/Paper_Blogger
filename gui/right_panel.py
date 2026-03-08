"""右パネル - タブビュー（要約・ブログ・Figure）"""

from tkinter import ttk

from gui.tabs.tab_summary import TabSummary
from gui.tabs.tab_markdown import TabMarkdown
from gui.tabs.tab_figures import TabFigures


class RightPanel(ttk.Frame):
    """右メインパネル: Notebook（タブビュー）"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=4, pady=4)

        self.tab_summary = TabSummary(self.notebook)
        self.tab_markdown = TabMarkdown(self.notebook)
        self.tab_figures = TabFigures(self.notebook)

        self.notebook.add(self.tab_summary, text="  Paper Summary  ")
        self.notebook.add(self.tab_markdown, text="  Blog Article  ")
        self.notebook.add(self.tab_figures, text="  Figures  ")

    def clear_all(self):
        self.tab_summary.clear()
        self.tab_markdown.clear()
        self.tab_figures.clear()
