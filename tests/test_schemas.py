from allen_neuro_mcp.schemas import (
    MorphologySummary,
    Provenance,
    ReconstructionDownloadResponse,
    SimulatorProject,
)

import pytest


def test_simulator_project_serializes() -> None:
    project = SimulatorProject(
        specimen_id=123,
        simulator="neuron",
        project_directory="/tmp/sim_projects/123/neuron",
        files=[
            "run.py",
            "README.md",
            "requirements.txt",
            "manifest.json",
            "reconstruction.swc",
            "metadata.json",
            "ephys_features.json",
            "morphology_summary.json",
        ],
        entrypoint="run.py",
        run_instructions=[
            "Create a fresh Python environment.",
            "Install requirements with pip install -r requirements.txt.",
            "Run python run.py.",
        ],
        warnings=[
            "This is a starter scaffold, not a fitted biophysical model.",
        ],
        provenance=Provenance(specimen_id=123),
    )

    dumped = project.model_dump(mode="json")

    assert dumped["specimen_id"] == 123
    assert dumped["simulator"] == "neuron"
    assert dumped["entrypoint"] == "run.py"
    assert "run.py" in dumped["files"]
    assert dumped["warnings"] == [
        "This is a starter scaffold, not a fitted biophysical model.",
    ]
    assert dumped["provenance"]["specimen_id"] == 123

def test_simulator_project_rejects_unsupported_simulator() -> None:
    try:
        SimulatorProject(
            specimen_id=123,
            simulator="brian2",
            project_directory="/tmp/sim_projects/123/brian2",
            files=[],
            entrypoint="run.py",
            run_instructions=[],
            provenance=Provenance(specimen_id=123),
        )
    except Exception as exc:
        assert "literal_error" in str(exc) or "Input should be 'neuron'" in str(exc)
    else:
        raise AssertionError("Expected SimulatorProject to reject unsupported simulator.")


def test_reconstruction_download_response_serializes() -> None:
    response = ReconstructionDownloadResponse(
        specimen_id=123,
        reconstruction_path="/tmp/reconstruction.swc",
        sha256="abc123",
        provenance=Provenance(specimen_id=123),
    )

    dumped = response.model_dump(mode="json")

    assert dumped["specimen_id"] == 123
    assert dumped["reconstruction_path"] == "/tmp/reconstruction.swc"
    assert dumped["sha256"] == "abc123"
    assert dumped["provenance"]["provider"] == "Allen Institute"


def test_morphology_summary_serializes() -> None:
    summary = MorphologySummary(
        specimen_id=123,
        node_count=6,
        edge_count=5,
        soma_node_count=1,
        basal_dendrite_node_count=4,
        apical_dendrite_node_count=1,
        total_cable_length_um=50.0,
        branch_point_count=2,
        terminal_tip_count=3,
        max_path_distance_um=30.0,
        bounding_box_um={"x": 20.0, "y": 30.0, "z": 0.0},
        warnings=["Example warning."],
        provenance=Provenance(specimen_id=123),
    )

    dumped = summary.model_dump(mode="json")

    assert dumped["specimen_id"] == 123
    assert dumped["node_count"] == 6
    assert dumped["branch_point_count"] == 2
    assert dumped["bounding_box_um"]["x"] == 20.0
    assert dumped["warnings"] == ["Example warning."]
    assert dumped["provenance"]["specimen_id"] == 123