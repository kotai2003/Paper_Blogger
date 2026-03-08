# Paper Blogger - Inno Setup Installer

## 概要

PyInstaller でビルドした Paper Blogger を Windows インストーラー (setup.exe) として配布するための Inno Setup スクリプトです。

## 前提条件

1. **Inno Setup 6** をインストール
   - https://jrsoftware.org/isdl.php
2. **PyInstaller ビルド済み**であること
   - `pyinstaller/build.bat` または `pyinstaller/secure_build.bat` を先に実行
   - ビルド出力: `%LOCALAPPDATA%\paper_blogger_build\dist\paper_blogger\`

## ビルド手順

```bash
cd inno_setup
build_installer.bat
```

出力先: `inno_setup/output/setup_paper_blogger.exe`

## インストーラー仕様

| 項目 | 内容 |
|------|------|
| インストール先 | `C:\Program Files\Paper Blogger` |
| デスクトップショートカット | あり (オプション) |
| スタートメニュー | Paper Blogger + アンインストール |
| アンインストール | Windows 設定 > アプリから削除可能 |
| 言語 | 日本語 / English |
| 圧縮 | LZMA2 + Solid |
| 完了時 | アプリ起動チェックボックス |

## インストーラー画面フロー

```
1. Welcome        - ようこそ画面
2. License        - ライセンス表示 (README.md)
3. Install Location - インストール先選択
4. Additional Tasks - デスクトップショートカット作成
5. Installing     - インストール進行
6. Finish         - 完了 (アプリ起動オプション)
```

## インストール後の構造

```
C:\Program Files\Paper Blogger\
  paper_blogger.exe
  _internal/
  assets/
    favicon.ico
    icons/
  paper_blog_pipeline/
    config.yaml
    prompts/
    ...
```

## スタートメニュー

```
Paper Blogger
  ├── Paper Blogger        (アプリ起動)
  └── Uninstall Paper Blogger  (アンインストール)
```

## カスタマイズ

### Wizard画像を追加する (商用ソフト風)

1. 左パネル画像: 164x314 px の BMP を用意 → `wizard_image.bmp`
2. 右上ロゴ: 55x55 px の BMP を用意 → `wizard_small_image.bmp`
3. `paper_blogger_installer.iss` のコメントを解除:

```ini
WizardImageFile=wizard_image.bmp
WizardSmallImageFile=wizard_small_image.bmp
```

### バージョン更新

`paper_blogger_installer.iss` の `#define MyAppVersion` を変更:

```ini
#define MyAppVersion "1.1.0"
```

## ファイル構成

```
inno_setup/
  paper_blogger_installer.iss   # Inno Setup スクリプト
  build_installer.bat           # ビルドスクリプト
  README.md                     # このファイル
  output/                       # ビルド出力 (自動作成)
    setup_paper_blogger.exe
```

## ビルドフロー全体

```
pyinstaller/build.bat (or secure_build.bat)
  → %LOCALAPPDATA%\paper_blogger_build\dist\paper_blogger\
    → inno_setup/build_installer.bat
      → inno_setup/output/setup_paper_blogger.exe
```

## ISS スクリプト主要設定

| 設定 | 値 |
|------|-----|
| `AppId` | `{A7E3F8B2-4D1C-4A5E-9B7F-2C8D6E0F1A3B}` |
| `DefaultDirName` | `{autopf}\Paper Blogger` |
| `Compression` | `lzma2` + `SolidCompression=yes` |
| `WizardStyle` | `modern` |
| `PrivilegesRequired` | `admin` |
| `ArchitecturesAllowed` | `x64compatible` |
| `MinVersion` | `10.0` (Windows 10+) |

## 注意事項

- Ollama はインストーラーに含まれません。別途インストールが必要です
- `config.yaml` はインストール先にコピーされ、ユーザーが編集可能です
- アンインストール時はインストールフォルダ全体が削除されます
- Inno Setup 6.4.x では `ArchitecturesInstallMode` は未サポート — `ArchitecturesAllowed` のみ使用
- `[Tasks]` の `Flags: checked` は未サポート — タスクはデフォルトでチェック済み
