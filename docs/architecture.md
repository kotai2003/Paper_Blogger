# Architecture

## Overview

Paper Blogger は **7 ステップの逐次パイプライン** で論文を処理します。
GUI は MVC パターンで実装され、パイプラインをワーカースレッドで非同期実行します。

## Pipeline Flow

```
PDF Input
  │
  ▼
┌─────────────────────────────────────────────┐
│ Step 1: PDF Parse (parser/pdf_parser.py)     │
│   PyMuPDF → ParsedPaper                      │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│ Step 2: Figure Extraction                    │
│   (figures/figure_extractor.py)              │
│   Embedded images + caption matching         │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│ Step 3: Figure Analysis (VLM)                │
│   (figures/figure_analyzer.py)               │
│   VLM describes each key figure              │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│ Step 4: Paper Analysis (LLM)                 │
│   (llm/paper_analyzer.py)                    │
│   Ochiai reading order analysis              │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│ Step 5: Insight Generation (LLM)             │
│   (llm/insight_generator.py)                 │
│   Significance, applications, future work    │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│ Step 6: Ochiai Summary Slide                 │
│   (slide/ochiai_summary.py)                  │
│   6-question one-slide summary               │
└──────────────────┬──────────────────────────┘
                   ▼
┌─────────────────────────────────────────────┐
│ Step 7: Blog Generation (LLM)                │
│   (llm/blog_generator.py)                    │
│   Publication-quality Markdown article       │
└──────────────────┬──────────────────────────┘
                   ▼
              Output Files
         article.md + images/
       paper_summary_slide.md
```

## GUI Architecture (MVC)

```
┌──────────────┐     ┌────────────────────┐     ┌──────────────┐
│   View       │◄────│   Controller       │────►│   Pipeline   │
│  (gui/)      │     │  (app/controller)  │     │  (paper_blog │
│              │     │                    │     │   _pipeline/) │
│  MainWindow  │     │ PipelineController │     │              │
│  LeftPanel   │     │  - run_pipeline()  │     │  parse_pdf() │
│  RightPanel  │     │  - stop_pipeline() │     │  extract()   │
│  Tabs        │     │  - open_pdf()      │     │  analyze()   │
│  StatusBar   │     │  - save_article()  │     │  generate()  │
└──────────────┘     └────────────────────┘     └──────────────┘
                           │
                     threading.Thread
                     (daemon=True)
```

### Thread Safety

- Pipeline runs in a daemon `threading.Thread`
- All GUI updates go through `root.after(0, callback)` to avoid Tkinter thread issues
- Stop is cooperative via `_stop_requested` flag checked between steps

## LLM/VLM Communication

All LLM and VLM calls go through a single module:

```
llm/ollama_client.py
  └── call_llm(prompt, model, base_url)  → str
  └── call_vlm(prompt, image, model, base_url) → str
         │
         ▼
    OpenAI-compatible API
    http://localhost:11434/v1
         │
         ▼
      Ollama Server
```

## Configuration Priority

```
CLI arguments  >  config.yaml  >  Hardcoded defaults
```

## Build & Distribution

```
Source Code
  │
  ├── pyinstaller/build.bat          → dist/paper_blogger/  (dev build)
  ├── pyinstaller/secure_build.bat   → dist/paper_blogger/  (Cython + PyInstaller)
  │
  └── inno_setup/build_installer.bat → setup_paper_blogger.exe  (Windows installer)
```
