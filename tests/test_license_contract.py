"""Exact, fail-closed license text and path-assignment contract."""

from __future__ import annotations

import hashlib
import re
import shutil
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
POLYFORM_BODY_SHA256 = "a6513117aee34e4eb91689a2f0eda9b1cea4612a69b45aa67c1e0bd19a979f27"
MIT_SHA256 = "8acf4c32df543719685a25ef0e07683242887f15ce4f1b93f55c35f39a8a7e34"
REQUIRED_NOTICE = (
    b"Required Notice: Copyright (c) 2026 Kemar Green / NeuroAgent AI / "
    b"eyeWalker Project"
)
# Reviewed upstream body:
# https://github.com/polyformproject/polyform-licenses/blob/1.0.0/PolyForm-Noncommercial-1.0.0.md
MIT_ALLOWLIST = (
    "LICENSE-MIT",
    "DUAL_LICENSE.md",
    "mobile/App.tsx",
    "mobile/README.md",
    "mobile/app.json",
    "mobile/package.json",
    "mobile/LICENSE-MIT.txt",
    "mobile/src/components/CameraView.tsx",
    "mobile/src/components/MapView.tsx",
    "mobile/src/components/ObstacleHUD.tsx",
    "mobile/src/hooks/useLocation.ts",
    "mobile/src/hooks/useObstacleDetection.ts",
    "mobile/src/safety.ts",
    "mobile/src/utils/avoidance.ts",
    "docs/index.html",
    "docs/pwa.html",
    "docs/service-worker.js",
    "docs/manifest.json",
    "docs/LICENSE-MIT.txt",
    "docs/icons/icon-192.png",
    "docs/icons/icon-512.png",
    "docs/icons/apple-touch-icon.png",
)


def validate_license_contract(root: Path) -> None:
    license_bytes = (root / "LICENSE").read_bytes()
    suffix = b"\n\n" + REQUIRED_NOTICE + b"\n"
    assert license_bytes.endswith(suffix), "exact required notice must be the final line"
    assert license_bytes.count(REQUIRED_NOTICE) == 1
    upstream_body = license_bytes[: -len(suffix)] + b"\n"
    assert hashlib.sha256(upstream_body).hexdigest() == POLYFORM_BODY_SHA256

    mit = (root / "LICENSE-MIT").read_bytes()
    assert hashlib.sha256(mit).hexdigest() == MIT_SHA256
    assert (root / "docs/LICENSE-MIT.txt").read_bytes() == mit
    assert (root / "mobile/LICENSE-MIT.txt").read_bytes() == mit

    assignment = (root / "DUAL_LICENSE.md").read_text()
    allowlist_block = assignment.split(
        "MIT license in `LICENSE-MIT` only for these exact files:\n",
        1,
    )[1].split("\nAll other paths", 1)[0]
    actual_allowlist = tuple(
        re.findall(r"(?m)^- `([^`]+)`$", allowlist_block)
    )
    assert actual_allowlist == MIT_ALLOWLIST
    assert len(actual_allowlist) == len(set(actual_allowlist))
    for relative in actual_allowlist:
        path = root / relative
        assert path.is_file() and not path.is_symlink(), relative

    service_worker = (root / "docs/service-worker.js").read_text()
    assert '"./LICENSE-MIT.txt"' in service_worker
    assert 'href="LICENSE-MIT.txt"' in (root / "docs/index.html").read_text()
    assert 'href="LICENSE-MIT.txt"' in (root / "docs/pwa.html").read_text()


def _copy_contract_fixture(destination: Path) -> None:
    for relative in ("LICENSE", "DUAL_LICENSE.md", *MIT_ALLOWLIST):
        source = ROOT / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def test_current_license_contract_is_exact() -> None:
    validate_license_contract(ROOT)


@pytest.mark.parametrize(
    ("relative", "mutation"),
    (
        ("LICENSE", "body"),
        ("LICENSE", "notice"),
        ("LICENSE-MIT", "mit"),
        ("docs/LICENSE-MIT.txt", "mit_copy"),
        ("mobile/LICENSE-MIT.txt", "mit_copy"),
        ("DUAL_LICENSE.md", "allowlist"),
        ("DUAL_LICENSE.md", "allowlist_reorder"),
        ("docs/service-worker.js", "service_worker"),
        ("docs/index.html", "notice_link"),
        ("docs/pwa.html", "notice_link"),
    ),
)
def test_contract_rejects_text_notice_copy_or_allowlist_tampering(
    tmp_path: Path,
    relative: str,
    mutation: str,
) -> None:
    _copy_contract_fixture(tmp_path)
    validate_license_contract(tmp_path)
    path = tmp_path / relative
    if mutation == "body":
        path.write_bytes(path.read_bytes().replace(b"noncommercial", b"commercial", 1))
    elif mutation == "notice":
        path.write_bytes(path.read_bytes() + REQUIRED_NOTICE + b"\n")
    elif mutation in {"mit", "mit_copy"}:
        path.write_bytes(path.read_bytes() + b"modified\n")
    elif mutation == "allowlist":
        path.write_text(
            path.read_text().replace(
                "- `mobile/App.tsx`\n",
                "- `mobile/App.tsx`\n- `mobile/unreviewed.ts`\n",
            )
        )
    elif mutation == "allowlist_reorder":
        path.write_text(
            path.read_text().replace(
                "- `LICENSE-MIT`\n- `DUAL_LICENSE.md`\n",
                "- `DUAL_LICENSE.md`\n- `LICENSE-MIT`\n",
            )
        )
    elif mutation == "service_worker":
        path.write_text(path.read_text().replace('"./LICENSE-MIT.txt", ', ""))
    else:
        path.write_text(path.read_text().replace('href="LICENSE-MIT.txt"', 'href="#"'))

    with pytest.raises((AssertionError, FileNotFoundError)):
        validate_license_contract(tmp_path)
