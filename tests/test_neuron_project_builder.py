import json
import py_compile
from pathlib import Path

import pytest

from allen_neuro_mcp.simulators.neuron import NEURONProjectBuilder


REQUIRED_BUNDLE_FILES = [
    "metadata.json",
    "ephys_features.json",
    "morphology_summary.json",
    "reconstruction.swc",
]


def make_fake_bundle(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)

    metadata = {
        "normalized": {
            "specimen_id": 1,
            "specimen_name": "Fake VISp specimen",
            "species": "Mus musculus",
            "structure_acronym": "VISp",
            "structure_layer_name": "5",
            "dendrite_type": "spiny",
            "cre_line": "Fake-Cre",
        }
    }

    ephys_features = {
        "features": {
            "vrest": -70.0,
            "input_resistance_mohm": 180.0,
            "tau": 20.0,
            "sag": 0.03,
            "adaptation": 0.1,
            "threshold_i_long_square": 70.0,
            "threshold_v_long_square": -40.0,
            "rheobase_sweep_number": 33,
        }
    }

    morphology_summary = {
        "node_count": 6,
        "edge_count": 5,
        "total_cable_length_um": 50.0,
        "branch_point_count": 2,
        "terminal_tip_count": 3,
        "max_path_distance_um": 30.0,
        "warnings": ["Fake morphology warning."],
    }

    reconstruction = (
        "# simple test morphology\n"
        "1 1 0 0 0 5 -1\n"
        "2 3 0 10 0 1 1\n"
    )

    (path / "metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )
    (path / "ephys_features.json").write_text(
        json.dumps(ephys_features),
        encoding="utf-8",
    )
    (path / "morphology_summary.json").write_text(
        json.dumps(morphology_summary),
        encoding="utf-8",
    )
    (path / "reconstruction.swc").write_text(
        reconstruction,
        encoding="utf-8",
    )

    return path


def test_neuron_project_builder_generates_expected_files(tmp_path: Path) -> None:
    bundle_dir = make_fake_bundle(tmp_path / "bundle")
    output_dir = tmp_path / "sim_projects" / "1" / "neuron"

    builder = NEURONProjectBuilder()
    project = builder.build(
        specimen_id=1,
        bundle_directory=bundle_dir,
        output_directory=output_dir,
    )

    assert project.specimen_id == 1
    assert project.simulator == "neuron"
    assert Path(project.project_directory) == output_dir.resolve()
    assert project.entrypoint == "run.py"

    for file_name in [
        *REQUIRED_BUNDLE_FILES,
        "README.md",
        "requirements.txt",
        "run.py",
        "manifest.json",
    ]:
        assert (output_dir / file_name).exists()
        assert file_name in project.files


def test_generated_run_py_compiles(tmp_path: Path) -> None:
    bundle_dir = make_fake_bundle(tmp_path / "bundle")
    output_dir = tmp_path / "project"

    builder = NEURONProjectBuilder()
    builder.build(
        specimen_id=1,
        bundle_directory=bundle_dir,
        output_directory=output_dir,
    )

    py_compile.compile(str(output_dir / "run.py"), doraise=True)


def test_manifest_records_source_bundle_and_warnings(tmp_path: Path) -> None:
    bundle_dir = make_fake_bundle(tmp_path / "bundle")
    output_dir = tmp_path / "project"

    builder = NEURONProjectBuilder()
    builder.build(
        specimen_id=1,
        bundle_directory=bundle_dir,
        output_directory=output_dir,
    )

    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == "0.3"
    assert manifest["project_type"] == "neuron-starter-scaffold"
    assert manifest["specimen_id"] == 1
    assert manifest["simulator"] == "neuron"
    assert manifest["source_bundle_directory"] == str(bundle_dir.resolve())
    assert "This is a starter scaffold, not a fitted biophysical model." in manifest["warnings"]


def test_neuron_project_builder_rejects_missing_bundle_files(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "incomplete_bundle"
    bundle_dir.mkdir()

    (bundle_dir / "metadata.json").write_text(
        "{}",
        encoding="utf-8",
    )

    builder = NEURONProjectBuilder()

    with pytest.raises(FileNotFoundError, match="missing required files"):
        builder.build(
            specimen_id=1,
            bundle_directory=bundle_dir,
            output_directory=tmp_path / "project",
        )