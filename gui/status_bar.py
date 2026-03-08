"""ステータスバー"""

import time
import tkinter as tk
from tkinter import ttk

from style.theme import AppTheme


class StatusBar(ttk.Frame):
    """アプリケーションステータスバー"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="StatusBar.TFrame", **kwargs)

        inner = ttk.Frame(self, style="StatusBar.TFrame")
        inner.pack(fill="x", padx=8, pady=2)

        # 左: ステータスメッセージ
        self.status_label = ttk.Label(
            inner, text="Ready", style="StatusBar.TLabel",
        )
        self.status_label.pack(side="left")

        # 右: タイマー
        self.timer_label = ttk.Label(
            inner, text="", style="StatusBar.TLabel",
        )
        self.timer_label.pack(side="right")

        # 中央: モデル情報
        self.model_label = ttk.Label(
            inner, text="", style="StatusBar.TLabel",
        )
        self.model_label.pack(side="right", padx=(0, 16))

        self._start_time = None
        self._timer_running = False

    def set_status(self, text: str):
        self.status_label.configure(text=text)

    def set_model(self, model: str):
        self.model_label.configure(text=f"Model: {model}")

    def start_timer(self):
        self._start_time = time.time()
        self._timer_running = True
        self._update_timer()

    def stop_timer(self):
        self._timer_running = False
        if self._start_time:
            elapsed = time.time() - self._start_time
            self.timer_label.configure(text=f"Elapsed: {elapsed:.1f}s")

    def _update_timer(self):
        if self._timer_running and self._start_time:
            elapsed = time.time() - self._start_time
            minutes, seconds = divmod(int(elapsed), 60)
            self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")
            self.after(1000, self._update_timer)
