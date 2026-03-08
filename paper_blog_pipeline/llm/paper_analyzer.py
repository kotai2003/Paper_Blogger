"""論文理解モジュール - 落合陽一式フレームワークでLLMによる論文分析"""

from dataclasses import dataclass

from llm.ollama_client import call_llm


@dataclass
class PaperAnalysis:
    purpose: str           # 研究の目的
    novelty: str           # 新規性
    method: str            # 手法
    results: str           # 実験結果
    limitations: str       # 限界
    raw_analysis: str      # LLMの全出力


OCHIAI_ANALYSIS_PROMPT = """あなたは研究論文の専門的分析者です。

以下の論文情報を「落合陽一式」の読み順で分析してください。

**読み順（この順番で論文を理解すること）:**
1. Abstract（概要を把握）
2. Conclusion（結論から成果を理解）
3. Experiments（実験でどう検証したか）
4. Related Work（先行研究との位置づけ）

---

## 論文タイトル
{title}

## 著者
{authors}

## Abstract
{abstract}

## Conclusion
{conclusion}

## Experiments / Results
{experiments}

## Related Work
{related_work}

## Method
{method}

## 全体テキスト（参考）
{full_text_excerpt}

---

上記を踏まえ、以下の5つの観点で論文を分析してください。
各項目は具体的かつ詳細に（各200-400字程度）記述してください。

## 研究の目的
この研究が解決しようとしている問題は何か。どんなリサーチクエスチョンに答えようとしているか。

## 新規性
先行研究と比較して、この研究の新しい点は何か。どのような貢献があるか。

## 手法
提案手法の核心的なアイデアと技術的詳細を説明せよ。

## 実験結果
主要な実験結果を定量的・定性的に説明せよ。ベースラインとの比較を含めよ。

## 限界と課題
この研究の限界、未解決の問題、今後の課題は何か。

日本語で回答してください。
"""


def analyze_paper(
    title: str,
    authors: list[str],
    abstract: str,
    conclusion: str,
    experiments: str,
    related_work: str,
    method: str,
    full_text: str,
    model: str | None = None,
    base_url: str | None = None,
) -> PaperAnalysis:
    """落合式読み順で論文を分析"""

    # テキストが長い場合は切り詰め（重要セクションは多めに確保）
    max_method = 6000      # 手法は最も重要なので長めに
    max_experiments = 6000  # 実験結果も定量データが多い
    max_section = 4000      # その他セクション
    max_full = 12000        # 全体テキスト（中盤も含むように）
    conclusion = conclusion[:max_section] if conclusion else "（セクション未検出）"
    experiments = experiments[:max_experiments] if experiments else "（セクション未検出）"
    related_work = related_work[:max_section] if related_work else "（セクション未検出）"
    method = method[:max_method] if method else "（セクション未検出）"
    # 全体テキストは先頭と中盤を含める
    if full_text:
        mid_start = len(full_text) // 3
        full_text_excerpt = full_text[:max_full // 2] + "\n...\n" + full_text[mid_start:mid_start + max_full // 2]
    else:
        full_text_excerpt = ""

    prompt = OCHIAI_ANALYSIS_PROMPT.format(
        title=title,
        authors=", ".join(authors) if authors else "不明",
        abstract=abstract or "（未検出）",
        conclusion=conclusion,
        experiments=experiments,
        related_work=related_work,
        method=method,
        full_text_excerpt=full_text_excerpt,
    )

    raw = call_llm(prompt, model=model, base_url=base_url)
    return _parse_analysis(raw)


def _parse_analysis(raw: str) -> PaperAnalysis:
    """LLM出力を構造化データにパース（フォールバック付き）"""
    sections = {
        "purpose": "",
        "novelty": "",
        "method": "",
        "results": "",
        "limitations": "",
    }

    # 見出しキーワード → セクションキーのマッピング（優先度順）
    keywords_map = {
        "研究の目的": "purpose",
        "目的": "purpose",
        "purpose": "purpose",
        "新規性": "novelty",
        "novelty": "novelty",
        "貢献": "novelty",
        "手法": "method",
        "method": "method",
        "アプローチ": "method",
        "実験結果": "results",
        "実験": "results",
        "result": "results",
        "experiment": "results",
        "限界": "limitations",
        "課題": "limitations",
        "limitation": "limitations",
    }

    current_key = None
    for line in raw.split("\n"):
        stripped = line.strip()
        matched = False
        # 見出し行の判定（#で始まるか、**太字**で始まる行）
        if stripped.startswith("#") or (stripped.startswith("**") and stripped.endswith("**")):
            for keyword, key in keywords_map.items():
                if keyword in stripped.lower():
                    current_key = key
                    matched = True
                    break
        if not matched and current_key:
            sections[current_key] += line + "\n"

    # パース成功率のチェック — 空セクションが多い場合はraw全体から再分割を試みる
    filled = sum(1 for v in sections.values() if v.strip())
    if filled < 3:
        # フォールバック: 段落分割で均等に割り当て
        paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip() and len(p.strip()) > 30]
        keys = ["purpose", "novelty", "method", "results", "limitations"]
        for i, key in enumerate(keys):
            if not sections[key].strip() and i < len(paragraphs):
                sections[key] = paragraphs[i]
        # それでもpurposeが空なら全体を使う
        if not sections["purpose"].strip():
            sections["purpose"] = raw[:800]

    return PaperAnalysis(
        purpose=sections["purpose"].strip(),
        novelty=sections["novelty"].strip(),
        method=sections["method"].strip(),
        results=sections["results"].strip(),
        limitations=sections["limitations"].strip(),
        raw_analysis=raw,
    )
