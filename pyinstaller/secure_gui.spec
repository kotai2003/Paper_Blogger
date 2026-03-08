# -*- mode: python ; coding: utf-8 -*-
"""
Paper Blogger - Secure PyInstaller spec file
Cython .pyd + optimize=2 + UPX
"""

import os
import glob

# プロジェクトルート
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, '..'))
PIPELINE_DIR = os.path.join(PROJECT_ROOT, 'paper_blog_pipeline')

# --- Cython .pyd ファイルを自動収集 ---
def collect_pyd_files(base_dir, dest_prefix=''):
    """指定ディレクトリ内の .pyd ファイルを datas 用タプルで返す"""
    results = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.pyd'):
                src = os.path.join(root, f)
                rel = os.path.relpath(root, PROJECT_ROOT)
                results.append((src, rel))
    return results

pyd_datas = []
for d in ['app', 'gui', 'widgets', 'style', 'paper_blog_pipeline']:
    pyd_datas.extend(collect_pyd_files(os.path.join(PROJECT_ROOT, d)))

a = Analysis(
    [os.path.join(PROJECT_ROOT, 'main_gui.py')],
    pathex=[
        PROJECT_ROOT,
        PIPELINE_DIR,
    ],
    binaries=pyd_datas,  # .pyd はバイナリとして追加
    datas=[
        # assets
        (os.path.join(PROJECT_ROOT, 'assets', 'favicon.ico'), 'assets'),
        (os.path.join(PROJECT_ROOT, 'assets', 'icons'), os.path.join('assets', 'icons')),
        # prompts
        (os.path.join(PIPELINE_DIR, 'prompts'), os.path.join('paper_blog_pipeline', 'prompts')),
        # config
        (os.path.join(PIPELINE_DIR, 'config.yaml'), 'paper_blog_pipeline'),
        # __init__.py（パッケージ構造維持に必要）
        (os.path.join(PROJECT_ROOT, 'app', '__init__.py'), 'app'),
        (os.path.join(PROJECT_ROOT, 'gui', '__init__.py'), 'gui'),
        (os.path.join(PROJECT_ROOT, 'gui', 'tabs', '__init__.py'), os.path.join('gui', 'tabs')),
        (os.path.join(PROJECT_ROOT, 'widgets', '__init__.py'), 'widgets'),
        (os.path.join(PROJECT_ROOT, 'style', '__init__.py'), 'style'),
        (os.path.join(PIPELINE_DIR, '__init__.py'), 'paper_blog_pipeline') if os.path.exists(os.path.join(PIPELINE_DIR, '__init__.py')) else (os.path.join(PIPELINE_DIR, 'config.yaml'), 'paper_blog_pipeline'),
        (os.path.join(PIPELINE_DIR, 'parser', '__init__.py'), os.path.join('paper_blog_pipeline', 'parser')),
        (os.path.join(PIPELINE_DIR, 'figures', '__init__.py'), os.path.join('paper_blog_pipeline', 'figures')),
        (os.path.join(PIPELINE_DIR, 'llm', '__init__.py'), os.path.join('paper_blog_pipeline', 'llm')),
        (os.path.join(PIPELINE_DIR, 'vlm', '__init__.py'), os.path.join('paper_blog_pipeline', 'vlm')),
        (os.path.join(PIPELINE_DIR, 'slide', '__init__.py'), os.path.join('paper_blog_pipeline', 'slide')),
    ],
    hiddenimports=[
        'yaml',
        'openai',
        'fitz',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        # pipeline サブモジュール（Cython .pyd 版）
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
        # GUI モジュール（Cython .pyd 版）
        'app.controller',
        'gui.main_window',
        'gui.left_panel',
        'gui.right_panel',
        'gui.toolbar',
        'gui.menu_bar',
        'gui.status_bar',
        'gui.tabs.tab_summary',
        'gui.tabs.tab_markdown',
        'gui.tabs.tab_figures',
        'widgets.file_selector',
        'widgets.log_console',
        'widgets.markdown_viewer',
        'widgets.image_viewer',
        'style.theme',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # ML/科学計算
        'matplotlib', 'matplotlib.pyplot', 'scipy', 'numpy.testing',
        'pandas', 'torch', 'torchvision', 'tensorflow', 'keras',
        'sklearn', 'scikit-learn',
        # Jupyter
        'notebook', 'jupyter', 'jupyter_client', 'jupyter_core',
        'IPython', 'ipykernel', 'ipywidgets', 'nbconvert', 'nbformat',
        # テスト・開発ツール
        'pytest', 'unittest', 'doctest',
        'setuptools', 'distutils', 'pip', 'wheel', 'pkg_resources',
        # 不要な標準ライブラリ
        'xmlrpc', 'pydoc', 'pydoc_data', 'lib2to3',
        'ensurepip', 'venv', 'turtledemo', 'test', 'idlelib',
        'multiprocessing',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    optimize=2,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
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
