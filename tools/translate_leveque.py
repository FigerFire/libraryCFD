#!/usr/bin/env python3
"""
Translate LeVeque's "Finite Volume Methods for Hyperbolic Problems"
first 100 pages from English to Chinese, output as LaTeX document.

Uses deep-translator (Google Translate) for translation.
"""

import re
import time
import os
import sys
from deep_translator import GoogleTranslator

# ============ CONFIGURATION ============
INPUT_TXT = "/Volumes/SSD_LPF/sonicSolver/sonicSolver/papers/Leveque_p1_100.txt"
OUTPUT_TEX = "/Volumes/SSD_LPF/sonicSolver/sonicSolver/papers/Leveque_zh.tex"

CHUNK_SIZE = 3500       # Max chars per translation request
DELAY_BETWEEN = 1.0     # Seconds between requests
MAX_RETRIES = 3
# =======================================

def clean_corrupted(text):
    """Remove PDF-extraction artifacts like fullwidth chars."""
    result = []
    for ch in text:
        cp = ord(ch)
        if 0xFF21 <= cp <= 0xFF3A:
            result.append(chr(cp - 0xFF21 + ord('A')))
        elif 0xFF41 <= cp <= 0xFF5A:
            result.append(chr(cp - 0xFF41 + ord('a')))
        else:
            result.append(ch)
    return ''.join(result)

def is_mostly_math(text):
    """Check if text is primarily mathematical notation."""
    alpha = sum(1 for c in text if c.isalpha())
    total = max(len(text), 1)
    return alpha / total < 0.15 and len(text) > 20

def split_into_sections(raw_text):
    """Split extracted text into logical sections."""
    pages = raw_text.split('===PAGE')
    sections = []
    
    for block in pages[1:]:
        lines = block.strip().split('\n')
        if not lines:
            continue
        
        page_num = lines[0].strip().rstrip('=')
        content_lines = lines[1:]
        content = '\n'.join(content_lines).strip()
        content = clean_corrupted(content)
        
        if not content or 'intentionally left blank' in content.lower():
            sections.append(('empty', page_num, ''))
            continue
        
        # Detect chapter headings: "N\nTitle Case Words"
        chapter_match = re.match(r'^(\d+)\s*\n\s*([A-Z][A-Za-z\s,\(\)\-]+)', content)
        if chapter_match:
            sections.append(('chapter', page_num, content))
            continue
        
        # Detect "Part" headings
        if re.match(r'^Part\s+', content, re.IGNORECASE):
            sections.append(('part', page_num, content))
            continue
        
        # Detect section headings: "N.N Title Case Words"
        section_match = re.match(r'^(\d+\.\d+)\s+([A-Z][A-Za-z\s,\(\)\-]+)', content)
        if section_match:
            sections.append(('section', page_num, content))
            continue
        
        # Special pages
        special_titles = ['Preface', 'Contents', 'Introduction', 'References', 
                         'Notation', 'Exercises', 'Bibliography', 'Index',
                         'Cambridge Texts in Applied Mathematics',
                         'Finite Volume Methods for Hyperbolic Problems']
        for title in special_titles:
            if content.strip().startswith(title):
                sections.append(('special', page_num, content))
                break
        else:
            sections.append(('content', page_num, content))
    
    return sections

def split_paragraphs(text):
    """Split text into paragraphs at double-newline boundaries."""
    raw = re.split(r'\n\s*\n', text)
    result = []
    for para in raw:
        para = para.strip()
        if para:
            para = re.sub(r'\n', ' ', para)
            para = re.sub(r'\s{2,}', ' ', para)
            result.append(para)
    return result

def chunk_for_translation(paragraphs, max_size=CHUNK_SIZE):
    """Group paragraphs into chunks that fit within translation limits."""
    chunks = []
    current = []
    current_len = 0
    
    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > max_size and current:
            chunks.append(' '.join(current))
            current = [para]
            current_len = para_len
        else:
            current.append(para)
            current_len += para_len
    
    if current:
        chunks.append(' '.join(current))
    
    return chunks

def translate_chunk(text, translator):
    """Translate a single chunk with retries."""
    if not text or not text.strip():
        return text
    
    if is_mostly_math(text):
        return text
    
    for attempt in range(MAX_RETRIES):
        try:
            result = translator.translate(text)
            return result
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    重试 {attempt+2}/{MAX_RETRIES}...")
                time.sleep(3 * (attempt + 1))
            else:
                print(f"    翻译失败，保留原文: {str(e)[:80]}")
                return text

def escape_latex(text):
    """Escape special LaTeX characters."""
    chars_to_escape = [
        ('&', '\\&'), ('%', '\\%'), ('#', '\\#'),
        ('$', '\\$'), ('{', '\\{'), ('}', '\\}'),
        ('~', '\\textasciitilde{}'), 
    ]
    result = text
    for char, escaped in chars_to_escape:
        result = result.replace(char, escaped)
    return result

