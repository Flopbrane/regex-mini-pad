from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QListWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from localization.translator import Translator

HELP_TOPICS = {
    "en": [
        (
            "File",
            """# File

- New: create a new document.
- Open: open a text file.
- Open with Encoding: open a file with a selected character encoding.
- Reload: reload the current file.
- Save / Save As: save the current text.
- Unsaved text is backed up locally and can be restored on the next launch.
- New creates a new tab without discarding existing tabs.
- Right-click a tab to close it, duplicate it, or move it to a new window.
""",
        ),
        (
            "Edit",
            """# Edit

- Undo: Ctrl+Z.
- Redo: Ctrl+Y or Ctrl+Shift+Z.
- Select All: Ctrl+A.
""",
        ),
        (
            "Search / Replace",
            """# Search / Replace

- Find / Replace: Ctrl+F.
- Use Case-sensitive, Regular expression, Whole word, Search only selected text, or Search only visible text as needed.
- Preview shows replacement results before applying them.
- Regex Help opens examples and can insert a pattern into the Find field.
- Use the arrow buttons next to the Find text field to move to the previous or next match.
- Replace Marked replaces the currently highlighted search markers.
""",
        ),
        (
            "Tag Insertion",
            """# Tag Insertion

- Insert Tag: Ctrl+Shift+T.
- Type in the filter field to narrow candidates.
- Use Tab or arrow keys to move through candidates.
- Press Enter to insert the selected snippet.
- Selected text is wrapped when the snippet supports it.
- The first snippet group is prioritized by file extension: .md, .html, or .wp.html.

## WordPress HTML Modes

- Normal shows the broadest WordPress HTML snippet set for ordinary editing.
- Business / Office hides snippets that are likely to depend on custom HTML, complex image rows, or float-based layouts.
- Hi-security shows only the stricter snippet set intended for safer standard WordPress blocks.
- Stricter modes hide risky snippets instead of merely moving them lower in the menu. This keeps accidental insertion less likely.
""",
        ),
        (
            "HTML Attribute Guide",
            """# HTML Attribute Guide

Use this topic as a small reference for tag hover hints and tag snippets.

## Common Attributes

| Attribute | Where it is used | Example | Notes |
| --- | --- | --- | --- |
| `href` | Links such as `<a>` | `href="https://www.example.com"` | Destination URL. Use `https://` for ordinary web links. |
| `src` | Images, video, audio | `src="images/photo.jpg"` | File path or URL to the media. The file must exist or the browser cannot show it. |
| `alt` | Images | `alt="Product photo"` | Alternative text for users who cannot see the image. Also useful when the image fails to load. |
| `class` | Most HTML tags | `class="note-box"` | A class does not change appearance by itself. It needs matching CSS such as `.note-box { ... }`. |
| `id` | Most HTML tags | `id="section-1"` | Should be unique on the page. Useful for links like `#section-1` and CSS selectors. |
| `style` | Most HTML tags | `style="color: red;"` | Inline CSS. Works without a separate CSS file, but can become hard to maintain. |
| `target` | Links | `target="_blank"` | Opens the link in a new tab/window. |
| `rel` | Links | `rel="noopener noreferrer"` | Recommended with `target="_blank"` for safety. |
| `title` | Most HTML tags | `title="Supplemental note"` | Browser tooltip text. Do not rely on it for important content. |
| `data-*` | Most HTML tags | `data-role="warning"` | Custom data for scripts or CSS selectors. |

## Writing Examples

```html
<a href="https://www.example.com">Example site</a>
<a href="https://www.example.com" target="_blank" rel="noopener noreferrer">Open in a new tab</a>
<img src="images/photo.jpg" alt="Product photo">
<p class="lead-text">Opening paragraph</p>
<section id="overview">Overview</section>
```

## CSS Needed

`class` and many layout-oriented values do not work visually unless CSS exists.

```html
<p class="lead-text">Opening paragraph</p>
```

This needs CSS such as:

```css
.lead-text {
  font-size: 1.2em;
  font-weight: 600;
}
```

Without that CSS, `class="lead-text"` is only a label.

## Common `style` Properties

| CSS property | Example | Effect |
| --- | --- | --- |
| `color` | `color: #333;` | Text color. |
| `background-color` | `background-color: #fff3cd;` | Background color. |
| `font-size` | `font-size: 16px;` | Text size. |
| `font-weight` | `font-weight: bold;` | Text weight. |
| `text-align` | `text-align: center;` | Text alignment. |
| `line-height` | `line-height: 1.6;` | Line spacing. |
| `margin` | `margin: 1em 0;` | Outer spacing. |
| `padding` | `padding: 12px;` | Inner spacing. |
| `border` | `border: 1px solid #999;` | Border line. |
| `border-radius` | `border-radius: 4px;` | Rounded corners. |
| `display` | `display: inline-block;` | Display behavior. |
| `max-width` | `max-width: 100%;` | Maximum width. |

Inline style example:

```html
<p style="color: #333; background-color: #fff3cd; padding: 12px;">
  Important note
</p>
```

## Practical Notes

- Prefer `class` when the same design is used repeatedly.
- Prefer `style` only for one-off small adjustments.
- Always write meaningful `alt` text for images.
- Use `target="_blank"` together with `rel="noopener noreferrer"`.
- CSS class names are case-sensitive in practice. Keep them simple, such as `note-box` or `lead-text`.
""",
        ),
        (
            "WordPress Parameter Notes",
            """# WordPress Parameter Notes

WordPress block comments can contain JSON parameters.

```html
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Heading</h3>
<!-- /wp:heading -->
```

These values are WordPress block attributes. They are not ordinary HTML attributes.

## Basic Rule

- Some values are read from the block comment, such as `level` on `wp:heading`.
- Some values are read from the inner HTML, such as image `src` and `alt`.
- If the block comment and HTML describe the same meaning, keep them aligned.
- When they disagree, WordPress may rewrite the block, drop a value, or show a block validation warning.

## Safer Examples

Heading level and HTML tag match:

```html
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">Heading</h3>
<!-- /wp:heading -->
```

Spacer height and CSS height match:

```html
<!-- wp:spacer {"height":"32px"} -->
<div style="height:32px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->
```

Image size and class match:

```html
<!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="sample.jpg" alt="Description"/></figure>
<!-- /wp:image -->
```

## Risky Examples

Heading parameter says level 3, but HTML is h2:

```html
<!-- wp:heading {"level":3} -->
<h2 class="wp-block-heading">Heading</h2>
<!-- /wp:heading -->
```

Spacer parameter says 64px, but HTML says 32px:

```html
<!-- wp:spacer {"height":"64px"} -->
<div style="height:32px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->
```

Image parameter says large, but class says full:

```html
<!-- wp:image {"sizeSlug":"large","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="sample.jpg" alt="Description"/></figure>
<!-- /wp:image -->
```

## Practical Notes

- Use only attributes that the target core block actually supports.
- Do not invent parameter names in `{}`.
- Use double quotes in JSON: `{"height":"32px"}`.
- Avoid trailing commas in JSON.
- Copying HTML from Gutenberg after saving is the safest source for dictionary snippets.
- Custom HTML blocks are different: inside `wp:html`, use ordinary HTML and avoid nested WordPress block comments.
""",
        ),
        (
            "View",
            """# View

- Line Numbers: show or hide line numbers.
- Word Wrap: wrap long lines at the editor edge.
- The status bar shows the current line, column, and character count.
""",
        ),
        (
            "Language",
            """# Language

- Switch the application display language from the Language menu.
- Open help dialogs follow the current application language.
""",
        ),
    ],
    "ja": [
        (
            "ファイル",
            """# ファイル

- 新規: 新しい文書を作成します。
- 開く: テキストファイルを開きます。
- 文字コードを指定して開く: 文字コードを選んでファイルを開きます。
- 読み直し: 現在のファイルを読み直します。
- 保存 / 名前を付けて保存: 現在の本文を保存します。
- 未保存の本文はローカルにバックアップされ、次回起動時に復元できます。
- 新規は、既存のタブを破棄せずに新しいタブを作成します。
- タブを右クリックすると、閉じる、複製、新規ウィンドウへの移動ができます。
""",
        ),
        (
            "編集",
            """# 編集

- 元に戻す: Ctrl+Z。
- やり直し: Ctrl+Y または Ctrl+Shift+Z。
- すべて選択: Ctrl+A。
""",
        ),
        (
            "検索 / 置換",
            """# 検索 / 置換

- 検索 / 置換: Ctrl+F。
- 必要に応じて、大文字小文字、正規表現、単語全体、選択範囲内だけ、表示中の範囲だけを指定できます。
- プレビューで、置換結果を実行前に確認できます。
- 正規表現ヘルプから例を確認し、検索欄へパターンを挿入できます。
- 検索欄横の矢印ボタンで、前または次の一致箇所へ移動できます。
- マーカー部分を全て置換で、現在ハイライトされている検索マーカー部分だけを置換できます。
""",
        ),
        (
            "タグ挿入",
            """# タグ挿入

- タグ挿入: Ctrl+Shift+T。
- 絞り込み欄に入力すると候補を絞り込めます。
- Tab または上下キーで候補を移動できます。
- Enter で選択中のスニペットを挿入します。
- スニペットが対応している場合、選択中の文字列を囲みます。
- .md、.html、.wp.html では拡張子に応じた候補グループが先頭になります。

## WordPress HTML モード

- Normal は通常編集向けに、もっとも広い WordPress HTML スニペット候補を表示します。
- 企業・事業所は、独自HTML、複雑な画像横並び、float系レイアウトに依存しやすい候補を隠します。
- Hi-security は、安全寄りの標準 WordPress ブロックとして扱いやすい候補だけを表示します。
- 厳しいモードでは、危険になりやすい候補を下位表示するだけでなく、候補から隠します。誤挿入を減らすためです。
""",
        ),
        (
            "HTML属性図鑑",
            """# HTML属性図鑑

タグのホバーヒントやタグ挿入スニペットで出てくる属性の小さな図鑑です。

## よく使う属性

| 属性 | 主な使用場所 | 記述例 | 補足 |
| --- | --- | --- | --- |
| `href` | `<a>` などのリンク | `href="https://www.example.com"` | リンク先URLです。通常のWebリンクでは `https://` から書きます。 |
| `src` | 画像、動画、音声 | `src="images/photo.jpg"` | 表示・再生するファイルパスまたはURLです。ファイルが無いと表示できません。 |
| `alt` | 画像 | `alt="商品写真"` | 画像が見えない場合の代替テキストです。画像読み込み失敗時にも役立ちます。 |
| `class` | 多くのHTMLタグ | `class="note-box"` | class だけでは見た目は変わりません。別途 `.note-box { ... }` のようなCSSが必要です。 |
| `id` | 多くのHTMLタグ | `id="section-1"` | ページ内で一意にします。`#section-1` のリンクやCSS指定に使えます。 |
| `style` | 多くのHTMLタグ | `style="color: red;"` | タグへ直接書くCSSです。別CSSなしで効きますが、多用すると管理しづらくなります。 |
| `target` | リンク | `target="_blank"` | リンクを新しいタブまたはウィンドウで開きます。 |
| `rel` | リンク | `rel="noopener noreferrer"` | `target="_blank"` と一緒に使う安全対策です。 |
| `title` | 多くのHTMLタグ | `title="補足説明"` | ブラウザ上の簡単な補足表示です。重要な説明は本文に書く方が安全です。 |
| `data-*` | 多くのHTMLタグ | `data-role="warning"` | スクリプトやCSS用の独自データです。 |

## 記述方法

```html
<a href="https://www.example.com">サンプルサイト</a>
<a href="https://www.example.com" target="_blank" rel="noopener noreferrer">新しいタブで開く</a>
<img src="images/photo.jpg" alt="商品写真">
<p class="lead-text">導入文</p>
<section id="overview">概要</section>
```

## CSSファイルが必要なもの

`class` やレイアウト目的の指定は、対応するCSSがないと見た目には反映されません。

```html
<p class="lead-text">導入文</p>
```

この場合は、別途CSS側に次のような指定が必要です。

```css
.lead-text {
  font-size: 1.2em;
  font-weight: 600;
}
```

CSSが無い場合、`class="lead-text"` は名前を付けているだけで、文字サイズや太字にはなりません。

## `style` でよく使うCSSプロパティ

| CSSプロパティ | 記述例 | 効果 |
| --- | --- | --- |
| `color` | `color: #333;` | 文字色を変えます。 |
| `background-color` | `background-color: #fff3cd;` | 背景色を変えます。 |
| `font-size` | `font-size: 16px;` | 文字サイズを変えます。 |
| `font-weight` | `font-weight: bold;` | 文字の太さを変えます。 |
| `text-align` | `text-align: center;` | 文字揃えを変えます。 |
| `line-height` | `line-height: 1.6;` | 行間を変えます。 |
| `margin` | `margin: 1em 0;` | 外側の余白を付けます。 |
| `padding` | `padding: 12px;` | 内側の余白を付けます。 |
| `border` | `border: 1px solid #999;` | 枠線を付けます。 |
| `border-radius` | `border-radius: 4px;` | 角を少し丸めます。 |
| `display` | `display: inline-block;` | 表示形式を変えます。 |
| `max-width` | `max-width: 100%;` | 最大幅を指定します。 |

style の記述例:

```html
<p style="color: #333; background-color: #fff3cd; padding: 12px;">
  重要なお知らせ
</p>
```

## 実用メモ

- 同じ見た目を何度も使うなら `class` が向いています。
- その場限りの小さな調整なら `style` が使いやすいです。
- 画像には、内容が分かる `alt` を入れておくと安全です。
- `target="_blank"` を使う場合は、`rel="noopener noreferrer"` も一緒に入れるのがおすすめです。
- class 名は、`note-box` や `lead-text` のように短く分かりやすくすると管理しやすくなります。
""",
        ),
        (
            "WPパラメータ記述の注意事項",
            """# WPパラメータ記述の注意事項

WordPress のブロックコメントには、JSON形式のパラメータを書けます。

```html
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">見出し</h3>
<!-- /wp:heading -->
```

この `{}` は WordPress ブロックの属性です。通常のHTML属性とは別物です。

## 基本ルール

- `wp:heading` の `level` のように、ブロックコメント側から読む値があります。
- 画像の `src` や `alt` のように、内側のHTMLから読む値があります。
- ブロックコメント側とHTML側が同じ意味を表す場合は、必ず一致させます。
- 食い違うと、WordPress が再保存時に書き換えたり、値を落としたり、ブロック検証エラーを出すことがあります。

## 安全寄りの例

見出しレベルとHTMLタグが一致しています。

```html
<!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">見出し</h3>
<!-- /wp:heading -->
```

スペーサーの高さとCSSの高さが一致しています。

```html
<!-- wp:spacer {"height":"32px"} -->
<div style="height:32px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->
```

画像サイズ指定とclassが一致しています。

```html
<!-- wp:image {"sizeSlug":"full","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="sample.jpg" alt="説明"/></figure>
<!-- /wp:image -->
```

## 危険な例

パラメータは level 3 ですが、HTML は h2 です。

```html
<!-- wp:heading {"level":3} -->
<h2 class="wp-block-heading">見出し</h2>
<!-- /wp:heading -->
```

パラメータは 64px ですが、HTML側は 32px です。

```html
<!-- wp:spacer {"height":"64px"} -->
<div style="height:32px" aria-hidden="true" class="wp-block-spacer"></div>
<!-- /wp:spacer -->
```

パラメータは large ですが、class は full です。

```html
<!-- wp:image {"sizeSlug":"large","linkDestination":"none"} -->
<figure class="wp-block-image size-full"><img src="sample.jpg" alt="説明"/></figure>
<!-- /wp:image -->
```

## 実用メモ

- `{}` には、そのコアブロックが実際に対応している属性だけを書きます。
- 存在しないパラメータ名を作らないようにします。
- JSONなので、文字列はダブルクォートで書きます: `{"height":"32px"}`。
- 末尾カンマは入れないでください。
- 辞書スニペットは、Gutenbergで作成して保存した後のHTMLを基準にするのが安全です。
- `wp:html` は別扱いです。中には通常のHTMLを書き、WordPressブロックコメントを入れ子にしない方が安全です。
""",
        ),
        (
            "表示",
            """# 表示

- 行番号: 行番号の表示 / 非表示を切り替えます。
- 右端で折り返す: 長い行をエディター幅で折り返します。
- ステータスバーには、現在の行、列、文字数が表示されます。
""",
        ),
        (
            "言語",
            """# 言語

- 言語メニューから表示言語を切り替えられます。
- 開いているヘルプダイアログも、現在の表示言語に追従します。
""",
        ),
    ],
}


