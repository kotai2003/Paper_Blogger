# -*- coding: utf-8 -*-
"""
Cython コンパイラ - .py を .pyd (Windows) にコンパイル

リバースエンジニアリング対策:
  .py → C言語 → .pyd (ネイティブバイナリ)
  逆コンパイルはほぼ不可能

Usage:
  python build_tools/setup_cython.py build_ext --inplace
"""

import os
import sys
import shutil
from pathlib import Path
from setuptools import setup, find_packages
from Cython.Build import cythonize
from Cython.Compiler import Options

# Cython 最適化オプション
Options.docstrings = False      # docstring 削除
Options.embed_pos_in_docstring = False
Options.annotate = False        # 注釈HTML生成しない

# プロジェクトルート
PROJECT_ROOT = Path(__file__).parent.parent

# コンパイル対象ディレクトリ
TARGET_DIRS = [
    'app',
    'gui',
    'gui/tabs',
    'widgets',
    'style',
    'paper_blog_pipeline',
    'paper_blog_pipeline/parser',
    'paper_blog_pipeline/figures',
    'paper_blog_pipeline/llm',
    'paper_blog_pipeline/vlm',
    'paper_blog_pipeline/slide',
]

# コンパイルしないファイル（エントリーポイント等）
EXCLUDE_FILES = {
    'main_gui.py',
    'paper_blog_pipeline/main.py',
}


def collect_py_files():
    """コンパイル対象の .py ファイルを収集"""
    py_files = []
    for dir_path in TARGET_DIRS:
        full_dir = PROJECT_ROOT / dir_path
        if not full_dir.exists():
            print(f"  [SKIP] {dir_path} (not found)")
            continue
        for py_file in full_dir.glob('*.py'):
            if py_file.name == '__init__.py':
                continue  # __init__.py はそのまま残す
            rel_path = str(py_file.relative_to(PROJECT_ROOT))
            rel_path_posix = rel_path.replace('\\', '/')
            if rel_path_posix in EXCLUDE_FILES:
                print(f"  [SKIP] {rel_path_posix} (excluded)")
                continue
            py_files.append(str(py_file))
            print(f"  [ADD]  {rel_path_posix}")
    return py_files


def clean_artifacts():
    """コンパイル後の .c ファイルを削除"""
    print("\n--- .c ファイルのクリーンアップ ---")
    for dir_path in TARGET_DIRS:
        full_dir = PROJECT_ROOT / dir_path
        if not full_dir.exists():
            continue
        for c_file in full_dir.glob('*.c'):
            c_file.unlink()
            print(f"  [DEL] {c_file.relative_to(PROJECT_ROOT)}")


if __name__ == '__main__':
    os.chdir(str(PROJECT_ROOT))

    print("=" * 50)
    print(" Cython Compiler - Anti Reverse Engineering")
    print("=" * 50)
    print(f"\nProject root: {PROJECT_ROOT}")
    print(f"\n--- コンパイル対象 ---")

    py_files = collect_py_files()

    if not py_files:
        print("\n[ERROR] コンパイル対象ファイルが見つかりません")
        sys.exit(1)

    print(f"\n合計: {len(py_files)} ファイル")
    print("\n--- Cython コンパイル開始 ---\n")

    setup(
        name='paper_blogger_compiled',
        ext_modules=cythonize(
            py_files,
            compiler_directives={
                'language_level': '3',
                'boundscheck': False,
                'wraparound': False,
                'cdivision': True,
                'always_allow_keywords': True,
            },
            nthreads=os.cpu_count() or 4,
            quiet=False,
        ),
        zip_safe=False,
    )

    clean_artifacts()

    print("\n" + "=" * 50)
    print(" コンパイル完了 - .pyd ファイルが生成されました")
    print("=" * 50)