def build_latex_document(translated_sections):
    """Build the final LaTeX document."""
    
    header = r"""% !TEX program = xelatex
\documentclass[12pt,a4paper]{ctexbook}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{geometry}
\usepackage{fancyhdr}
\usepackage{enumitem}
\geometry{margin=2.5cm}

\newtheorem{theorem}{定理}[chapter]
\newtheorem{lemma}[theorem]{引理}
\newtheorem{corollary}[theorem]{推论}
\newtheorem{definition}[theorem]{定义}
\newtheorem{example}{例}[chapter]
\newtheorem{remark}{注记}[chapter]

\title{双曲问题的有限体积方法}
\author{Randall J. LeVeque \\ 华盛顿大学 \\[6pt] \small 中文翻译版}
\date{2002}

\begin{document}

\maketitle

\chapter*{译者序}
本文档为 Randall J. LeVeque 所著《Finite Volume Methods for Hyperbolic Problems》
（剑桥大学出版社，2002年）前100页的中文翻译。
翻译使用自动化工具辅助完成，仅供学习参考。
原文版权归原作者和出版社所有。

\tableofcontents

"""
    
    footer = r"""
\end{document}
"""
    
    body_parts = []
    
    for sec_type, page_num, content in translated_sections:
        if not content.strip():
            continue
        
        escaped = escape_latex(content)
        
        if sec_type == 'chapter':
            lines = content.strip().split('\n')
            if len(lines) >= 2:
                ch_num = lines[0].strip()
                ch_title = ' '.join(lines[1:]).strip()
                body_parts.append(f'\n\\chapter{{{ch_title}}}\n')
                body_parts.append(f'\\label{{ch:{ch_num}}}\n')
                body_parts.append(f'% 原文第{page_num}页\n\n')
            else:
                body_parts.append(f'\n\\chapter{{{escaped[:80]}}}\n')
                
        elif sec_type == 'part':
            body_parts.append(f'\n\\part*{{{escaped.strip()}}}\n')
            body_parts.append(f'% 原文第{page_num}页\n\n')
            
        elif sec_type == 'section':
            lines = content.strip().split('\n')
            if len(lines) >= 2:
                sec_title = ' '.join(lines[1:]).strip()
                body_parts.append(f'\n\\section{{{sec_title}}}\n')
            body_parts.append(f'% 原文第{page_num}页\n')
            body_parts.append(f'{escaped}\n\n')
            
        elif sec_type == 'special':
            title = content.strip().split('\n')[0]
            body_parts.append(f'\n\\section*{{{title}}}\n')
            body_parts.append(f'% 原文第{page_num}页\n')
            body_parts.append(f'{escaped}\n\n')
            
        else:
            body_parts.append(f'% 原文第{page_num}页\n')
            body_parts.append(f'{escaped}\n\n')
    
    return header + '\n'.join(body_parts) + footer

def main():
    print("=" * 70)
    print("  LeVeque 前100页 英→中翻译")
    print("=" * 70)
    
    print(f"\n读取: {INPUT_TXT}")
    with open(INPUT_TXT, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    print(f"总字符数: {len(raw_text):,}")
    
    print("\n分析文档结构...")
    sections = split_into_sections(raw_text)
    print(f"识别到 {len(sections)} 个逻辑节")
    
    type_counts = {}
    for st, _, _ in sections:
        type_counts[st] = type_counts.get(st, 0) + 1
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")
    
    print("\n初始化翻译器...")
    translator = GoogleTranslator(source='en', target='zh-CN')
    
    print("\n开始翻译...")
    translated_sections = []
    total_paras = 0
    translated_paras = 0
    
    for idx, (sec_type, page_num, content) in enumerate(sections):
        if sec_type == 'empty' or not content.strip():
            translated_sections.append((sec_type, page_num, content))
            continue
        
        preview = content[:80].replace('\n', ' ')
        print(f"\n  [{idx+1}/{len(sections)}] 第{page_num}页 ({sec_type}): {preview}...")
        
        if is_mostly_math(content):
            print(f"    主要是数学符号，跳过翻译")
            translated_sections.append((sec_type, page_num, content))
            continue
        
        paragraphs = split_paragraphs(content)
        if not paragraphs:
            translated_sections.append((sec_type, page_num, content))
            continue
        
        total_paras += len(paragraphs)
        
        if len(content) < 200:
            translated = translate_chunk(content, translator)
            translated_sections.append((sec_type, page_num, translated))
            translated_paras += len(paragraphs)
            print(f"    ✓ 完成")
        else:
            chunks = chunk_for_translation(paragraphs)
            translated_chunks = []
            
            for ci, chunk in enumerate(chunks):
                sys.stdout.write(f"    翻译块 {ci+1}/{len(chunks)} ({len(chunk)}字符)... ")
                sys.stdout.flush()
                result = translate_chunk(chunk, translator)
                translated_chunks.append(result)
                translated_paras += 1
                print("✓")
                if ci < len(chunks) - 1:
                    time.sleep(DELAY_BETWEEN)
            
            translated_content = '\n\n'.join(translated_chunks)
            translated_sections.append((sec_type, page_num, translated_content))
            print(f"    ✓ 完成")
        
        time.sleep(DELAY_BETWEEN * 0.5)
    
    print(f"\n{'='*70}")
    print(f"翻译统计: {translated_paras}/{total_paras} 段落")
    print(f"\n生成 LaTeX 文档...")
    
    latex_content = build_latex_document(translated_sections)
    
    with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    file_size = os.path.getsize(OUTPUT_TEX)
    print(f"输出文件: {OUTPUT_TEX}")
    print(f"文件大小: {file_size:,} 字节")
    print(f"字符数: {len(latex_content):,}")
    print(f"\n使用 XeLaTeX 编译: xelatex {os.path.basename(OUTPUT_TEX)}")

if __name__ == '__main__':
    main()
