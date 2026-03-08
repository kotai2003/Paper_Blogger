# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Research paper (PDF) to technical blog article generation pipeline implementing the **Ochiai Yoichi paper reading framework**. PDFs go into `input/`, and the system produces Markdown blog articles and one-slide summaries in `output/`. All LLM/VLM calls go through **Ollama** (OpenAI-compatible API).

The project has two interfaces:
- **CLI** — `paper_blog_pipeline/main.py` (batch processing)
- **GUI** — `main_gui.py` (Tkinter + ttk, commercial-grade UI)

## Commands

```bash
# Install dependencies
pip install -r paper_blog_pipeline/requirements.txt

# Run GUI
python main_gui.py

# Run the pipeline — batch mode (all PDFs in input/ folder)
python paper_blog_pipeline/main.py

# Run the pipeline — single PDF
python paper_blog_pipeline/main.py paper.pdf

# Override config with CLI args
python paper_blog_pipeline/main.py --model qwen3.5:cloud --vlm-model glm-5:cloud
python paper_blog_pipeline/main.py --skip-figures
python paper_blog_pipeline/main.py --config my_config.yaml
```

No test suite or linter is configured yet.

### Build & Distribution

```bash
# Normal build (development/testing)
cd pyinstaller
build.bat

# Secure build (distribution — Cython + PyInstaller)
cd pyinstaller
secure_build.bat

# Cython compile only
python build_tools/setup_cython.py build_ext --inplace

# Build Windows installer (requires Inno Setup 6)
cd inno_setup
build_installer.bat

# Build documentation site
mkdocs build

# Documentation dev server (live reload)
mkdocs serve
```

