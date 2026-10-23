from __future__ import annotations

import io
import json
import os
import threading
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from dialogs.grammar_check_dialog import GrammarCheckDialog
from localization.translator import Translator
from main import MainWindow
from preview import wordpress_runtime
from preview.wordpress_preview import WordPressPreview


@pytest.fixture(scope="session")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    return application


def test_cached_runtime_preparation_needs_no_network(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "ready.json").write_text(json.dumps({"playground": wordpress_runtime.PLAYGROUND_VERSION}))
    for relative in (
        "wordpress.zip", "sqlite.zip", "node_modules/@wp-playground/wordpress/index.js",
        "node_modules/@php-wasm/node-8-3/index.js",
    ):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"cached")
    node = tmp_path / "node.exe"
    monkeypatch.setattr(wordpress_runtime, "find_node", lambda root: node)
    monkeypatch.setattr(wordpress_runtime, "urlopen", lambda *args, **kwargs: pytest.fail("unexpected network"))
    assert wordpress_runtime.prepare_runtime(tmp_path, lambda stage: None, threading.Event()) == node


def test_incomplete_runtime_is_not_ready(tmp_path: Path) -> None:
    (tmp_path / "ready.json").write_text(json.dumps({"playground": wordpress_runtime.PLAYGROUND_VERSION}))
    assert not wordpress_runtime.runtime_ready(tmp_path)


def test_cancelled_download_preserves_previous_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    save_file_path = tmp_path / "wordpress.zip"
    save_file_path.write_bytes(b"original")
    cancel = threading.Event()

    class Response(io.BytesIO):
        def read(self, size: int | None = -1) -> bytes:
            cancel.set()
            return super().read(size)

    monkeypatch.setattr(wordpress_runtime, "urlopen", lambda *args, **kwargs: Response(b"incomplete"))
    with pytest.raises(wordpress_runtime.PreparationCancelled):
        wordpress_runtime._download("https://wordpress.org/latest.zip", save_file_path, cancel)
    assert save_file_path.read_bytes() == b"original"
    assert not save_file_path.with_suffix(".zip.partial").exists()


def test_cancelled_setup_does_not_start_install(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cancel = threading.Event()
    cancel.set()
    monkeypatch.setattr(wordpress_runtime, "find_node", lambda root: pytest.fail("should cancel first"))
    with pytest.raises(wordpress_runtime.PreparationCancelled):
        wordpress_runtime.prepare_runtime(tmp_path, lambda stage: None, cancel)
    assert not (tmp_path / "ready.json").exists()


@pytest.mark.parametrize("url", ["https://example.com/", "http://localhost:4321/", "http://127.0.0.1:4322/"])
def test_preview_rejects_foreign_or_wrong_port_url(
    app: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, url: str,
) -> None:
    preview = WordPressPreview(tmp_path, tmp_path / "bridge.mjs")
    preview.origin = "http://127.0.0.1:4321"
    preview.sequence = 1
    failures = []
    preview.failed.connect(failures.append)
    monkeypatch.setattr("preview.wordpress_preview.QDesktopServices.openUrl", lambda url: pytest.fail("opened foreign URL"))
    preview._handle_message({"event": "rendered", "id": 1, "url": url})
    assert len(failures) == 1


def test_preview_ignores_stale_results_and_opens_current_page(
    app: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    preview = WordPressPreview(tmp_path, tmp_path / "bridge.mjs")
    preview.origin = "http://127.0.0.1:4321"
    preview.sequence = 2
    opened = []
    failures = []
    monkeypatch.setattr("preview.wordpress_preview.QDesktopServices.openUrl", lambda url: opened.append(url.toString()) or True)
    preview.failed.connect(failures.append)
    preview._handle_message({"event": "rendered", "id": 1, "url": "http://127.0.0.1:4321/old"})
    preview._handle_message({"event": "error", "id": 1, "message": "old error"})
    assert opened == [] and failures == []
    preview._handle_message({"event": "rendered", "id": 2, "url": "http://127.0.0.1:4321/current"})
    assert opened == ["http://127.0.0.1:4321/current"]


def test_runtime_failure_is_reported_once(app: QApplication, tmp_path: Path) -> None:
    preview = WordPressPreview(tmp_path, tmp_path / "bridge.mjs")
    failures = []
    preview.failed.connect(failures.append)
    preview._handle_message({"event": "error", "message": "original error"})
    preview._process_finished(1, preview.process.exitStatus())
    assert failures == ["original error"]


def test_main_preview_sends_unsaved_snapshot_without_modifying_document(
    app: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    snapshots = []
    monkeypatch.setattr(WordPressPreview, "show_preview", lambda self, title, source: snapshots.append((title, source)))
    window = MainWindow(settings_path=tmp_path / "settings.json")
    source = '<!-- wp:html --><div>style="color:red"</div><!-- /wp:html -->'
    window.editor.setPlainText(source)
    modified = window.editor.document().isModified()
    window.wordpress_preview_action.trigger()
    assert window.wordpress_preview_action in window.view_menu.actions()
    assert window.wordpress_preview_action.shortcut().toString() == "Ctrl+Alt+P"
    assert snapshots[0][1] == source
    assert window.editor.toPlainText() == source
    assert window.editor.document().isModified() == modified
    window.stop_wordpress_preview()
    assert not window.stop_wordpress_preview_action.isEnabled()


def test_wordpress_success_feedback_does_not_hide_static_structure_errors(app: QApplication, tmp_path: Path) -> None:
    window = MainWindow(settings_path=tmp_path / "settings.json")
    source = '<!-- wp:html -->\n<div>\nstyle="color:red"\n>\nBody</div>\n<!-- /wp:html -->'
    window.editor.setPlainText(source)
    window.wordpress_preview_snapshot = (window.editor, window._source_hash(source))
    window._wordpress_preview_feedback(1, 200, "")
    assert window.grammar_check_dialog is not None
    assert window.grammar_check_dialog.message_list.count() == 1
    assert window.editor.grammar_issue_lines == [3]
    assert "200" in window.grammar_check_dialog.runtime_feedback_label.text()
    assert window.editor.toPlainText() == source
    window.editor.insertPlainText("changed")
    assert window.grammar_check_dialog.runtime_feedback_label.text() == ""


def test_stale_feedback_is_not_applied_to_edited_document(app: QApplication, tmp_path: Path) -> None:
    window = MainWindow(settings_path=tmp_path / "settings.json")
    window.editor.setPlainText("original")
    window.wordpress_preview_snapshot = (window.editor, window._source_hash("original"))
    window.editor.setPlainText("edited")
    window._wordpress_preview_feedback(1, 200, "old warning")
    assert window.grammar_check_dialog is None


def test_engine_feedback_has_no_fake_article_line_and_can_be_copied(app: QApplication) -> None:
    dialog = GrammarCheckDialog(Translator(Path("resources"), "ja"))
    dialog.set_result("Static check", [])
    dialog.set_runtime_feedback("WordPress internal warning")
    assert dialog.message_list.count() == 0
    assert dialog.copy_button.isEnabled()
    dialog.copy_results_to_clipboard()
    assert QApplication.clipboard().text() == "WordPress internal warning"
    dialog.set_result("New document", [])
    assert not dialog.runtime_feedback_label.text()
