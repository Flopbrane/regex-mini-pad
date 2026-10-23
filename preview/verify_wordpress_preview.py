"""Opt-in integration check: python -m preview.verify_wordpress_preview.

Uses real WordPress/PHP.wasm and HTTP, without opening a browser or a public site.
This is deliberately outside normal pytest: it may prepare/download the runtime.
"""
from __future__ import annotations

import argparse
import json
import queue
import subprocess
import threading
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from portable_runtime import app_base_dir, bundled_base_dir
from preview.wordpress_runtime import CREATE_NO_WINDOW, prepare_runtime
from search.html_typo_lint import lint_html_typos


def verify(runtime_root: Path) -> dict[str, object]:
    runtime_root = runtime_root.resolve()
    node = prepare_runtime(runtime_root, lambda stage: print(f"Preparing: {stage}", flush=True), threading.Event())
    messages: queue.Queue[dict[str, object]] = queue.Queue()
    bridge = bundled_base_dir() / "resources/wordpress_preview/bridge.mjs"
    log_path = runtime_root / "verification.log"
    with log_path.open("w", encoding="utf-8") as errors, subprocess.Popen(
        [str(node), str(bridge), str(runtime_root)], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE, stderr=errors, text=True, encoding="utf-8",
        creationflags=CREATE_NO_WINDOW,
    ) as process:
        assert process.stdin is not None and process.stdout is not None

        def read_messages() -> None:
            assert process.stdout is not None
            for line in process.stdout:
                if line.startswith("REGEXPAD_PREVIEW "):
                    messages.put(json.loads(line.split(" ", 1)[1]))
            messages.put({"event": "stopped"})

        reader = threading.Thread(target=read_messages, daemon=True)
        reader.start()

        def wait_for(event: str) -> dict[str, object]:
            while True:
                message = messages.get(timeout=90)
                if message.get("event") in {"error", "stopped"}:
                    raise RuntimeError(f"Backend failed: {message}. Details: {log_path}")
                if message.get("event") == event:
                    return message

        def render(request_id: int, content: str) -> tuple[dict[str, object], str, str]:
            assert process.stdin is not None
            process.stdin.write(json.dumps({
                "command": "render", "id": request_id, "title": "RegexPad normal preview",
                "content": content,
            }, ensure_ascii=False) + "\n")
            process.stdin.flush()
            feedback = wait_for("feedback")
            page = wait_for("rendered")
            url = str(page["url"])
            with urlopen(url, timeout=30) as response:
                assert response.status == 200
                html = response.read().decode("utf-8")
            return feedback, url, html

        url = ""
        try:
            ready = wait_for("ready")
            content = '<!-- wp:heading {"level":3} --><h3>Normal preview test</h3><!-- /wp:heading --><!-- wp:latest-posts /-->'
            _feedback, url, html = render(1, content)
            assert "Normal preview test" in html and "wp-block-latest-posts" in html
            assert "wp-content/themes/" + str(ready["theme"]) in html
            for method, host, expected in (("POST", None, 405), ("GET", "example.com", 403)):
                headers = {"Host": host} if host else {}
                try:
                    with urlopen(Request(url, method=method, headers=headers), timeout=10):
                        raise AssertionError("Unexpectedly accepted a write or foreign Host")
                except HTTPError as error:
                    assert error.code == expected

            case_root = app_base_dir() / "tests/fixtures/linter_cases/qualification_article_20261023"
            results = []
            for request_id, name, count in ((2, "broken.wp_html", 11), (3, "fixed.wp_html", 0)):
                source = (case_root / name).read_text(encoding="utf-8-sig")
                feedback, url, html = render(request_id, source)
                findings = lint_html_typos(source)
                assert len(findings) == count
                assert feedback["status"] == 200
                assert "事務職" in html
                results.append({
                    "sample": name, "static_findings": len(findings),
                    "wordpress_http": feedback["status"], "runtime_warnings": feedback.get("warnings", ""),
                })
            return {
                "wordpress": ready["version"], "theme": ready["theme"],
                "dynamic_block": "latest-posts rendered", "loopback_only": True,
                "http_writes_rejected": True, "article_results": results,
            }
        finally:
            if process.poll() is None:
                process.stdin.write('{"command":"shutdown"}\n')
                process.stdin.flush()
                process.stdin.close()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            reader.join(timeout=2)
            if url:
                try:
                    with urlopen(url, timeout=2):
                        raise AssertionError("Preview server remained running after shutdown")
                except (URLError, OSError):
                    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, default=app_base_dir() / "runtime/wordpress-preview")
    arguments = parser.parse_args()
    print(json.dumps(verify(arguments.runtime_root), ensure_ascii=False, indent=2))
