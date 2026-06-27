from __future__ import annotations

from pathlib import Path

from allen_neuro_mcp.cache import FileCache
from allen_neuro_mcp.schemas import SimulatorProject
from allen_neuro_mcp.services.cells import CellWorkflowService
from allen_neuro_mcp.simulators.neuron import NEURONProjectBuilder


class SimulatorWorkflowService:
    """
    Workflow service for generating simulator starter projects.

    This service bridges v0.2 morphology-aware Allen bundles into v0.3
    simulator-specific project scaffolds.
    """

    def __init__(
        self,
        cell_service: CellWorkflowService,
        cache: FileCache | None = None,
    ) -> None:
        self.cell_service = cell_service
        self.cache = cache or FileCache()

    def generate_project(
        self,
        specimen_id: int,
        simulator: str = "neuron",
    ) -> SimulatorProject:
        """
        Generate a local simulator starter project for one Allen Cell Types specimen.

        v0.3 supports NEURON only.
        """

        if simulator != "neuron":
            raise ValueError(
                f"Unsupported simulator: {simulator!r}. "
                "v0.3 currently supports only simulator='neuron'."
            )

        bundle = self.cell_service.prepare_bundle(
            specimen_id,
            include_morphology=True,
        )

        bundle_directory = Path(bundle.bundle_directory)

        output_directory = (
            self.cache.root
            / "sim_projects"
            / str(specimen_id)
            / "neuron"
        )

        builder = NEURONProjectBuilder()

        return builder.build(
            specimen_id=specimen_id,
            bundle_directory=bundle_directory,
            output_directory=output_directory,
        )