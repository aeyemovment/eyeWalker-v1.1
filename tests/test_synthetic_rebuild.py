"""Adversarial safety and reproducibility tests for synthetic fixtures/corpus."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import struct
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
FRAME_SCRIPT = REPO / "scripts" / "v11" / "rebuild_synthetic_frames.py"
DATASET_SCRIPT = REPO / "scripts" / "v11" / "rebuild_synthetic_dataset.py"
LEGACY_SCRIPT = REPO / "scripts" / "v11" / "dt_ritual_all_at_once.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


frame_module = _load("eyewalker_synthetic_frames_test", FRAME_SCRIPT)
rebuild_module = _load("eyewalker_synthetic_rebuild_test", DATASET_SCRIPT)


def _layout(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    root = tmp_path / "repo"
    frames = root / "docs" / "training" / "frames"
    out = root / "docs" / "training" / "synthetic"
    exports = root / "docs" / "training" / "exports"
    out.mkdir(parents=True)
    exports.mkdir(parents=True)
    (root / "VERSION").write_text("1.1.9\n")
    return root, frames, out, exports


def _build_fixtures(root: Path, frames: Path) -> None:
    frame_module.rebuild(root=root, frames_dir=frames)


def _snapshot(root: Path) -> dict[str, tuple[str, bytes | str]]:
    """Capture files, symlinks, and directories without following symlinks."""

    snapshot: dict[str, tuple[str, bytes | str]] = {}
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in sorted(directories + files):
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                snapshot[relative] = ("symlink", os.readlink(path))
            elif path.is_dir():
                snapshot[relative] = ("directory", "")
            else:
                snapshot[relative] = ("file", path.read_bytes())
    return snapshot


def _rows(out: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in (out / rebuild_module.AGGREGATE_NAME).read_text().splitlines()
        if line.strip()
    ]


def test_fixture_rebuild_is_exact_distinct_metadata_free_and_deterministic(tmp_path: Path):
    root, frames, _, _ = _layout(tmp_path)

    records = frame_module.rebuild(root=root, frames_dir=frames)

    paths = sorted(frames.iterdir())
    assert [path.name for path in paths] == list(frame_module.CANONICAL_NAMES)
    assert len(paths) == len(records) == frame_module.FRAME_COUNT == 26
    assert frame_module.WATERMARK == (
        "SIMULATED RESEARCH FIXTURE \N{EM DASH} NOT A DETECTION"
    )
    hashes = set()
    for index, path in enumerate(paths, start=1):
        raw = path.read_bytes()
        properties = frame_module.inspect_png(raw)
        assert raw.startswith(frame_module.PNG_SIGNATURE)
        assert raw == frame_module.expected_fixture_bytes(index)
        assert properties == {
            "width": 640,
            "height": 480,
            "bit_depth": 8,
            "color_type": 3,
            "chunks": ("IHDR", "PLTE", "IDAT", "IEND"),
            "metadata_free": True,
            "pixel_sha256": hashlib.sha256(
                frame_module._pack_scanlines(
                    frame_module._fixture_pixels(index), bit_depth=8
                )
            ).hexdigest(),
        }
        hashes.add(hashlib.sha256(raw).hexdigest())
    assert len(hashes) == 26

    first = _snapshot(root)
    frame_module.rebuild(root=root, frames_dir=frames)
    assert _snapshot(root) == first


def test_fixture_rebuild_refuses_extra_path_before_mutation(tmp_path: Path):
    root, frames, _, _ = _layout(tmp_path)
    _build_fixtures(root, frames)
    (frames / "notes.txt").write_text("not generator-owned\n")
    before = _snapshot(root)

    with pytest.raises(ValueError, match="unexpected path"):
        frame_module.rebuild(root=root, frames_dir=frames)

    assert _snapshot(root) == before


def test_fixture_rebuild_does_not_fill_missing_file_when_another_is_tampered(
    tmp_path: Path,
):
    root, frames, _, _ = _layout(tmp_path)
    _build_fixtures(root, frames)
    (frames / frame_module.CANONICAL_NAMES[0]).write_bytes(b"not a PNG")
    (frames / frame_module.CANONICAL_NAMES[1]).unlink()
    before = _snapshot(root)

    with pytest.raises(ValueError, match="refusing to overwrite"):
        frame_module.rebuild(root=root, frames_dir=frames)

    assert _snapshot(root) == before


def test_rebuild_is_complete_and_preserves_unowned_output_paths(tmp_path: Path):
    root, frames, out, exports = _layout(tmp_path)
    _build_fixtures(root, frames)
    unowned_json = out / "research_notes.json"
    unowned_jsonl = out / "research_notes.jsonl"
    unowned_directory = out / "archive.json"
    unowned_json.write_text('{"owner":"researcher"}\n')
    unowned_jsonl.write_text('{"note":"preserve"}\n')
    unowned_directory.mkdir()
    (unowned_directory / "note.txt").write_text("preserve directory\n")

    manifest = rebuild_module.rebuild(
        root=root,
        frames_dir=frames,
        out_dir=out,
        exports_dir=exports,
    )

    label_paths = sorted(
        path
        for path in out.glob("*.json")
        if path.is_file()
        and path.name not in {rebuild_module.MANIFEST_NAME, unowned_json.name}
    )
    rows = _rows(out)
    labels = [json.loads(path.read_text()) for path in label_paths]

    assert manifest["generator_id"] == rebuild_module.GENERATOR_ID
    assert manifest["software_version"] == "1.1.9"
    assert manifest["dataset_schema_version"] == "1.1.0"
    assert manifest["n_frames"] == 26
    assert manifest["n_rows"] == 312
    assert manifest["left_right_convention"] == rebuild_module.LEFT_RIGHT_CONVENTION
    assert manifest["source_fixture_contract"] == {
        "generator_id": frame_module.FRAME_GENERATOR_ID,
        "count": 26,
        "media_type": "image/png",
        "width": 640,
        "height": 480,
        "metadata_free": True,
        "png_chunks": ["IHDR", "PLTE", "IDAT", "IEND"],
        "ownership": "exact deterministic generator pixels and PNG structure",
        "watermark": frame_module.WATERMARK,
    }
    assert len(label_paths) == len(rows) == len(labels) == 312
    assert len({(r["source_frame"], r["condition"], r["twin_id"]) for r in rows}) == 312
    assert {json.dumps(row, sort_keys=True) for row in rows} == {
        json.dumps(label, sort_keys=True) for label in labels
    }
    assert all(not Path(row["source_frame"]).is_absolute() for row in rows)
    assert all((root / row["source_frame"]).is_file() for row in rows)
    assert all(Path(row["source_frame"]).suffix == ".png" for row in rows)
    assert all(len(row["source_sha256"]) == 64 for row in rows)
    assert all(
        hashlib.sha256((root / row["source_frame"]).read_bytes()).hexdigest()
        == row["source_sha256"]
        for row in rows
    )
    assert all(rebuild_module.SAFETY_PREFIX in row["guidance"] for row in rows)
    assert all(rebuild_module.SAFETY_SUFFIX in row["guidance"] for row in rows)
    centered_rows = 0
    for row in rows:
        bearing = row["obstacles"][0]["bearing_deg"]
        if bearing < -8:
            assert "step right." in row["guidance"]
        elif bearing > 8:
            assert "step left." in row["guidance"]
        else:
            centered_rows += 1
            assert "HOLD and stop and verify." in row["guidance"]
            assert "step side-step" not in row["guidance"]
    assert centered_rows == 96
    assert any(row["obstacles"][0]["bearing_deg"] == -8.0 for row in rows)
    assert manifest["aggregate_sha256"] == hashlib.sha256(
        (out / rebuild_module.AGGREGATE_NAME).read_bytes()
    ).hexdigest()
    generated_paths = label_paths + [
        out / rebuild_module.AGGREGATE_NAME,
        out / rebuild_module.MANIFEST_NAME,
        exports / rebuild_module.EXPORT_MANIFEST_NAME,
    ]
    assert all((path.stat().st_mode & 0o777) == 0o644 for path in generated_paths)
    assert unowned_json.read_text() == '{"owner":"researcher"}\n'
    assert unowned_jsonl.read_text() == '{"note":"preserve"}\n'
    assert (unowned_directory / "note.txt").read_text() == "preserve directory\n"

    first = _snapshot(root)
    rebuild_module.rebuild(
        root=root,
        frames_dir=frames,
        out_dir=out,
        exports_dir=exports,
    )
    assert _snapshot(root) == first


def test_extra_source_file_fails_before_touching_outputs(tmp_path: Path):
    root, frames, out, exports = _layout(tmp_path)
    _build_fixtures(root, frames)
    (frames / "fixture_9999.jpg").write_bytes(frame_module.expected_fixture_bytes(1))
    (out / "keep.json").write_text('{"keep":true}\n')
    before = _snapshot(root)

    with pytest.raises(ValueError, match="exactly 26 owned PNG files"):
        rebuild_module.rebuild(
            root=root,
            frames_dir=frames,
            out_dir=out,
            exports_dir=exports,
        )

    assert _snapshot(root) == before


@pytest.mark.parametrize("tamper", ["magic", "dimensions", "metadata", "ownership"])
def test_invalid_png_or_ownership_fails_before_output_mutation(
    tmp_path: Path,
    tamper: str,
):
    root, frames, out, exports = _layout(tmp_path)
    _build_fixtures(root, frames)
    target = frames / frame_module.CANONICAL_NAMES[0]
    raw = target.read_bytes()
    if tamper == "magic":
        target.write_bytes(b"not a PNG")
        expected_error = "PNG magic"
    elif tamper == "dimensions":
        ihdr = struct.pack(">IIBBBBB", 320, 480, 8, 3, 0, 0, 0)
        target.write_bytes(
            frame_module.PNG_SIGNATURE
            + frame_module._chunk(b"IHDR", ihdr)
            + raw[len(frame_module.PNG_SIGNATURE) + 25 :]
        )
        expected_error = "dimensions"
    elif tamper == "metadata":
        target.write_bytes(
            raw[:-12]
            + frame_module._chunk(b"tEXt", b"note=value")
            + raw[-12:]
        )
        expected_error = "chunk contract"
    else:
        altered = bytearray(raw)
        altered[-20] ^= 1
        target.write_bytes(altered)
        expected_error = "CRC|ownership|decompress"
    (out / "keep.jsonl").write_text('{"keep":true}\n')
    before = _snapshot(root)

    with pytest.raises(ValueError, match=expected_error):
        rebuild_module.rebuild(
            root=root,
            frames_dir=frames,
            out_dir=out,
            exports_dir=exports,
        )

    assert _snapshot(root) == before


def test_missing_fixture_fails_before_output_mutation(tmp_path: Path):
    root, frames, out, exports = _layout(tmp_path)
    _build_fixtures(root, frames)
    (frames / frame_module.CANONICAL_NAMES[-1]).unlink()
    (out / "keep.jsonl").write_text('{"keep":true}\n')
    before = _snapshot(root)

    with pytest.raises(ValueError, match="exactly 26 owned PNG files"):
        rebuild_module.rebuild(
            root=root,
            frames_dir=frames,
            out_dir=out,
            exports_dir=exports,
        )

    assert _snapshot(root) == before


def test_external_source_symlink_is_rejected_before_output_mutation(tmp_path: Path):
    root, frames, out, exports = _layout(tmp_path)
    _build_fixtures(root, frames)
    target = frames / frame_module.CANONICAL_NAMES[0]
    outside = tmp_path / target.name
    outside.write_bytes(target.read_bytes())
    target.unlink()
    target.symlink_to(outside)
    (out / "keep.jsonl").write_text('{"keep":true}\n')
    before = _snapshot(root)

    with pytest.raises(ValueError, match="regular file"):
        rebuild_module.rebuild(
            root=root,
            frames_dir=frames,
            out_dir=out,
            exports_dir=exports,
        )

    assert _snapshot(root) == before


def test_unowned_label_target_collision_is_rejected_without_mutation(tmp_path: Path):
    root, frames, out, exports = _layout(tmp_path)
    _build_fixtures(root, frames)
    collision = out / "fixture_0001_day_t0.json"
    collision.write_text('{"owner":"researcher"}\n')
    before = _snapshot(root)

    with pytest.raises(ValueError, match="unowned output collision"):
        rebuild_module.rebuild(
            root=root,
            frames_dir=frames,
            out_dir=out,
            exports_dir=exports,
        )

    assert _snapshot(root) == before


def test_late_unowned_manifest_collision_is_atomic(tmp_path: Path):
    root, frames, out, exports = _layout(tmp_path)
    _build_fixtures(root, frames)
    rebuild_module.rebuild(
        root=root,
        frames_dir=frames,
        out_dir=out,
        exports_dir=exports,
    )
    export_manifest = exports / rebuild_module.EXPORT_MANIFEST_NAME
    export_manifest.write_text('{"owner":"researcher"}\n')
    before = _snapshot(root)

    with pytest.raises(ValueError, match="unowned output collision"):
        rebuild_module.rebuild(
            root=root,
            frames_dir=frames,
            out_dir=out,
            exports_dir=exports,
        )

    assert _snapshot(root) == before


def test_legacy_one_frame_api_only_accepts_canonical_owned_set(tmp_path: Path, monkeypatch):
    root, frames, out, _ = _layout(tmp_path)
    _build_fixtures(root, frames)
    monkeypatch.syspath_prepend(str(LEGACY_SCRIPT.parent))
    legacy = _load("legacy_dt_ritual", LEGACY_SCRIPT)

    frame = frames / frame_module.CANONICAL_NAMES[0]
    rows = legacy.ritual_for_frame(frame, out, root=root)

    assert len(rows) == 12
    assert len(list(out.glob("fixture_0001_*.json"))) == 12
    assert all(rebuild_module.SAFETY_PREFIX in row["guidance"] for row in rows)
    assert all(rebuild_module.SAFETY_SUFFIX in row["guidance"] for row in rows)

    arbitrary = root / "arbitrary.png"
    arbitrary.write_bytes(frame.read_bytes())
    before = _snapshot(root)
    with pytest.raises(ValueError):
        legacy.ritual_for_frame(arbitrary, out, root=root)
    assert _snapshot(root) == before
