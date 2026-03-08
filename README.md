# Paper Blogger - 研究論文 → 技術ブログ記事生成パイプライン

研究論文（PDF）を入力すると、**落合陽一式論文読みフレームワーク**に基づいて論文を解析し、技術ブログ記事と1枚スライド要約を自動生成するシステムです。

LLM/VLMはすべて**Ollama**経由で動作します。

**2つのインターフェース:**
- **CLI** — `paper_blog_pipeline/main.py`（バッチ処理向け）
- **GUI** — `main_gui.py`（Tkinter、商用ソフト風UI）

## 出力

| ファイル | 内容 |
|---------|------|
| `article.md` | 技術ブログ記事（公開品質のMarkdown） |
| `paper_summary_slide.md` | 落合式1枚スライド要約 |
| `images/` | 論文から抽出した図（スコアリングで重要図を自動選択） |

## セットアップ

### 1. 依存パッケージ

```bash
pip install -r paper_blog_pipeline/requirements.txt
```

### 2. Ollama

Ollamaをインストールし、使用するモデルをpullしてください。

```bash
# モデル例
ollama pull minimax-m2.5:cloud
ollama pull qwen3-vl:235b-cloud
ollama pull qwen3.5:cloud
ollama pull glm-5:cloud
```

## 使い方

### GUI（推奨）

```bash
python main_gui.py
```

Tkinter GUIが起動します。PDFを選択し、「Run Pipeline」ボタンで実行。結果はタブで確認できます。

- **Paper Summary** タブ — 落合式1枚スライド要約
- **Blog Article** タブ — 技術ブログ記事（図のインライン表示対応）
- **Figures** タブ — 抽出された図のプレビュー
- **Output** セクション — 出力先フォルダの指定・変更、「Open in Explorer」でフォルダを直接開く

キーボードショートカット: `Ctrl+O`（Open）、`F5`（Run）、`Ctrl+S`（Save）

### CLI — 基本（input/フォルダから一括処理）

`paper_blog_pipeline/input/` にPDFを配置して実行：

```bash
python paper_blog_pipeline/main.py
```

### CLI — 単一PDF指定

```bash
python paper_blog_pipeline/main.py paper.pdf
```

### CLI — オプション

```bash
# モデル指定
python paper_blog_pipeline/main.py --model minimax-m2.5:cloud

# LLMとVLMで別モデルを使用
python paper_blog_pipeline/main.py --model minimax-m2.5:cloud --vlm-model qwen3-vl:235b-cloud

# 図解析をスキップ（高速）
python paper_blog_pipeline/main.py --skip-figures

# 出力先変更
python paper_blog_pipeline/main.py -o ./my_output

# リモートOllama
python paper_blog_pipeline/main.py --base-url http://192.168.1.10:11434/v1

# 解析する図の最大数
python paper_blog_pipeline/main.py --max-figures 3
```

### 設定ファイル（config.yaml）

全オプションは `paper_blog_pipeline/config.yaml` で管理できます。
CLI引数で指定した場合はCLI側が優先されます。

```yaml
# パス設定
input_dir: "input"
output_dir: "output"

# Ollama設定
base_url: "http://localhost:11434/v1"
model: "minimax-m2.5:cloud"
vlm_model: "qwen3-vl:235b-cloud"   # null = modelと同じ

# 図解析設定
max_figures: 7
skip_figures: false
```

別の設定ファイルを使う場合：

```bash
python paper_blog_pipeline/main.py --config my_config.yaml
```

### 全オプション一覧

| オプション | config.yamlキー | デフォルト | 説明 |
|-----------|----------------|-----------|------|
| `pdf` | - | (省略可) | PDFファイルパス。省略時は`input/`フォルダ内を処理 |
| `--config`, `-c` | - | `config.yaml` | 設定ファイルパス |
| `--input`, `-i` | `input_dir` | `input/` | 入力PDFフォルダ |
| `--output`, `-o` | `output_dir` | `output/` | 出力ディレクトリ |
| `--model`, `-m` | `model` | `minimax-m2.5:cloud` | Ollamaモデル名 |
| `--vlm-model` | `vlm_model` | `qwen3-vl:235b-cloud` | 図解析用VLMモデル名 |
| `--base-url` | `base_url` | `http://localhost:11434/v1` | Ollama APIベースURL |
| `--max-figures` | `max_figures` | `7` | 解析する図の最大数 |
| `--skip-figures` | `skip_figures` | `false` | 図解析をスキップ |

