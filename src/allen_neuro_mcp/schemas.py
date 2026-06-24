from typing import Any, Literal

from pydantic import BaseModel, Field

Species = Literal["mouse", "human"]


class Provenance(BaseModel):
    """
    Provenance information for a dataset, including the source and any relevant metadata.
    
    This is important because scientific tools should tell the user where the data 
    is coming from. They need to know what to cite and if the data is reputable and useful
    """
    provider: str = "Allen Institute"
    dataset: str = "Allen Cell Types Database"
    access_library: str = "AllenSDK"
    specimen_id: int | None = None
    

class CellSearchFilters(BaseModel):
    species: Species = Field(
        default="mouse",
        description="Species to search. v0 supports mouse and human Cell Types data.",
    )
    structure: str | None = Field(
        default=None,
        description=(
            "Case-insensitive brain structure name or acronym fragment, "
            "for example VISp, visual, motor, cortex."
        ),
    )
    dendrite_type: str | None = Field(
        default=None,
        description="Optional dendrite type filter, for example spiny, aspiny, or sparsely spiny.",
    )
    require_reconstruction: bool = Field(
        default=False,
        description="If true, only return cells with a morphology reconstruction.",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of candidate cells to return.",
    )

class CellSummary(BaseModel):
    """ 
    This is the information returned by the search

    Keep it small so that MCP resources do not flood model context with 
    raw Allen Institute data
    """
    specimen_id: int
    specimen_name: str | None = None
    species: str | None = None

    structure_name: str | None = None
    structure_acronym: str | None = None
    structure_area_id: int | None = None
    structure_layer_name: str | None = None

    dendrite_type: str | None = None
    cre_line: str | None = None

    has_reconstruction: bool = False


class CellSearchResponse(BaseModel):
    """
    Response from search_cell_types.
    """
    filters: CellSearchFilters
    returned: int
    cells: list[CellSummary]
    provenance: Provenance


class CellMetadataResponse(BaseModel):
    """
    Response from get_cell_metadata.

    Return both:
    1. normalized: stable, easy-to-read fields
    2. raw_metadata: original Allen metadata for transparency/debugging
    """
    specimen_id: int
    normalized: CellSummary
    raw_metadata: dict[str, Any]
    provenance: Provenance


class EphysFeatureResponse(BaseModel):
    """
    Response from get_cell_ephys_features.

    v0 returns Allen's precomputed electrophysiology features, not raw NWB traces.
    That keeps the tool response compact and useful for LLM interaction.
    """

    specimen_id: int
    feature_count: int
    features: dict[str, Any]
    provenance: Provenance


class ModelingBundle(BaseModel):
    """
    Response from prepare_modeling_bundle.

    This is the key object that makes the project more than an API wrapper:
    it represents a local artifact prepared for downstream modeling workflows.
    """

    specimen_id: int
    bundle_directory: str
    files: list[str]
    next_steps: list[str]
    provenance: Provenance


class ReconstructionDownloadResponse(BaseModel):
    """
    Response from download_cell_reconstruction.

    Represents a downloaded Allen morphology reconstruction file.
    """

    specimen_id: int
    reconstruction_path: str
    sha256: str
    provenance: Provenance


class MorphologySummary(BaseModel):
    """
    Response from summarize_cell_morphology.

    This converts an SWC morphology reconstruction into compact structural
    features that are useful for biological inspection and downstream modeling.
    """

    specimen_id: int

    node_count: int
    edge_count: int

    soma_node_count: int = 0
    axon_node_count: int = 0
    basal_dendrite_node_count: int = 0
    apical_dendrite_node_count: int = 0
    unknown_node_count: int = 0

    total_cable_length_um: float
    branch_point_count: int
    terminal_tip_count: int
    max_path_distance_um: float

    bounding_box_um: dict[str, float]

    warnings: list[str] = []
    provenance: Provenance