#!/usr/bin/env python3
"""Fail closed when tracked public files leak private or unsupported claims.

Every git-tracked path name and working-tree payload is inspected. Payloads are
searched as UTF-8, UTF-16 LE/BE, and NUL-stripped text so a binary/NUL marker
cannot make a tracked leak invisible. Tokens are reversed in this source and
restored at runtime, allowing the checker to inspect itself without exemptions.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import unicodedata
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# Fixed public branding is admitted only at the exact path and SHA-256. A
# same-named replacement, path alias, or newly added media asset fails closed.
FIXED_PNG_SHA256 = {
    "docs/icons/apple-touch-icon.png": (
        "3b87bee9d07e5ef678c9b77fd61215125729e0c3622f654e55d5e865d6b64c58"
    ),
    "docs/icons/icon-192.png": (
        "e80b1cd1f21562ed3a1055f195a4fc3f57cd0cac4a0f373309f3c6268b3aaf95"
    ),
    "docs/icons/icon-512.png": (
        "86f74ed26d465654de6cf13b34034c45813e56228a8c99800a33c2e2be12d201"
    ),
    "docs/neuroagent_eye_logo.png": (
        "f612bd94451e9f0daf62ff4955b4fd32aee8af8c4dc7ae41ce95dfa2e6ecfe2c"
    ),
    "meta_submission/docs/neuroagent_eye_logo.png": (
        "f612bd94451e9f0daf62ff4955b4fd32aee8af8c4dc7ae41ce95dfa2e6ecfe2c"
    ),
}
CANONICAL_FIXTURE_PATHS = frozenset(
    f"docs/training/frames/fixture_{index:04d}.png" for index in range(1, 27)
)


def _canonical_fixture_sha256() -> dict[str, str]:
    """Derive exact fixture bytes from the reviewed deterministic generator."""

    generator_path = ROOT / "scripts/v11/rebuild_synthetic_frames.py"
    spec = importlib.util.spec_from_file_location(
        "eyewalker_public_tree_frame_contract",
        generator_path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load fixture generator: {generator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {
        f"docs/training/frames/fixture_{index:04d}.png": hashlib.sha256(
            module.expected_fixture_bytes(index)
        ).hexdigest()
        for index in range(1, 27)
    }


CANONICAL_FIXTURE_SHA256 = _canonical_fixture_sha256()
if frozenset(CANONICAL_FIXTURE_SHA256) != CANONICAL_FIXTURE_PATHS:
    raise RuntimeError("fixture path/hash contract mismatch")

# Extension policy is deliberately broader than the currently tracked tree.
# New image, audio, video, archive, model, font, database, or executable
# formats are denied until an exact public contract is reviewed and added.
BINARY_MEDIA_SUFFIXES = frozenset(
    {
        ".7z",
        ".aac",
        ".avi",
        ".avif",
        ".bin",
        ".bmp",
        ".bz2",
        ".class",
        ".ckpt",
        ".dat",
        ".db",
        ".dll",
        ".doc",
        ".docx",
        ".dylib",
        ".eot",
        ".exe",
        ".flac",
        ".flv",
        ".gif",
        ".gz",
        ".heic",
        ".heif",
        ".ico",
        ".jar",
        ".jbig2",
        ".jpeg",
        ".jpg",
        ".joblib",
        ".jxl",
        ".m4a",
        ".m4v",
        ".mkv",
        ".mov",
        ".mp3",
        ".mp4",
        ".mpeg",
        ".mpg",
        ".npy",
        ".npz",
        ".ogg",
        ".onnx",
        ".opus",
        ".otf",
        ".pdf",
        ".pickle",
        ".pkl",
        ".png",
        ".ppt",
        ".pptx",
        ".pt",
        ".pth",
        ".pyc",
        ".pyo",
        ".rar",
        ".safetensors",
        ".so",
        ".sqlite",
        ".sqlite3",
        ".svg",
        ".tar",
        ".tgz",
        ".tif",
        ".tiff",
        ".ttf",
        ".wasm",
        ".wav",
        ".webm",
        ".webp",
        ".wmv",
        ".woff",
        ".woff2",
        ".xls",
        ".xlsx",
        ".xz",
        ".zip",
    }
)
BINARY_MAGIC_PREFIXES = (
    PNG_SIGNATURE,
    b"\xff\xd8\xff",
    b"GIF87a",
    b"GIF89a",
    b"%PDF-",
    b"PK\x03\x04",
    b"PK\x05\x06",
    b"\x1f\x8b",
    b"\x7fELF",
    b"MZ",
    b"SQLite format 3\x00",
    b"\x00asm",
)


def _restore(value: str) -> str:
    return value[::-1]


# Keep literal sensitive strings out of the checker: this file is scanned too.
BANNED = {
    "private product name": _restore("seyE yzaH").replace(" ", ""),
    "legacy defense sensor": _restore("MACSEW"),
    "legacy defense route": _restore("tortxoF"),
    "private approval phone": _restore("0632207743"),
    "private commercial domain": _restore("moc.iaseyeyzah"),
    "private operator username": _restore("strevstocirahsel"),
    "absolute macOS home path": _restore("/sresU/"),
    "unsupported secured claim": _restore("deruces walComeN"),
    "unsupported cryptography mock": _restore("kcom_tpyCrneG"),
    "unsupported sandbox claim": _restore("xobdnas eruces"),
    "unsupported telemetry guarantee": _restore("yrtemelet/sgol duolc oN"),
    "unsupported allowlist guarantee": _restore("ylno tsilwolla"),
    "unsupported exfiltration guarantee": _restore("l ifxe_bgr_spg_war_on").replace(" ", ""),
    "unsupported anonymization claim": _restore("dezimonyna tub emas"),
    "unsupported blueprint enforcement": _restore("tnirpeulb ni decrofne"),
    "dual-use situational-awareness wording": _restore("ssenerawa lanoitautis etomer"),
}

# These private identifiers must also be caught when punctuation, spacing, or
# NULs are inserted. Other policy phrases remain exact phrase checks to avoid
# broad false positives in ordinary prose.
COMPACT_LABELS = {
    "private product name",
    "private approval phone",
    "private commercial domain",
    "private operator username",
}


def tracked_paths(root: Path = ROOT) -> list[Path]:
    """Return every index-tracked path without directory or extension filters."""

    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    return [Path(os.fsdecode(raw)) for raw in output.split(b"\0") if raw]


def _normalized(text: str) -> str:
    return unicodedata.normalize("NFKC", text).casefold()


def _compact(text: str) -> str:
    return "".join(char for char in _normalized(text) if char.isalnum())


def findings_in_text(text: str) -> set[str]:
    """Return policy labels found in one decoded text or path-name view."""

    folded = _normalized(text)
    compact = _compact(text)
    findings: set[str] = set()
    for label, token in BANNED.items():
        if _normalized(token) in folded:
            findings.add(label)
            continue
        if label in COMPACT_LABELS and _compact(token) in compact:
            findings.add(label)
    return findings


def decoded_views(payload: bytes) -> tuple[str, ...]:
    """Decode all payloads, including binary/NUL payloads, through safe views."""

    views: list[str] = []

    def add(value: str) -> None:
        if value not in views:
            views.append(value)

    add(payload.decode("utf-8-sig", errors="replace"))
    add(payload.decode("utf-16-le", errors="replace"))
    add(payload.decode("utf-16-be", errors="replace"))
    if b"\0" in payload:
        add(payload.replace(b"\0", b"").decode("utf-8", errors="replace"))
    return tuple(views)


def findings_in_payload(payload: bytes) -> set[str]:
    findings: set[str] = set()
    for view in decoded_views(payload):
        findings.update(findings_in_text(view))
    return findings


def private_path_findings(relative: Path) -> set[str]:
    """Reject forced-tracked private/review lanes independent of .gitignore."""

    folded_parts = tuple(part.casefold() for part in relative.parts)
    findings: set[str] = set()
    if any(part.startswith("review_pass_") for part in folded_parts):
        findings.add("review-pass path is forbidden in public tree")
    if any(part.endswith("_private") for part in folded_parts):
        findings.add("private-lane path is forbidden in public tree")
    if len(folded_parts) >= 2 and folded_parts[:2] == ("docs", "product_suite"):
        findings.add("private product-suite path is forbidden in public tree")
    return findings


def looks_binary(payload: bytes) -> bool:
    """Conservatively detect binary/media even when its extension is disguised."""

    if not payload:
        return False
    if payload.startswith(BINARY_MAGIC_PREFIXES):
        return True
    if len(payload) >= 12 and payload[4:8] == b"ftyp":
        return True
    if b"\0" in payload:
        return True
    sample = payload[:8192]
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return True
    control_count = sum(
        byte < 32 and byte not in {8, 9, 10, 12, 13} for byte in sample
    )
    return bool(sample) and control_count / len(sample) > 0.01


def binary_media_findings(
    relative: Path,
    payload: bytes,
    *,
    is_symlink: bool = False,
) -> set[str]:
    """Enforce the deny-by-default tracked binary and media policy."""

    display = relative.as_posix()
    fixed_digest = FIXED_PNG_SHA256.get(display)
    fixture_digest = CANONICAL_FIXTURE_SHA256.get(display)
    canonical_fixture = fixture_digest is not None
    allowed_png = fixed_digest is not None or canonical_fixture
    findings: set[str] = set()

    if allowed_png:
        if is_symlink:
            findings.add("allowed PNG must be a regular non-symlink file")
        if not payload.startswith(PNG_SIGNATURE):
            findings.add("allowed PNG has invalid PNG magic")
        if fixed_digest is not None:
            actual_digest = hashlib.sha256(payload).hexdigest()
            if actual_digest != fixed_digest:
                findings.add("fixed public PNG hash mismatch")
        elif fixture_digest is not None:
            actual_digest = hashlib.sha256(payload).hexdigest()
            if actual_digest != fixture_digest:
                findings.add("canonical synthetic fixture hash mismatch")
        return findings

    suffix = relative.suffix.casefold()
    if suffix in BINARY_MEDIA_SUFFIXES:
        findings.add(f"unallowlisted tracked media/binary extension ({suffix})")
    elif looks_binary(payload):
        findings.add("unallowlisted binary payload")
    return findings


def scan_tracked_tree(
    root: Path = ROOT,
    relative_paths: Iterable[Path] | None = None,
) -> tuple[list[str], int, int]:
    """Scan paths and payloads; return findings, path count, NUL-payload count."""

    paths = list(relative_paths if relative_paths is not None else tracked_paths(root))
    findings: list[str] = []
    nul_payloads = 0
    for relative in paths:
        display = relative.as_posix()
        for label in sorted(private_path_findings(relative)):
            findings.append(f"{display}: {label} (path)")
        for label in sorted(findings_in_text(display)):
            findings.append(f"{display}: {label} (path)")

        path = root / relative
        try:
            is_symlink = path.is_symlink()
            if is_symlink:
                findings.append(f"{display}: tracked symlink is forbidden")
                payload = os.fsencode(os.readlink(path))
            else:
                payload = path.read_bytes()
        except OSError as exc:
            findings.append(f"{display}: unreadable tracked content: {exc}")
            continue

        if b"\0" in payload:
            nul_payloads += 1
        for label in sorted(
            binary_media_findings(relative, payload, is_symlink=is_symlink)
        ):
            findings.append(f"{display}: {label}")
        for label in sorted(findings_in_payload(payload)):
            findings.append(f"{display}: {label} (content)")

    return findings, len(paths), nul_payloads


def main() -> int:
    findings, path_count, nul_payloads = scan_tracked_tree()
    if findings:
        print("public-tree scrub failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print(
        "public-tree scrub OK "
        f"({path_count} tracked paths; {nul_payloads} NUL/binary payloads decoded and scanned)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