**優先順位:** CLI引数 > config.yaml > ハードコードデフォルト

## フォルダ構成

```
project root/
    main_gui.py                 # GUI エントリーポイント

    app/
        controller.py           # MVC Controller（GUI ↔ Pipeline接続）

    gui/
        main_window.py          # メインウィンドウ（Menu + Toolbar + Pane + StatusBar）
        menu_bar.py             # メニューバー
        toolbar.py              # ツールバー（Open / Run / Stop / Save / Open Output + Progress）
        status_bar.py           # ステータスバー（状態 / モデル / タイマー）
        left_panel.py           # 左パネル（PDF選択 / 設定 / Output指定 / ログ）
        right_panel.py          # 右パネル（Notebook）
        tabs/
            tab_summary.py      # 落合式要約タブ
            tab_markdown.py     # ブログ記事タブ（Rendered / Raw切替）
            tab_figures.py      # Figure一覧 + プレビュータブ

    style/
        theme.py                # 統一テーマシステム（AppTheme）

    widgets/
        file_selector.py        # ファイル選択コンポーネント
        log_console.py          # ダークテーマログコンソール
        markdown_viewer.py      # Markdown整形ビューア（画像インライン表示）
        image_viewer.py         # Figure画像ビューア

    assets/
        favicon.ico             # アプリアイコン

    docs/                       # MkDocs ドキュメントソース
        index.md
        architecture.md
        api.md
        usage.md
    mkdocs.yml                  # MkDocs 設定
    site/                       # 生成済みHTMLサイト（mkdocs build）

    paper_blog_pipeline/
        main.py                 # CLI エントリーポイント
        config.yaml             # 設定ファイル

        input/                  # PDFを配置するフォルダ
        output/                 # 生成結果（article.md / paper_summary_slide.md / images/）

        parser/
            pdf_parser.py       # PDF構造解析（PyMuPDF）

        figures/
            figure_extractor.py # 図・テーブル抽出
            figure_analyzer.py  # VLMによる図解析

        llm/
            ollama_client.py    # Ollama共通クライアント
            paper_analyzer.py   # 落合式論文理解
            insight_generator.py# 研究インサイト生成
            blog_generator.py   # ブログ記事生成（図の自動挿入後処理付き）

        vlm/
            vlm_interface.py    # Ollama VLMインターフェース

        slide/
            ochiai_summary.py   # 落合式1枚スライド要約

        prompts/                # プロンプトテンプレート（参考用）

    pyinstaller/                # PyInstaller ビルド設定
        paper_blogger.spec      # 通常ビルド用 spec
        build.bat               # 通常ビルドスクリプト
        secure_gui.spec         # セキュアビルド用 spec
        secure_build.bat        # セキュアビルドスクリプト

    inno_setup/                 # Windows インストーラー
        paper_blogger_installer.iss  # Inno Setup スクリプト
        build_installer.bat     # インストーラービルドスクリプト

    build_tools/
        setup_cython.py         # Cython コンパイラ設定
```

## パイプライン処理フロー

```
PDF
 |
 v
[Step 1] PDF解析 ---- タイトル / 著者 / Abstract / セクション分割
 |
 v
[Step 2] 図抽出 ---- Figure / Table / Caption を画像として保存
 |                    重要図をスコアリングで自動選択
 |                    (引用回数/キャプション内容/図番号/サイズ)
 |
 v
[Step 3] 図解析 (VLM) ---- 図の意味・構造・論文との関係を説明
 |
 v
[Step 4] 論文理解 (LLM) ---- 落合式読み順で分析
 |                            1. Abstract
 |                            2. Conclusion
 |                            3. Experiments
 |                            4. Related Work
 |
 +---> [Step 5] Insight生成 ---- 研究の意味 / 産業応用 / 差分分析
 |
 +---> [Step 6] 落合式スライド ---- 1枚スライド要約（6項目）
 |
 v
[Step 7] ブログ記事生成 ---- 公開品質のMarkdown技術ブログ
```

## 重要図の自動選択

抽出された全図から、以下のスコアリング基準で重要度を判定し上位N枚を選択します：

| 基準 | スコア | 説明 |
|-----|--------|------|
| 本文中の引用回数 | 最大+15 | 本文で多く引用される図ほど重要（1回=+5, 上限3回） |
| キャプション内容 | +5/-5 | "overview", "architecture", "comparison" 等のキーワードで加点。"appendix" 等で減点 |
| キャプション有無 | +8 | キャプションが紐付いている図を優先 |
| 図の種別 | +3~+5 | figure (+5) > table (+3) > page (0) |
| 図の番号 | 最大+5 | Figure 1: +5, Figure 2: +4, Figure 3: +3（概要図は若い番号が多い） |
| 画像サイズ | +1~+3 | 大きい図は重要な傾向 |

