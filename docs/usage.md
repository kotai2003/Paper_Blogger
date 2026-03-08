# Usage Guide

## Prerequisites

### Ollama

Paper Blogger requires [Ollama](https://ollama.com/) running locally.

```bash
# Install Ollama (see https://ollama.com/download)
# Start the server
ollama serve

# Pull required models
ollama pull minimax-m2.5:cloud    # Default LLM
ollama pull qwen3-vl:235b-cloud  # Default VLM (figure analysis)
```

### Python Dependencies

```bash
pip install -r paper_blog_pipeline/requirements.txt
pip install Pillow  # Required for GUI image rendering
```

## GUI Mode

```bash
python main_gui.py
```

### Workflow

1. **Open PDF** — Click "Open" or press `Ctrl+O` to select a PDF file
2. **Configure** — Set model, VLM model, max figures in the left panel
3. **Run** — Click "Run" or press `F5` to start the pipeline
4. **View Results** — Results appear in three tabs:
    - **Summary** — Ochiai one-slide summary
    - **Article** — Generated blog article (rendered / raw toggle)
    - **Figures** — Extracted figures with image preview
5. **Save** — Click "Save" or press `Ctrl+S` to export the article

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open PDF file |
| `F5` | Run pipeline |
| `Ctrl+S` | Save article |

## CLI Mode

### Batch Mode (All PDFs in input/)

```bash
python paper_blog_pipeline/main.py
```

### Single PDF

```bash
python paper_blog_pipeline/main.py path/to/paper.pdf
```

### CLI Options

```bash
# Override LLM model
python paper_blog_pipeline/main.py --model qwen3.5:cloud

# Override VLM model
python paper_blog_pipeline/main.py --vlm-model glm-5:cloud

# Skip figure analysis
python paper_blog_pipeline/main.py --skip-figures

# Use custom config file
python paper_blog_pipeline/main.py --config my_config.yaml

# Change Ollama endpoint
python paper_blog_pipeline/main.py --base-url http://remote-server:11434
```

## Configuration

Settings are in `paper_blog_pipeline/config.yaml`:

```yaml
# LLM model for text analysis and generation
model: minimax-m2.5:cloud

# VLM model for figure analysis (null = use same as model)
vlm_model: qwen3-vl:235b-cloud

# Ollama API endpoint
base_url: http://localhost:11434

# I/O paths (relative to paper_blog_pipeline/)
input_dir: input
output_dir: output

# Figure analysis settings
max_figures: 7
skip_figures: false
```

**Priority:** CLI arguments > config.yaml > hardcoded defaults

## Output Structure

Each processed paper creates a subfolder:

```
output/
└── paper_name/
    ├── article.md              # Blog article with figure references
    ├── paper_summary_slide.md  # Ochiai one-slide summary
    └── images/
        ├── figure_1.png
        ├── figure_2.png
        └── ...
```

## Building for Distribution

### PyInstaller Build

```bash
# Development build
cd pyinstaller
build.bat

# Secure build (Cython + PyInstaller)
cd pyinstaller
secure_build.bat
```

### Windows Installer (Inno Setup)

```bash
# Requires: Inno Setup 6 installed
cd inno_setup
build_installer.bat
```

Output: `inno_setup/output/setup_paper_blogger.exe`

## Documentation

### Build Documentation

```bash
pip install mkdocs mkdocs-material mkdocstrings[python]

# Development server (live reload)
mkdocs serve

# Build static site
mkdocs build
```

Generated site: `site/index.html`
