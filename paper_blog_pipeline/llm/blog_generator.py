"""ブログ記事生成モジュール - 技術ブログ品質のMarkdown記事を生成

論文の分析結果とインサイトを統合し、出版品質のMarkdownブログ記事を生成する。
LLMが生成した記事に対して後処理を行い、すべての解析済み図が
記事中に確実に埋め込まれることを保証する。
"""

import re

from llm.ollama_client import call_llm
from figures.figure_analyzer import AnalyzedFigure


BLOG_PROMPT = """あなたはトップレベルの技術ブログライターです。

以下の論文の原文と分析結果を基に、**技術ブログとして公開できる品質**のMarkdown記事を生成してください。

=== 論文情報 ===
- タイトル: {title}
- 著者: {authors}

=== 論文原文（セクション別） ===

### Abstract
{abstract}

### Method（原文）
{raw_method}

### Experiments / Results（原文）
{raw_experiments}

=== AI分析結果 ===

### 研究の目的
{purpose}

### 新規性
{novelty}

### 手法（分析）
{method}

### 実験結果（分析）
{results}

### 限界
{limitations}

### 研究の意味
{significance}

### 産業応用
{industry_applications}

### 既存研究との差
{differentiation}

### 今後の研究方向
{future_directions}

=== 図の解析結果 ===
{figure_descriptions}

=== 図とセクションの対応 ===
{figure_context}

---

以下の構成でMarkdownブログ記事を生成してください。

**執筆ガイドライン:**
- 論文原文から具体的な数値・手法名・データセット名を正確に引用すること
- 専門家でなくても理解できるよう、難しい概念は平易に説明する
- ただし技術的正確性は犠牲にしない
- 各セクションは十分な分量（200-500字）で記述する
- 読者の興味を引く導入文を書く
- 図は関連するセクション内に自然に組み込むこと（手法の図は手法セクションに、実験の図は実験セクションに）
- 「図Xに示すように〜」のような自然な参照を使う

**出力フォーマット:**

# [論文タイトルを日本語で意訳した魅力的なタイトル]

> 原題: {title}
> 著者: {authors}

## TL;DR（3行まとめ）
[箇条書き3行で論文の核心を要約]

## はじめに
[この研究が解決する問題の背景と重要性。読者を引き込む導入]

## 背景と関連研究
[この分野の現状と課題。先行研究の限界]

## 核心アイデア
[提案手法の直感的な説明。「なぜこのアプローチなのか」を説明]

## 手法の詳細
[技術的な詳細。数式があれば平易に解説。アーキテクチャの説明]
[手法の概要図があればここに含める]

## 実験と結果
[実験設定、データセット、主要結果の解説。結果の図やテーブルがあればここに含める]
[具体的な数値を原文から引用すること]

## この研究が意味すること
[学術的・産業的インパクト。応用可能性]

## 限界と今後の展望
[現在の限界と、今後どう発展しうるか]

## まとめ
[記事全体の要約と、読者へのメッセージ]

---
*この記事は研究論文を基に自動生成されました。*

日本語で回答してください。
"""


def _classify_figure_section(figure: "AnalyzedFigure") -> str:
    """図がどのセクションに関連するか推定"""
    caption = (figure.figure.caption or "").lower()
    desc = (figure.description or "").lower()
    sig = (figure.significance or "").lower()
    combined = caption + " " + desc + " " + sig

    method_keywords = ["architecture", "overview", "framework", "pipeline", "model",
                       "module", "structure", "network", "diagram", "flow",
                       "アーキテクチャ", "概要", "構造", "手法", "提案"]
    result_keywords = ["result", "comparison", "performance", "accuracy", "score",
                       "ablation", "benchmark", "evaluation", "table", "bar", "plot",
                       "結果", "比較", "精度", "性能", "グラフ"]

    method_score = sum(1 for kw in method_keywords if kw in combined)
    result_score = sum(1 for kw in result_keywords if kw in combined)

    if method_score > result_score:
        return "手法"
    elif result_score > 0:
        return "実験結果"
    else:
        return "その他"


