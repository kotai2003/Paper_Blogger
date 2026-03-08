"""PDF論文解析モジュール - PyMuPDFを使用してPDFから構造化データを抽出

PyMuPDF (pymupdf) を使用して学術論文PDFを解析し、タイトル・著者・
アブストラクト・セクション・参考文献を構造化データ (ParsedPaper) として抽出する。
セクション検索にはファジーマッチングを使用し、論文フォーマットの違いを吸収する。
"""

import re
from pathlib import Path
from dataclasses import dataclass, field

import pymupdf


@dataclass
class PaperSection:
    """論文の1セクションを表すデータクラス

    Attributes
    ----------
    title : str
        セクションのタイトル (e.g., "Introduction", "Methods")
    content : str
        セクションの本文テキスト
    level : int
        見出しレベル (1 = H1, 2 = H2, etc.)
    """
    title: str
    content: str
    level: int = 1


@dataclass
class ParsedPaper:
    """解析済み論文の構造化データ

    PDF論文から抽出された全情報を保持する。セクション検索には
    ファジーマッチングヘルパーメソッドを提供する。

    Attributes
    ----------
    title : str
        論文タイトル
    authors : list[str]
        著者リスト
    abstract : str
        アブストラクト
    sections : list[PaperSection]
        セクション一覧
    full_text : str
        全文テキスト
    references : list[str]
        参考文献リスト
    """
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    sections: list[PaperSection] = field(default_factory=list)
    full_text: str = ""
    references: list[str] = field(default_factory=list)

    def get_section(self, keyword: str) -> str | None:
        """キーワードでセクションを検索（部分一致、最初の1件）"""
        keyword_lower = keyword.lower()
        for section in self.sections:
            if keyword_lower in section.title.lower():
                return section.content
        return None

    def get_sections_by_keywords(self, keywords: list[str]) -> str:
        """複数キーワードに一致する全セクションを結合して返す"""
        parts = []
        seen_titles = set()
        for kw in keywords:
            kw_lower = kw.lower()
            for section in self.sections:
                title_lower = section.title.lower()
                if kw_lower in title_lower and title_lower not in seen_titles:
                    seen_titles.add(title_lower)
                    parts.append(f"### {section.title}\n{section.content}")
        return "\n\n".join(parts)

    def get_conclusion(self) -> str:
        return self.get_sections_by_keywords(
            ["conclusion", "concluding", "summary", "discussion"]
        )

    def get_experiments(self) -> str:
        return self.get_sections_by_keywords(
            ["experiment", "result", "evaluation", "empirical",
             "ablation", "analysis", "comparison", "benchmark"]
        )

    def get_related_work(self) -> str:
        return self.get_sections_by_keywords(
            ["related work", "background", "prior work", "literature", "preliminary"]
        )

    def get_method(self) -> str:
        return self.get_sections_by_keywords(
            ["method", "approach", "model", "framework", "architecture",
             "proposed", "system", "design", "formulation", "training"]
        )


# 学術論文でよく使われるセクション見出しパターン
SECTION_PATTERNS = [
    # "1. Introduction" or "1 Introduction"
    re.compile(r"^(\d+)\s*\.?\s+([A-Z][A-Za-z\s:&\-]+)$"),
    # "I. Introduction" (ローマ数字)
    re.compile(r"^(I{1,3}|IV|V|VI{0,3}|IX|X)\s*\.?\s+([A-Z][A-Za-z\s:&\-]+)$"),
    # "Introduction" (番号なし、大文字始まり、短い行)
    re.compile(r"^([A-Z][A-Za-z\s:&\-]{3,40})$"),
]

KNOWN_SECTIONS = [
    "abstract", "introduction", "related work", "background",
    "method", "methodology", "approach", "model", "framework",
    "experiment", "experiments", "results", "evaluation",
    "discussion", "conclusion", "conclusions", "acknowledgment",
    "acknowledgments", "references", "appendix",
    "proposed method", "experimental setup", "experimental results",
    "limitations", "future work",
]


def _is_section_heading(line: str) -> tuple[bool, str, int]:
    """行がセクション見出しかどうか判定"""
    line = line.strip()
    if not line or len(line) > 80:
        return False, "", 0

    for pattern in SECTION_PATTERNS[:2]:
        match = pattern.match(line)
        if match:
            title = match.group(2).strip()
            if any(kw in title.lower() for kw in KNOWN_SECTIONS):
                return True, title, 1
            if len(title.split()) <= 6:
                return True, title, 1

    # 番号なしの見出しは既知セクション名のみ
    if any(line.lower().startswith(kw) for kw in KNOWN_SECTIONS):
        if len(line.split()) <= 8:
            return True, line, 1

    return False, "", 0


