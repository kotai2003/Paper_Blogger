"""メニューバー"""

import tkinter as tk
from style.theme import AppTheme


class MenuBar(tk.Menu):
    """アプリケーションメニューバー"""

    def __init__(self, parent, controller):
        super().__init__(parent, bg=AppTheme.COLOR_BG, fg=AppTheme.COLOR_TEXT,
                         font=AppTheme.FONT_NORMAL, relief="flat", borderwidth=0)
        self.controller = controller

        # ファイルメニュー
        file_menu = tk.Menu(self, tearoff=0, font=AppTheme.FONT_NORMAL)
        file_menu.add_command(label="Open PDF...", accelerator="Ctrl+O",
                              command=controller.open_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Save Article...", accelerator="Ctrl+S",
                              command=controller.save_article)
        file_menu.add_command(label="Save Summary...",
                              command=controller.save_summary)
        file_menu.add_separator()
        file_menu.add_command(label="Open Output Folder",
                              command=controller.open_output_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Alt+F4",
                              command=controller.quit_app)
        self.add_cascade(label="File", menu=file_menu)

        # 実行メニュー
        run_menu = tk.Menu(self, tearoff=0, font=AppTheme.FONT_NORMAL)
        run_menu.add_command(label="Run Pipeline", accelerator="F5",
                             command=controller.run_pipeline)
        run_menu.add_command(label="Stop", accelerator="Ctrl+C",
                             command=controller.stop_pipeline)
        run_menu.add_separator()
        run_menu.add_command(label="Clear Log",
                             command=controller.clear_log)
        self.add_cascade(label="Run", menu=run_menu)

        # 設定メニュー
        settings_menu = tk.Menu(self, tearoff=0, font=AppTheme.FONT_NORMAL)
        settings_menu.add_command(label="Settings...",
                                  command=controller.open_settings)
        self.add_cascade(label="Settings", menu=settings_menu)

        # ヘルプメニュー
        help_menu = tk.Menu(self, tearoff=0, font=AppTheme.FONT_NORMAL)
        help_menu.add_command(label="About", command=controller.show_about)
        self.add_cascade(label="Help", menu=help_menu)
