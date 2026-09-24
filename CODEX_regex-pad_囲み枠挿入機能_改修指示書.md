# CODEX 指示書：regex-pad 囲み枠挿入機能の改修

作成日: 2026-09-24

対象プロジェクト: `D:/PC/Python/regex_pad_project`

対象機能: regex-pad の「囲み枠」挿入機能

## 目的

regex-pad に登録済みの「囲み枠」挿入機能を、WordPress の Gutenberg ブロックで壊れにくい形式に整える。

特に、装飾付きの囲み枠は `wp:group` や `wp:paragraph` の混在ではなく、原則として 1 個の `wp:html` ブロックとして挿入する。

## 背景

WordPress では、次のような構造がエラーやブロック破損の原因になりやすい。

- `wp:html` の中に `<!-- wp:paragraph -->` などの Gutenberg ブロックコメントを入れる
- `wp:paragraph` の中に `<div>` を入れる
- `wp:paragraph` の中に `<p>...</p>` が無い
- `wp:html` の閉じコメント `<!-- /wp:html -->` を忘れる
- 装飾枠を `wp:group` とインライン style で表現して、WordPress 側で無効ブロックになる

そのため、囲み枠の挿入機能は「WordPress 貼り付け前の安全な定型文」として動作させる。

## 基本方針

囲み枠は、次の形で挿入する。

```html
<!-- wp:html -->
<div style="border: 2px solid #8bc34a; background-color: #f7fff2; padding: 14px 16px; border-radius: 8px;">
ここに本文を入れます。
</div>
<!-- /wp:html -->
```

重要:

- `wp:html` ブロック全体で 1 つの囲み枠にする
- `wp:html` の内側には Gutenberg ブロックコメントを入れない
- `div` の中には通常の HTML だけを入れる
- 段落を分けたい場合は `<br><br>` を使う
- 箇条書きを入れたい場合は、事業所 WordPress の CSS 事情を考慮し、必要に応じて `・` や `1.` を本文として書く

## 挿入テンプレート

まずは、以下のテンプレートを登録する。

### 通常の囲み枠

用途: 補足、まとめ、注意しすぎないメモ

```html
<!-- wp:html -->
<div style="border: 2px solid #8bc34a; background-color: #f7fff2; padding: 14px 16px; border-radius: 8px;">
$selected_text
</div>
<!-- /wp:html -->
```

### やさしい注意枠

用途: 読者に少し気をつけてほしい内容

```html
<!-- wp:html -->
<div style="border: 2px solid #f0b84a; background-color: #fffaf0; padding: 14px 16px; border-radius: 8px;">
$selected_text
</div>
<!-- /wp:html -->
```

### 重要ポイント枠

用途: 記事の要点、結論、覚えておく内容

```html
<!-- wp:html -->
<div style="border: 2px solid #5aa7d8; background-color: #f0f9ff; padding: 14px 16px; border-radius: 8px;">
$selected_text
</div>
<!-- /wp:html -->
```

### 小見出し風の1行枠

用途: `h3` を使いたくない記事で、本文中の区切りを少し目立たせる

```html
<!-- wp:html -->
<div style="background-color: #eef8f2; padding: 10px 12px; border-left: 4px solid #6abf8f; font-weight: bold;">
$selected_text
</div>
<!-- /wp:html -->
```

## `$selected_text` の扱い

囲み枠挿入時は、選択文字列がある場合と無い場合で動作を分ける。

### 選択文字列がある場合

選択中の本文を `$selected_text` に差し込む。

例:

```text
朝ごはんを少し食べるだけでも、気持ちが安定しやすくなることがあります。
```

挿入後:

```html
<!-- wp:html -->
<div style="border: 2px solid #8bc34a; background-color: #f7fff2; padding: 14px 16px; border-radius: 8px;">
朝ごはんを少し食べるだけでも、気持ちが安定しやすくなることがあります。
</div>
<!-- /wp:html -->
```

### 選択文字列がない場合

次の仮文を入れる。

```text
ここに本文を入れます。
```

## 改行ルール

囲み枠内で段落を分けたい場合は、Gutenberg ブロックを入れずに `<br><br>` を使う。

例:

```html
<!-- wp:html -->
<div style="border: 2px solid #8bc34a; background-color: #f7fff2; padding: 14px 16px; border-radius: 8px;">
朝ごはんを少し食べるだけでも、<br><br>
気持ちが安定しやすくなることがあります。
</div>
<!-- /wp:html -->
```

スマホ表示を考慮する場合、長い一文は 18〜22 文字前後を目安に、意味の切れ目で `<br><br>` を入れる。

囲み枠内は横幅が少し狭くなるため、16〜20 文字前後を目安にする。

## 箇条書きルール

事業所 WordPress では、リストのマーカーが CSS で消える可能性がある。

そのため、囲み枠内の箇条書きは、まず次の形式を優先する。

```html
<!-- wp:html -->
<div style="border: 2px solid #8bc34a; background-color: #f7fff2; padding: 14px 16px; border-radius: 8px;">
・朝ごはんを軽く食べる<br><br>
・水分をとる<br><br>
・眠る前にスマホを見すぎない
</div>
<!-- /wp:html -->
```

`<ul>` / `<ol>` を使うテンプレートを追加する場合も、`wp:html` の中だけで完結させる。

