"""ツールバー"""

import tkinter as tk
from tkinter import ttk

from style.theme import AppTheme


class Toolbar(ttk.Frame):
    """アプリケーションツールバー"""

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, style="Toolbar.TFrame", **kwargs)
        self.controller = controller

        inner = ttk.Frame(self, style="Toolbar.TFrame")
        inner.pack(fill="x", padx=8, pady=4)

        # 左側: アクションボタン
        left = ttk.Frame(inner, style="Toolbar.TFrame")
        left.pack(side="left")

        self.open_btn = ttk.Button(
            left, text="Open PDF", style="Toolbar.TButton",
            command=controller.open_pdf,
        )
        self.open_btn.pack(side="left", padx=(0, 2))

        # セパレータ
        ttk.Separator(left, orient="vertical").pack(side="left", fill="y", padx=6, pady=2)

        self.run_btn = ttk.Button(
            left, text="Run Pipeline", style="Primary.TButton",
            command=controller.run_pipeline,
        )
        self.run_btn.pack(side="left", padx=(0, 2))

        self.stop_btn = ttk.Button(
            left, text="Stop", style="Danger.TButton",
            command=controller.stop_pipeline,
            state="disabled",
        )
        self.stop_btn.pack(side="left", padx=(0, 2))

        ttk.Separator(left, orient="vertical").pack(side="left", fill="y", padx=6, pady=2)

        self.save_btn = ttk.Button(
            left, text="Save Article", style="Toolbar.TButton",
            command=controller.save_article,
        )
        self.save_btn.pack(side="left", padx=(0, 2))

        self.folder_btn = ttk.Button(
            left, text="Open Output", style="Toolbar.TButton",
            command=controller.open_output_folder,
        )
        self.folder_btn.pack(side="left", padx=(0, 2))

        # 右側: 状態表示
        right = ttk.Frame(inner, style="Toolbar.TFrame")
        right.pack(side="right")

        self.progress = ttk.Progressbar(
            right, mode="determinate", length=150,
        )
        self.progress.pack(side="left", padx=(0, 12))

        self.step_label = ttk.Label(
            right, text="Ready", style="Toolbar.TLabel",
        )
        self.step_label.pack(side="left")

    def set_running(self, running: bool):
        """実行中/待機中の表示切替"""
        if running:
            self.run_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            self.open_btn.configure(state="disabled")
        else:
            self.run_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.open_btn.configure(state="normal")

    def set_progress(self, step: int, total: int, label: str = ""):
        """進捗を更新"""
        pct = (step / total * 100) if total > 0 else 0
        self.progress["value"] = pct
        if label:
            self.step_label.configure(text=label)