def _extract_abstract(full_text: str) -> str:
    """Abstractを抽出"""
    patterns = [
        re.compile(r"(?:Abstract|ABSTRACT)\s*[-—:]?\s*\n?(.*?)(?=\n\s*(?:\d+\s*\.?\s+)?(?:Introduction|INTRODUCTION|1\s))", re.DOTALL | re.IGNORECASE),
        re.compile(r"(?:Abstract|ABSTRACT)\s*[-—:]?\s*\n?(.*?)(?=\n\n)", re.DOTALL | re.IGNORECASE),
    ]
    for pattern in patterns:
        match = pattern.search(full_text)
        if match:
            abstract = match.group(1).strip()
            if len(abstract) > 50:
                return abstract
    return ""


def _extract_title_and_authors(doc: pymupdf.Document) -> tuple[str, list[str]]:
    """最初のページからタイトルと著者を推定"""
    if len(doc) == 0:
        return "", []

    page = doc[0]
    blocks = page.get_text("dict")["blocks"]

    text_blocks = []
    for block in blocks:
        if block["type"] == 0:  # テキストブロック
            for line in block["lines"]:
                text = ""
                max_size = 0
                for span in line["spans"]:
                    text += span["text"]
                    max_size = max(max_size, span["size"])
                text = text.strip()
                if text:
                    text_blocks.append({"text": text, "size": max_size, "y": line["bbox"][1]})

    if not text_blocks:
        return "", []

    # 最大フォントサイズの行をタイトルとする
    max_size = max(b["size"] for b in text_blocks)
    title_parts = [b["text"] for b in text_blocks if b["size"] >= max_size * 0.9]
    title = " ".join(title_parts)

    # タイトルの次に来る、中間サイズのテキストを著者とする
    authors = []
    title_y = max(b["y"] for b in text_blocks if b["size"] >= max_size * 0.9)
    median_size = sorted(b["size"] for b in text_blocks)[len(text_blocks) // 2]

    for b in sorted(text_blocks, key=lambda x: x["y"]):
        if b["y"] > title_y and abs(b["size"] - median_size) < 2:
            author_text = b["text"].strip()
            if author_text and not any(kw in author_text.lower() for kw in ["abstract", "introduction", "university", "institute", "department", "@"]):
                # カンマやandで分割
                parts = re.split(r"[,;]|\band\b", author_text)
                for part in parts:
                    part = part.strip()
                    if part and len(part) > 2 and len(part) < 50:
                        authors.append(part)
                if authors:
                    break

    return title.strip(), authors


def parse_pdf(pdf_path: str | Path) -> ParsedPaper:
    """PDFファイルを解析して構造化データを返す"""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = pymupdf.open(str(pdf_path))
    paper = ParsedPaper()

    # タイトルと著者の抽出
    paper.title, paper.authors = _extract_title_and_authors(doc)

    # 全テキスト抽出
    full_text_parts = []
    for page in doc:
        full_text_parts.append(page.get_text())
    paper.full_text = "\n".join(full_text_parts)

    # Abstract抽出
    paper.abstract = _extract_abstract(paper.full_text)

    # セクション分割
    lines = paper.full_text.split("\n")
    current_section = None
    current_content = []

    for line in lines:
        is_heading, heading_title, level = _is_section_heading(line)
        if is_heading:
            if current_section:
                current_section.content = "\n".join(current_content).strip()
                paper.sections.append(current_section)
            current_section = PaperSection(title=heading_title, content="", level=level)
            current_content = []
        elif current_section:
            current_content.append(line)

    # 最後のセクション
    if current_section:
        current_section.content = "\n".join(current_content).strip()
        paper.sections.append(current_section)

    # Referencesの簡易抽出
    ref_section = paper.get_section("references")
    if ref_section:
        ref_lines = ref_section.split("\n")
        current_ref = ""
        for line in ref_lines:
            line = line.strip()
            if re.match(r"^\[?\d+\]?\s", line):
                if current_ref:
                    paper.references.append(current_ref.strip())
                current_ref = line
            elif current_ref:
                current_ref += " " + line
        if current_ref:
            paper.references.append(current_ref.strip())

    doc.close()
    return paper