## 小見出しの扱い

PC関連記事では `h3` を使ってもよい。

ただし、生活系・支援系・やわらかい記事では、`h3` の装飾が強すぎる場合がある。

その場合は、次の段落型または小見出し風の1行枠を使う。

### 段落型

```html
<!-- wp:paragraph -->
<p><span style="font-size: 1.08em; font-weight: bold;">$selected_text</span></p>
<!-- /wp:paragraph -->
```

### 1行枠型

```html
<!-- wp:html -->
<div style="background-color: #eef8f2; padding: 10px 12px; border-left: 4px solid #6abf8f; font-weight: bold;">
$selected_text
</div>
<!-- /wp:html -->
```

## 正規表現置換との関係

regex-pad では、正規表現置換時に `$1`, `$2`, `${name}` を使えるようにする。

内部では Python の `re.sub()` 用に変換してよい。

仕様:

```text
$1       -> \g<1>
$2       -> \g<2>
${name}  -> \g<name>
$$1      -> 文字としての $1
```

囲み枠テンプレート内の `$selected_text` は、正規表現の `$1` とは別扱いにする。

実装上は、テンプレート挿入処理で `$selected_text` を先に展開し、正規表現置換処理には渡さない。

## lint に追加したいチェック

囲み枠挿入機能と合わせて、文法チェックで次を警告する。

### 高優先度

- `<!-- wp:html -->` があるのに `<!-- /wp:html -->` が無い
- `wp:html` の中に `<!-- wp:` が含まれている
- `wp:paragraph` の中に `<div>` が含まれている
- `wp:paragraph` の中に `<p>` が無い
- `wp:paragraph` の中に `</p>` が無い

### 中優先度

- `<p>` の中に `<p>` が入っている
- `<br><br><br>` のように、過剰な連続改行がある
- `wp:list` と `<ul>` / `<ol>` の対応が崩れている

## 警告メッセージ例

### `wp:html` の閉じ忘れ

```text
wp:html ブロックの終了コメントがありません。この後ろの本文が HTML ブロック扱いになる可能性があります。
```

### `wp:html` 内の Gutenberg ブロックコメント

```text
wp:html ブロックの中に WordPress ブロックコメントがあります。カスタムHTML内では通常のHTMLだけにしてください。
```

### `wp:paragraph` 内の `<div>`

```text
wp:paragraph ブロックの中に div タグがあります。div を使う場合は wp:html ブロックに分けてください。
```

### `<p>` 抜け

```text
wp:paragraph ブロック内に p タグが見つかりません。<p>...</p> で囲んでください。
```

## テストケース

最低限、次のテストを追加する。

### 囲み枠テンプレート挿入

- 選択文字列ありで、囲み枠内に本文が入る
- 選択文字列なしで、仮文が入る
- 挿入結果に `<!-- wp:html -->` と `<!-- /wp:html -->` が両方ある
- 挿入結果の `wp:html` 内に `<!-- wp:paragraph -->` が入らない

### lint

- `wp:html` 閉じ忘れを警告する
- `wp:html` 内の `<!-- wp:paragraph -->` を警告する
- `wp:paragraph` 内の `<div>` を警告する
- `wp:paragraph` の `<p>` 抜けを警告する
- `wp:paragraph` の `</p>` 抜けを警告する

### 正規表現置換

- `$1` が 1 番目のキャプチャに置換される
- `${name}` が名前付きキャプチャに置換される
- `$$1` は文字として `$1` を出す
- 存在しない `$2` は lint で警告する

## 実装時の注意

- 既存の typo lint を壊さない
- 日本語と英語のメッセージリソースを両方追加する
- PySide6 の入力欄ハイライトがある場合、正規表現ONの時だけ有効にする
- 囲み枠テンプレートの挿入は、通常文書編集として扱う
- Gutenberg ブロックコメントの整合性チェックは、通常の HTML タグ typo チェックとは別の層として扱う

## 完了条件

次を満たしたら完了とする。

```text
pytest: all passed
ruff: All checks passed
pyright: 0 errors
JSON validation: app_text_ja.json OK, app_text_en.json OK
```

さらに、手動確認として regex-pad を起動し、次を確認する。

1. テキストを選択して囲み枠を挿入できる
2. 未選択状態でも囲み枠を挿入できる
3. 挿入結果を WordPress に貼っても無効ブロックにならない
4. `wp:html` の閉じ忘れを文法チェックで警告できる
5. `wp:html` 内に `wp:paragraph` を混ぜた場合に警告できる

## Codex への依頼文例

```text
regex-pad の囲み枠挿入機能を、添付の指示書に沿って改修してください。

方針は、装飾付き囲み枠を 1 個の wp:html ブロックとして挿入することです。
wp:html の中に wp:paragraph などの Gutenberg ブロックコメントを入れないでください。

選択文字列がある場合は、その文字列を囲み枠内に入れてください。
選択文字列がない場合は、「ここに本文を入れます。」を入れてください。

あわせて、wp:html の閉じ忘れ、wp:html 内の Gutenberg ブロックコメント混入、wp:paragraph 内の div 混入を lint で警告できるようにしてください。

既存テストを壊さず、pytest / ruff / pyright / JSON validation まで確認してください。
```

