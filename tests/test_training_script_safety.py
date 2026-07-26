"""Personal-media helpers must stay explicit and outside the public checkout."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load_train_module():
    path = ROOT / "scripts" / "v11" / "train_from_video.py"
    spec = importlib.util.spec_from_file_location("safe_train_from_video", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_path_containment_guard_distinguishes_repo_and_external(tmp_path):
    module = _load_train_module()
    assert module._is_within(ROOT / "docs" / "frame.jpg", ROOT)
    assert not module._is_within(tmp_path / "frame.jpg", ROOT)


def test_safe_prep_has_no_personal_media_discovery_or_error_masking():
    script = (ROOT / "scripts" / "v11" / "Listen-to-me-rant-3.sh").read_text()

    assert "Downloads" not in script
    assert "walk*.mp4" not in script
    assert "cp " not in script
    assert "|| true" not in script
    assert "rebuild_synthetic_frames.py" in script
    assert "rebuild_synthetic_dataset.py" in script


def test_video_wrapper_requires_explicit_source_and_external_destination():
    wrapper = (ROOT / "scripts" / "v11" / "train_from_video.sh").read_text()

    assert '"$#" -ne 2' in wrapper
    assert "--video" in wrapper
    assert "--output-dir" in wrapper
    assert "--seed-only" not in wrapper


def test_direct_extract_rejects_repo_source_before_subprocess(monkeypatch, tmp_path):
    module = _load_train_module()
    output = tmp_path / "frames"
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("invalid source reached ffmpeg"),
    )

    with pytest.raises(ValueError, match="outside the public repository"):
        module.extract_frames(
            ROOT / "README.md",
            output,
            repository_root=ROOT,
        )

    assert not output.exists()


def test_direct_extract_rejects_repo_output_before_mutation(monkeypatch, tmp_path):
    module = _load_train_module()
    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic placeholder")
    output = ROOT / "direct-api-output-must-not-exist"
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("invalid output reached ffmpeg"),
    )

    with pytest.raises(ValueError, match="outside the public repository"):
        module.extract_frames(source, output, repository_root=ROOT)

    assert not output.exists()


def test_direct_extract_rejects_source_symlink_and_nonfile(monkeypatch, tmp_path):
    module = _load_train_module()
    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic placeholder")
    source_link = tmp_path / "source-link.mp4"
    source_link.symlink_to(source)
    source_dir = tmp_path / "source-dir"
    source_dir.mkdir()
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("invalid source reached ffmpeg"),
    )

    with pytest.raises(ValueError, match="symbolic link"):
        module.extract_frames(
            source_link,
            tmp_path / "frames-link",
            repository_root=ROOT,
        )
    with pytest.raises(ValueError, match="regular file"):
        module.extract_frames(
            source_dir,
            tmp_path / "frames-dir",
            repository_root=ROOT,
        )

    assert not (tmp_path / "frames-link").exists()
    assert not (tmp_path / "frames-dir").exists()


def test_direct_extract_rejects_output_symlink_before_subprocess(monkeypatch, tmp_path):
    module = _load_train_module()
    source = tmp_path / "source.mp4"
    source.write_bytes(b"synthetic placeholder")
    target = tmp_path / "target"
    target.mkdir()
    output_link = tmp_path / "output-link"
    output_link.symlink_to(target, target_is_directory=True)
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("symlink output reached ffmpeg"),
    )

    with pytest.raises(ValueError, match="symbolic link"):
        module.extract_frames(source, output_link, repository_root=ROOT)

    assert list(target.iterdir()) == []
