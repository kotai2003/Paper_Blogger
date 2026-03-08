"""画像ビューアウィジェット - Figure表示用"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from style.theme import AppTheme

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ImageViewer(ttk.Frame):
    """Figure画像のサムネイル一覧 + プレビュー表示"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # 上下分割: リスト + プレビュー
        self.pane = ttk.PanedWindow(self, orient="vertical")
        self.pane.pack(fill="both", expand=True)

        # 上部: サムネイルリスト
        list_frame = ttk.Frame(self.pane)
        self.pane.add(list_frame, weight=1)

        list_header = ttk.Frame(list_frame)
        list_header.pack(fill="x", pady=(0, 4))
        ttk.Label(list_header, text="Figures", style="Large.TLabel").pack(side="left")
        self.count_label = ttk.Label(list_header, text="0 images", style="Muted.TLabel")
        self.count_label.pack(side="right")

        # Treeviewで図一覧
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("name", "size"),
            show="headings",
            selectmode="browse",
            height=6,
        )
        self.tree.heading("name", text="File Name")
        self.tree.heading("size", text="Size")
        self.tree.column("name", width=300)
        self.tree.column("size", width=100, anchor="e")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # 下部: プレビュー
        preview_frame = ttk.Frame(self.pane)
        self.pane.add(preview_frame, weight=2)

        self.preview_label = ttk.Label(
            preview_frame, text="Select a figure to preview",
            style="Muted.TLabel", anchor="center",
        )
        self.preview_label.pack(fill="both", expand=True)

        self._images = {}  # path -> PhotoImage を保持
        self._image_paths = []  # (item_id, path) リスト

    def load_images(self, image_dir: str | Path):
        """ディレクトリ内の画像を読み込み"""
        self.clear()
        image_dir = Path(image_dir)
        if not image_dir.exists():
            return

        extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"}
        files = sorted(
            f for f in image_dir.iterdir()
            if f.suffix.lower() in extensions
        )

        for f in files:
            size_kb = f.stat().st_size / 1024
            size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb / 1024:.1f} MB"
            item_id = self.tree.insert("", "end", values=(f.name, size_str))
            self._image_paths.append((item_id, f))

        self.count_label.configure(text=f"{len(files)} images")

    def clear(self):
        """表示をクリア"""
        self.tree.delete(*self.tree.get_children())
        self._images.clear()
        self._image_paths.clear()
        self.preview_label.configure(image="", text="Select a figure to preview")
        self.count_label.configure(text="0 images")

    def _on_select(self, event):
        """Treeview選択時にプレビュー更新"""
        if not HAS_PIL:
            self.preview_label.configure(text="Pillow not installed. Run: pip install Pillow")
            return

        sel = self.tree.selection()
        if not sel:
            return

        item_id = sel[0]
        for iid, path in self._image_paths:
            if iid == item_id:
                self._show_preview(path)
                break

    def _show_preview(self, path: Path):
        """画像をプレビュー表示（リサイズ対応）"""
        if not HAS_PIL:
            return

        try:
            img = Image.open(path)

            # プレビュー領域のサイズに合わせてリサイズ
            self.update_idletasks()
            max_w = self.preview_label.winfo_width() - 20
            max_h = self.preview_label.winfo_height() - 20
            if max_w < 100:
                max_w = 500
            if max_h < 100:
                max_h = 400

            img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)

            self.preview_label.configure(image=tk_img, text="")
            self.preview_label.image = tk_img  # 参照を保持

        except Exception as e:
            self.preview_label.configure(image="", text=f"Error: {e}")