実行時にスコア一覧が表示されるため、選択結果を確認できます。

## 落合陽一式 1枚スライド要約

生成されるスライド要約は以下の6項目で構成されます：

- **どんなもの？** - 研究の概要
- **先行研究と比べてどこがすごい？** - 新規性・優位性
- **技術や手法のキモはどこ？** - 核心的アイデア
- **どうやって有効だと検証した？** - 実験設定と結果
- **議論はある？** - 限界と未解決問題
- **次に読むべき論文は？** - 関連論文の推薦

## GUI アーキテクチャ

```
Controller ──→ Pipeline（既存CLIコード）
    ↑↓
MainWindow ──→ LeftPanel（PDF選択 / 設定 / ログ）
           ──→ RightPanel（Notebook: 要約 / ブログ / Figure）
           ──→ Toolbar / MenuBar / StatusBar
    ↑
  AppTheme（style/theme.py）← 全ウィジェット共通
```

- **MVC構造**: Controller がGUIとPipelineを分離
- **非同期実行**: `threading.Thread` でLLM処理をバックグラウンド実行
- **統一テーマ**: `style/theme.py` の `AppTheme` クラスを全アプリで共有可能
- **フォント**: Meiryo（日本語対応）
- **配色**: `#f5f6f8` 背景 + `#4f6bed` アクセント
- **画像インライン表示**: MarkdownViewer が `![alt](path)` を検出しPillowで描画
- **出力フォルダ管理**: GUI上で出力先を指定可能。「Open in Explorer」ボタンでOS標準のファイルエクスプローラーから直接アクセス（Windows/Mac/Linux対応）

## ドキュメント（MkDocs）

MkDocs + Material テーマでプロフェッショナルなドキュメントサイトを生成できます。

```bash
# 依存パッケージ
pip install mkdocs mkdocs-material "mkdocstrings[python]"

# 開発サーバー（ライブリロード）
mkdocs serve
# → http://127.0.0.1:8000

# 静的サイト生成
mkdocs build
# → site/index.html をブラウザで開く
```

| ページ | ファイル | 内容 |
|--------|---------|------|
| Home | `docs/index.md` | プロジェクト概要、Quick Start |
| Architecture | `docs/architecture.md` | パイプラインフロー、MVC構成、スレッド安全性 |
| API Reference | `docs/api.md` | Python docstring からの自動生成APIドキュメント |
| Usage Guide | `docs/usage.md` | CLI/GUI の使い方、設定、ビルド手順 |

## ビルド & 配布

### PyInstaller（onedirモード）

```bash
# 通常ビルド（開発・テスト用）
cd pyinstaller
build.bat

# セキュアビルド（配布用：Cython + PyInstaller）
cd pyinstaller
secure_build.bat
```

ビルド出力先: `%LOCALAPPDATA%\paper_blogger_build\dist\paper_blogger\`

### Windows インストーラー（Inno Setup）

PyInstallerビルド後、Inno Setup で商用ソフト風インストーラーを作成できます。

```bash
# 前提: Inno Setup 6 がインストール済み
cd inno_setup
build_installer.bat
```

出力: `inno_setup/output/setup_paper_blogger.exe`

インストーラーの機能:
- `C:\Program Files\Paper Blogger` にインストール
- スタートメニュー登録（アプリ + アンインストール）
- デスクトップショートカット（オプション）
- インストール完了後にアプリ起動
- 日本語 / English 対応
- LZMA2 + Solid 圧縮
- 商用ソフト風 Wizard UI (`WizardStyle=modern`)

ビルドフロー:
```
PyInstaller (build.bat) → dist/paper_blogger/ → Inno Setup (build_installer.bat) → setup_paper_blogger.exe
```

## 対応モデル例

Ollamaで利用可能なモデルであれば何でも使用できます。

| モデル | 用途 |
|-------|------|
| `minimax-m2.5:cloud` | テキスト分析・生成（デフォルト） |
| `qwen3.5:cloud` | テキスト分析・生成 |
| `glm-5:cloud` | テキスト分析・生成 |
| `qwen3-vl:235b-cloud` | 図解析VLM（デフォルト） |
