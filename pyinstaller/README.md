# Paper Blogger - PyInstaller ビルド手順

## ビルドモード

2種類のビルドを用意しています。

| モード | スクリプト | 用途 |
|--------|-----------|------|
| **通常ビルド** | `build.bat` | 開発・テスト用。高速ビルド |
| **セキュアビルド** | `secure_build.bat` | 配布用。Cython + リバースエンジニアリング対策 |

## 前提条件

```bash
# 共通
pip install pyinstaller
pip install -r paper_blog_pipeline/requirements.txt
pip install Pillow

# セキュアビルドのみ
pip install cython
```

## 通常ビルド

```bash
cd pyinstaller
build.bat
```

または手動で:

```bash
cd pyinstaller
python -m PyInstaller paper_blogger.spec --clean --noconfirm
```

## セキュアビルド (配布用)

```bash
cd pyinstaller
secure_build.bat
```

ビルドフロー:

```
[Step 1] Cython compile (.py → .pyd ネイティブバイナリ)
[Step 2] PyInstaller build (.pyd を含めてパッケージ化)
[Step 3] ソースツリーから .pyd を削除 (開発環境を汚さない)
```

手動で実行する場合:

```bash
# 1. Cython コンパイル
cd project_root
python build_tools/setup_cython.py build_ext --inplace

# 2. PyInstaller ビルド
cd pyinstaller
python -m PyInstaller secure_gui.spec --clean --noconfirm
```

## 出力先

OneDrive ファイルロック回避のため、ビルド出力先は:

```
%LOCALAPPDATA%\paper_blogger_build\dist\paper_blogger\
```

ビルド完了後、自動でエクスプローラーが開きます。

## 出力構造

```
dist/paper_blogger/
  paper_blogger.exe              # メインアプリ
  _internal/                     # Python ランタイム + 依存ライブラリ
    app/
      controller.cp313-win_amd64.pyd   # Cython コンパイル済み (セキュアビルドのみ)
      __init__.py
    gui/
      main_window.cp313-win_amd64.pyd
      tabs/
        tab_summary.cp313-win_amd64.pyd
        ...
    widgets/
      ...
    paper_blog_pipeline/
      config.yaml
      prompts/
        analyze_paper.txt
        analyze_figure.txt
        generate_blog.txt
        ochiai_summary.txt
      parser/
        pdf_parser.cp313-win_amd64.pyd
      ...
  assets/
    favicon.ico
    icons/
```

## リバースエンジニアリング対策 (セキュアビルド)

| レイヤー | 対策 | 効果 |
|----------|------|------|
| **L1: ソースコード** | Cython → `.pyd` | Python → C → ネイティブDLL。decompile ほぼ不可能 |
| **L2: Bytecode** | `optimize=2` | docstring・assert 完全削除 |
| **L3: Binary** | UPX 圧縮 | 静的解析を困難に |
| **L4: UI** | `console=False` | デバッグ出力を非表示 |

## 設計方針

| 項目 | 設定 | 理由 |
|------|------|------|
| `--onedir` | Yes | 起動高速・容量小 |
| `--onefile` | No | 起動遅い・展開で容量増 |
| `console=False` | Yes | GUI アプリのためコンソール非表示 |
| `optimize=2` | Yes | docstring 除去でサイズ削減 |
| `strip=False` | Yes | Windows では strip コマンドが無いため無効 |
| `upx=True` | Yes | バイナリ圧縮 (UPX がある場合) |

## UPX でさらに圧縮する場合

[UPX](https://upx.github.io/) をダウンロードし、PATH に追加してからビルドすると自動で適用されます。

## ファイル一覧

```
pyinstaller/
  paper_blogger.spec     # 通常ビルド用 spec
  build.bat              # 通常ビルドスクリプト
  secure_gui.spec        # セキュアビルド用 spec
  secure_build.bat       # セキュアビルドスクリプト
  README.md              # このファイル

build_tools/
  setup_cython.py        # Cython コンパイラ設定
```

## 注意事項

- Ollama が `localhost:11434` で動作している必要があります (アプリ同梱ではありません)
- `config.yaml` は配布物にコピーされます。配布後のカスタマイズも可能です
- input/output フォルダはアプリ実行時に自動作成されます
- セキュアビルドには C コンパイラ (MSVC) が必要です。Visual Studio Build Tools をインストールしてください
