from pathlib import Path
from typing import Protocol

from allen_neuro_mcp.schemas import SimulatorProject


class SimulatorProjectBuilder(Protocol):
    """
    Interface for simulator-specific project builders.

    A builder takes an existing Allen modeling bundle and creates a local
    simulator starter project from it.

    v0.3 will implement NEURON first. Future versions can add Brian2 or other
    simulator backends without changing the workflow service contract.
    """

    def build(
        self,
        *,
        specimen_id: int,
        bundle_directory: Path,
        output_directory: Path,
    ) -> SimulatorProject:
        """
        Build a simulator project for one Allen Cell Types specimen.

        Args:
            specimen_id: Allen Cell Types specimen ID.
            bundle_directory: Path to an existing morphology-aware modeling bundle.
            output_directory: Directory where the simulator project should be written.

        Returns:
            SimulatorProject describing the generated project.
        """
        ...