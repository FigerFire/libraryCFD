#!/usr/bin/env python3
"""Generate a checkpointed Chinese LaTeX translation of LeVeque's book.

The script extracts one source-PDF page at a time and persists each translated
page in JSON.  It can therefore be interrupted and resumed without repeating
completed translation requests.  Mathematical expressions are retained as
literal text when the PDF's text layer cannot reliably reconstruct LaTeX.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from pathlib import Path

from deep_translator import GoogleTranslator
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parent
INPUT_PDF = ROOT / "Leveque.pdf"
CACHE_FILE = ROOT / "Leveque_zh_cache.json"
OUTPUT_TEX = ROOT / "Leveque_zh.tex"
MAX_CHARS = 4_000
# 原书目录占用的连续 PDF 页；重排版版本不保留原书页码目录。
CONTENTS_PAGES = set(range(11, 19))
# 译文版只保留有阅读价值的前言与正文；封面、出版社广告、版权页和原书目录不再
# 混入正文流。键为原 PDF 页号，值为整理后的章节题名。
EXCLUDED_FRONT_PAGES = set(range(1, 19))
PREFACE_PAGES = range(19, 22)
CHAPTER_STARTS = {
    23: "简介",
    37: "守恒定律和微分方程",
    69: "线性双曲方程的特征和黎曼问题",
    86: "有限体积法",
    109: "CLAWPACK 软件简介",
    122: "高分辨率方法",
    151: "边界条件和幽灵单元",
    161: "收敛性、准确性和稳定性",
    180: "变系数线性方程",
    210: "实现高分辨率的其他方法",
    225: "非线性标量守恒定律",
    249: "非线性标量守恒定律的有限体积方法",
    275: "非线性守恒定律系统",
    313: "气体动力学和欧拉方程",
    334: "非线性系统的有限体积方法",
    372: "一些非经典双曲问题",
    397: "源项与平衡方法",
    443: "多维双曲问题",
    458: "多维数值方法",
    469: "多维标量方程",
    491: "多维系统",
    513: "弹性波",
    536: "四边形网格上的有限体积方法",
}


def normalize_page(text: str) -> str:
    """Remove recurring running heads and normalize the text layer."""
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            lines.append("")
            continue
        if re.fullmatch(r"\d+", line):
            continue
        if re.fullmatch(r"Finite Volume Methods for Hyperbolic Problems", line):
            continue
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_chunks(text: str) -> list[str]:
    """Split on paragraph/sentence boundaries below Google Translate's limit."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if len(para) > MAX_CHARS:
            sentences = re.split(r"(?<=[.!?])\s+", para)
        else:
            sentences = [para]
        for sentence in sentences:
            if current and len(current) + len(sentence) + 2 > MAX_CHARS:
                chunks.append(current)
                current = sentence
            elif current:
                current += "\n\n" + sentence
            else:
                current = sentence
    if current:
        chunks.append(current)
    return chunks


def translate(text: str, translator: GoogleTranslator) -> str:
    """Translate a chunk with bounded retries; errors remain explicit."""
    if not re.search(r"[A-Za-z]{3}", text):
        return text
    for attempt in range(4):
        try:
            return translator.translate(text)
        except Exception as error:  # Network services can transiently throttle.
            if attempt == 3:
                raise RuntimeError(f"Google Translate request failed: {error}") from error
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def escape_latex(text: str) -> str:
    """Typeset extracted formulas literally rather than corrupting them."""
    # The PDF text layer uses Apple private-use glyphs for matrix delimiters
    # and a few ligatures.  Replace them with readable Unicode/ASCII forms
    # before XeLaTeX sees them, otherwise they render as blank boxes.
    private_letters = {
        chr(code): chr(ord("a") + code - 0xF761)
        for code in range(0xF761, 0xF77B)
    }
    extracted_symbols = {
        **private_letters,
        "\uf8ee": "[", "\uf8ef": "[", "\uf8f0": "[",
        "\uf8f1": "[", "\uf8f2": "[",
        "\uf8f9": "]", "\uf8fa": "]", "\uf8fb": "]",
        "\uf8f3": "]", "\uf8f4": "]",
        "\u23d0": "|", "\u20d7": "->", "\u03f5": "ε",
        "\ued79": "", "\u301c": "~",
    }
    text = "".join(extracted_symbols.get(char, char) for char in text)
    substitutions = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(substitutions.get(char, char) for char in html.unescape(text))


def is_empty_page(text: str) -> bool:
    """Return true for PDF pages without extractable, translated body text."""
    stripped = text.strip()
    return not stripped or stripped.startswith("[此页没有可提取") or stripped.startswith("[此页未能提取")


def remove_source_page_label(text: str) -> str:
    """Drop a source-page label from an extracted running head."""
    text = re.sub(r"^(?:\d+|[ivxlcdm]+)\s+", "", text.strip(), flags=re.IGNORECASE)
    return re.sub(r"(?<=[^\d])\d{1,3}\s*$", "", text).strip()


