"""図・テーブル抽出モジュール - PDFからFigure/Tableを画像として抽出

PyMuPDF を使用してPDFから埋め込み画像を抽出し、テキスト中のキャプションと
マッチングする。抽出した図にはスコアリングを行い、重要度の高い図を選別する。
"""

import re
from pathlib import Path
from dataclasses import dataclass

import pymupdf


@dataclass
class ExtractedFigure:
    """PDFから抽出された図・テーブルのデータクラス

    Attributes
    ----------
    figure_id : str
        図の識別子 (e.g., "Figure 1", "Table 2")
    image_path : str
        抽出画像の保存先パス
    caption : str
        キャプションテキスト
    page_number : int
        元PDFのページ番号
    figure_type : str
        種別 ("figure" or "table")
    bbox : tuple or None
        バウンディングボックス座標
    """
    figure_id: str        # "Figure 1", "Table 2" etc.
    image_path: str       # 保存先パス
    caption: str          # キャプションテキスト
    page_number: int      # ページ番号
    figure_type: str      # "figure" or "table"
    bbox: tuple = None    # バウンディングボックス


def _extract_captions(text: str) -> list[dict]:
    """テキストからFigure/Tableキャプションを抽出"""
    patterns = [
        re.compile(r"(Figure|Fig\.?|TABLE|Table)\s*(\d+)[.:]\s*(.*?)(?=\n\n|\n(?:Figure|Fig\.?|TABLE|Table)\s*\d+|$)", re.DOTALL | re.IGNORECASE),
    ]
    captions = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            fig_type = match.group(1).lower()
            fig_num = match.group(2)
            caption_text = match.group(3).strip().replace("\n", " ")
            # キャプションが長すぎる場合は切り詰め
            if len(caption_text) > 500:
                caption_text = caption_text[:500] + "..."

            if "fig" in fig_type:
                fig_type = "figure"
                fig_id = f"Figure {fig_num}"
            else:
                fig_type = "table"
                fig_id = f"Table {fig_num}"

            captions.append({
                "figure_id": fig_id,
                "caption": caption_text,
                "figure_type": fig_type,
            })
    return captions


def extract_figures(pdf_path: str | Path, output_dir: str | Path) -> list[ExtractedFigure]:
    """PDFからすべての画像を抽出し、キャプションと紐付ける"""
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(str(pdf_path))
    extracted = []
    image_counter = 0

    # 全ページからキャプション情報を収集
    all_captions = []
    for page in doc:
        page_captions = _extract_captions(page.get_text())
        for cap in page_captions:
            cap["page"] = page.number
        all_captions.extend(page_captions)

    # 各ページから画像を抽出
    caption_index = 0
    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            try:
                base_image = doc.extract_image(xref)
            except Exception:
                continue

            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            width = base_image.get("width", 0)
            height = base_image.get("height", 0)

            # 小さすぎる画像はスキップ（ロゴやアイコン）
            if width < 100 or height < 100:
                continue

            image_counter += 1

            # キャプションとの紐付け
            caption_info = None
            for cap in all_captions:
                if cap["page"] == page_num and cap not in [e.__dict__ for e in extracted]:
                    caption_info = cap
                    break

            if caption_info:
                fig_id = caption_info["figure_id"]
                caption = caption_info["caption"]
                fig_type = caption_info["figure_type"]
                filename = f"{fig_id.lower().replace(' ', '_')}.{image_ext}"
            else:
                fig_id = f"Figure {image_counter}"
                caption = ""
                fig_type = "figure"
                filename = f"image_{image_counter}.{image_ext}"

            # 画像を保存
            image_path = output_dir / filename
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            extracted.append(ExtractedFigure(
                figure_id=fig_id,
                image_path=str(image_path),
                caption=caption,
                page_number=page_num + 1,
                figure_type=fig_type,
            ))

    doc.close()

    # 画像が少ない場合、ページレンダリングでフォールバック
    if len(extracted) < 2:
        extracted.extend(_extract_by_page_render(pdf_path, output_dir, len(extracted)))

    return extracted


def _extract_by_page_render(pdf_path: Path, output_dir: Path, start_index: int) -> list[ExtractedFigure]:
    """ページを画像としてレンダリングし、図が含まれるページを保存"""
    doc = pymupdf.open(str(pdf_path))
    extracted = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().lower()

        # 図やテーブルへの言及があるページをレンダリング
        if any(kw in text for kw in ["figure", "fig.", "table"]):
            has_caption = bool(re.search(r"(figure|fig\.?|table)\s*\d+", text, re.IGNORECASE))
            if not has_caption:
                continue

            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))  # 2x解像度
            filename = f"page_{page_num + 1}.png"
            image_path = output_dir / filename
            pix.save(str(image_path))

            extracted.append(ExtractedFigure(
                figure_id=f"Page {page_num + 1}",
                image_path=str(image_path),
                caption=f"Page {page_num + 1} containing figures",
                page_number=page_num + 1,
                figure_type="page",
            ))

    doc.close()
    return extracted


