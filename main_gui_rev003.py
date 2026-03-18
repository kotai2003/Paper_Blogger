"""
Paper Blogger GUI Rev003 - デフォルトLLM: gpt-oss:120b-cloud

Rev002 との差分:
  - デフォルトLLMモデルを gpt-oss:120b-cloud に変更
  - パイプライン Step 8 (中国語フィルター) はRev002と同様

Usage:
    python main_gui_rev003.py
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import tkinter as tk

from style.theme import AppTheme
from app.controller_rev002 import PipelineController
from gui.main_window import MainWindow


def main():
    root = tk.Tk()
    root.title("Paper Blogger Rev003 - gpt-oss:120b-cloud")
    root.geometry("1280x800")
    root.minsize(900, 600)

    # テーマ適用
    theme = AppTheme(root)
    theme.apply()

    # favicon
    icon_path = PROJECT_ROOT / "assets" / "favicon.ico"
    if icon_path.exists():
        root.iconbitmap(str(icon_path))

    # MVC: Controller → MainWindow
    controller = PipelineController(root)
    main_window = MainWindow(root, controller)
    controller.set_main_window(main_window)

    # config.yamlから初期設定を読み込み
    config_path = PROJECT_ROOT / "paper_blog_pipeline" / "config.yaml"
    if config_path.exists():
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        main_window.left_panel.load_config(config)

    # Rev003: デフォルトモデルを gpt-oss:120b-cloud に強制設定
    main_window.left_panel.model_var.set("gpt-oss:120b-cloud")

    # ウィンドウを画面中央に配置
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.protocol("WM_DELETE_WINDOW", controller.quit_app)
    root.mainloop()


if __name__ == "__main__":
    main()