def math_latex(text: str) -> tuple[str, str | None]:
    """Convert a simple extracted equation into readable LaTeX math."""
    # Backslashes occurring in the machine-translated cache are extraction
    # artifacts (for example ``\\uqt``), not authored LaTeX commands.
    text = text.replace("\\", "")
    equation_number = None
    match = re.search(r"\s*\((\d+(?:\.\d+)+)\)\s*$", text)
    if match:
        equation_number = match.group(1)
        text = text[:match.start()].strip()
    text = text.rstrip("。.,;；")
    replacements = {
        "−": "-", "–": "-", "×": r"\times ", "≤": r"\leq ",
        "≥": r"\geq ", "≠": r"\neq ", "≈": r"\approx ",
        "∞": r"\infty ", "∈": r"\in ", "∇": r"\nabla ",
        "ρ": r"\rho ", "α": r"\alpha ", "β": r"\beta ",
        "γ": r"\gamma ", "δ": r"\delta ", "ε": r"\epsilon ",
        "κ": r"\kappa ", "σ": r"\sigma ", "φ": r"\phi ",
        "θ": r"\theta ", "λ": r"\lambda ", "μ": r"\mu ",
        "ω": r"\omega ", "ψ": r"\psi ", "Ψ": r"\Psi ",
        "ν": r"\nu ", "η": r"\eta ", "τ": r"\tau ",
        "ϵ": r"\epsilon ", "Σ": r"\Sigma ",
        "ℓ": r"\ell ", "→": r"\to ", "⇒": r"\Rightarrow ",
        # OCR frequently loses the radicand delimiters, so retain ``sqrt``
        # as readable math text instead of emitting an invalid \sqrt command.
        "√": "sqrt", "∫": r"\int ", "~": r"\sim ",
        "⃗": "", "̸": "/", "ˆ": "", "́": "", "ú": "u", "û": "u", "ü": "u",
        "⏐": "|", "\ued79": "",
    }
    text = "".join(replacements.get(char, char) for char in text)
    # The extraction layer commonly emits qt(x,t) rather than q_t(x,t).
    text = re.sub(r"\b([A-Za-z])([tx])(?=\s*\()", r"\1_\2", text)
    text = re.sub(r"\s+", " ", text)
    return text, equation_number


def looks_like_equation(text: str) -> bool:
    """Conservatively recognize standalone formula blocks, not prose."""
    compact = text.replace("\n", " ").strip()
    chinese = len(re.findall(r"[\u4e00-\u9fff]", compact))
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return (
        "=" in compact
        and chinese == 0
        and len(compact) <= 240
        and len(lines) <= 2
        and not any("{" in line or re.search(r"\bif\b", line, re.IGNORECASE) for line in lines)
        and bool(re.search(r"[A-Za-z]\s*(?:\(|_|=)|[∫∇ρσκαβγδθλμ]", compact))
    )


def format_paragraph(text: str) -> str:
    if not looks_like_equation(text):
        return escape_latex(text)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    converted = [math_latex(line) for line in lines]
    formula = r" \\ ".join(item for item, _ in converted)
    if len(converted) > 1:
        formula = f"\\begin{{aligned}}\n{formula}\n\\end{{aligned}}"
    # Do not reuse the source equation labels: OCR may duplicate one label on
    # multiple extracted blocks, while LaTeX anchors must remain unique.
    return f"\\begin{{equation}}\n{formula}\n\\end{{equation}}"


def page_body(text: str, current_chapter: str | None, seen_sections: set[str]) -> str:
    """Suppress repeated source running heads and style real section headings."""
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    # PDF footer page numbers are often extracted as standalone Chinese
    # numerals.  They have no value once the output uses its own pagination.
    paragraphs = [
        part for part in paragraphs
        if not re.fullmatch(r"[一二三四五六七八九十百千零〇]+", part)
    ]
    if not paragraphs:
        return ""

    raw_first = paragraphs[0]
    first = remove_source_page_label(raw_first)
    first = re.sub(r"^(前言)[一二三四五六七八九十百]+$", r"\1", first)
    current_key = re.sub(r"\s+", "", current_chapter or "")
    first_key = re.sub(r"\s+", "", first)
    is_running_section = bool(
        re.match(r"^\d+\.\d+(?:\.\d+)?\s*.*(?<=[^\d])\d{1,3}\s*$", raw_first)
    )
    if (
        (current_key and current_key in first_key and len(first) <= 100)
        or first in {"前言", current_chapter}
        or is_running_section
    ):
        # These are source running heads, not new text hierarchy.  In
        # particular, ``1.1 标题3`` is a page head; the real section title
        # appears in the following body paragraph without the trailing 3.
        paragraphs.pop(0)

    rendered: list[str] = []
    for paragraph in paragraphs:
        lines = paragraph.splitlines()
        first_line = lines[0].strip() if lines else ""
        match = re.match(r"^(\d+\.\d+(?:\.\d+)?)\s*(.+)$", first_line)
        if match:
            number, title = match.groups()
            title = re.sub(r"(?<=[^\d])\d{1,3}\s*$", "", title).strip()
            key = f"{number} {title}"
            if key not in seen_sections:
                seen_sections.add(key)
                command = "subsection" if number.count(".") >= 2 else "section"
                rendered.append(f"\\{command}{{{escape_latex(key)}}}")
            remainder = "\n".join(lines[1:]).strip()
            if remainder:
                rendered.append(format_paragraph(remainder))
        else:
            rendered.append(format_paragraph(paragraph))
    return "\n\n".join(rendered)


