from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

from scripts import check_public_tree as scrub


def _private_product() -> str:
    return "seyE yzaH"[::-1].replace(" ", "")


def _scan_payload(
    tmp_path: Path,
    relative: Path,
    payload: bytes,
) -> list[str]:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    findings, count, _ = scrub.scan_tracked_tree(tmp_path, [relative])
    assert count == 1
    return findings


@pytest.mark.parametrize("encoding", ["utf-8", "utf-16-le", "utf-16-be"])
def test_encoded_private_text_is_detected_case_insensitively(encoding: str) -> None:
    payload = ("prefix " + _private_product().swapcase() + " suffix").encode(encoding)
    assert "private product name" in scrub.findings_in_payload(payload)


def test_nul_obfuscation_and_binary_prefix_do_not_skip_scan() -> None:
    token = _private_product().encode()
    payload = b"\xff\xfeBINARY\x00" + b"\0".join(bytes([byte]) for byte in token)
    assert "private product name" in scrub.findings_in_payload(payload)


@pytest.mark.parametrize("label,token", list(scrub.BANNED.items()))
def test_every_policy_token_has_a_detectable_encoded_form(label: str, token: str) -> None:
    assert label in scrub.findings_in_payload(token.swapcase().encode("utf-16-le"))


def test_private_identifiers_are_detected_through_formatting() -> None:
    phone = "0632-207-743"[::-1]
    product = "seyE_yzaH"[::-1]
    assert "private approval phone" in scrub.findings_in_text(phone)
    assert "private product name" in scrub.findings_in_text(product)


@pytest.mark.parametrize(
    "encoded_component,label",
    [
        ("seyE yzaH"[::-1].replace(" ", ""), "private product name"),
        ("moc.iaseyeyzah"[::-1], "private commercial domain"),
        ("0632-207-743"[::-1], "private approval phone"),
        ("strevstocirahsel"[::-1], "private operator username"),
        ("sresU"[::-1], "absolute macOS home path"),
    ],
)
def test_private_path_names_are_scanned(
    tmp_path: Path,
    encoded_component: str,
    label: str,
) -> None:
    relative = Path("docs") / encoded_component / "readme.txt"
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text("clean")
    findings, count, _ = scrub.scan_tracked_tree(tmp_path, [relative])
    assert count == 1
    assert any(f"{label} (path)" in finding for finding in findings)


