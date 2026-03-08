"""落合陽一式1枚スライド要約生成モジュール"""

from llm.ollama_client import call_llm


OCHIAI_SLIDE_PROMPT = """あなたは研究論文の要約専門家です。

以下の論文情報を基に、「落合陽一式 1枚スライド要約」を生成してください。

## 論文タイトル
{title}

## 著者
{authors}

## Abstract
{abstract}

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

## 既存研究との差
{differentiation}

## 参考文献リスト（先頭10件）
{references}

---

以下のテンプレートに従い、各項目を簡潔かつ具体的に記述してください（各項目3-5文）。
技術者が読んで論文の核心をすぐに理解できるレベルの具体性を保ってください。

出力フォーマット（このまま出力すること）:

# Paper Summary: {title}

**著者:** {authors}

## どんなもの？
[この研究が何をするものか、一言で説明した後に具体的な内容を記述]

## 先行研究と比べてどこがすごい？
[従来手法の問題点と、本研究の優位性を対比して記述]

## 技術や手法のキモはどこ？
[提案手法の核心的なアイデアを技術的に記述]

## どうやって有効だと検証した？
[実験設定、データセット、評価指標、主要な定量結果を記述]

## 議論はある？
[限界、未解決の問題、著者自身の議論を記述]

## 次に読むべき論文は？
[関連する重要論文を3-5本、理由とともに挙げよ]

日本語で回答してください。
"""


def generate_ochiai_summary(
    title: str,
    authors: list[str],
    abstract: str,
    purpose: str,
    novelty: str,
    method: str,
    results: str,
    limitations: str,
    differentiation: str,
    references: list[str],
    model: str | None = None,
    base_url: str | None = None,
) -> str:
    """落合式1枚スライド要約を生成"""

    authors_str = ", ".join(authors) if authors else "不明"
    refs_str = "\n".join(references[:10]) if references else "（参考文献未抽出）"

    prompt = OCHIAI_SLIDE_PROMPT.format(
        title=title,
        authors=authors_str,
        abstract=abstract or "（未検出）",
        purpose=purpose,
        novelty=novelty,
        method=method,
        results=results,
        limitations=limitations,
        differentiation=differentiation,
        references=refs_str,
    )

    return call_llm(prompt, model=model, base_url=base_url)