def _count_references(fig_id: str, full_text: str) -> int:
    """本文中で図が引用されている回数をカウント"""
    # "Figure 1" → パターン: Figure 1, Fig. 1, Fig 1 (大文字小文字不問)
    parts = fig_id.split()
    if len(parts) != 2:
        return 0
    fig_type_str, fig_num = parts[0], parts[1]

    if fig_type_str.lower() in ("figure", "fig"):
        patterns = [
            rf"(?:Figure|Fig\.?)\s*{re.escape(fig_num)}(?!\d)",  # Fig 1 にマッチ、Fig 10 にはマッチしない
        ]
    elif fig_type_str.lower() == "table":
        patterns = [
            rf"Table\s*{re.escape(fig_num)}(?!\d)",
        ]
    else:
        return 0

    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, full_text, re.IGNORECASE))

    # キャプション自体の1回分を除く（本文中の引用のみカウント）
    return max(0, count - 1)


# 重要度の高い図であることを示すキャプションキーワード
_HIGH_IMPORTANCE_KEYWORDS = [
    # 手法・アーキテクチャ概要図
    "overview", "architecture", "framework", "pipeline", "model",
    "proposed", "our method", "our approach", "system",
    "概要", "全体像", "アーキテクチャ", "提案手法",
    # 主要実験結果
    "main result", "comparison", "performance", "ablation",
    "benchmark", "evaluation", "accuracy", "state-of-the-art", "sota",
    "比較", "性能", "結果", "精度",
    # 定性的結果
    "qualitative", "visualization", "example", "sample",
    "可視化", "定性",
]

_LOW_IMPORTANCE_KEYWORDS = [
    # 補足的な図
    "appendix", "supplementary", "additional",
    "付録", "補足",
]


def _caption_importance_score(caption: str) -> int:
    """キャプション内容から重要度スコアを算出"""
    if not caption:
        return 0

    caption_lower = caption.lower()
    score = 0

    for kw in _HIGH_IMPORTANCE_KEYWORDS:
        if kw in caption_lower:
            score += 5
            break  # 1つ見つかれば十分

    for kw in _LOW_IMPORTANCE_KEYWORDS:
        if kw in caption_lower:
            score -= 5
            break

    # キャプションが長い = 詳細な説明がある = 重要な傾向
    if len(caption) > 100:
        score += 2

    return score


def select_key_figures(
    figures: list[ExtractedFigure],
    max_count: int = 5,
    full_text: str = "",
) -> list[ExtractedFigure]:
    """重要な図をスコアリングで選択する

    スコアリング基準:
      1. 本文中の引用回数（多く引用される図 = 重要）
      2. キャプション内容（手法概要図、主要結果を示すキーワード）
      3. 図の種別（figure > table > page）
      4. キャプションの有無
      5. 図の番号（若い番号は概要図であることが多い）
      6. 画像サイズ（大きい図は重要な傾向）
    """
    if len(figures) <= max_count:
        return figures

    scored = []
    for fig in figures:
        score = 0

        # 1. 本文中の引用回数（最大+15）
        if full_text:
            ref_count = _count_references(fig.figure_id, full_text)
            score += min(ref_count * 5, 15)

        # 2. キャプション内容分析
        score += _caption_importance_score(fig.caption)

        # 3. 図の種別
        if fig.figure_type == "figure":
            score += 5
        elif fig.figure_type == "table":
            score += 3
        # "page" タイプ（フォールバック）は加点なし

        # 4. キャプションの有無
        if fig.caption:
            score += 8

        # 5. 図の番号（Figure 1-3 は概要図・主要結果であることが多い）
        num_match = re.search(r"\d+", fig.figure_id)
        if num_match:
            fig_num = int(num_match.group())
            if fig_num <= 3:
                score += 6 - fig_num  # Figure 1: +5, Figure 2: +4, Figure 3: +3

        # 6. 画像サイズ（大きい図は重要な傾向）
        if fig.bbox:
            width = fig.bbox[2] - fig.bbox[0]
            height = fig.bbox[3] - fig.bbox[1]
            area = width * height
            if area > 200000:   # 大きい図
                score += 3
            elif area > 100000:  # 中程度
                score += 1

        scored.append((score, fig))

    scored.sort(key=lambda x: x[0], reverse=True)

    selected = [fig for _, fig in scored[:max_count]]

    # デバッグ出力
    print("  図の重要度スコア:")
    for s, fig in scored:
        marker = " *" if fig in selected else ""
        print(f"    {fig.figure_id}: score={s}{marker}")

    return selected
