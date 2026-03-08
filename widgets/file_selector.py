"""ファイル選択ウィジェット"""

import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path

from style.theme import AppTheme


class FileSelector(ttk.Frame):
    """PDFファイル選択コンポーネント（親のスタイルを継承）"""

    def __init__(self, parent, label: str = "PDF File", **kwargs):
        super().__init__(parent, **kwargs)

        self._path = tk.StringVar()
        self._on_change_callback = None

        # 親のスタイルに合わせたラベルスタイルを判定
        style_name = kwargs.get("style", "")
        is_sidebar = "Sidebar" in style_name
        label_style = "Sidebar.Large.TLabel" if is_sidebar else "Large.TLabel"
        info_style = "Sidebar.Small.TLabel" if is_sidebar else "Small.TLabel"
        frame_style = "Sidebar.TFrame" if is_sidebar else "TFrame"

        ttk.Label(self, text=label, style=label_style).pack(
            anchor="w", pady=(0, 4)
        )

        input_frame = ttk.Frame(self, style=frame_style)
        input_frame.pack(fill="x")

        self.entry = ttk.Entry(
            input_frame,
            textvariable=self._path,
            state="readonly",
            font=AppTheme.FONT_NORMAL,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.browse_btn = ttk.Button(
            input_frame,
            text="Browse...",
            command=self._browse,
        )
        self.browse_btn.pack(side="right")

        # ファイル情報
        self.info_label = ttk.Label(self, text="", style=info_style)
        self.info_label.pack(anchor="w", pady=(4, 0))

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if path:
            self.set_path(path)

    def set_path(self, path: str):
        self._path.set(path)
        p = Path(path)
        if p.exists():
            size_mb = p.stat().st_size / (1024 * 1024)
            self.info_label.configure(text=f"{p.name}  ({size_mb:.1f} MB)")
        else:
            self.info_label.configure(text="")
        if self._on_change_callback:
            self._on_change_callback(path)

    def get_path(self) -> str:
        return self._path.get()

    def on_change(self, callback):
        self._on_change_callback = callback
