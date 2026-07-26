#!/usr/bin/env python3
"""Deterministically rebuild the synthetic DT research-label corpus.

Every source and destination is validated before the first filesystem mutation.
Only artifacts carrying this generator's ownership markers may be replaced or
removed; unrelated JSON/JSONL files and directories are never touched.

Research prototype only. synthetic_only=true. Not a medical device.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from types import ModuleType
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
FRAME_GENERATOR_SCRIPT = Path(__file__).with_name("rebuild_synthetic_frames.py")


def _load_frame_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "eyewalker_synthetic_frame_rebuild",
        FRAME_GENERATOR_SCRIPT,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load canonical frame generator: {FRAME_GENERATOR_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FRAME_GENERATOR = _load_frame_generator()
FRAMES = ROOT / "docs" / "training" / "frames"
OUT = ROOT / "docs" / "training" / "synthetic"
EXPORTS = ROOT / "docs" / "training" / "exports"

CONDITIONS = ("day", "dusk", "night", "rain")
CLASSES = (
    ("manhole", "HIGH"),
    ("shadow_trap", "MEDIUM"),
    ("crack", "MEDIUM"),
    ("curb", "LOW"),
    ("trash_bin", "MEDIUM"),
    ("bench", "LOW"),
    ("bike", "MEDIUM"),
    ("pier_edge", "HIGH"),
)

AGGREGATE_NAME = "dt_ritual_all.jsonl"
MANIFEST_NAME = "dt_ritual_manifest.json"
EXPORT_MANIFEST_NAME = "v1_1_synthetic_manifest.json"
RITUAL_ID = "all_at_once_v1.1"
GENERATOR_ID = "eyewalker.synthetic.rebuild.v1"
DATASET_SCHEMA_VERSION = "1.1.0"
SAFETY_PREFIX = "SIMULATED RESEARCH CUE:"
SAFETY_SUFFIX = "Keep your cane or guide dog. Not a medical device."
TWIN_COUNT = 3
LEFT_RIGHT_CONVENTION = (
    "bearing < -8 degrees: step right; bearing > +8 degrees: step left; "
    "bearing in [-8, +8] degrees: HOLD and stop-and-verify"
)


def _load_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _software_version(root: Path) -> str:
    version_path = root / "VERSION"
    if version_path.is_symlink():
        raise ValueError(f"VERSION must not be a symlink: {version_path}")
    try:
        version = version_path.read_text().strip()
    except OSError as exc:
        raise ValueError(f"cannot read VERSION: {version_path}") from exc
    if not version:
        raise ValueError("VERSION must not be empty")
    return version


def _repo_root(root: Path) -> Path:
    try:
        resolved = root.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"repository root does not exist: {root}") from exc
    if not resolved.is_dir():
        raise ValueError(f"repository root is not a directory: {root}")
    return resolved


def _relative_to_repo(path: Path, root: Path, *, description: str) -> Path:
    """Resolve ``path`` and prove its real target is inside ``root``."""

    root_resolved = _repo_root(root)
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f"{description} does not exist: {path}") from exc
    try:
        relative = resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(
            f"{description} resolves outside repository root: {path} -> {resolved}"
        ) from exc
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"{description} is not repo-relative: {path}")
    return relative


def _discover_frames(frames_dir: Path, root: Path) -> list[Path]:
    relative_dir = _relative_to_repo(
        frames_dir,
        root,
        description="source-frame directory",
    )
    resolved_dir = _repo_root(root) / relative_dir
    if not resolved_dir.is_dir():
        raise ValueError(f"source-frame path is not a directory: {frames_dir}")
    records = FRAME_GENERATOR.validate_fixture_directory(resolved_dir)
    frames = [record[0] for record in records]
    if len(frames) != FRAME_GENERATOR.FRAME_COUNT:
        raise ValueError(
            "canonical source-frame count invariant failed: "
            f"{len(frames)} != {FRAME_GENERATOR.FRAME_COUNT}"
        )
    return frames


def _source_record(frame: Path, root: Path) -> tuple[str, str, bytes]:
    relative = _relative_to_repo(frame, root, description="source frame")
    resolved = _repo_root(root) / relative
    if not resolved.is_file():
        raise ValueError(f"source frame is not a regular file: {frame}")
    try:
        raw = resolved.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read source frame: {frame}") from exc
    digest = hashlib.sha256(raw).hexdigest()
    return relative.as_posix(), digest, raw


def _source_path(frame: Path, root: Path) -> str:
    """Compatibility helper returning a validated, resolved repo-relative path."""

    source_frame, _, _ = _source_record(frame, root)
    return source_frame


def _label_name(source_frame: str, condition: str, twin: int) -> str:
    return f"{Path(source_frame).stem}_{condition}_t{twin}.json"


def _assert_unique_source_stems(frames: Iterable[Path]) -> None:
    """Reject inputs that would map to the same case-insensitive label name."""

    seen: dict[str, Path] = {}
    for frame in frames:
        key = frame.stem.casefold()
        previous = seen.get(key)
        if previous is not None:
            raise ValueError(
                "duplicate source-frame stem would overwrite labels: "
                f"{previous.name!r} and {frame.name!r}"
            )
        seen[key] = frame


def _is_owned_row(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    dt9 = payload.get("dt9")
    return (
        isinstance(dt9, dict)
        and dt9.get("ritual") == RITUAL_ID
        and dt9.get("synthetic_only") is True
        and dt9.get("research_prototype") is True
        and dt9.get("not_medical_device") is True
        and isinstance(payload.get("source_frame"), str)
        and payload.get("condition") in CONDITIONS
        and isinstance(payload.get("twin_id"), int)
    )


def _is_owned_label(path: Path) -> bool:
    return not path.is_symlink() and path.is_file() and _is_owned_row(_load_json(path))


def _is_owned_manifest(path: Path) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    payload = _load_json(path)
    if not isinstance(payload, dict):
        return False
    if payload.get("generator_id") == GENERATOR_ID:
        return True
    # Recognize only the complete pre-generator-id manifest emitted by the
    # immediately preceding canonical rebuild, so it can be migrated safely.
    return (
        payload.get("synthetic_only") is True
        and payload.get("research_prototype") is True
        and payload.get("not_medical_device") is True
        and payload.get("conditions") == list(CONDITIONS)
        and payload.get("twins_per_condition") == TWIN_COUNT
        and isinstance(payload.get("n_frames"), int)
        and payload.get("n_rows") == payload.get("n_frames") * len(CONDITIONS) * TWIN_COUNT
        and payload.get("path_policy") == "repo-relative existing sources only"
        and "left_right_convention" in payload
        and (
            isinstance(payload.get("software_version"), str)
            or payload.get("version") == "v1.1.0"
        )
    )


def _is_owned_aggregate(path: Path) -> bool:
    if path.is_symlink() or not path.is_file():
        return False
    try:
        lines = [line for line in path.read_text().splitlines() if line.strip()]
        return bool(lines) and all(_is_owned_row(json.loads(line)) for line in lines)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False


def _validate_output_directory(path: Path, root: Path) -> Path:
    """Validate an output directory without creating or modifying it."""

    root_resolved = _repo_root(root)
    root_lexical = Path(os.path.abspath(root))
    output_lexical = Path(os.path.abspath(path))
    try:
        relative = output_lexical.relative_to(root_lexical)
    except ValueError as exc:
        raise ValueError(f"output directory is outside repository root: {path}") from exc
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"output directory is not repo-relative: {path}")

    cursor = root_lexical
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError(f"output path must not traverse a symlink: {cursor}")
        if cursor.exists() and not cursor.is_dir():
            raise ValueError(f"output path component is not a directory: {cursor}")

    existing = output_lexical
    while not existing.exists():
        if existing == root_lexical:
            break
        existing = existing.parent
    try:
        existing.resolve(strict=True).relative_to(root_resolved)
    except (OSError, ValueError) as exc:
        raise ValueError(f"output directory resolves outside repository root: {path}") from exc
    return output_lexical


def _variation_digest(source_sha256: str, condition: str, twin: int) -> bytes:
    seed_material = f"{source_sha256}\0{condition}\0{twin}\0{GENERATOR_ID}".encode()
    return hashlib.sha256(seed_material).digest()


def _rows_for_source(source_frame: str, source_sha256: str) -> list[dict]:
    rows: list[dict] = []
    for condition in CONDITIONS:
        for twin in range(TWIN_COUNT):
            variation = _variation_digest(source_sha256, condition, twin)
            cls, urgency = CLASSES[variation[0] % len(CLASSES)]
            bearing = (int.from_bytes(variation[1:3], "big") % 601 - 300) / 10
            distance = round(
                0.7 + (int.from_bytes(variation[3:5], "big") % 231) / 100,
                2,
            )
            if bearing < -8:
                step = "right"
            elif bearing > 8:
                step = "left"
            else:
                step = None
            obstacle = {
                "class": cls,
                "distance_m": distance,
                "bearing_deg": bearing,
                "urgency": urgency,
                "source": f"dt_{condition}_t{twin}",
                "simulated": True,
            }
            row = {
                "source_frame": source_frame,
                "source_sha256": source_sha256,
                "condition": condition,
                "twin_id": twin,
                "modulators": {"lighting": condition, "bound": [0.25, 3.0]},
                "obstacles": [obstacle],
                "guidance": (
                    f"{SAFETY_PREFIX} {cls.replace('_', ' ').upper()} "
                    f"{distance}m ahead (bearing {bearing:+.1f}\N{DEGREE SIGN}), "
                    + (
                        f"step {step}. "
                        if step is not None
                        else "centered or ambiguous bearing; HOLD and stop and verify. "
                    )
                    + SAFETY_SUFFIX
                ),
                "provenance": {
                    "generator_id": GENERATOR_ID,
                    "source_sha256": source_sha256,
                },
                "dt9": {
                    "synthetic_only": True,
                    "research_prototype": True,
                    "not_medical_device": True,
                    "ritual": RITUAL_ID,
                },
            }
            rows.append(row)
    return rows


def _json_bytes(payload: object, *, compact: bool = False) -> bytes:
    if compact:
        return (json.dumps(payload, separators=(",", ":")) + "\n").encode()
    return (json.dumps(payload, indent=2) + "\n").encode()


def _existing_casefold_entries(directory: Path) -> dict[str, list[Path]]:
    if not directory.exists():
        return {}
    entries: dict[str, list[Path]] = {}
    for path in directory.iterdir():
        entries.setdefault(path.name.casefold(), []).append(path)
    return entries


def _preflight_target(
    target: Path,
    *,
    kind: str,
    existing_entries: dict[str, list[Path]],
) -> None:
    matches = existing_entries.get(target.name.casefold(), [])
    if len(matches) > 1 or (matches and matches[0].name != target.name):
        names = ", ".join(sorted(path.name for path in matches))
        raise ValueError(
            f"case-insensitive output collision for {target.name!r}: {names}"
        )
    if not matches:
        return

    existing = matches[0]
    if existing.is_symlink() or not existing.is_file():
        raise ValueError(f"unowned output collision at {existing}")
    owned = {
        "label": _is_owned_label,
        "manifest": _is_owned_manifest,
        "aggregate": _is_owned_aggregate,
    }[kind](existing)
    if not owned:
        raise ValueError(f"unowned output collision at {existing}")


def _preflight_outputs(
    contents: dict[Path, bytes],
    kinds: dict[Path, str],
    *,
    out_dir: Path,
    exports_dir: Path,
) -> list[Path]:
    """Validate all target collisions and plan stale owned-label removals."""

    target_keys: dict[str, Path] = {}
    for target in contents:
        key = os.path.normcase(str(target)).casefold()
        previous = target_keys.get(key)
        if previous is not None:
            raise ValueError(f"generated outputs collide: {previous} and {target}")
        target_keys[key] = target

    entries_by_dir = {
        out_dir: _existing_casefold_entries(out_dir),
        exports_dir: _existing_casefold_entries(exports_dir),
    }
    for target in contents:
        _preflight_target(
            target,
            kind=kinds[target],
            existing_entries=entries_by_dir[target.parent],
        )

    expected_label_names = {
        target.name.casefold()
        for target, kind in kinds.items()
        if target.parent == out_dir and kind == "label"
    }
    stale_owned_labels: list[Path] = []
    if out_dir.exists():
        for path in out_dir.iterdir():
            if (
                path.name.casefold() not in expected_label_names
                and path.name != MANIFEST_NAME
                and path.suffix.casefold() == ".json"
                and _is_owned_label(path)
            ):
                stale_owned_labels.append(path)
    return stale_owned_labels


def _replace_atomically(contents: dict[Path, bytes]) -> None:
    """Stage all bytes, then atomically replace each already-preflighted target."""

    staged: list[tuple[Path, Path]] = []
    try:
        for target, data in contents.items():
            descriptor, temporary_name = tempfile.mkstemp(
                prefix=f".{target.name}.",
                suffix=".tmp",
                dir=target.parent,
            )
            temporary = Path(temporary_name)
            os.fchmod(descriptor, 0o644)
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            staged.append((temporary, target))
        for temporary, target in staged:
            os.replace(temporary, target)
    finally:
        for temporary, _ in staged:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _frame_records(frames: Iterable[Path], root: Path) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []
    resolved_sources: dict[str, Path] = {}
    for frame in frames:
        source_frame, source_sha256, _ = _source_record(frame, root)
        previous = resolved_sources.get(source_frame.casefold())
        if previous is not None:
            raise ValueError(
                f"duplicate resolved source frame: {previous} and {frame}"
            )
        resolved_sources[source_frame.casefold()] = frame
        records.append((source_frame, source_sha256))
    return records


def _label_contents(rows: Iterable[dict], out_dir: Path) -> dict[Path, bytes]:
    contents: dict[Path, bytes] = {}
    names: dict[str, str] = {}
    for row in rows:
        name = _label_name(row["source_frame"], row["condition"], row["twin_id"])
        previous = names.get(name.casefold())
        if previous is not None:
            raise ValueError(f"generated label filenames collide: {previous!r} and {name!r}")
        names[name.casefold()] = name
        contents[out_dir / name] = _json_bytes(row)
    return contents


def ritual_for_frame(
    path: Path,
    out_dir: Path,
    *,
    root: Path = ROOT,
) -> list[dict]:
    """Legacy one-frame API with the same containment and ownership safeguards."""

    root_resolved = _repo_root(root)
    canonical_frames = _discover_frames(path.parent, root_resolved)
    requested = path.resolve(strict=True)
    if requested not in {frame.resolve(strict=True) for frame in canonical_frames}:
        raise ValueError(f"source frame is not a canonical owned fixture: {path}")
    output = _validate_output_directory(out_dir, root_resolved)
    source_frame, source_sha256, _ = _source_record(path, root_resolved)
    rows = _rows_for_source(source_frame, source_sha256)
    contents = _label_contents(rows, output)
    kinds = {target: "label" for target in contents}
    stale = _preflight_outputs(
        contents,
        kinds,
        out_dir=output,
        exports_dir=output,
    )
    if stale:
        # A one-frame compatibility call must never prune another frame's labels.
        stale = []
    output.mkdir(parents=True, exist_ok=True)
    _replace_atomically(contents)
    return rows


def rebuild(
    *,
    root: Path = ROOT,
    frames_dir: Path = FRAMES,
    out_dir: Path = OUT,
    exports_dir: Path = EXPORTS,
) -> dict:
    root_resolved = _repo_root(root)
    frames = _discover_frames(frames_dir, root_resolved)
    _assert_unique_source_stems(frames)
    records = _frame_records(frames, root_resolved)
    if len(records) != FRAME_GENERATOR.FRAME_COUNT:
        raise ValueError(
            "canonical source-frame count invariant failed: "
            f"{len(records)} != {FRAME_GENERATOR.FRAME_COUNT}"
        )

    rows = [
        row
        for source_frame, source_sha256 in records
        for row in _rows_for_source(source_frame, source_sha256)
    ]
    expected_rows = len(records) * len(CONDITIONS) * TWIN_COUNT
    if len(rows) != expected_rows:
        raise ValueError(f"row-count invariant failed: {len(rows)} != {expected_rows}")
    if any(
        SAFETY_PREFIX not in row["guidance"] or SAFETY_SUFFIX not in row["guidance"]
        for row in rows
    ):
        raise ValueError("safety cue invariant failed")

    output = _validate_output_directory(out_dir, root_resolved)
    exports = _validate_output_directory(exports_dir, root_resolved)
    if output == exports:
        raise ValueError("synthetic and export output directories must be distinct")

    aggregate_bytes = b"".join(_json_bytes(row, compact=True) for row in rows)
    manifest = {
        "generator_id": GENERATOR_ID,
        "software_version": _software_version(root_resolved),
        "dataset_schema_version": DATASET_SCHEMA_VERSION,
        "n_rows": len(rows),
        "n_frames": len(records),
        "conditions": list(CONDITIONS),
        "twins_per_condition": TWIN_COUNT,
        "synthetic_only": True,
        "research_prototype": True,
        "not_medical_device": True,
        "path_policy": "resolved repo-relative existing sources only",
        "source_fixture_contract": {
            "generator_id": FRAME_GENERATOR.FRAME_GENERATOR_ID,
            "count": FRAME_GENERATOR.FRAME_COUNT,
            "media_type": "image/png",
            "width": FRAME_GENERATOR.WIDTH,
            "height": FRAME_GENERATOR.HEIGHT,
            "metadata_free": True,
            "png_chunks": [kind.decode("ascii") for kind in FRAME_GENERATOR.PNG_CHUNK_CONTRACT],
            "ownership": "exact deterministic generator pixels and PNG structure",
            "watermark": FRAME_GENERATOR.WATERMARK,
        },
        "source_frames": [
            {"path": source_frame, "sha256": source_sha256}
            for source_frame, source_sha256 in records
        ],
        "aggregate_sha256": hashlib.sha256(aggregate_bytes).hexdigest(),
        "safety_cue_contract": f"{SAFETY_PREFIX} ... {SAFETY_SUFFIX}",
        "left_right_convention": LEFT_RIGHT_CONVENTION,
    }
    manifest_bytes = _json_bytes(manifest)

    contents = _label_contents(rows, output)
    kinds = {target: "label" for target in contents}
    aggregate = output / AGGREGATE_NAME
    local_manifest = output / MANIFEST_NAME
    export_manifest = exports / EXPORT_MANIFEST_NAME
    contents[aggregate] = aggregate_bytes
    kinds[aggregate] = "aggregate"
    contents[local_manifest] = manifest_bytes
    kinds[local_manifest] = "manifest"
    contents[export_manifest] = manifest_bytes
    kinds[export_manifest] = "manifest"

    # This validates every target and plans every deletion before mkdir/write/unlink.
    stale_owned_labels = _preflight_outputs(
        contents,
        kinds,
        out_dir=output,
        exports_dir=exports,
    )

    output.mkdir(parents=True, exist_ok=True)
    exports.mkdir(parents=True, exist_ok=True)
    _replace_atomically(contents)
    for stale in stale_owned_labels:
        stale.unlink()

    print(f"rebuilt {len(rows)} synthetic rows \N{RIGHTWARDS ARROW} {aggregate}")
    return manifest


def main() -> None:
    rebuild()


if __name__ == "__main__":
    main()
