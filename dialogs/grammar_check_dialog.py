from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from localization.translator import Translator


class GrammarCheckDialog(QDialog):
    line_selected = Signal(int)
    refresh_requested = Signal()

    def __init__(
        self,
        translator: Translator,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.translator = translator
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)

        self.summary_label = QLabel(self)
        self.summary_label.setWordWrap(True)
        self.message_list = QListWidget(self)
        self.refresh_button = QPushButton(self)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        self.button_box.addButton(
            self.refresh_button,
            QDialogButtonBox.ButtonRole.ActionRole,
        )

        layout = QVBoxLayout()
        layout.addWidget(self.summary_label)
        layout.addWidget(self.message_list, 1)
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        self.resize(620, 360)

        self.message_list.itemActivated.connect(self._emit_line_selected)
        self.message_list.itemClicked.connect(self._emit_line_selected)
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        self.button_box.rejected.connect(self.hide)
        self.apply_language()

    def apply_language(self) -> None:
        self.setWindowTitle(self.translator.text("grammar_check.title"))
        self.refresh_button.setText(self.translator.text("grammar_check.refresh"))

    def set_result(
        self,
        summary: str,
        rows: list[tuple[int, str]],
    ) -> None:
        self.summary_label.setText(summary)
        self.message_list.clear()
        for line_number, message_text in rows:
            item = QListWidgetItem(
                self.translator.text(
                    "grammar_check.issue_row",
                    line=line_number,
                    message=message_text,
                )
            )
            item.setData(Qt.ItemDataRole.UserRole, line_number)
            self.message_list.addItem(item)

    def _emit_line_selected(self, item: QListWidgetItem) -> None:
        line_number = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(line_number, int):
            self.line_selected.emit(line_number)