class UserHelpDialog(QDialog):
    def __init__(self, translator: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.translator = translator
        self.resize(820, 560)

        self.topic_list = QListWidget(self)
        self.topic_list.setMaximumWidth(180)
        self.help_browser = QTextBrowser(self)
        self.help_browser.setOpenExternalLinks(False)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close,
            self,
        )
        self.button_box.rejected.connect(self.close)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.topic_list)
        content_layout.addWidget(self.help_browser, 1)

        layout = QVBoxLayout()
        layout.addLayout(content_layout)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        self.topic_list.currentRowChanged.connect(self._show_topic)
        self.apply_language()

    def apply_language(self) -> None:
        self.setWindowTitle(self.translator.text("help.title"))
        self.button_box.button(QDialogButtonBox.StandardButton.Close).setText(
            self.translator.text("help.close")
        )
        current_row = max(self.topic_list.currentRow(), 0)
        self._load_topics()
        self.topic_list.setCurrentRow(min(current_row, self.topic_list.count() - 1))

    def _load_topics(self) -> None:
        self.topic_list.clear()
        language_code = "en" if self.translator.language_code == "en" else "ja"
        for title, _body in HELP_TOPICS[language_code]:
            self.topic_list.addItem(title)
        if self.topic_list.currentRow() < 0 and self.topic_list.count() > 0:
            self.topic_list.setCurrentRow(0)

    def _show_topic(self, row: int) -> None:
        if row < 0:
            self.help_browser.clear()
            return
        language_code = "en" if self.translator.language_code == "en" else "ja"
        topics = HELP_TOPICS[language_code]
        if row >= len(topics):
            return
        _title, body = topics[row]
        self.help_browser.setMarkdown(body)
