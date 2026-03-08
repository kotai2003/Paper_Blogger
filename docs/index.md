# Paper Blogger

**Research Paper to Technical Blog Pipeline**

Paper Blogger は、研究論文 (PDF) を技術ブログ記事に変換するパイプラインです。
落合陽一の論文読みフレームワークに基づき、論文の構造的理解からブログ品質の記事を自動生成します。

## Features

- **PDF 解析** — PyMuPDF による論文構造の自動抽出（タイトル、著者、セクション）
- **図表抽出・分析** — VLM (Vision Language Model) による図の自動解析
- **落合式要約** — 6 つの質問に基づく一枚スライド要約
- **ブログ記事生成** — LLM による出版品質の Markdown 記事生成
- **GUI / CLI** — Tkinter GUI とコマンドラインの両方に対応

## Quick Start

```bash
# Install dependencies
pip install -r paper_blog_pipeline/requirements.txt

# Run GUI
python main_gui.py

# Run CLI (batch mode)
python paper_blog_pipeline/main.py

# Run CLI (single PDF)
python paper_blog_pipeline/main.py paper.pdf
```

## Prerequisites

- **Ollama** running at `http://localhost:11434`
- LLM model pulled (e.g., `minimax-m2.5:cloud`)
- VLM model pulled (e.g., `qwen3-vl:235b-cloud`)

## Project Structure

```
paper_blogger/
├── main_gui.py                  # GUI entry point
├── app/
│   └── controller.py            # MVC Controller
├── gui/                         # GUI components
│   ├── main_window.py
│   ├── left_panel.py
│   ├── right_panel.py
│   └── tabs/
├── widgets/                     # Reusable UI widgets
├── style/                       # Theme system
├── paper_blog_pipeline/         # Core pipeline
│   ├── main.py                  # CLI entry point
│   ├── config.yaml              # Configuration
│   ├── parser/                  # PDF parsing
│   ├── figures/                 # Figure extraction & analysis
│   ├── llm/                     # LLM calls (Ollama)
│   ├── vlm/                     # VLM interface
│   └── slide/                   # Ochiai summary
├── pyinstaller/                 # PyInstaller build configs
└── inno_setup/                  # Windows installer (Inno Setup)
```

## Links

- [Architecture](architecture.md) — System design and pipeline details
- [API Reference](api.md) — Auto-generated module documentation
- [Usage Guide](usage.md) — Configuration and usage instructions
