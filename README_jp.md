# ミニエディター

ミニエディターは、Windows 11向けの軽量なポータブルテキストエディターです。

インストーラー、管理者権限、レジストリ変更、オンラインサービスを使わず、フォルダ一つで動かせることを目標にしています。

## 目的

- フォルダ単位で持ち運べる実行形式。
- 設定はローカルファイルに保存。
- Python 3.12。
- GUIはPySide6。
- 正規表現検索・置換を重視。
- 日本語と英語のUI表示。
- 日本語と英語の正規表現ヘルプ。

## 現在の機能

- 新規作成、開く、保存、名前を付けて保存、終了。
- 文字コードを指定して開く。
- 読み直し、文字コードを指定して読み直し。
- 保存時の文字コード選択。
- 元に戻す、やり直し、すべて選択。
- 行番号表示。
- 右端で折り返し。
- 検索 / 置換ダイアログ。
- 正規表現検索・置換。
- 大文字と小文字を区別する検索。
- 単語全体に一致する検索。
- 選択範囲内だけの検索。
- 正規表現の挿入ポップアップ。
- 正規表現の警告表示。
- 実例と置換例つきの正規表現ヘルプ。
- HTML、Markdown、WordPress HTML向けのタグ挿入補助。
- WordPress向けの段落分割とスニペット挿入補助。
- HTML / WordPressブロック向けの文法チェック。
- 文法チェック結果一覧のコピー。
- 保存前のHTML / WordPress typoチェック。

## HTML / WordPress 文法チェック

文法チェックは、貼り付け前・保存前の事故を減らすための軽量linterです。
ブラウザやWordPress本体と同じ完全なパーサではありませんが、記事HTMLを壊しやすい典型的なミスを見つけることを目的にしています。

- 未登録のHTMLタグや、HTML属性のtypo候補を検出します。
- 未登録のWordPressコアブロック名を検出します。
- WordPressブロックコメント内の `{}` パラメータがJSONとして読めない場合に警告します。
- 代表的なWordPressコアブロックについて、想定外の `{}` パラメータを警告します。
- WordPressブロックの開始・終了の不一致、終了コメント抜け、`wp:list-item` などの閉じ忘れを検出します。
- WordPressブロック内でHTMLタグが完結しているかを確認します。
- WordPressブロックコメントを使っていない純粋なHTMLファイルでは、ファイル全体をHTML構造として確認します。
- `</div>` 抜け、閉じ順の逆転、`</p>` 前のインラインタグ閉じ忘れなどを検出します。
- separatorブロックに不要な `<code>` が混入した場合など、原因が同じ連鎖エラーは代表的な警告に抑えます。
- `<code>...</code>` 内のエスケープ済みコード例は、表示用テキストとして扱えるように過剰検出を避けます。

## タグスニペット

- タグ候補は `dictionaries/html_dict.json`、`dictionaries/markdown_dict.json`、
  `dictionaries/wordpress_html_dict.json` に候補を分けて管理。
- 右クリックメニューからタグやスニペットを選び、カーソル位置へ挿入。
- HTML、Markdown、WordPress HTMLの記事作成向けスニペットを挿入できます。
- WordPress向けスニペットは、記事ブロックの境界を壊さないよう保守的に扱います。

## 今後の方針

- 日本語Typoや表記ゆれチェックは、辞書と設定切替を準備した後に追加予定です。
- 実例を集めながら、WordPressブロックの `{}` パラメータ許可リストを保守的に広げます。

## 対応文字コード

- UTF-8
- UTF-8 with BOM
- CP932 / Shift_JIS
- Shift_JIS
- EUC-JP
- UTF-16
- UTF-16 LE
- UTF-16 BE

指定した文字コードで開いた、または読み直したファイルは、その文字コードを維持して保存します。

## 起動方法

プロジェクト指定の仮想環境を使います。

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" main.py
```

## 検証方法

```powershell
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m ruff check .
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pyright
"D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe" -m pytest
```

## フォルダ構成

```text
mini_editor_project/
├─ main.py
├─ dialogs/
├─ editor/
├─ fileio/
├─ localization/
├─ resources/
├─ search/
├─ settings/
└─ tests/
```

## 注意

正規表現エンジンには、Python標準ライブラリの `re` を使います。

検索だけでは本文を変更しません。本文が変更されるのは、ユーザーが置換またはすべて置換を実行した時だけです。

正しくない正規表現はエラーとして表示し、本文は変更しません。