def make_tex(cache: dict[str, str], page_count: int) -> str:
    header = r"""% !TEX program = xelatex
% 自动生成。译文对应 Randall J. LeVeque, Finite Volume Methods for
% Hyperbolic Problems (Cambridge University Press, 2002)。仅供学习参考。
\documentclass[11pt,a4paper,openany,fontset=none]{ctexbook}
\usepackage[margin=2.55cm]{geometry}
\usepackage{microtype}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{titlesec}
\usepackage{amsmath,amssymb,amsfonts,bm,mathtools}
\setmainfont{Arial Unicode MS}
\setCJKmainfont{Songti SC}
\setCJKsansfont{Songti SC}
\setCJKmonofont{Songti SC}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.65em}
\linespread{1.28}\selectfont
\xeCJKsetup{CJKglue = \hskip 0.07em plus 0.04em minus 0.03em}
\titleformat{\chapter}[display]{\bfseries\Huge\centering}{第\thechapter 章}{0.7em}{}
\titleformat{\section}{\large\bfseries}{}{0pt}{}
\titleformat{\subsection}{\normalsize\bfseries}{}{0pt}{}
\titlespacing*{\section}{0pt}{1.35em}{0.65em}
\titlespacing*{\subsection}{0pt}{1.15em}{0.5em}
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\title{双曲问题的有限体积方法\\\large 中文自动译文}
\author{Randall J. LeVeque 著\\\small 译文由自动化工具生成，供学习与检索使用}
\date{原著：2002\\生成日期：\today}
\begin{document}
\frontmatter
\maketitle
\chapter*{说明}
本文件是 Randall J. LeVeque 所著《Finite Volume Methods for Hyperbolic Problems》的中文自动译文，
按正常阅读顺序重新排版。文字识别与机器翻译对复杂公式、图形、表格和个别符号的还原存在局限；
这些内容应以原书为准。原著版权归作者与 Cambridge University Press 所有。
"""
    preface: list[str] = [r"\chapter*{前言}\addcontentsline{toc}{chapter}{前言}"]
    seen_sections: set[str] = set()
    for number in PREFACE_PAGES:
        translated = cache.get(str(number), "")
        if is_empty_page(translated):
            continue
        content = page_body(translated, "前言", seen_sections)
        if content:
            preface.append(content)

    body: list[str] = [r"\tableofcontents", r"\mainmatter"]
    current_chapter: str | None = None
    for number in range(19, page_count + 1):
        if number in EXCLUDED_FRONT_PAGES or number in PREFACE_PAGES:
            continue
        if number in CHAPTER_STARTS:
            current_chapter = CHAPTER_STARTS[number]
            body.append(f"\\chapter{{{current_chapter}}}")
            seen_sections.clear()
        translated = cache.get(str(number), "")
        if is_empty_page(translated):
            continue
        content = page_body(translated, current_chapter, seen_sections)
        if content:
            body.append(content)
    return header + "\n\n".join(preface) + "\n\n" + "\n\n".join(body) + "\n\\end{document}\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-page", type=int, default=1)
    parser.add_argument("--to-page", type=int)
    parser.add_argument("--assemble-only", action="store_true")
    args = parser.parse_args()

    reader = PdfReader(INPUT_PDF)
    page_count = len(reader.pages)
    cache = json.loads(CACHE_FILE.read_text(encoding="utf-8")) if CACHE_FILE.exists() else {}

    if not args.assemble_only:
        stop = min(args.to_page or page_count, page_count)
        translator = GoogleTranslator(source="en", target="zh-CN")
        for number in range(max(args.from_page, 1), stop + 1):
            if str(number) in cache:
                print(f"[{number}/{page_count}] 已在检查点中，跳过")
                continue
            source = normalize_page(reader.pages[number - 1].extract_text(extraction_mode="layout") or "")
            chunks = split_chunks(source)
            print(f"[{number}/{page_count}] {len(source)} 字符，{len(chunks)} 个翻译块", flush=True)
            translated = "\n\n".join(translate(chunk, translator) for chunk in chunks)
            cache[str(number)] = translated or "[此页没有可提取的文字。]"
            CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
            time.sleep(0.35)

    OUTPUT_TEX.write_text(make_tex(cache, page_count), encoding="utf-8")
    print(f"已写入 {OUTPUT_TEX}；已翻译 {len(cache)}/{page_count} 页。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
