"""
Paper Blogger GUI Rev004 - Ollama インストール済みモデルから動的に選択

Rev003 との差分:
  - LLM/VLM モデル名を YAML から固定指定するのを廃止
  - `ollama list` の結果を取得し、GUI のプルダウンメニューに動的に表示
  - 単一のマルチモーダル LLM で LLM/VLM 両方をカバーする統一モデル方式
    (VLM プルダウンは非表示、LLM 用に選んだモデルが VLM にも使われる)
  - 中国語フィルター (Step 8) を廃止 → 7ステップ構成
    （中国語が含まれていてもフィルタリングしない）

Usage:
    python main_gui.py
"""

import sys
import subprocess
from pathlib import Path
from tkinter import messagebox
from tkinter import ttk

# プロジェクトルートをパスに追加
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

import tkinter as tk

from style.theme import AppTheme
from app.controller_rev004 import PipelineController  # Rev004: 中国語フィルター無し
from gui.main_window import MainWindow


# ============================================================
# Rev004: Ollama モデル一覧取得
# ============================================================
def fetch_ollama_models() -> list[str]:
    """`ollama list` の結果からインストール済みモデル名一覧を取得する。

    Returns
    -------
    list[str]
        モデル名 (NAME 列) のリスト。取得失敗時は空リスト。

    Raises
    ------
    RuntimeError
        ollama コマンドが見つからない / 実行失敗した場合。
    """
    try:
        # Windows でコンソールウィンドウを出さないフラグ
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            creationflags=creationflags,
        )
    except FileNotFoundError as e:
        raise RuntimeError(
            "`ollama` コマンドが見つかりません。Ollama がインストールされ、"
            "PATH に登録されているか確認してください。"
        ) from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            "`ollama list` がタイムアウトしました。Ollama サーバが起動しているか確認してください。"
        ) from e
    except Exception as e:
        raise RuntimeError(f"`ollama list` の実行に失敗しました: {e}") from e

    if result.returncode != 0:
        stderr = (result.stderr or "").strip() or "(no stderr)"
        raise RuntimeError(
            f"`ollama list` がエラー終了しました (exit={result.returncode}):\n{stderr}"
        )

    # 出力をパース: 1行目はヘッダ、2行目以降が "NAME ID SIZE MODIFIED"
    lines = (result.stdout or "").splitlines()
    models: list[str] = []
    for line in lines[1:]:
        line = line.rstrip()
        if not line:
            continue
        # 先頭の空白を許容し、最初の空白までを NAME とする
        name = line.split()[0] if line.split() else ""
        if name:
            models.append(name)
    return models


# ============================================================
# Rev004: VLM 関連ウィジェットの非表示・LLM ラベルのリネーム用ヘルパ
# ============================================================
def _hide_vlm_widgets(left_panel) -> None:
    """VLM プルダウンと「VLM Model」ラベルを左パネルから取り除き、
    「LLM Model」ラベルを「Model (Multimodal)」へリネームする。

    LeftPanel のラベル参照が保存されていないため、vlm_combo の親フレームの
    children を走査して、対応する Label をテキスト一致で見つけて操作する。
    """
    vlm_combo = left_panel.vlm_combo
    settings_frame = vlm_combo.master

    for child in list(settings_frame.winfo_children()):
        if isinstance(child, (ttk.Label, tk.Label)):
            text = child.cget("text")
            if text == "VLM Model":
                child.pack_forget()
            elif text == "LLM Model":
                child.configure(text="Model (Multimodal)")

    # VLM コンボボックス自体を非表示に
    vlm_combo.pack_forget()


def main():
    root = tk.Tk()
    root.title("Paper Blogger Rev004 - Unified Multimodal Model")
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

    # ============================================================
    # Rev004: config.yaml はモデル以外のキー (base_url など) のみ反映する
    # LLM/VLM モデルは YAML ではなく ollama list から取得する
    # ============================================================
    config_path = PROJECT_ROOT / "paper_blog_pipeline" / "config.yaml"
    if config_path.exists():
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        # Rev004: YAML 側の model / vlm_model は使わない
        config.pop("model", None)
        config.pop("vlm_model", None)
        main_window.left_panel.load_config(config)

    # ============================================================
    # Rev004: ollama list からモデル一覧を取得し、プルダウンに反映
    # ============================================================
    try:
        models = fetch_ollama_models()
    except RuntimeError as e:
        messagebox.showerror(
            "Ollama Error",
            f"Ollama モデル一覧の取得に失敗しました。\n\n{e}\n\n"
            "Ollama を起動してから再度アプリを立ち上げてください。"
        )
        models = []

    # ============================================================
    # Rev004: 統一モデル方式
    #   - VLM プルダウン (および "VLM Model" ラベル) は非表示にする
    #   - vlm_var を空文字列に固定 → controller 側で vlm_model=None として扱われ、
    #     LLM 用に選んだモデルがそのまま VLM 呼び出しにも使われる
    #   - "LLM Model" ラベルを "Model (Multimodal)" にリネームし、ユーザーに
    #     マルチモーダル対応モデルを選んでもらうことを明示する
    # ============================================================
    _hide_vlm_widgets(main_window.left_panel)

    if not models:
        # 取得失敗 or 空リストの場合はユーザーに通知し、プルダウンを空にする
        messagebox.showwarning(
            "No Ollama Models",
            "インストール済みの Ollama モデルが見つかりませんでした。\n"
            "`ollama pull <model>` でモデルを取得してから再起動してください。\n\n"
            "プルダウンは空のままになります。"
        )
        main_window.left_panel.model_combo.configure(values=[])
        main_window.left_panel.model_var.set("")
        main_window.left_panel.vlm_var.set("")
    else:
        # 統一モデル用プルダウン: 取得したモデル一覧をそのまま設定
        main_window.left_panel.model_combo.configure(values=models)

        # デフォルト選択: ollama list の先頭モデル
        # (ユーザーが任意のマルチモーダル対応モデルをプルダウンから選択する)
        main_window.left_panel.model_var.set(models[0])

        # Rev004: VLM 変数は常に空 → controller で LLM と同じモデルが使われる
        main_window.left_panel.vlm_var.set("")

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
