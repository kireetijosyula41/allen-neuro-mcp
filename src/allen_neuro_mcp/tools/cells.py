from mcp.server.fastmcp import FastMCP

from allen_neuro_mcp.schemas import CellSearchFilters
from allen_neuro_mcp.services.cells import CellWorkflowService


def register_cell_tools(mcp: FastMCP, service: CellWorkflowService) -> None:
    @mcp.tool()
    def search_cell_types(
        species: str = "mouse",
        structure: str | None = None,
        dendrite_type: str | None = None,
        require_reconstruction: bool = False,
        limit: int = 20,
    ) -> dict:
        filters = CellSearchFilters(
            species=species,
            structure=structure,
            dendrite_type=dendrite_type,
            require_reconstruction=require_reconstruction,
            limit=limit,
        )
        return service.search(filters).model_dump(mode="json")

    @mcp.tool()
    def get_cell_metadata(specimen_id: int) -> dict:
        return service.metadata(specimen_id).model_dump(mode="json")

    @mcp.tool()
    def get_cell_ephys_features(specimen_id: int) -> dict:
        return service.ephys_features(specimen_id).model_dump(mode="json")

    @mcp.tool()
    def download_cell_reconstruction(specimen_id: int) -> dict:
        return service.download_reconstruction(specimen_id).model_dump(mode="json")

    @mcp.tool()
    def summarize_cell_morphology(specimen_id: int) -> dict:
        return service.summarize_morphology(specimen_id).model_dump(mode="json")

    @mcp.tool()
    def prepare_modeling_bundle(
        specimen_id: int,
        include_morphology: bool = False,
    ) -> dict:
        return service.prepare_bundle(
            specimen_id,
            include_morphology=include_morphology,
        ).model_dump(mode="json")