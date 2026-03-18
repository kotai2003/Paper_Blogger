"""左パネル - PDF選択、設定、ログ"""

import tkinter as tk
from tkinter import ttk

from style.theme import AppTheme
from widgets.file_selector import FileSelector
from widgets.log_console import LogConsole


class LeftPanel(ttk.Frame):
    """左サイドパネル: ファイル選択 + 設定 + ログコンソール"""

    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, style="Sidebar.TFrame", **kwargs)
        self.controller = controller

        container = ttk.Frame(self, style="Sidebar.TFrame")
        container.pack(fill="both", expand=True, padx=12, pady=12)

        # ================================================================
        # PDF選択
        # ================================================================
        self.file_selector = FileSelector(container, label="PDF File",
                                          style="Sidebar.TFrame")
        self.file_selector.pack(fill="x", pady=(0, 12))

        # ================================================================
        # 設定セクション
        # ================================================================
        settings_frame = ttk.LabelFrame(
            container, text="Settings", padding=(12, 8),
            style="Sidebar.TLabelframe",
        )
        settings_frame.pack(fill="x", pady=(0, 12))

        # Model
        ttk.Label(settings_frame, text="LLM Model",
                  style="Sidebar.Small.TLabel").pack(anchor="w")
        self.model_var = tk.StringVar(value="gpt-oss:120b-cloud")
        self.model_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.model_var,
            values=[
                "gpt-oss:120b-cloud",
                "minimax-m2.5:cloud",
                "qwen3.5:cloud",
                "glm-5:cloud",
            ],
            font=AppTheme.FONT_NORMAL,
        )
        self.model_combo.pack(fill="x", pady=(2, 8))

        # VLM Model
        ttk.Label(settings_frame, text="VLM Model",
                  style="Sidebar.Small.TLabel").pack(anchor="w")
        self.vlm_var = tk.StringVar(value="")
        self.vlm_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.vlm_var,
            values=[
                "",
                "qwen3-vl:235b-cloud",
                "qwen3.5:397b-cloud",
                "glm-5:cloud",
            ],
            font=AppTheme.FONT_NORMAL,
        )
        self.vlm_combo.pack(fill="x", pady=(2, 8))

        # Max Figures
        fig_frame = ttk.Frame(settings_frame, style="Sidebar.TFrame")
        fig_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(fig_frame, text="Max Figures",
                  style="Sidebar.Small.TLabel").pack(side="left")
        self.max_figures_var = tk.IntVar(value=7)
        self.max_figures_spin = ttk.Spinbox(
            fig_frame, from_=1, to=20, width=5,
            textvariable=self.max_figures_var,
            font=AppTheme.FONT_NORMAL,
        )
        self.max_figures_spin.pack(side="right")

        # Skip Figures
        self.skip_figures_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            settings_frame, text="Skip figure analysis",
            variable=self.skip_figures_var,
            style="Sidebar.TCheckbutton",
        ).pack(anchor="w")

        # Base URL
        ttk.Label(settings_frame, text="Ollama URL",
                  style="Sidebar.Small.TLabel").pack(anchor="w", pady=(8, 0))
        self.base_url_var = tk.StringVar(value="http://localhost:11434/v1")
        ttk.Entry(
            settings_frame,
            textvariable=self.base_url_var,
            font=AppTheme.FONT_SMALL,
        ).pack(fill="x", pady=(2, 0))

        # ================================================================
        # Output Folder
        # ================================================================
        output_frame = ttk.LabelFrame(
            container, text="Output", padding=(12, 8),
            style="Sidebar.TLabelframe",
        )
        output_frame.pack(fill="x", pady=(0, 12))

        dir_row = ttk.Frame(output_frame, style="Sidebar.TFrame")
        dir_row.pack(fill="x")

        self.output_dir_var = tk.StringVar()
        self.output_dir_entry = ttk.Entry(
            dir_row,
            textvariable=self.output_dir_var,
            font=AppTheme.FONT_SMALL,
        )
        self.output_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        ttk.Button(
            dir_row, text="...",
            command=controller.browse_output_dir,
            width=3,
        ).pack(side="right")

        self.open_folder_btn = ttk.Button(
            output_frame, text="Open in Explorer",
            command=controller.open_output_folder,
        )
        self.open_folder_btn.pack(fill="x", pady=(6, 0))

        # ================================================================
        # 実行ボタン
        # ================================================================
        self.run_btn = ttk.Button(
            container,
            text="Run Pipeline",
            style="Primary.TButton",
            command=controller.run_pipeline,
        )
        self.run_btn.pack(fill="x", pady=(0, 12), ipady=4)

        # ================================================================
        # ログコンソール
        # ================================================================
        self.log_console = LogConsole(container, sidebar=True,
                                       style="Sidebar.TFrame")
        self.log_console.pack(fill="both", expand=True)

    def get_settings(self) -> dict:
        """現在の設定値を辞書で返す"""
        vlm = self.vlm_var.get().strip()
        return {
            "pdf_path": self.file_selector.get_path(),
            "model": self.model_var.get(),
            "vlm_model": vlm if vlm else None,
            "max_figures": self.max_figures_var.get(),
            "skip_figures": self.skip_figures_var.get(),
            "base_url": self.base_url_var.get(),
            "output_dir": self.output_dir_var.get(),
        }

    def load_config(self, config: dict):
        """config辞書から設定を読み込み"""
        if "model" in config and config["model"]:
            self.model_var.set(config["model"])
        if "vlm_model" in config and config["vlm_model"]:
            self.vlm_var.set(config["vlm_model"])
        if "max_figures" in config:
            self.max_figures_var.set(config["max_figures"])
        if "skip_figures" in config:
            self.skip_figures_var.set(config["skip_figures"])
        if "base_url" in config and config["base_url"]:
            self.base_url_var.set(config["base_url"])

    def set_output_dir(self, path: str):
        """出力ディレクトリを設定"""
        self.output_dir_var.set(path)

    def set_running(self, running: bool):
        state = "disabled" if running else "normal"
        self.run_btn.configure(state=state)
        self.model_combo.configure(state=state)
        self.vlm_combo.configure(state=state)
