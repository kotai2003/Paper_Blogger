"""図解析モジュール - VLMを使って図の内容を分析"""

from pathlib import Path
from dataclasses import dataclass

from figures.figure_extractor import ExtractedFigure
from vlm.vlm_interface import OllamaVLM


@dataclass
class AnalyzedFigure:
    figure: ExtractedFigure
    description: str      # 図の説明
    structure: str         # 図の構造（グラフ、フローチャートなど）
    significance: str      # 論文における意味


FIGURE_ANALYSIS_PROMPT = """あなたは研究論文の図を解析する専門家です。

以下の図を詳細に分析してください。

キャプション: {caption}

以下の3つの観点で分析結果を出力してください:

## 図の説明
この図が何を示しているか、具体的に説明してください。グラフであれば軸の意味、値の傾向、比較対象などを述べてください。

## 図の構造
この図の種類（棒グラフ、折れ線グラフ、フローチャート、アーキテクチャ図、表、ヒートマップなど）と、その構成要素を説明してください。

## 論文における意義
この図が論文の主張をどのように支えているか、研究のどの部分に関連するかを述べてください。

日本語で回答してください。
"""


def analyze_figures(
    figures: list[ExtractedFigure],
    vlm: OllamaVLM,
) -> list[AnalyzedFigure]:
    """VLMを使って図を解析"""
    analyzed = []

    for figure in figures:
        if not Path(figure.image_path).exists():
            continue

        prompt = FIGURE_ANALYSIS_PROMPT.format(caption=figure.caption or "キャプションなし")

        try:
            result = vlm.analyze_image(figure.image_path, prompt)
        except Exception as e:
            print(f"  Warning: Failed to analyze {figure.figure_id}: {e}")
            result = "解析に失敗しました。"

        # レスポンスをパースして3つのセクションに分割
        description = ""
        structure = ""
        significance = ""

        current = ""
        for line in result.split("\n"):
            if "図の説明" in line:
                current = "description"
                continue
            elif "図の構造" in line:
                current = "structure"
                continue
            elif "論文における意義" in line or "論文における意味" in line:
                current = "significance"
                continue

            if current == "description":
                description += line + "\n"
            elif current == "structure":
                structure += line + "\n"
            elif current == "significance":
                significance += line + "\n"

        # パースに失敗した場合は全体をdescriptionに
        if not description and not structure:
            description = result

        analyzed.append(AnalyzedFigure(
            figure=figure,
            description=description.strip(),
            structure=structure.strip(),
            significance=significance.strip(),
        ))

    return analyzed