Requires: `pip install pyinstaller cython`
Secure build also requires MSVC (Visual Studio Build Tools).
Installer build requires [Inno Setup 6](https://jrsoftware.org/isdl.php).

## Prerequisites

- **Ollama** running at `http://localhost:11434` (configurable via `--base-url` or `config.yaml`)
- Models pulled in Ollama: `minimax-m2.5:cloud` (default LLM), `qwen3-vl:235b-cloud` (default VLM), etc.
- **Pillow** for GUI image rendering (`pip install Pillow`)
- No API keys required (Ollama is local)

## Configuration

Settings are managed in `paper_blog_pipeline/config.yaml` (YAML). CLI arguments override config values. GUI reads the same config on startup.

**Priority:** CLI args > config.yaml > hardcoded defaults

Key config fields:
- `model` — LLM model (default: `minimax-m2.5:cloud`)
- `vlm_model` — VLM model for figure analysis (default: `qwen3-vl:235b-cloud`, `null` = same as `model`)
- `base_url` — Ollama API endpoint
- `input_dir` / `output_dir` — I/O paths (relative to `paper_blog_pipeline/`)
- `max_figures` — max figures to analyze (default: `7`)
- `skip_figures` — skip VLM figure analysis

Use `--config path/to/other.yaml` to load a different config file.

## Architecture

### Pipeline (7 sequential steps)

Orchestrated by `paper_blog_pipeline/main.py:run_pipeline()`:

1. **PDF Parse** (`parser/pdf_parser.py`) — PyMuPDF extracts title, authors, abstract, sections. `ParsedPaper` has fuzzy section matching helpers (`get_conclusion()`, `get_experiments()`, `get_related_work()`, `get_method()`).

2. **Figure Extraction** (`figures/figure_extractor.py`) — Extracts embedded images via PyMuPDF, matches to captions. Falls back to page rendering. `select_key_figures(figures, max_count, full_text)` scores each figure by: body-text reference count, caption keyword analysis (overview/architecture/comparison etc.), caption presence, figure type, figure number (lower = higher score), and image size. Prints score breakdown at runtime.

3. **Figure Analysis** (`figures/figure_analyzer.py` + `vlm/vlm_interface.py`) — Sends key figures to VLM via Ollama for analysis (description, structure, significance).

4. **Paper Analysis** (`llm/paper_analyzer.py`) — Analyzes paper following **Ochiai reading order**: Abstract -> Conclusion -> Experiments -> Related Work. Outputs `PaperAnalysis`.

5. **Insight Generation** (`llm/insight_generator.py`) — Produces `ResearchInsight` (significance, industry applications, differentiation, future directions).

6. **Ochiai Summary Slide** (`slide/ochiai_summary.py`) — Generates the 6-question one-slide summary.

7. **Blog Generation** (`llm/blog_generator.py`) — Produces a publication-quality Markdown blog article with figure references. Post-processing via `_ensure_figures_in_article()` guarantees all analyzed figures are embedded in the article markdown even if the LLM omitted them.

### GUI (MVC, Tkinter + ttk)

```
main_gui.py                     # Entry point
app/controller.py               # MVC Controller — connects GUI to pipeline
gui/main_window.py              # Root frame: Menu + Toolbar + PanedWindow + StatusBar
gui/menu_bar.py                 # File / Run / Settings / Help menus
gui/toolbar.py                  # Open / Run / Stop / Save / Open Output buttons + progress bar
gui/status_bar.py               # Status message, model info, elapsed timer
gui/left_panel.py               # PDF selector, settings (model/VLM/figures), output dir selector, log console
gui/right_panel.py              # ttk.Notebook with 3 tabs
gui/tabs/tab_summary.py         # Ochiai summary display
gui/tabs/tab_markdown.py        # Blog article (rendered/raw toggle, save)
gui/tabs/tab_figures.py         # Figure list + image preview
```

**Reusable widgets** (`widgets/`):
- `log_console.py` — Dark-themed log with color-coded levels (info/warn/error/success/step)
- `markdown_viewer.py` — Renders markdown with headings, bold, code, lists, and **inline images** (Pillow). Requires `set_base_dir()` for resolving relative image paths like `images/figure_1.png`.
- `image_viewer.py` — Treeview file list + Pillow image preview
- `file_selector.py` — PDF file browser with info display

**Theme system** (`style/theme.py`):
- `AppTheme` class defines fonts, colors, padding, and configures all ttk styles
- Font: **Meiryo** (Windows) for proper Japanese rendering
- Colors: `#f5f6f8` background, `#4f6bed` accent
- All GUI apps can share this theme for unified UI

**Key GUI patterns**:
- Pipeline runs in `threading.Thread` (daemon) to keep UI responsive
- All GUI updates from worker thread go through `root.after(0, callback)`
- Keyboard shortcuts: `Ctrl+O` (Open), `F5` (Run), `Ctrl+S` (Save)
- Output folder is configurable in the left panel; "Open in Explorer" button opens it in OS file manager (`os.startfile` on Windows, `open` on Mac, `xdg-open` on Linux). Also available via toolbar and File menu.

## Input / Output

- **Input**: Place PDFs in `paper_blog_pipeline/input/`. Or pass a PDF path as argument. GUI uses file dialog.
- **Output**: Default is `paper_blog_pipeline/output/`. GUI allows changing via left panel Output section or folder browse dialog. When processing multiple PDFs (CLI), each gets a subfolder named after the PDF stem (e.g., `output/paper_name/`). GUI always creates a subfolder per PDF stem under the chosen output directory.
- Output per paper: `article.md` (with `![Figure](images/xxx.png)` references), `paper_summary_slide.md`, `images/`

## Build & Distribution

### PyInstaller (onedir mode)

Two build modes in `pyinstaller/`:

| Mode | Spec | Script | Purpose |
|------|------|--------|---------|
| Normal | `paper_blogger.spec` | `build.bat` | Dev/test, fast build |
| Secure | `secure_gui.spec` | `secure_build.bat` | Distribution, Cython anti-RE |

Build output goes to `%LOCALAPPDATA%\paper_blogger_build\dist\` to avoid OneDrive file locking.

### Cython Compilation (`build_tools/setup_cython.py`)

Compiles `.py` → `.pyd` (native DLL) for reverse engineering protection. Targets:
- `app/`, `gui/`, `gui/tabs/`, `widgets/`, `style/`
- `paper_blog_pipeline/` and all subpackages (`parser/`, `figures/`, `llm/`, `vlm/`, `slide/`)

Excluded from compilation: `main_gui.py` (entry point), `paper_blog_pipeline/main.py` (CLI entry), all `__init__.py`.

### Anti-Reverse-Engineering Layers

1. **Cython .pyd** — Source → C → native binary. Cannot be decompiled by `uncompyle6` etc.
2. **optimize=2** — Strips docstrings and assert statements from bytecode
3. **UPX compression** — Obfuscates binary structure
4. **console=False** — No debug console output

### Inno Setup Installer (`inno_setup/`)

Creates a Windows installer (`setup_paper_blogger.exe`) from the PyInstaller build output.

| File | Purpose |
|------|---------|
| `paper_blogger_installer.iss` | Inno Setup script |
| `build_installer.bat` | Build script (auto-locates ISCC.exe) |
| `README.md` | Installer documentation |

Installer features:
- Installs to `C:\Program Files\Paper Blogger`
- Start Menu shortcuts (app + uninstall)
- Desktop shortcut (optional)
- Launch app on finish
- Japanese + English language support
- LZMA2 + Solid compression
- `WizardStyle=modern` for commercial-grade UI

Build flow: PyInstaller (`pyinstaller/build.bat`) → Inno Setup (`inno_setup/build_installer.bat`) → `inno_setup/output/setup_paper_blogger.exe`

Source path: reads from `%LOCALAPPDATA%\paper_blogger_build\dist\paper_blogger\` (PyInstaller output).

### Key Build Notes

- `strip=False` in spec (Windows has no `strip` command — causes warnings if True)
- `pathex` includes both project root and `paper_blog_pipeline/` (for `sys.path.insert` dynamic imports in `controller.py`)
- All pipeline submodules listed in `hiddenimports` (PyInstaller cannot detect `sys.path.insert` + relative imports)
- `.pyd` files collected as `binaries`, `__init__.py` as `datas` in secure spec

## Documentation (MkDocs)

Project documentation uses MkDocs with Material theme and mkdocstrings for auto-generated API docs.

```bash
# Install docs dependencies
pip install mkdocs mkdocs-material "mkdocstrings[python]"

# Development server (live reload at http://127.0.0.1:8000)
mkdocs serve

# Build static site
mkdocs build
```

| File | Content |
|------|---------|
| `mkdocs.yml` | MkDocs configuration |
| `docs/index.md` | Home page |
| `docs/architecture.md` | System design, pipeline flow, MVC |
| `docs/api.md` | Auto-generated API reference (mkdocstrings) |
| `docs/usage.md` | CLI/GUI usage, configuration, build instructions |
| `site/` | Generated static HTML (gitignored) |

Docstring style: **NumPy** format. mkdocstrings scans both `.` and `paper_blog_pipeline/` paths.

## Key Design Decisions

- **All LLM/VLM calls go through Ollama** via `llm/ollama_client.py`, which uses the `openai` library with `base_url=http://localhost:11434/v1`. This single module (`call_llm()` / `call_vlm()`) is used by all other modules — no duplicated API code.
- **Config-driven**: `config.yaml` holds all defaults. `main.py` loads it with `_load_config()`, then CLI args override. GUI reads the same config on startup. Paths in config are resolved relative to `paper_blog_pipeline/`.
- **Figure insertion guarantee**: `blog_generator.py` post-processes LLM output to ensure all analyzed figures appear in the article. Figures are classified by section type (method/result/other) and inserted at the appropriate section end if the LLM didn't include them.
- Prompts are embedded in Python modules as constants and also stored as reference templates in `prompts/`.
- The project uses `sys.path.insert` in `main.py` and `main_gui.py` — all modules use package-relative imports from their respective roots.
- `main.py` supports both single-PDF and batch modes. With no positional argument, it discovers all `*.pdf` files in the `input/` folder.

## Language

This is a Japanese-language project. All prompts, generated content, and user-facing output are in Japanese. Code comments and variable names mix Japanese and English.
