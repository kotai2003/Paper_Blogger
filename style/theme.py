"""
Paper Blogger GUI - 統一テーマシステム

全GUIアプリケーションがこのテーマを読み込むことで
商用ソフトレベルの統一UIを実現する。

使用方法:
    from style.theme import AppTheme
    theme = AppTheme(root)
    theme.apply()
"""

import tkinter as tk
from tkinter import ttk
import platform


class AppTheme:
    """統一テーマ定義 - 全アプリ共通"""

    # ================================================================
    # フォント
    # ================================================================
    _SYSTEM = platform.system()
    _FONT_FAMILY = {
        "Windows": "Meiryo",
        "Darwin": "Hiragino Sans",
        "Linux": "Noto Sans CJK JP",
    }.get(_SYSTEM, "Meiryo")

    _FONT_FAMILY_MONO = {
        "Windows": "Cascadia Code",
        "Darwin": "SF Mono",
        "Linux": "Noto Sans Mono",
    }.get(_SYSTEM, "Consolas")

    FONT_SMALL = (_FONT_FAMILY, 9)
    FONT_NORMAL = (_FONT_FAMILY, 10)
    FONT_MEDIUM = (_FONT_FAMILY, 11)
    FONT_LARGE = (_FONT_FAMILY, 13, "bold")
    FONT_TITLE = (_FONT_FAMILY, 16, "bold")
    FONT_HEADING = (_FONT_FAMILY, 20, "bold")

    FONT_MONO_SMALL = (_FONT_FAMILY_MONO, 9)
    FONT_MONO = (_FONT_FAMILY_MONO, 10)

    # ================================================================
    # カラーパレット
    # ================================================================
    COLOR_BG = "#f5f6f8"
    COLOR_BG_DARK = "#ebedf2"
    COLOR_BG_WHITE = "#ffffff"
    COLOR_BG_INPUT = "#ffffff"

    COLOR_PRIMARY = "#4f6bed"
    COLOR_PRIMARY_HOVER = "#3d59d4"
    COLOR_PRIMARY_LIGHT = "#e8ecfc"
    COLOR_PRIMARY_PRESSED = "#2e45b8"

    COLOR_ACCENT = "#4f6bed"
    COLOR_SUCCESS = "#22c55e"
    COLOR_WARNING = "#f59e0b"
    COLOR_ERROR = "#ef4444"
    COLOR_INFO = "#3b82f6"

    COLOR_TEXT = "#2d2d2d"
    COLOR_TEXT_SECONDARY = "#6b7280"
    COLOR_TEXT_MUTED = "#9ca3af"
    COLOR_TEXT_INVERSE = "#ffffff"

    COLOR_BORDER = "#d1d5db"
    COLOR_BORDER_LIGHT = "#e5e7eb"
    COLOR_SEPARATOR = "#e5e7eb"

    COLOR_SIDEBAR = "#ebedf2"
    COLOR_TOOLBAR = "#f0f1f5"

    COLOR_TAB_ACTIVE = "#ffffff"
    COLOR_TAB_INACTIVE = "#e8e9ed"

    COLOR_LOG_BG = "#1e1e2e"
    COLOR_LOG_FG = "#cdd6f4"
    COLOR_LOG_INFO = "#89b4fa"
    COLOR_LOG_WARN = "#f9e2af"
    COLOR_LOG_ERROR = "#f38ba8"
    COLOR_LOG_SUCCESS = "#a6e3a1"

    # ================================================================
    # サイズ・余白
    # ================================================================
    PAD_XS = 2
    PAD_SM = 4
    PAD_MD = 8
    PAD_LG = 12
    PAD_XL = 16
    PAD_XXL = 24

    BORDER_RADIUS = 6
    BORDER_WIDTH = 1

    BUTTON_PAD_X = 16
    BUTTON_PAD_Y = 6
    BUTTON_HEIGHT = 32

    TOOLBAR_HEIGHT = 44
    STATUSBAR_HEIGHT = 28
    SIDEBAR_WIDTH = 320

    ICON_SIZE = 16
    ICON_SIZE_LG = 20

    # ================================================================
    # テーマ適用
    # ================================================================

    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style(root)

    def apply(self):
        """テーマを全ウィジェットに適用"""
        self.style.theme_use("clam")
        self._configure_root()
        self._configure_frames()
        self._configure_labels()
        self._configure_buttons()
        self._configure_entries()
        self._configure_checkbutton()
        self._configure_radiobutton()
        self._configure_labelframe()
        self._configure_notebook()
        self._configure_panedwindow()
        self._configure_scrollbar()
        self._configure_treeview()
        self._configure_combobox()
        self._configure_separator()
        self._configure_progressbar()
        self._configure_spinbox()

    def _configure_root(self):
        self.root.configure(bg=self.COLOR_BG)

    def _configure_frames(self):
        self.style.configure("TFrame", background=self.COLOR_BG)
        self.style.configure("Sidebar.TFrame", background=self.COLOR_SIDEBAR)
        self.style.configure("Toolbar.TFrame", background=self.COLOR_TOOLBAR)
        self.style.configure("Card.TFrame", background=self.COLOR_BG_WHITE, relief="flat")
        self.style.configure("StatusBar.TFrame", background=self.COLOR_BG_DARK)

    def _configure_labels(self):
        self.style.configure(
            "TLabel",
            background=self.COLOR_BG,
            foreground=self.COLOR_TEXT,
            font=self.FONT_NORMAL,
        )
        self.style.configure("Title.TLabel", font=self.FONT_TITLE, foreground=self.COLOR_TEXT)
        self.style.configure("Heading.TLabel", font=self.FONT_HEADING, foreground=self.COLOR_TEXT)
        self.style.configure("Large.TLabel", font=self.FONT_LARGE, foreground=self.COLOR_TEXT)
        self.style.configure("Small.TLabel", font=self.FONT_SMALL, foreground=self.COLOR_TEXT_SECONDARY)
        self.style.configure("Muted.TLabel", font=self.FONT_NORMAL, foreground=self.COLOR_TEXT_MUTED)
        self.style.configure(
            "Sidebar.TLabel",
            background=self.COLOR_SIDEBAR,
            foreground=self.COLOR_TEXT,
            font=self.FONT_NORMAL,
        )
        self.style.configure(
            "Sidebar.Small.TLabel",
            background=self.COLOR_SIDEBAR,
            foreground=self.COLOR_TEXT_SECONDARY,
            font=self.FONT_SMALL,
        )
        self.style.configure(
            "Sidebar.Large.TLabel",
            background=self.COLOR_SIDEBAR,
            foreground=self.COLOR_TEXT,
            font=self.FONT_LARGE,
        )
        self.style.configure(
            "Sidebar.Muted.TLabel",
            background=self.COLOR_SIDEBAR,
            foreground=self.COLOR_TEXT_MUTED,
            font=self.FONT_NORMAL,
        )
        self.style.configure(
            "Toolbar.TLabel",
            background=self.COLOR_TOOLBAR,
            foreground=self.COLOR_TEXT,
            font=self.FONT_NORMAL,
        )
        self.style.configure(
            "StatusBar.TLabel",
            background=self.COLOR_BG_DARK,
            foreground=self.COLOR_TEXT_SECONDARY,
            font=self.FONT_SMALL,
        )
        self.style.configure(
            "Success.TLabel",
            foreground=self.COLOR_SUCCESS,
            font=self.FONT_NORMAL,
        )
        self.style.configure(
            "Error.TLabel",
            foreground=self.COLOR_ERROR,
            font=self.FONT_NORMAL,
        )

    def _configure_buttons(self):
        # Primary button
        self.style.configure(
            "Primary.TButton",
            font=self.FONT_NORMAL,
            padding=(self.BUTTON_PAD_X, self.BUTTON_PAD_Y),
            background=self.COLOR_PRIMARY,
            foreground=self.COLOR_TEXT_INVERSE,
            borderwidth=0,
        )
        self.style.map(
            "Primary.TButton",
            background=[
                ("active", self.COLOR_PRIMARY_HOVER),
                ("pressed", self.COLOR_PRIMARY_PRESSED),
                ("disabled", self.COLOR_BORDER),
            ],
            foreground=[("disabled", self.COLOR_TEXT_MUTED)],
        )

        # Default button
        self.style.configure(
            "TButton",
            font=self.FONT_NORMAL,
            padding=(self.BUTTON_PAD_X, self.BUTTON_PAD_Y),
            background=self.COLOR_BG_WHITE,
            foreground=self.COLOR_TEXT,
            borderwidth=1,
            relief="solid",
        )
        self.style.map(
            "TButton",
            background=[
                ("active", self.COLOR_BG_DARK),
                ("disabled", self.COLOR_BG),
            ],
            foreground=[("disabled", self.COLOR_TEXT_MUTED)],
        )

        # Toolbar button (flat)
        self.style.configure(
            "Toolbar.TButton",
            font=self.FONT_NORMAL,
            padding=(10, 4),
            background=self.COLOR_TOOLBAR,
            foreground=self.COLOR_TEXT,
            borderwidth=0,
            relief="flat",
        )
        self.style.map(
            "Toolbar.TButton",
            background=[("active", self.COLOR_BORDER_LIGHT)],
        )

        # Danger button
        self.style.configure(
            "Danger.TButton",
            font=self.FONT_NORMAL,
            padding=(self.BUTTON_PAD_X, self.BUTTON_PAD_Y),
            background=self.COLOR_ERROR,
            foreground=self.COLOR_TEXT_INVERSE,
            borderwidth=0,
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", "#dc2626")],
        )

    def _configure_entries(self):
        self.style.configure(
            "TEntry",
            font=self.FONT_NORMAL,
            padding=(8, 6),
            fieldbackground=self.COLOR_BG_INPUT,
            foreground=self.COLOR_TEXT,
            borderwidth=1,
            relief="solid",
        )
        self.style.map(
            "TEntry",
            bordercolor=[("focus", self.COLOR_PRIMARY)],
            lightcolor=[("focus", self.COLOR_PRIMARY)],
        )

    def _configure_checkbutton(self):
        self.style.configure(
            "TCheckbutton",
            background=self.COLOR_BG,
            foreground=self.COLOR_TEXT,
            font=self.FONT_NORMAL,
            indicatormargin=4,
        )
        self.style.map(
            "TCheckbutton",
            background=[("active", self.COLOR_BG)],
            indicatorcolor=[
                ("selected", self.COLOR_PRIMARY),
                ("!selected", self.COLOR_BG_WHITE),
            ],
        )
        # サイドバー用
        self.style.configure(
            "Sidebar.TCheckbutton",
            background=self.COLOR_SIDEBAR,
            foreground=self.COLOR_TEXT,
            font=self.FONT_NORMAL,
        )
        self.style.map(
            "Sidebar.TCheckbutton",
            background=[("active", self.COLOR_SIDEBAR)],
            indicatorcolor=[
                ("selected", self.COLOR_PRIMARY),
                ("!selected", self.COLOR_BG_WHITE),
            ],
        )

    def _configure_radiobutton(self):
        self.style.configure(
            "TRadiobutton",
            background=self.COLOR_BG,
            foreground=self.COLOR_TEXT,
            font=self.FONT_NORMAL,
            indicatormargin=4,
        )
        self.style.map(
            "TRadiobutton",
            background=[("active", self.COLOR_BG)],
            indicatorcolor=[
                ("selected", self.COLOR_PRIMARY),
                ("!selected", self.COLOR_BG_WHITE),
            ],
        )

    def _configure_labelframe(self):
        self.style.configure(
            "TLabelframe",
            background=self.COLOR_BG,
            foreground=self.COLOR_TEXT,
            borderwidth=1,
            relief="solid",
            bordercolor=self.COLOR_BORDER_LIGHT,
        )
        self.style.configure(
            "TLabelframe.Label",
            background=self.COLOR_BG,
            foreground=self.COLOR_TEXT,
            font=self.FONT_NORMAL,
        )
        # サイドバー用
        self.style.configure(
            "Sidebar.TLabelframe",
            background=self.COLOR_SIDEBAR,
            foreground=self.COLOR_TEXT,
            borderwidth=1,
            relief="solid",
            bordercolor=self.COLOR_BORDER_LIGHT,
        )
        self.style.configure(
            "Sidebar.TLabelframe.Label",
            background=self.COLOR_SIDEBAR,
            foreground=self.COLOR_TEXT,
            font=self.FONT_NORMAL,
        )

    def _configure_notebook(self):
        self.style.configure(
            "TNotebook",
            background=self.COLOR_BG,
            borderwidth=0,
            tabmargins=(8, 4, 8, 0),
        )
        self.style.configure(
            "TNotebook.Tab",
            font=self.FONT_NORMAL,
            padding=(16, 8),
            background=self.COLOR_TAB_INACTIVE,
            foreground=self.COLOR_TEXT_SECONDARY,
            borderwidth=0,
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", self.COLOR_TAB_ACTIVE)],
            foreground=[("selected", self.COLOR_PRIMARY)],
            expand=[("selected", [0, 0, 0, 2])],
        )

    def _configure_panedwindow(self):
        self.style.configure(
            "TPanedwindow",
            background=self.COLOR_SEPARATOR,
        )
        self.style.configure(
            "Sash",
            sashthickness=4,
            gripcount=0,
        )

    def _configure_scrollbar(self):
        self.style.configure(
            "TScrollbar",
            background=self.COLOR_BG_DARK,
            troughcolor=self.COLOR_BG,
            borderwidth=0,
            arrowsize=0,
        )
        self.style.map(
            "TScrollbar",
            background=[("active", self.COLOR_BORDER)],
        )

    def _configure_treeview(self):
        self.style.configure(
            "Treeview",
            font=self.FONT_NORMAL,
            background=self.COLOR_BG_WHITE,
            foreground=self.COLOR_TEXT,
            fieldbackground=self.COLOR_BG_WHITE,
            borderwidth=0,
            rowheight=28,
        )
        self.style.configure(
            "Treeview.Heading",
            font=self.FONT_NORMAL,
            background=self.COLOR_BG_DARK,
            foreground=self.COLOR_TEXT,
            borderwidth=1,
            relief="flat",
        )
        self.style.map(
            "Treeview",
            background=[("selected", self.COLOR_PRIMARY_LIGHT)],
            foreground=[("selected", self.COLOR_PRIMARY)],
        )

    def _configure_combobox(self):
        self.style.configure(
            "TCombobox",
            font=self.FONT_NORMAL,
            padding=(8, 6),
            fieldbackground=self.COLOR_BG_INPUT,
            foreground=self.COLOR_TEXT,
            borderwidth=1,
        )
        self.style.map(
            "TCombobox",
            bordercolor=[("focus", self.COLOR_PRIMARY)],
            fieldbackground=[("readonly", self.COLOR_BG_INPUT)],
        )

    def _configure_separator(self):
        self.style.configure(
            "TSeparator",
            background=self.COLOR_SEPARATOR,
        )

    def _configure_progressbar(self):
        self.style.configure(
            "TProgressbar",
            background=self.COLOR_PRIMARY,
            troughcolor=self.COLOR_BG_DARK,
            borderwidth=0,
            thickness=4,
        )
        self.style.configure(
            "Success.Horizontal.TProgressbar",
            background=self.COLOR_SUCCESS,
        )

    def _configure_spinbox(self):
        self.style.configure(
            "TSpinbox",
            font=self.FONT_NORMAL,
            padding=(8, 6),
            fieldbackground=self.COLOR_BG_INPUT,
            foreground=self.COLOR_TEXT,
            borderwidth=1,
            background=self.COLOR_BG,
            arrowcolor=self.COLOR_TEXT_SECONDARY,
        )
        self.style.map(
            "TSpinbox",
            bordercolor=[("focus", self.COLOR_PRIMARY)],
            arrowcolor=[("active", self.COLOR_PRIMARY)],
        )
