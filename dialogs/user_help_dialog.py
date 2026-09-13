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
