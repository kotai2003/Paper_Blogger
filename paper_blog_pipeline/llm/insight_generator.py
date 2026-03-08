"""Insight生成モジュール - 研究の意味・産業応用・差分分析"""

from dataclasses import dataclass

from llm.ollama_client import call_llm


@dataclass
class ResearchInsight:
    significance: str        # 研究の意味
    industry_applications: str  # 産業応用
    differentiation: str     # 既存研究との差
    future_directions: str   # 今後の方向性


INSIGHT_PROMPT = """あなたは技術トレンド分析の専門家です。

以下の論文分析結果を基に、この研究のインサイトを生成してください。

## 論文タイトル
{title}

## 研究の目的
{purpose}

## 新規性
{novelty}

## 手法
{method}

## 実験結果
{results}

## 限界
{limitations}

---

以下の4つの観点で詳細なインサイトを生成してください（各300-500字）:

## 研究の意味
この研究が学術界・技術コミュニティに与えるインパクトは何か。なぜこの研究が重要なのか。

## 産業応用
この研究成果はどのような産業・製品・サービスに応用できるか。具体的なユースケースを挙げよ。

## 既存研究との差分
従来のアプローチと比較して、この研究がもたらすパラダイムシフトや技術的ブレイクスルーは何か。

## 今後の研究方向
この研究を発展させるとしたら、どのような方向性が考えられるか。

日本語で回答してください。
"""


def generate_insights(
    title: str,
    purpose: str,
    novelty: str,
    method: str,
    results: str,
    limitations: str,
    model: str | None = None,
    base_url: str | None = None,
) -> ResearchInsight:
    """論文分析結果からインサイトを生成"""

    prompt = INSIGHT_PROMPT.format(
        title=title,
        purpose=purpose,
        novelty=novelty,
        method=method,
        results=results,
        limitations=limitations,
    )

    raw = call_llm(prompt, model=model, base_url=base_url)
    return _parse_insights(raw)


def _parse_insights(raw: str) -> ResearchInsight:
    sections = {
        "significance": "",
        "industry_applications": "",
        "differentiation": "",
        "future_directions": "",
    }

    keywords_map = {
        "研究の意味": "significance",
        "意味": "significance",
        "significance": "significance",
        "インパクト": "significance",
        "産業応用": "industry_applications",
        "応用": "industry_applications",
        "application": "industry_applications",
        "ユースケース": "industry_applications",
        "既存研究との差": "differentiation",
        "差分": "differentiation",
        "differentiation": "differentiation",
        "ブレイクスルー": "differentiation",
        "今後の研究": "future_directions",
        "今後の方向": "future_directions",
        "future": "future_directions",
        "発展": "future_directions",
    }

    current_key = None
    for line in raw.split("\n"):
        stripped = line.strip()
        matched = False
        if stripped.startswith("#") or (stripped.startswith("**") and stripped.endswith("**")):
            for keyword, key in keywords_map.items():
                if keyword in stripped.lower():
                    current_key = key
                    matched = True
                    break
        if not matched and current_key:
            sections[current_key] += line + "\n"

    # フォールバック
    filled = sum(1 for v in sections.values() if v.strip())
    if filled < 2:
        paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip() and len(p.strip()) > 30]
        keys = ["significance", "industry_applications", "differentiation", "future_directions"]
        for i, key in enumerate(keys):
            if not sections[key].strip() and i < len(paragraphs):
                sections[key] = paragraphs[i]
        if not sections["significance"].strip():
            sections["significance"] = raw[:500]

    return ResearchInsight(
        significance=sections["significance"].strip(),
        industry_applications=sections["industry_applications"].strip(),
        differentiation=sections["differentiation"].strip(),
        future_directions=sections["future_directions"].strip(),
    )
