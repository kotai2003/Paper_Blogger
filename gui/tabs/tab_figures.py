"""Figureタブ - 抽出された図の一覧とプレビュー"""

from tkinter import ttk
from pathlib import Path

from widgets.image_viewer import ImageViewer


class TabFigures(ttk.Frame):
    """抽出された図の表示タブ"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.viewer = ImageViewer(self)
        self.viewer.pack(fill="both", expand=True, padx=8, pady=8)

    def load_images(self, image_dir: str | Path):
        self.viewer.load_images(image_dir)

    def clear(self):
        self.viewer.clear()
