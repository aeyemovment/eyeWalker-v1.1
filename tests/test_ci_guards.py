import shutil
import subprocess
import sys
from pathlib import Path

import pytest


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/ci.yml"


def _step(name: str, next_name: str) -> str:
    text = WORKFLOW.read_text()
    return text.split(f"      - name: {name}\n", 1)[1].split(
        f"      - name: {next_name}\n", 1
    )[0]


def _python_heredoc(name: str, next_name: str) -> str:
    body = _step(name, next_name)
    source = body.split("          python - <<'PY'\n", 1)[1].rsplit("          PY\n", 1)[0]
    return "\n".join(
        line[10:] if line.startswith("          ") else line
        for line in source.splitlines()
    )


def _copy_version_fixture(destination: Path) -> None:
    root = WORKFLOW.parents[2]
    paths = (
        "VERSION",
        "pyproject.toml",
        "README.md",
        "SAFETY.md",
        "OPEN_SOURCE.md",
        "mobile/App.tsx",
        "mobile/app.json",
        "mobile/package.json",
        "docs/index.html",
        "docs/manifest.json",
        "docs/service-worker.js",
        "docs/pwa.html",
        "docs/training/synthetic/dt_ritual_manifest.json",
        "docs/training/exports/v1_1_synthetic_manifest.json",
        "eyewalker/nemoclaw/blueprint.yaml",
        "scripts/v11/Listen-to-me-rant-3.sh",
        "hf-space-final/app.py",
        "hf-space-final/README.md",
        "meta_submission/app.py",
        "meta_submission/README_HF.md",
        "meta_submission/llama_stack_tool.json",
    )
    for relative in paths:
        source = root / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _run_version_contract(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-"],
        cwd=root,
        input=_python_heredoc("Version surfaces aligned", "No root pwa.html duplicate"),
        text=True,
        capture_output=True,
        check=False,
    )


def test_install_step_has_no_tolerated_failure() -> None:
    body = _step("Install", "Unit tests")
    assert "|| true" not in body
    assert "pip install numpy pillow pytest" in body
    assert "pip install -e . --no-deps" in body


def test_frame_rebuild_precedes_dataset_and_uses_pillow_contract() -> None:
    text = WORKFLOW.read_text()
    frame_rebuild = text.index("      - name: Rebuild synthetic frames\n")
    frame_contract = text.index("      - name: Synthetic frame fixture contract\n")
    dataset_rebuild = text.index("      - name: Rebuild synthetic dataset\n")
    corpus_contract = text.index("      - name: Synthetic corpus contract and reproducibility\n")
    assert frame_rebuild < frame_contract < dataset_rebuild < corpus_contract
    assert "run: python scripts/v11/rebuild_synthetic_frames.py" in text
    assert "run: python scripts/v11/rebuild_synthetic_dataset.py" in text

    body = _step("Synthetic frame fixture contract", "Rebuild synthetic dataset")
    for guard in (
        "from PIL import Image",
        'expected_names = [f"fixture_{index:04d}.png" for index in range(1, 27)]',
        "assert len(paths) == 26",
        'png_signature = b"\\x89PNG\\r\\n\\x1a\\n"',
        'assert image.format == "PNG"',
        "image.verify()",
        "width >= 640 and height >= 480",
        "assert len(content_hashes) == 26",
    ):
        assert guard in body


def test_synthetic_contract_checks_semantics_and_extra_artifacts() -> None:
    body = _step("Synthetic corpus contract and reproducibility", "Version surfaces aligned")
    for guard in (
        'expected_software_version = "1.1.9"',
        'expected_schema_version = "1.1.0"',
        'expected_prefix = "SIMULATED RESEARCH CUE:"',
        'expected_suffix = "Keep your cane or guide dog. Not a medical device."',
        'obstacle["simulated"] is True',
        'row["provenance"] ==',
        "actual_out_paths == expected_out_paths",
        '"git", "ls-files", "--others", "-z"',
        '"docs/training/frames"',
        "git diff --exit-code --",
        "docs/training/frames \\",
        "docs/training/synthetic \\",
        "docs/training/exports",
        "collections.Counter",
    ):
        assert guard in body


def test_version_contract_parses_exact_values_instead_of_grep() -> None:
    body = _step("Version surfaces aligned", "No root pwa.html duplicate")
    assert "grep" not in body
    assert "tomllib.loads" in body
    assert "json.loads" in body
    assert "without_block_comments" in body
    assert "payload_blocks" in body
    assert "guarded_versions" in body
    assert "sw_versions == [expected]" in body
    assert "pwa_payload_versions == [expected]" in body
    assert "manifest == export" in body


@pytest.mark.parametrize(
    "surface",
    [
        "version_file",
        "toml_comment",
        "sw_comment",
        "pwa_comment",
        "mobile_package",
        "docs_manifest",
        "hf_app",
    ],
)
def test_version_contract_rejects_values_hidden_by_loose_grep(
    tmp_path: Path,
    surface: str,
) -> None:
    _copy_version_fixture(tmp_path)
    assert _run_version_contract(tmp_path).returncode == 0

    if surface == "version_file":
        (tmp_path / "VERSION").write_text("1.1.9\n0.0.0\n")
    elif surface == "toml_comment":
        path = tmp_path / "pyproject.toml"
        path.write_text(
            path.read_text().replace('version = "1.1.9"', 'version = "0.0.0"')
            + '\n# version = "1.1.9"\n'
        )
    elif surface == "sw_comment":
        path = tmp_path / "docs/service-worker.js"
        path.write_text(
            '/*\nconst CACHE = "eyewalker-v1.1.9";\n*/\n'
            + path.read_text().replace("eyewalker-v1.1.9", "eyewalker-v0.0.0")
        )
    elif surface == "pwa_comment":
        path = tmp_path / "docs/pwa.html"
        path.write_text(
            '<!--\nversion: "1.1.9",\n-->\n'
            + path.read_text().replace('version: "1.1.9",', 'version: "0.0.0",')
        )
    elif surface == "mobile_package":
        path = tmp_path / "mobile/package.json"
        path.write_text(path.read_text().replace('"version": "1.1.9"', '"version": "0.0.0"'))
    elif surface == "docs_manifest":
        path = tmp_path / "docs/manifest.json"
        path.write_text(path.read_text().replace("eyeWalker v1.1.9", "eyeWalker v0.0.0"))
    else:
        path = tmp_path / "hf-space-final/app.py"
        path.write_text(
            path.read_text().replace('VERSION = "1.1.9"', 'VERSION = "0.0.0"')
            + '\n# VERSION = "1.1.9"\n'
        )

    result = _run_version_contract(tmp_path)
    assert result.returncode != 0, result.stdout + result.stderr


def test_runtime_lifecycle_harness_remains_a_ci_gate() -> None:
    text = WORKFLOW.read_text()
    assert "run: node tests/pwa_lifecycle_harness.js" in text


def test_exact_license_contract_remains_a_ci_gate() -> None:
    text = WORKFLOW.read_text()
    assert "- name: License contracts exact" in text
    assert "pytest -q tests/test_license_contract.py" in text
