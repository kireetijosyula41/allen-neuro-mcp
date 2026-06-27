from pathlib import Path

from allen_neuro_mcp.schemas import Provenance, SimulatorProject
from allen_neuro_mcp.simulators.base import SimulatorProjectBuilder


class FakeSimulatorProjectBuilder:
    def build(
        self,
        *,
        specimen_id: int,
        bundle_directory: Path,
        output_directory: Path,
    ) -> SimulatorProject:
        output_directory.mkdir(parents=True, exist_ok=True)

        return SimulatorProject(
            specimen_id=specimen_id,
            simulator="neuron",
            project_directory=str(output_directory),
            files=[],
            entrypoint="run.py",
            run_instructions=["Run python run.py."],
            warnings=["Fake builder for tests."],
            provenance=Provenance(specimen_id=specimen_id),
        )


def test_fake_builder_matches_project_builder_protocol(tmp_path: Path) -> None:
    builder: SimulatorProjectBuilder = FakeSimulatorProjectBuilder()

    project = builder.build(
        specimen_id=123,
        bundle_directory=tmp_path / "bundle",
        output_directory=tmp_path / "project",
    )

    assert project.specimen_id == 123
    assert project.simulator == "neuron"
    assert project.project_directory.endswith("project")