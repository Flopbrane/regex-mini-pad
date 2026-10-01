from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QHideEvent
from PySide6.QtWidgets import (
    QApplication,
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
    dismissed = Signal()

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
        self.copy_button = QPushButton(self)
        self.refresh_button = QPushButton(self)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, self)
        self.button_box.addButton(
            self.copy_button,
            QDialogButtonBox.ButtonRole.ActionRole,
        )
        self.button_box.addButton(
            self.refresh_button,
            QDialogButtonBox.ButtonRole.ActionRole,
        )
        self._copy_text = ""

        layout = QVBoxLayout()
        layout.addWidget(self.summary_label)
        layout.addWidget(self.message_list, 1)
        layout.addWidget(self.button_box)
        self.setLayout(layout)
        self.resize(930, 360)

        self.message_list.itemActivated.connect(self._emit_line_selected)
        self.message_list.itemClicked.connect(self._emit_line_selected)
        self.copy_button.clicked.connect(self.copy_results_to_clipboard)
        self.refresh_button.clicked.connect(self.refresh_requested.emit)
        self.button_box.rejected.connect(self.hide)
        self.apply_language()

    def apply_language(self) -> None:
        self.setWindowTitle(self.translator.text("grammar_check.title"))
        self.copy_button.setText(self.translator.text("grammar_check.copy_results"))
        self.refresh_button.setText(self.translator.text("grammar_check.refresh"))

    def set_result(
        self,
        summary: str,
        rows: list[tuple[int, str]],
    ) -> None:
        self.summary_label.setText(summary)
        self.message_list.clear()
        row_texts: list[str] = []
        for line_number, message_text in rows:
            row_text = self.translator.text(
                "grammar_check.issue_row",
                line=line_number,
                message=message_text,
            )
            row_texts.append(row_text)
            item = QListWidgetItem(row_text)
            item.setData(Qt.ItemDataRole.UserRole, line_number)
            self.message_list.addItem(item)
        self._copy_text = "\n".join(row_texts)
        self.copy_button.setEnabled(bool(row_texts))

    def copy_results_to_clipboard(self) -> None:
        if not self._copy_text:
            return
        QApplication.clipboard().setText(self._copy_text)

    def _emit_line_selected(self, item: QListWidgetItem) -> None:
        line_number = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(line_number, int):
            self.line_selected.emit(line_number)

    def hideEvent(self, event: QHideEvent) -> None:
        super().hideEvent(event)
        self.dismissed.emit()
