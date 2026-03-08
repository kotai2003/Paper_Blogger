"""ログコンソールウィジェット - ダークテーマのログ表示"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from style.theme import AppTheme


class LogConsole(ttk.Frame):
    """研究アプリ用ログコンソール（ダークテーマ）"""

    def __init__(self, parent, sidebar: bool = False, **kwargs):
        super().__init__(parent, **kwargs)

        self._sidebar = sidebar
        frame_style = "Sidebar.TFrame" if sidebar else "TFrame"
        label_style = "Sidebar.Large.TLabel" if sidebar else "Large.TLabel"

        # ヘッダー
        header = ttk.Frame(self, style=frame_style)
        header.pack(fill="x")
        ttk.Label(header, text="Log", style=label_style).pack(
            side="left", padx=(0, 8)
        )
        clear_btn = ttk.Button(
            header, text="Clear", style="Toolbar.TButton",
            command=self.clear,
        )
        clear_btn.pack(side="right")

        # テキストエリア + スクロールバー
        text_frame = ttk.Frame(self)
        text_frame.pack(fill="both", expand=True, pady=(4, 0))

        self.text = tk.Text(
            text_frame,
            wrap="word",
            font=AppTheme.FONT_MONO_SMALL,
            bg=AppTheme.COLOR_LOG_BG,
            fg=AppTheme.COLOR_LOG_FG,
            insertbackground=AppTheme.COLOR_LOG_FG,
            selectbackground=AppTheme.COLOR_PRIMARY,
            selectforeground=AppTheme.COLOR_TEXT_INVERSE,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=8,
            state="disabled",
            cursor="arrow",
        )

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        # タグ設定
        self.text.tag_configure("timestamp", foreground=AppTheme.COLOR_TEXT_MUTED)
        self.text.tag_configure("info", foreground=AppTheme.COLOR_LOG_INFO)
        self.text.tag_configure("warn", foreground=AppTheme.COLOR_LOG_WARN)
        self.text.tag_configure("error", foreground=AppTheme.COLOR_LOG_ERROR)
        self.text.tag_configure("success", foreground=AppTheme.COLOR_LOG_SUCCESS)
        self.text.tag_configure("step", foreground="#cba6f7", font=AppTheme.FONT_MONO)
        self.text.tag_configure("normal", foreground=AppTheme.COLOR_LOG_FG)

    def log(self, msg: str, level: str = "info"):
        """メッセージをログに追加"""
        self.text.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text.insert("end", f"[{timestamp}] ", "timestamp")

        tag = level if level in ("info", "warn", "error", "success", "step") else "normal"
        self.text.insert("end", msg + "\n", tag)

        self.text.see("end")
        self.text.configure(state="disabled")
        self.update_idletasks()

    def clear(self):
        """ログをクリア"""
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.configure(state="disabled")
