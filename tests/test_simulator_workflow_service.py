from pathlib import Path

import pytest

from allen_neuro_mcp.cache import FileCache
from allen_neuro_mcp.services.cells import CellWorkflowService
from allen_neuro_mcp.services.simulators import SimulatorWorkflowService


def test_generate_neuron_project_with_fake_client(
    fake_client,
    tmp_path: Path,
) -> None:
    cache = FileCache(tmp_path)

    cell_service = CellWorkflowService(
        fake_client,
        cache=cache,
    )

    sim_service = SimulatorWorkflowService(
        cell_service,
        cache=cache,
    )

    project = sim_service.generate_project(
        specimen_id=1,
        simulator="neuron",
    )

    project_dir = Path(project.project_directory)

    assert project.specimen_id == 1
    assert project.simulator == "neuron"
    assert project_dir.exists()

    assert (project_dir / "run.py").exists()
    assert (project_dir / "README.md").exists()
    assert (project_dir / "requirements.txt").exists()
    assert (project_dir / "manifest.json").exists()

    assert (project_dir / "metadata.json").exists()
    assert (project_dir / "ephys_features.json").exists()
    assert (project_dir / "morphology_summary.json").exists()
    assert (project_dir / "reconstruction.swc").exists()

    assert project.entrypoint == "run.py"
    assert "run.py" in project.files
    assert "reconstruction.swc" in project.files


def test_generate_project_rejects_unsupported_simulator(
    fake_client,
    tmp_path: Path,
) -> None:
    cache = FileCache(tmp_path)

    cell_service = CellWorkflowService(
        fake_client,
        cache=cache,
    )

    sim_service = SimulatorWorkflowService(
        cell_service,
        cache=cache,
    )

    with pytest.raises(ValueError, match="Unsupported simulator"):
        sim_service.generate_project(
            specimen_id=1,
            simulator="brian2",
        )