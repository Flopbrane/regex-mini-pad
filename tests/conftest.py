from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_default_config_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import main as main_module

    monkeypatch.setattr(
        main_module,
        "default_config_path",
        lambda: tmp_path / "config.json",
    )
