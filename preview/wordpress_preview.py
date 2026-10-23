"""Asynchronous, on-demand WordPress preview displayed by the default browser."""
from __future__ import annotations

import json
import threading
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, QThread, QUrl, Signal
from PySide6.QtGui import QDesktopServices

from preview.wordpress_runtime import PreparationCancelled, prepare_runtime

PROTOCOL_PREFIX = b"REGEXPAD_PREVIEW "


class RuntimePreparation(QThread):
    progress = Signal(str)
    prepared = Signal(str)
    failed = Signal(str)

    def __init__(self, runtime_root: Path, parent: QObject) -> None:
        super().__init__(parent)
        self.runtime_root = runtime_root
        self.cancel = threading.Event()

    def run(self) -> None:
        try:
            node = prepare_runtime(self.runtime_root, self.progress.emit, self.cancel)
            if not self.cancel.is_set():
                self.prepared.emit(str(node))
        except PreparationCancelled:
            pass
        except Exception as error:  # noqa: BLE001 - report all failures at the QThread boundary.
            self.failed.emit(str(error))


class WordPressPreview(QObject):
    progress = Signal(str)
    rendered = Signal(str, str)
    failed = Signal(str)
    active_changed = Signal(bool)
    feedback = Signal(int, int, str)

    def __init__(self, runtime_root: Path, bridge_path: Path, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.runtime_root = runtime_root.resolve()
        self.bridge_path = bridge_path.resolve()
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._read_output)
        self.process.readyReadStandardError.connect(self._read_errors)
        self.process.errorOccurred.connect(self._process_error)
        self.process.finished.connect(self._process_finished)
        self.preparation: RuntimePreparation | None = None
        self.pending: tuple[int, str, str] | None = None
        self.sequence = 0
        self.ready = False
        self.closing = False
        self.version = ""
        self.origin = ""
        self.buffer = b""
        self.error_tail = ""
        self.reported_failure = False

    def show_preview(self, title: str, source_text: str) -> None:
        self.closing = False
        self.reported_failure = False
        self.sequence += 1
        self.pending = (self.sequence, title, source_text)
        self.active_changed.emit(True)
        if self.ready:
            self._send_pending()
        elif self.preparation is not None and self.preparation.isRunning() or self.process.state() != QProcess.ProcessState.NotRunning:
            return
        else:
            self.progress.emit("prepare")
            preparation = RuntimePreparation(self.runtime_root, self)
            self.preparation = preparation
            preparation.progress.connect(self.progress.emit)
            preparation.prepared.connect(self._start_bridge)
            preparation.failed.connect(self._fail)
            preparation.start()

    def _start_bridge(self, node_path: str) -> None:
        if self.closing:
            return
        self.buffer = b""
        self.error_tail = ""
        self.progress.emit("boot")
        self.process.setWorkingDirectory(str(self.runtime_root))
        self.process.start(node_path, [str(self.bridge_path), str(self.runtime_root)])

    def _send_pending(self) -> None:
        if self.pending is None:
            return
        request_id, title, content = self.pending
        self.pending = None
        self.progress.emit("render")
        command = {"command": "render", "id": request_id, "title": title, "content": content}
        self.process.write((json.dumps(command, ensure_ascii=False) + "\n").encode("utf-8"))

    def _read_output(self) -> None:
        self.buffer += bytes(self.process.readAllStandardOutput().data())
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            if line.startswith(PROTOCOL_PREFIX):
                try:
                    message = json.loads(line[len(PROTOCOL_PREFIX):])
                    self._handle_message(message)
                except (ValueError, TypeError, AttributeError) as error:
                    self._fail(f"Invalid preview response: {error}")

    def _handle_message(self, message: dict[str, object]) -> None:
        if self.closing:
            return
        event = message.get("event")
        if event == "ready":
            origin = QUrl(str(message.get("origin", "")))
            if origin.scheme() != "http" or origin.host() != "127.0.0.1" or origin.port() <= 0:
                self._fail("Unexpected WordPress preview origin.")
                return
            self.origin = origin.toString().rstrip("/")
            self.version = str(message.get("version", ""))
            self.ready = True
            self._send_pending()
        elif event == "rendered" and message.get("id") == self.sequence:
            url = QUrl(str(message.get("url", "")))
            if url.scheme() != "http" or url.host() != "127.0.0.1" or (
                f"http://127.0.0.1:{url.port()}" != self.origin
            ):
                self._fail("Unexpected WordPress preview URL.")
                return
            if not QDesktopServices.openUrl(url):
                self._fail("The default browser could not be opened.")
                return
            self.active_changed.emit(False)
            self.rendered.emit(self.version, url.toString())
        elif event == "error" and message.get("id", self.sequence) == self.sequence:
            self._fail(str(message.get("message", "WordPress preview failed.")))
        elif event == "feedback" and message.get("id") == self.sequence:
            self.feedback.emit(self.sequence, int(str(message.get("status", 0))), str(message.get("warnings", "")))
        elif event == "progress":
            self.progress.emit(str(message.get("stage", "boot")))

    def _read_errors(self) -> None:
        self.error_tail = (self.error_tail + bytes(self.process.readAllStandardError().data()).decode(
            "utf-8", errors="replace",
        ))[-3000:]

    def _process_error(self, error: QProcess.ProcessError) -> None:
        if not self.closing and error == QProcess.ProcessError.FailedToStart:
            self._fail(self.process.errorString())

    def _process_finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self.ready = False
        if not self.closing:
            self._fail(self.error_tail or f"WordPress preview stopped ({exit_code}).")

    def _fail(self, message: str) -> None:
        if self.closing or self.reported_failure:
            return
        self.reported_failure = True
        self.active_changed.emit(False)
        self.failed.emit(message)

    def stop(self) -> None:
        """Stop only this editor's preview; leave any unrelated server untouched."""
        self.closing = True
        self.ready = False
        self.pending = None
        if self.preparation is not None and self.preparation.isRunning():
            self.preparation.cancel.set()
            self.preparation.wait(25000)
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.write(b'{"command":"shutdown"}\n')
            self.process.closeWriteChannel()
            if not self.process.waitForFinished(3000):
                self.process.kill()
                self.process.waitForFinished(3000)
        self.active_changed.emit(False)