def test_git_listing_includes_dot_github_and_checker_path(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    paths = [Path(".github/workflows/ci.yml"), Path("scripts/check_public_tree.py")]
    for relative in paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("clean")
    subprocess.run(["git", "add", "--", *(str(path) for path in paths)], cwd=tmp_path, check=True)
    assert set(scrub.tracked_paths(tmp_path)) == set(paths)


def test_checker_source_does_not_match_its_runtime_tokens() -> None:
    checker = Path(scrub.__file__)
    assert scrub.findings_in_payload(checker.read_bytes()) == set()


@pytest.mark.parametrize("relative_text,expected_digest", scrub.FIXED_PNG_SHA256.items())
def test_only_exact_fixed_brand_and_icon_png_hashes_are_allowed(
    tmp_path: Path,
    relative_text: str,
    expected_digest: str,
) -> None:
    relative = Path(relative_text)
    payload = (scrub.ROOT / relative).read_bytes()
    assert payload.startswith(scrub.PNG_SIGNATURE)
    assert hashlib.sha256(payload).hexdigest() == expected_digest
    assert _scan_payload(tmp_path, relative, payload) == []


def test_tampered_fixed_png_fails_hash_allowlist(tmp_path: Path) -> None:
    relative = Path("docs/icons/icon-192.png")
    payload = (scrub.ROOT / relative).read_bytes() + b"tamper"
    findings = _scan_payload(tmp_path, relative, payload)
    assert any("fixed public PNG hash mismatch" in finding for finding in findings)


def test_canonical_fixture_path_requires_png_magic(tmp_path: Path) -> None:
    relative = Path("docs/training/frames/fixture_0001.png")
    payload = (scrub.ROOT / relative).read_bytes()
    assert _scan_payload(tmp_path, relative, payload) == []

    findings = _scan_payload(tmp_path, relative, b"not a png")
    assert any("invalid PNG magic" in finding for finding in findings)


def test_canonical_fixture_path_rejects_other_valid_looking_png_bytes(tmp_path: Path) -> None:
    relative = Path("docs/training/frames/fixture_0001.png")
    payload = (scrub.ROOT / relative).read_bytes() + b"tamper"

    findings = _scan_payload(tmp_path, relative, payload)

    assert any("canonical synthetic fixture hash mismatch" in finding for finding in findings)


@pytest.mark.parametrize(
    "relative",
    [
        Path("docs/training/frames/fixture_0000.png"),
        Path("docs/training/frames/fixture_0027.png"),
        Path("docs/training/frames/FIXTURE_0001.PNG"),
        Path("docs/other/fixture_0001.png"),
    ],
)
def test_fixture_allowlist_is_exact_path_and_range(
    tmp_path: Path,
    relative: Path,
) -> None:
    findings = _scan_payload(tmp_path, relative, scrub.PNG_SIGNATURE + b"fixture")
    assert any("unallowlisted tracked media/binary extension" in finding for finding in findings)


@pytest.mark.parametrize(
    "suffix",
    [".jpg", ".gif", ".webp", ".svg", ".mp4", ".wav", ".pdf", ".zip", ".onnx", ".npy"],
)
def test_all_other_media_and_binary_extensions_fail_closed(
    tmp_path: Path,
    suffix: str,
) -> None:
    relative = Path("public") / f"clean-looking{suffix}"
    findings = _scan_payload(tmp_path, relative, b"otherwise clean text")
    assert any("unallowlisted tracked media/binary extension" in finding for finding in findings)


def test_disguised_binary_magic_fails_even_with_text_extension(tmp_path: Path) -> None:
    relative = Path("docs/disguised.txt")
    findings = _scan_payload(tmp_path, relative, scrub.PNG_SIGNATURE + b"payload")
    assert any("unallowlisted binary payload" in finding for finding in findings)


def test_allowed_png_symlink_fails_closed(tmp_path: Path) -> None:
    relative = Path("docs/training/frames/fixture_0001.png")
    target = tmp_path / "target.txt"
    target.write_text("clean")
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.symlink_to(target)
    findings, _, _ = scrub.scan_tracked_tree(tmp_path, [relative])
    assert any("regular non-symlink" in finding for finding in findings)


@pytest.mark.parametrize("target", ["inside.txt", "../outside.txt", "/etc/passwd"])
def test_every_tracked_symlink_fails_closed(tmp_path: Path, target: str) -> None:
    relative = Path("docs/innocent.txt")
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.symlink_to(target)

    findings, _, _ = scrub.scan_tracked_tree(tmp_path, [relative])

    assert any("tracked symlink is forbidden" in finding for finding in findings)


@pytest.mark.parametrize(
    "relative",
    [
        Path("review_pass_2099-01-01/note.txt"),
        Path("example_PRIVATE/note.txt"),
        Path("nested/example_private/note.txt"),
        Path("docs/product_suite/note.txt"),
    ],
)
def test_forced_tracked_private_and_review_paths_fail_closed(
    tmp_path: Path,
    relative: Path,
) -> None:
    findings = _scan_payload(tmp_path, relative, b"otherwise clean")
    assert any("forbidden in public tree" in finding for finding in findings)


def test_fixture_allowlist_contains_exactly_26_canonical_paths() -> None:
    assert scrub.CANONICAL_FIXTURE_PATHS == {
        f"docs/training/frames/fixture_{index:04d}.png" for index in range(1, 27)
    }
    assert set(scrub.CANONICAL_FIXTURE_SHA256) == scrub.CANONICAL_FIXTURE_PATHS
    assert len(set(scrub.CANONICAL_FIXTURE_SHA256.values())) == 26
