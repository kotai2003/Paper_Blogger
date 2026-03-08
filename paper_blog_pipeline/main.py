"""
研究論文 → 技術ブログ記事生成パイプライン

落合陽一式論文読みフレームワークを実装した、
PDF論文から技術ブログ記事と1枚スライド要約を自動生成するシステム。
LLM/VLMはすべてOllama経由で利用。

使用方法:
    python main.py                          # input/ フォルダ内の全PDFを処理
    python main.py paper.pdf                # 単一PDF指定
    python main.py --model qwen3.5:cloud    # モデル指定
    python main.py --model minimax-m2.5:cloud --vlm-model glm-5:cloud
"""

import argparse
import sys
import time
from pathlib import Path

import yaml

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from parser.pdf_parser import parse_pdf
from figures.figure_extractor import extract_figures, select_key_figures
from figures.figure_analyzer import analyze_figures
from vlm.vlm_interface import get_vlm
from llm.paper_analyzer import analyze_paper
from llm.insight_generator import generate_insights
from llm.blog_generator import generate_blog_article
from slide.ochiai_summary import generate_ochiai_summary


def run_pipeline(
    pdf_path: str,
    output_dir: str = "output",
    model: str = "qwen3.5:cloud",
    vlm_model: str | None = None,
    base_url: str = "http://localhost:11434/v1",
    max_figures: int = 5,
    skip_figures: bool = False,
):
    """メインパイプライン実行"""
    output_path = Path(output_dir)
    images_path = output_path / "images"
    images_path.mkdir(parents=True, exist_ok=True)

    # VLMモデルが未指定の場合はLLMモデルと同じ
    vlm_model = vlm_model or model

    start_time = time.time()

    print(f"  Ollama: {base_url}")
    print(f"  LLMモデル: {model}")
    print(f"  VLMモデル: {vlm_model}")

    # ============================================================
    # Step 1: PDF解析
    # ============================================================
    print("\n" + "=" * 60)
    print("[Step 1/7] PDF解析中...")
    print("=" * 60)

    paper = parse_pdf(pdf_path)

    print(f"  タイトル: {paper.title}")
    print(f"  著者: {', '.join(paper.authors) if paper.authors else '不明'}")
    print(f"  セクション数: {len(paper.sections)}")
    print(f"  Abstract: {paper.abstract[:100]}..." if paper.abstract else "  Abstract: 未検出")
    for section in paper.sections:
        print(f"    - {section.title} ({len(section.content)} chars)")

    # ============================================================
    # Step 2: 図・テーブル抽出
    # ============================================================
    print("\n" + "=" * 60)
    print("[Step 2/7] 図・テーブル抽出中...")
    print("=" * 60)

    all_figures = extract_figures(pdf_path, images_path)
    key_figures = select_key_figures(all_figures, max_count=max_figures, full_text=paper.full_text)

    print(f"  抽出された図: {len(all_figures)} 枚")
    print(f"  選択された重要図: {len(key_figures)} 枚")
    for fig in key_figures:
        print(f"    - {fig.figure_id}: {fig.caption[:60]}..." if fig.caption else f"    - {fig.figure_id}")

    # ============================================================
    # Step 3: 図解析 (VLM)
    # ============================================================
    analyzed_figures = []
    if not skip_figures and key_figures:
        print("\n" + "=" * 60)
        print(f"[Step 3/7] 図解析中 (VLM: {vlm_model})...")
        print("=" * 60)

        vlm = get_vlm(model=vlm_model, base_url=base_url)
        analyzed_figures = analyze_figures(key_figures, vlm)

        for af in analyzed_figures:
            print(f"  {af.figure.figure_id}: {af.description[:80]}...")
    else:
        print("\n[Step 3/7] 図解析スキップ")

    # ============================================================
    # Step 4: 論文理解 (LLM) - 落合式読み順
    # ============================================================
    print("\n" + "=" * 60)
    print("[Step 4/7] 論文理解中 (落合式: Abstract→Conclusion→Experiments→Related Work)...")
    print(f"  モデル: {model}")
    print("=" * 60)

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

    print(f"  目的: {analysis.purpose[:100]}...")
    print(f"  新規性: {analysis.novelty[:100]}...")
    print(f"  手法: {analysis.method[:100]}...")

    # ============================================================
    # Step 5 & 6: Insight生成 → 落合式スライド生成
    # ============================================================
    print("\n" + "=" * 60)
    print("[Step 5/7] Insight生成中...")
    print("=" * 60)

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

    print(f"  研究の意味: {insights.significance[:100]}...")
    print(f"  産業応用: {insights.industry_applications[:100]}...")

    print("\n" + "=" * 60)
    print("[Step 6/7] 落合式1枚スライド要約生成中...")
    print("=" * 60)

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

    slide_path = output_path / "paper_summary_slide.md"
    slide_path.write_text(slide_content, encoding="utf-8")
    print(f"  保存: {slide_path}")

    # ============================================================
    # Step 7: ブログ記事生成
    # ============================================================
    print("\n" + "=" * 60)
    print("[Step 7/7] 技術ブログ記事生成中...")
    print("=" * 60)

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

    article_path = output_path / "article.md"
    article_path.write_text(blog_content, encoding="utf-8")
    print(f"  保存: {article_path}")

    # ============================================================
    # 完了
    # ============================================================
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("パイプライン完了!")
    print("=" * 60)
    print(f"  処理時間: {elapsed:.1f}秒")
    print(f"  出力ディレクトリ: {output_path}")
    print(f"  - ブログ記事: {article_path}")
    print(f"  - 落合式要約: {slide_path}")
    print(f"  - 図: {images_path} ({len(all_figures)} 枚)")

    return {
        "article_path": str(article_path),
        "slide_path": str(slide_path),
        "images_dir": str(images_path),
        "figures_count": len(all_figures),
        "elapsed_seconds": elapsed,
    }


