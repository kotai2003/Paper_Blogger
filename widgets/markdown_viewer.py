"""Markdownビューアウィジェット - テキスト + 画像インライン表示"""

import re
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from style.theme import AppTheme

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class MarkdownViewer(ttk.Frame):
    """Markdownテキストを整形表示するビューア（画像インライン表示対応）"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # 画像のベースディレクトリ（article.mdの親ディレクトリ）
        self._base_dir = None
        # PhotoImage参照を保持（GC防止）
        self._photo_images = []

        # ツールバー
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 4))

        self.copy_btn = ttk.Button(
            toolbar, text="Copy All", style="Toolbar.TButton",
            command=self._copy_all,
        )
        self.copy_btn.pack(side="right")

        self.word_count_label = ttk.Label(toolbar, text="", style="Muted.TLabel")
        self.word_count_label.pack(side="right", padx=(0, 12))

        # テキストエリア
        text_frame = ttk.Frame(self)
        text_frame.pack(fill="both", expand=True)

        self.text = tk.Text(
            text_frame,
            wrap="word",
            font=AppTheme.FONT_NORMAL,
            bg=AppTheme.COLOR_BG_WHITE,
            fg=AppTheme.COLOR_TEXT,
            insertbackground=AppTheme.COLOR_TEXT,
            selectbackground=AppTheme.COLOR_PRIMARY_LIGHT,
            selectforeground=AppTheme.COLOR_TEXT,
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=16,
            state="disabled",
            cursor="arrow",
            spacing1=2,
            spacing2=2,
            spacing3=4,
        )

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        # タグ設定（Meiryo対応）
        _ff = AppTheme._FONT_FAMILY
        self.text.tag_configure("h1", font=(_ff, 20, "bold"), foreground=AppTheme.COLOR_TEXT, spacing1=16, spacing3=8)
        self.text.tag_configure("h2", font=(_ff, 16, "bold"), foreground=AppTheme.COLOR_TEXT, spacing1=14, spacing3=6)
        self.text.tag_configure("h3", font=(_ff, 13, "bold"), foreground=AppTheme.COLOR_TEXT, spacing1=10, spacing3=4)
        self.text.tag_configure("bold", font=(_ff, 10, "bold"))
        self.text.tag_configure("code", font=AppTheme.FONT_MONO, background="#f1f5f9", foreground="#1e40af")
        self.text.tag_configure("codeblock", font=AppTheme.FONT_MONO_SMALL, background="#f8fafc", foreground=AppTheme.COLOR_TEXT, spacing1=4, spacing3=4, lmargin1=20, lmargin2=20)
        self.text.tag_configure("bullet", lmargin1=24, lmargin2=40, font=(_ff, 10))
        self.text.tag_configure("quote", foreground=AppTheme.COLOR_TEXT_SECONDARY, lmargin1=20, lmargin2=20, font=(_ff, 10, "italic"))
        self.text.tag_configure("hr", foreground=AppTheme.COLOR_BORDER)
        self.text.tag_configure("normal", foreground=AppTheme.COLOR_TEXT, font=(_ff, 10))
        self.text.tag_configure("img_caption", foreground=AppTheme.COLOR_TEXT_SECONDARY, font=(_ff, 9), justify="center", spacing1=4, spacing3=12)
        self.text.tag_configure("img_center", justify="center", spacing1=8, spacing3=4)

    def set_base_dir(self, base_dir: str | Path):
        """画像の相対パスを解決するためのベースディレクトリを設定"""
        self._base_dir = Path(base_dir) if base_dir else None

    def load(self, markdown_text: str, base_dir: str | Path | None = None):
        """Markdownテキストを読み込んで表示"""
        if base_dir:
            self._base_dir = Path(base_dir)

        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self._photo_images.clear()

        if not markdown_text:
            self.text.configure(state="disabled")
            return

        in_code_block = False
        lines = markdown_text.split("\n")

        for line in lines:
            # コードブロック
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                if in_code_block:
                    self.text.insert("end", "\n", "normal")
                continue

            if in_code_block:
                self.text.insert("end", line + "\n", "codeblock")
                continue

            # 画像行: ![alt](path)
            img_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line.strip())
            if img_match:
                alt_text = img_match.group(1)
                img_path = img_match.group(2)
                self._insert_image(img_path, alt_text)
                continue

            # 見出し
            if line.startswith("# "):
                self.text.insert("end", line[2:] + "\n", "h1")
            elif line.startswith("## "):
                self.text.insert("end", line[3:] + "\n", "h2")
            elif line.startswith("### "):
                self.text.insert("end", line[4:] + "\n", "h3")
            # 水平線
            elif line.strip() in ("---", "***", "___"):
                self.text.insert("end", "\u2500" * 60 + "\n", "hr")
            # 引用
            elif line.startswith("> "):
                self.text.insert("end", line[2:] + "\n", "quote")
            # リスト
            elif re.match(r"^[\s]*[-*+]\s", line):
                self.text.insert("end", line + "\n", "bullet")
            elif re.match(r"^[\s]*\d+\.\s", line):
                self.text.insert("end", line + "\n", "bullet")
            # 通常テキスト（画像がインラインにある場合も処理）
            else:
                # インライン画像をチェック: テキスト中の ![alt](path)
                if "![" in line and "](" in line:
                    self._insert_line_with_images(line)
                else:
                    self._insert_inline(line + "\n")

        # 文字数カウント
        content = self.text.get("1.0", "end").strip()
        char_count = len(content)
        self.word_count_label.configure(text=f"{char_count:,} chars")

        self.text.configure(state="disabled")

    def _insert_image(self, img_path: str, alt_text: str = ""):
        """画像をテキストウィジェットにインライン挿入"""
        if not HAS_PIL:
            self.text.insert("end", f"[Image: {alt_text or img_path}]\n", "img_caption")
            return

        # パスの解決
        resolved = self._resolve_image_path(img_path)
        if not resolved or not resolved.exists():
            self.text.insert("end", f"[Image not found: {img_path}]\n", "img_caption")
            return

        try:
            img = Image.open(resolved)

            # テキストウィジェット幅に合わせてリサイズ
            self.update_idletasks()
            max_w = self.text.winfo_width() - 80
            if max_w < 200:
                max_w = 600

            # アスペクト比を維持してリサイズ
            orig_w, orig_h = img.size
            if orig_w > max_w:
                ratio = max_w / orig_w
                new_h = int(orig_h * ratio)
                img = img.resize((max_w, new_h), Image.Resampling.LANCZOS)

            tk_img = ImageTk.PhotoImage(img)
            self._photo_images.append(tk_img)  # GC防止

            # 画像を挿入
            self.text.insert("end", "\n", "img_center")
            self.text.image_create("end", image=tk_img, padx=10)
            self.text.insert("end", "\n", "img_center")

            # キャプション
            if alt_text:
                self.text.insert("end", f"{alt_text}\n", "img_caption")

        except Exception as e:
            self.text.insert("end", f"[Image error: {e}]\n", "img_caption")

    def _insert_line_with_images(self, line: str):
        """テキスト中の画像参照を処理"""
        parts = re.split(r"(!\[[^\]]*\]\([^)]+\))", line)
        for part in parts:
            img_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", part)
            if img_match:
                alt_text = img_match.group(1)
                img_path = img_match.group(2)
                self._insert_image(img_path, alt_text)
            else:
                if part.strip():
                    self._insert_inline(part)
        self.text.insert("end", "\n", "normal")

    def _resolve_image_path(self, img_path: str) -> Path | None:
        """画像パスを解決"""
        p = Path(img_path)

        # 絶対パスならそのまま
        if p.is_absolute() and p.exists():
            return p

        # ベースディレクトリからの相対パス
        if self._base_dir:
            resolved = self._base_dir / img_path
            if resolved.exists():
                return resolved

        return None

    def _insert_inline(self, text: str):
        """インラインマークアップを処理して挿入"""
        parts = re.split(r"(`[^`]+`)", text)
        for part in parts:
            if part.startswith("`") and part.endswith("`"):
                self.text.insert("end", part[1:-1], "code")
            elif "**" in part:
                bold_parts = re.split(r"(\*\*[^*]+\*\*)", part)
                for bp in bold_parts:
                    if bp.startswith("**") and bp.endswith("**"):
                        self.text.insert("end", bp[2:-2], "bold")
                    else:
                        self.text.insert("end", bp, "normal")
            else:
                self.text.insert("end", part, "normal")

    def _copy_all(self):
        """全テキストをクリップボードにコピー"""
        content = self.text.get("1.0", "end").strip()
        if content:
            self.clipboard_clear()
            self.clipboard_append(content)

    def get_text(self) -> str:
        return self.text.get("1.0", "end").strip()

    def get_raw_markdown(self) -> str:
        """保持している元のMarkdownテキストを返す"""
        return getattr(self, "_raw_markdown", "")