def generate_blog_article(
    title: str,
    authors: list[str],
    abstract: str,
    purpose: str,
    novelty: str,
    method: str,
    results: str,
    limitations: str,
    significance: str,
    industry_applications: str,
    differentiation: str,
    future_directions: str,
    analyzed_figures: list[AnalyzedFigure],
    raw_method: str = "",
    raw_experiments: str = "",
    model: str | None = None,
    base_url: str | None = None,
) -> str:
    """技術ブログ記事を生成"""

    authors_str = ", ".join(authors) if authors else "不明"

    # 原文セクションの切り詰め（ブログ用）
    max_raw = 5000
    raw_method_text = raw_method[:max_raw] if raw_method else "（原文未抽出）"
    raw_experiments_text = raw_experiments[:max_raw] if raw_experiments else "（原文未抽出）"

    # 図の解析結果と、セクション対応情報を生成
    figure_desc_parts = []
    figure_context_parts = []
    for af in analyzed_figures:
        fig = af.figure
        img_filename = fig.image_path.replace("\\", "/").split("/")[-1]
        section_type = _classify_figure_section(af)

        figure_desc_parts.append(
            f"### {fig.figure_id}\n"
            f"- キャプション: {fig.caption}\n"
            f"- 説明: {af.description}\n"
            f"- 構造: {af.structure}\n"
            f"- 意義: {af.significance}\n"
            f"- Markdown: ![{fig.figure_id}](images/{img_filename})\n"
        )

        figure_context_parts.append(
            f"- {fig.figure_id} → 関連セクション: **{section_type}** "
            f"| ![{fig.figure_id}](images/{img_filename}) "
            f"| {af.description[:80]}"
        )

    figure_descriptions = "\n".join(figure_desc_parts) if figure_desc_parts else "（図の解析結果なし）"
    figure_context = "\n".join(figure_context_parts) if figure_context_parts else "（図なし）"

    prompt = BLOG_PROMPT.format(
        title=title,
        authors=authors_str,
        abstract=abstract or "（未検出）",
        raw_method=raw_method_text,
        raw_experiments=raw_experiments_text,
        purpose=purpose,
        novelty=novelty,
        method=method,
        results=results,
        limitations=limitations,
        significance=significance,
        industry_applications=industry_applications,
        differentiation=differentiation,
        future_directions=future_directions,
        figure_descriptions=figure_descriptions,
        figure_context=figure_context,
    )

    article = call_llm(prompt, model=model, base_url=base_url, max_tokens=8192)

    # 後処理: LLMが図を含めなかった場合に確実に挿入する
    if analyzed_figures:
        article = _ensure_figures_in_article(article, analyzed_figures)

    return article


# ====================================================================
# セクション見出しパターン（図の挿入先を特定するため）
# ====================================================================
_SECTION_PATTERNS = {
    "method": re.compile(
        r"^##\s*.*(手法|核心|アーキテクチャ|アプローチ|提案|method|approach|architecture)",
        re.IGNORECASE | re.MULTILINE,
    ),
    "result": re.compile(
        r"^##\s*.*(実験|結果|評価|比較|result|experiment|evaluation)",
        re.IGNORECASE | re.MULTILINE,
    ),
    "discussion": re.compile(
        r"^##\s*.*(意味|考察|インパクト|応用|discussion|impact|implication)",
        re.IGNORECASE | re.MULTILINE,
    ),
    "conclusion": re.compile(
        r"^##\s*.*(まとめ|結論|展望|conclusion|summary)",
        re.IGNORECASE | re.MULTILINE,
    ),
}


def _find_section_end(article: str, section_match: re.Match) -> int:
    """セクションの終端（次の ## 見出し or 記事末尾）を返す"""
    start = section_match.end()
    next_heading = re.search(r"^##\s", article[start:], re.MULTILINE)
    if next_heading:
        return start + next_heading.start()
    return len(article)


def _figure_already_referenced(article: str, img_filename: str) -> bool:
    """記事中にこの図への参照が既にあるか"""
    return img_filename in article


def _ensure_figures_in_article(
    article: str, analyzed_figures: list[AnalyzedFigure]
) -> str:
    """LLMが含めなかった図を適切なセクションに挿入する"""
    figures_to_insert = {
        "method": [],
        "result": [],
        "other": [],
    }

    for af in analyzed_figures:
        fig = af.figure
        img_filename = fig.image_path.replace("\\", "/").split("/")[-1]

        if _figure_already_referenced(article, img_filename):
            continue

        section_type = _classify_figure_section(af)
        caption = fig.caption or fig.figure_id
        md_img = f"\n\n![{caption}](images/{img_filename})\n"

        if section_type == "手法":
            figures_to_insert["method"].append(md_img)
        elif section_type == "実験結果":
            figures_to_insert["result"].append(md_img)
        else:
            figures_to_insert["other"].append(md_img)

    # 全ての図が既に記事内にある場合はそのまま返す
    all_figs = figures_to_insert["method"] + figures_to_insert["result"] + figures_to_insert["other"]
    if not all_figs:
        return article

    # 手法の図 → 手法セクション末尾に挿入
    if figures_to_insert["method"]:
        match = _SECTION_PATTERNS["method"].search(article)
        if match:
            pos = _find_section_end(article, match)
            insert_block = "".join(figures_to_insert["method"])
            article = article[:pos] + insert_block + "\n" + article[pos:]

    # 実験結果の図 → 実験セクション末尾に挿入
    if figures_to_insert["result"]:
        match = _SECTION_PATTERNS["result"].search(article)
        if match:
            pos = _find_section_end(article, match)
            insert_block = "".join(figures_to_insert["result"])
            article = article[:pos] + insert_block + "\n" + article[pos:]

    # その他の図 → 考察セクション末尾、なければまとめの前に挿入
    if figures_to_insert["other"]:
        match = _SECTION_PATTERNS["discussion"].search(article)
        if not match:
            match = _SECTION_PATTERNS["conclusion"].search(article)
        if match:
            pos = _find_section_end(article, match)
            insert_block = "".join(figures_to_insert["other"])
            article = article[:pos] + insert_block + "\n" + article[pos:]
        else:
            # 最後に追加
            article += "\n" + "".join(figures_to_insert["other"])

    return article