def _load_config(config_path: str | Path) -> dict:
    """config.yamlを読み込む。ファイルが存在しなければ空dictを返す"""
    config_path = Path(config_path)
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _find_input_pdfs(input_dir: str | Path) -> list[Path]:
    """input/ディレクトリ内のPDFファイルを取得"""
    input_path = Path(input_dir)
    if not input_path.exists():
        input_path.mkdir(parents=True, exist_ok=True)
        print(f"inputフォルダを作成しました: {input_path}")
        return []
    pdfs = sorted(input_path.glob("*.pdf"))
    return pdfs


def main():
    pipeline_dir = Path(__file__).parent
    config_path = pipeline_dir / "config.yaml"

    # config.yaml読み込み
    cfg = _load_config(config_path)

    # config.yamlの値をデフォルトとして使用（パスはpipeline_dirからの相対パスを解決）
    def resolve_path(value: str, fallback: str) -> str:
        p = value or fallback
        path = Path(p)
        if not path.is_absolute():
            path = pipeline_dir / path
        return str(path)

    default_input = resolve_path(cfg.get("input_dir"), "input")
    default_output = resolve_path(cfg.get("output_dir"), "output")
    default_model = cfg.get("model", "qwen3.5:cloud")
    default_vlm_model = cfg.get("vlm_model")  # None = modelと同じ
    default_base_url = cfg.get("base_url", "http://localhost:11434/v1")
    default_max_figures = cfg.get("max_figures", 5)
    default_skip_figures = cfg.get("skip_figures", False)

    parser = argparse.ArgumentParser(
        description="研究論文 → 技術ブログ記事生成パイプライン（落合陽一式 / Ollama）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
設定ファイル:
  {config_path}
  CLI引数で指定した値が優先されます。

使用例:
  python main.py                              # input/ 内の全PDFを処理
  python main.py paper.pdf                    # 単一PDF指定
  python main.py --model minimax-m2.5:cloud   # モデル指定
  python main.py --skip-figures               # 図解析スキップ

利用可能なモデル例:
  qwen3.5:cloud        (デフォルト)
  minimax-m2.5:cloud
  glm-5:cloud
        """,
    )
    parser.add_argument("pdf", nargs="?", default=None,
                        help="入力PDFファイルのパス (省略時はinput/フォルダ内の全PDFを処理)")
    parser.add_argument("--config", "-c", default=str(config_path),
                        help=f"設定ファイルパス (default: {config_path})")
    parser.add_argument("--input", "-i", default=None,
                        help=f"入力PDFフォルダ (config: {default_input})")
    parser.add_argument("--output", "-o", default=None,
                        help=f"出力ディレクトリ (config: {default_output})")
    parser.add_argument("--model", "-m", default=None,
                        help=f"Ollamaモデル名 (config: {default_model})")
    parser.add_argument("--vlm-model", default=None,
                        help="図解析用VLMモデル名 (未指定時は--modelと同じ)")
    parser.add_argument("--base-url", default=None,
                        help=f"Ollama APIベースURL (config: {default_base_url})")
    parser.add_argument("--max-figures", type=int, default=None,
                        help=f"解析する図の最大数 (config: {default_max_figures})")
    parser.add_argument("--skip-figures", action="store_true", default=None,
                        help="図解析をスキップ")

    args = parser.parse_args()

    # --config が別ファイルを指定された場合は再読み込み
    if args.config != str(config_path):
        cfg = _load_config(args.config)
        default_input = resolve_path(cfg.get("input_dir"), "input")
        default_output = resolve_path(cfg.get("output_dir"), "output")
        default_model = cfg.get("model", "qwen3.5:cloud")
        default_vlm_model = cfg.get("vlm_model")
        default_base_url = cfg.get("base_url", "http://localhost:11434/v1")
        default_max_figures = cfg.get("max_figures", 5)
        default_skip_figures = cfg.get("skip_figures", False)

    # CLI引数 > config.yaml > ハードコードデフォルト
    input_dir = args.input or default_input
    output_dir = args.output or default_output
    model = args.model or default_model
    vlm_model = args.vlm_model or default_vlm_model
    base_url = args.base_url or default_base_url
    max_figures = args.max_figures if args.max_figures is not None else default_max_figures
    skip_figures = args.skip_figures if args.skip_figures is not None else default_skip_figures

    print(f"設定: {args.config}")

    # PDF一覧を決定
    if args.pdf:
        pdf_path = Path(args.pdf)
        if not pdf_path.exists():
            print(f"Error: PDF file not found: {args.pdf}")
            sys.exit(1)
        pdf_files = [pdf_path]
    else:
        pdf_files = _find_input_pdfs(input_dir)
        if not pdf_files:
            print(f"input/フォルダにPDFがありません: {input_dir}")
            print("  PDFファイルをinput/フォルダに配置するか、引数で直接指定してください。")
            print("  例: python main.py paper.pdf")
            sys.exit(1)
        print(f"input/フォルダから {len(pdf_files)} 件のPDFを検出:")
        for p in pdf_files:
            print(f"  - {p.name}")
        print()

    # 各PDFを処理
    results = []
    for pdf_path in pdf_files:
        if len(pdf_files) > 1:
            out_dir = str(Path(output_dir) / pdf_path.stem)
        else:
            out_dir = output_dir

        print(f"\n{'#' * 60}")
        print(f"# 処理中: {pdf_path.name}")
        print(f"{'#' * 60}")

        try:
            result = run_pipeline(
                pdf_path=str(pdf_path),
                output_dir=out_dir,
                model=model,
                vlm_model=vlm_model,
                base_url=base_url,
                max_figures=max_figures,
                skip_figures=skip_figures,
            )
            results.append((pdf_path.name, result))
        except Exception as e:
            print(f"\nError processing {pdf_path.name}: {e}")
            results.append((pdf_path.name, None))

    # 複数PDF処理の場合、サマリー表示
    if len(pdf_files) > 1:
        print(f"\n{'=' * 60}")
        print(f"全 {len(pdf_files)} 件の処理結果:")
        print(f"{'=' * 60}")
        for name, result in results:
            if result:
                print(f"  OK: {name} → {result['article_path']}")
            else:
                print(f"  NG: {name}")


if __name__ == "__main__":
    main()
