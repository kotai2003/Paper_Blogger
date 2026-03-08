"""ブログ記事タブ - 生成されたMarkdownブログ記事を表示"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from style.theme import AppTheme
from widgets.markdown_viewer import MarkdownViewer


class TabMarkdown(ttk.Frame):
    """ブログ記事の表示・保存タブ"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # ツールバー
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=(8, 0))

        self.save_btn = ttk.Button(
            toolbar, text="Save as...",
            style="Toolbar.TButton",
            command=self._save_as,
        )
        self.save_btn.pack(side="right")

        # 表示切替
        self._view_mode = tk.StringVar(value="rendered")
        ttk.Radiobutton(
            toolbar, text="Rendered", variable=self._view_mode,
            value="rendered", command=self._switch_view,
        ).pack(side="left", padx=(0, 8))
        ttk.Radiobutton(
            toolbar, text="Raw Markdown", variable=self._view_mode,
            value="raw", command=self._switch_view,
        ).pack(side="left")

        # Rendered view
        self.rendered_viewer = MarkdownViewer(self)

        # Raw view
        self.raw_text = tk.Text(
            self,
            wrap="word",
            font=AppTheme.FONT_MONO,
            bg=AppTheme.COLOR_BG_WHITE,
            fg=AppTheme.COLOR_TEXT,
            relief="flat",
            borderwidth=0,
            padx=16,
            pady=12,
        )

        # デフォルトはRendered表示
        self.rendered_viewer.pack(fill="both", expand=True, padx=8, pady=8)

        self._raw_content = ""

    def load(self, markdown_text: str, base_dir: str | Path | None = None):
        self._raw_content = markdown_text
        self.rendered_viewer.load(markdown_text, base_dir=base_dir)
        self.raw_text.delete("1.0", "end")
        self.raw_text.insert("1.0", markdown_text)

    def clear(self):
        self._raw_content = ""
        self.rendered_viewer.load("")
        self.raw_text.delete("1.0", "end")

    def _switch_view(self):
        mode = self._view_mode.get()
        if mode == "rendered":
            self.raw_text.pack_forget()
            self.rendered_viewer.pack(fill="both", expand=True, padx=8, pady=8)
        else:
            self.rendered_viewer.pack_forget()
            self.raw_text.pack(fill="both", expand=True, padx=8, pady=8)

    def _save_as(self):
        path = filedialog.asksaveasfilename(
            title="Save Blog Article",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")],
        )
        if path:
            Path(path).write_text(self._raw_content, encoding="utf-8")
