"""中国語フィルター - LLMによる記事検収

生成されたブログ記事・要約に混入した中国語（簡体字・中国語表現）を
gpt-oss:20b-cloud を使って検出・修正する。
ollama_client.py の _sanitize_japanese() はルールベースだが、
本モジュールはLLMを使ってより高精度にフィルタリングする。
"""

from llm.ollama_client import get_client

# 検収用モデル（固定）
FILTER_MODEL = "gpt-oss:20b-cloud"

FILTER_SYSTEM_PROMPT = """\
あなたは日本語テキストの品質検査を行う校正エキスパートです。

以下のMarkdownテキストには、中国語の簡体字や中国語的な表現が混入している可能性があります。
あなたの仕事は：

1. 中国語の簡体字を日本語の対応する漢字に置換する
   例: 异常→異常、检测→検知、数据→データ、实现→実現、结果→結果、应用→応用
2. 中国語的な語順・表現を自然な日本語表現に修正する
   例: "通过...实现" → "…を通じて…を実現"、"基于" → "に基づく"
3. Markdownの書式（見出し、箇条書き、画像参照、コードブロック等）は一切変更しない
4. 英語の専門用語・固有名詞はそのまま残す
5. 内容の追加・削除・要約は行わない。修正は中国語→日本語の変換のみ
6. 修正不要の場合はそのまま元テキストを返す

重要：出力はMarkdownテキストのみ。説明や前置きは不要。"""


def filter_chinese(
    text: str,
    base_url: str = "http://localhost:11434/v1",
    max_tokens: int = 16384,
) -> str:
    """LLMを使って中国語混入をフィルタリングする

    Parameters
    ----------
    text : str
        フィルタリング対象のMarkdownテキスト
    base_url : str
        Ollama APIベースURL
    max_tokens : int
        最大出力トークン数

    Returns
    -------
    str
        中国語が修正された日本語テキスト
    """
    if not text or not text.strip():
        return text

    client = get_client(base_url)

    prompt = f"""\
以下のMarkdownテキストから中国語の簡体字・中国語表現を検出し、
正しい日本語に修正して全文を返してください。

---
{text}
---"""

    response = client.chat.completions.create(
        model=FILTER_MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": FILTER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    result = response.choices[0].message.content

    # LLMが```markdownで囲んだ場合のストリップ
    if result.startswith("```markdown"):
        result = result[len("```markdown"):].strip()
    if result.startswith("```"):
        result = result[3:].strip()
    if result.endswith("```"):
        result = result[:-3].strip()

    return result
