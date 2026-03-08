# -*- mode: python ; coding: utf-8 -*-
"""
Paper Blogger - PyInstaller spec file
--onedir モード（高速起動・軽量）
"""

import os
import sys

# プロジェクトルート（specファイルの親ディレクトリ）
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))

block_cipher = None

a = Analysis(
    [os.path.join(PROJECT_ROOT, 'main_gui.py')],
    pathex=[
        PROJECT_ROOT,
        os.path.join(PROJECT_ROOT, 'paper_blog_pipeline'),
    ],
    binaries=[],
    datas=[
        # assets（favicon, icons）
        (os.path.join(PROJECT_ROOT, 'assets', 'favicon.ico'), os.path.join('assets')),
        (os.path.join(PROJECT_ROOT, 'assets', 'icons'), os.path.join('assets', 'icons')),
        # LLM プロンプトテンプレート
        (os.path.join(PROJECT_ROOT, 'paper_blog_pipeline', 'prompts'), os.path.join('paper_blog_pipeline', 'prompts')),
        # 設定ファイル
        (os.path.join(PROJECT_ROOT, 'paper_blog_pipeline', 'config.yaml'), os.path.join('paper_blog_pipeline')),
    ],
    hiddenimports=[
        'yaml',
        'openai',
        'fitz',           # PyMuPDF
        'PIL',            # Pillow
        'PIL.Image',
        'PIL.ImageTk',
        # paper_blog_pipeline サブモジュール（sys.path.insert による動的インポート対応）
        'parser',
        'parser.pdf_parser',
        'figures',
        'figures.figure_extractor',
        'figures.figure_analyzer',
        'vlm',
        'vlm.vlm_interface',
        'llm',
        'llm.ollama_client',
        'llm.paper_analyzer',
        'llm.insight_generator',
        'llm.blog_generator',
        'slide',
        'slide.ochiai_summary',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 科学計算・ML（不要）
        'matplotlib',
        'matplotlib.pyplot',
        'scipy',
        'numpy.testing',
        'pandas',
        'torch',
        'torchvision',
        'tensorflow',
        'keras',
        'sklearn',
        'scikit-learn',
        # Jupyter / IPython（不要）
        'notebook',
        'jupyter',
        'jupyter_client',
        'jupyter_core',
        'IPython',
        'ipykernel',
        'ipywidgets',
        'nbconvert',
        'nbformat',
        # テスト関連
        'pytest',
        'unittest',
        'doctest',
        # その他不要
        'setuptools',
        'distutils',
        'pip',
        'wheel',
        'pkg_resources',
        'xmlrpc',
        'pydoc',
        'pydoc_data',
        'lib2to3',
        'ensurepip',
        'venv',
        'turtledemo',
        'test',
        'idlelib',
        'multiprocessing',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=2,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='paper_blogger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(PROJECT_ROOT, 'assets', 'favicon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='paper_blogger',
)
