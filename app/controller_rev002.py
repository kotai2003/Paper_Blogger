"""Controller Rev002 - 中国語フィルター付きパイプラインコントローラー

Rev001 (controller.py) との差分:
  - パイプラインが 7→8 ステップに拡張
  - Step 8: gpt-oss:20b-cloud による中国語フィルター（記事・要約の検収）
"""

import os
import sys
import subprocess
import platform
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

import yaml


class PipelineController:
    """パイプライン実行を管理するMVCコントローラー（Rev002: 8ステップ）

    Parameters
    ----------
    root : tk.Tk
        Tkinter ルートウィンドウ。GUI更新のスレッド同期に使用。
    """

    TOTAL_STEPS = 8  # Rev002: 7→8

    def __init__(self, root: tk.Tk):
        self.root = root
        self.main_window = None
        self._worker_thread = None
        self._stop_requested = False
        self._pipeline_dir = Path(__file__).parent.parent / "paper_blog_pipeline"

    def set_main_window(self, main_window):
        self.main_window = main_window

    # ================================================================
    # ファイル操作
    # ================================================================

    def open_pdf(self):
        path = filedialog.askopenfilename(
            title="Open PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if path:
            self.main_window.left_panel.file_selector.set_path(path)

    def save_article(self):
        text = self.main_window.right_panel.tab_markdown.rendered_viewer.get_text()
        if not text:
            messagebox.showinfo("Save", "No article content to save.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Blog Article",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")],
        )
        if path:
            raw = self.main_window.right_panel.tab_markdown._raw_content
            Path(path).write_text(raw or text, encoding="utf-8")
            self._log("Article saved: " + path, "success")

    def save_summary(self):
        text = self.main_window.right_panel.tab_summary.viewer.get_text()
        if not text:
            messagebox.showinfo("Save", "No summary content to save.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Summary",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("All files", "*.*")],
        )
        if path:
            Path(path).write_text(text, encoding="utf-8")
            self._log("Summary saved: " + path, "success")

    # ================================================================
    # Output Folder
    # ================================================================

    def browse_output_dir(self):
        current = self.main_window.left_panel.output_dir_var.get()
        initial = current if current and Path(current).exists() else str(self._pipeline_dir / "output")
        path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=initial,
        )
        if path:
            self.main_window.left_panel.set_output_dir(path)

    def open_output_folder(self):
        output_dir = self.main_window.left_panel.output_dir_var.get()
        if not output_dir:
            output_dir = str(self._pipeline_dir / "output")
        path = Path(output_dir)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        self._open_in_explorer(path)

    def _open_in_explorer(self, path: Path):
        path_str = str(path)
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(path_str)
            elif system == "Darwin":
                subprocess.Popen(["open", path_str])
            else:
                subprocess.Popen(["xdg-open", path_str])
        except Exception as e:
            self._log(f"Failed to open explorer: {e}", "error")

    # ================================================================
    # パイプライン実行
    # ================================================================

    def run_pipeline(self):
        if self._worker_thread and self._worker_thread.is_alive():
            messagebox.showwarning("Running", "Pipeline is already running.")
            return

        settings = self.main_window.left_panel.get_settings()
        pdf_path = settings["pdf_path"]

        if not pdf_path or not Path(pdf_path).exists():
            messagebox.showerror("Error", "Please select a valid PDF file.")
            return

        self._stop_requested = False
        self.main_window.set_running(True)
        self.main_window.right_panel.clear_all()
        self.main_window.status_bar.start_timer()
        self.main_window.status_bar.set_model(settings["model"])

        self._worker_thread = threading.Thread(
            target=self._run_pipeline_worker,
            args=(pdf_path, settings),
            daemon=True,
        )
        self._worker_thread.start()

    def stop_pipeline(self):
        self._stop_requested = True
        self._log("Stop requested...", "warn")

    def _run_pipeline_worker(self, pdf_path: str, settings: dict):
        """ワーカースレッドでパイプラインを実行（8ステップ）"""
        N = self.TOTAL_STEPS  # 8

        try:
            pipeline_dir = str(self._pipeline_dir)
            if pipeline_dir not in sys.path:
                sys.path.insert(0, pipeline_dir)

            from parser.pdf_parser import parse_pdf
            from figures.figure_extractor import extract_figures, select_key_figures
            from figures.figure_analyzer import analyze_figures
            from vlm.vlm_interface import get_vlm
            from llm.paper_analyzer import analyze_paper
            from llm.insight_generator import generate_insights
            from llm.blog_generator import generate_blog_article
            from slide.ochiai_summary import generate_ochiai_summary
            from llm.chinese_filter import filter_chinese

            model = settings["model"]
            vlm_model = settings["vlm_model"] or model
            base_url = settings["base_url"]
            max_figures = settings["max_figures"]
            skip_figures = settings["skip_figures"]

            # 出力ディレクトリ
            pdf_stem = Path(pdf_path).stem
            custom_output = settings.get("output_dir", "").strip()
            if custom_output:
                output_dir = Path(custom_output) / pdf_stem
            else:
                output_dir = self._pipeline_dir / "output" / pdf_stem
            images_dir = output_dir / "images"
            images_dir.mkdir(parents=True, exist_ok=True)

            self.root.after(0, lambda d=str(output_dir): self.main_window.left_panel.set_output_dir(d))

            # Step 1: PDF解析
            self._update_progress(1, N, "Step 1/8: PDF Parsing...")
            self._log("Step 1/8: PDF parsing...", "step")

            paper = parse_pdf(pdf_path)

            self._log(f"  Title: {paper.title}", "info")
            self._log(f"  Authors: {', '.join(paper.authors) if paper.authors else 'Unknown'}", "info")
            self._log(f"  Sections: {len(paper.sections)}", "info")

            if self._stop_requested:
                self._on_complete(cancelled=True)
                return

            # Step 2: 図抽出
            self._update_progress(2, N, "Step 2/8: Figure Extraction...")
            self._log("Step 2/8: Extracting figures...", "step")

            all_figures = extract_figures(pdf_path, images_dir)
            key_figures = select_key_figures(all_figures, max_count=max_figures, full_text=paper.full_text)

            self._log(f"  Extracted: {len(all_figures)} figures", "info")
            self._log(f"  Selected: {len(key_figures)} key figures", "info")

            if self._stop_requested:
                self._on_complete(cancelled=True)
                return

            # Step 3: 図解析 (VLM)
            analyzed_figures = []
            if not skip_figures and key_figures:
                self._update_progress(3, N, "Step 3/8: Figure Analysis (VLM)...")
                self._log(f"Step 3/8: Analyzing figures (VLM: {vlm_model})...", "step")

                vlm = get_vlm(model=vlm_model, base_url=base_url)
                analyzed_figures = analyze_figures(key_figures, vlm)

                for af in analyzed_figures:
                    self._log(f"  {af.figure.figure_id}: analyzed", "info")
            else:
                self._update_progress(3, N, "Step 3/8: Skipped")
                self._log("Step 3/8: Figure analysis skipped", "step")

            if self._stop_requested:
                self._on_complete(cancelled=True)
                return

            # Step 4: 論文理解
            self._update_progress(4, N, "Step 4/8: Paper Analysis (LLM)...")
            self._log("Step 4/8: Analyzing paper (Ochiai method)...", "step")

            analysis = analyze_paper(
                title=paper.title,
                authors=paper.authors,
                abstract=paper.abstract,
                conclusion=paper.get_conclusion(),
                experiments=paper.get_experiments(),
                related_work=paper.get_related_work(),
                method=paper.get_method(),
                full_text=paper.full_text,
                model=model,
                base_url=base_url,
            )

            self._log(f"  Purpose: {analysis.purpose[:80]}...", "info")
            self._log(f"  Novelty: {analysis.novelty[:80]}...", "info")

            if self._stop_requested:
                self._on_complete(cancelled=True)
                return

            # Step 5: Insight生成
            self._update_progress(5, N, "Step 5/8: Insight Generation...")
            self._log("Step 5/8: Generating insights...", "step")

            insights = generate_insights(
                title=paper.title,
                purpose=analysis.purpose,
                novelty=analysis.novelty,
                method=analysis.method,
                results=analysis.results,
                limitations=analysis.limitations,
                model=model,
                base_url=base_url,
            )

            if self._stop_requested:
                self._on_complete(cancelled=True)
                return

            # Step 6: 落合式スライド
            self._update_progress(6, N, "Step 6/8: Ochiai Summary...")
            self._log("Step 6/8: Generating Ochiai summary...", "step")

            slide_content = generate_ochiai_summary(
                title=paper.title,
                authors=paper.authors,
                abstract=paper.abstract,
                purpose=analysis.purpose,
                novelty=analysis.novelty,
                method=analysis.method,
                results=analysis.results,
                limitations=analysis.limitations,
                differentiation=insights.differentiation,
                references=paper.references,
                model=model,
                base_url=base_url,
            )

            if self._stop_requested:
                self._on_complete(cancelled=True)
                return

            # Step 7: ブログ記事生成
            self._update_progress(7, N, "Step 7/8: Blog Article...")
            self._log("Step 7/8: Generating blog article...", "step")

            blog_content = generate_blog_article(
                title=paper.title,
                authors=paper.authors,
                abstract=paper.abstract,
                purpose=analysis.purpose,
                novelty=analysis.novelty,
                method=analysis.method,
                results=analysis.results,
                limitations=analysis.limitations,
                significance=insights.significance,
                industry_applications=insights.industry_applications,
                differentiation=insights.differentiation,
                future_directions=insights.future_directions,
                analyzed_figures=analyzed_figures,
                raw_method=paper.get_method(),
                raw_experiments=paper.get_experiments(),
                model=model,
                base_url=base_url,
            )

            if self._stop_requested:
                self._on_complete(cancelled=True)
                return

            # ============================================================
            # Step 8: 中国語フィルター（gpt-oss:20b-cloud による検収）
            # ============================================================
            self._update_progress(8, N, "Step 8/8: Chinese Filter (gpt-oss)...")
            self._log("Step 8/8: Filtering Chinese text (gpt-oss:20b-cloud)...", "step")

            blog_content = filter_chinese(blog_content, base_url=base_url)
            self._log("  Blog article filtered", "info")

            slide_content = filter_chinese(slide_content, base_url=base_url)
            self._log("  Ochiai summary filtered", "info")

            # フィルター後のファイルを保存
            article_path = output_dir / "article.md"
            article_path.write_text(blog_content, encoding="utf-8")

            slide_path = output_dir / "paper_summary_slide.md"
            slide_path.write_text(slide_content, encoding="utf-8")

            # 結果をGUIに反映
            self.root.after(0, lambda: self._display_results(
                slide_content, blog_content, str(images_dir), str(output_dir),
            ))

            self._log("Pipeline completed!", "success")
            self._log(f"  Output: {output_dir}", "info")
            self._on_complete(cancelled=False)

        except Exception as e:
            self._log(f"Error: {e}", "error")
            import traceback
            self._log(traceback.format_exc(), "error")
            self._on_complete(cancelled=False, error=True)

    def _display_results(self, summary: str, article: str, images_dir: str, output_dir: str = ""):
        base_dir = output_dir or str(Path(images_dir).parent)
        self.main_window.right_panel.tab_summary.load(summary, base_dir)
        self.main_window.right_panel.tab_markdown.load(article, base_dir)
        self.main_window.right_panel.tab_figures.load_images(images_dir)
        self.main_window.right_panel.notebook.select(0)

    def _update_progress(self, step: int, total: int, label: str):
        self.root.after(0, lambda: self.main_window.toolbar.set_progress(step, total, label))

    def _on_complete(self, cancelled: bool = False, error: bool = False):
        N = self.TOTAL_STEPS
        def _finish():
            self.main_window.set_running(False)
            self.main_window.status_bar.stop_timer()
            if cancelled:
                self.main_window.status_bar.set_status("Cancelled")
                self.main_window.toolbar.set_progress(0, N, "Cancelled")
            elif error:
                self.main_window.status_bar.set_status("Error")
                self.main_window.toolbar.set_progress(0, N, "Error")
            else:
                self.main_window.status_bar.set_status("Complete")
                self.main_window.toolbar.set_progress(N, N, "Complete")
        self.root.after(0, _finish)

    def _log(self, msg: str, level: str = "info"):
        self.root.after(0, lambda: self.main_window.left_panel.log_console.log(msg, level))

    # ================================================================
    # その他
    # ================================================================

    def clear_log(self):
        self.main_window.left_panel.log_console.clear()

    def open_settings(self):
        config_path = self._pipeline_dir / "config.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            self.main_window.left_panel.load_config(config)
            self._log(f"Loaded config: {config_path}", "info")
        else:
            messagebox.showinfo("Settings", f"Config not found: {config_path}")

    def show_about(self):
        messagebox.showinfo(
            "About Paper Blogger",
            "Paper Blogger GUI (Rev002)\n\n"
            "Research Paper to Technical Blog Pipeline\n"
            "Ochiai Yoichi Framework\n\n"
            "Rev002: Chinese text filter (gpt-oss:20b-cloud)\n"
            "Powered by Ollama (Local LLM/VLM)",
        )

    def quit_app(self):
        if self._worker_thread and self._worker_thread.is_alive():
            if not messagebox.askyesno("Quit", "Pipeline is running. Quit anyway?"):
                return
        self.root.quit()
