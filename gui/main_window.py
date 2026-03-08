"""メインウィンドウ - アプリケーションのルートフレーム"""

import tkinter as tk
from tkinter import ttk

from style.theme import AppTheme
from gui.menu_bar import MenuBar
from gui.toolbar import Toolbar
from gui.status_bar import StatusBar
from gui.left_panel import LeftPanel
from gui.right_panel import RightPanel


class MainWindow(ttk.Frame):
    """メインウィンドウ: MenuBar + Toolbar + PanedWindow + StatusBar"""

    def __init__(self, root: tk.Tk, controller):
        super().__init__(root)
        self.root = root
        self.controller = controller
        self.pack(fill="both", expand=True)

        # メニューバー
        self.menu_bar = MenuBar(root, controller)
        root.configure(menu=self.menu_bar)

        # ツールバー
        self.toolbar = Toolbar(self, controller)
        self.toolbar.pack(fill="x")

        # セパレータ
        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # メインペイン（左右分割）
        self.main_pane = ttk.PanedWindow(self, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True)

        # 左パネル
        self.left_panel = LeftPanel(self.main_pane, controller)
        self.main_pane.add(self.left_panel, weight=1)

        # 右パネル
        self.right_panel = RightPanel(self.main_pane)
        self.main_pane.add(self.right_panel, weight=3)

        # セパレータ
        ttk.Separator(self, orient="horizontal").pack(fill="x")

        # ステータスバー
        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill="x")

        # キーバインド
        root.bind("<Control-o>", lambda e: controller.open_pdf())
        root.bind("<Control-s>", lambda e: controller.save_article())
        root.bind("<F5>", lambda e: controller.run_pipeline())

    def set_running(self, running: bool):
        """パイプライン実行中/待機中の表示切替"""
        self.toolbar.set_running(running)
        self.left_panel.set_running(running)
        if running:
            self.status_bar.set_status("Running...")
