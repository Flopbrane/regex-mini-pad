from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from editor.ruler import Ruler
from editor.text_editor import TextEditor


class EditorTab(QWidget):
    def __init__(self, editor: TextEditor, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editor = editor
        self.ruler = Ruler(self)
        self.ruler.set_editor(editor)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.ruler)
        layout.addWidget(editor)
        self.setLayout(layout)

    def set_ruler_visible(self, visible: bool) -> None:
        self.ruler.setVisible(visible)
