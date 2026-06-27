from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from allen_neuro_mcp.services.simulators import SimulatorWorkflowService


def register_simulator_tools(
    mcp: FastMCP,
    service: SimulatorWorkflowService,
) -> None:
    """
    Register simulator-generation MCP tools.
    """

    @mcp.tool()
    def generate_simulator_project(
        specimen_id: int,
        simulator: str = "neuron",
    ) -> dict:
        """
        Generate a local simulator starter project from an Allen Cell Types specimen.

        v0.3 supports NEURON project scaffolds.

        The generated project includes:
        - metadata.json
        - ephys_features.json
        - morphology_summary.json
        - reconstruction.swc
        - run.py
        - requirements.txt
        - README.md
        - manifest.json

        The generated NEURON scaffold is not a fitted biophysical model.
        """
        return service.generate_project(
            specimen_id=specimen_id,
            simulator=simulator,
        ).model_dump(mode="json")