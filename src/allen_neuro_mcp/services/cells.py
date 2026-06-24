from typing import Any

from allen_neuro_mcp.clients.base import AllenCellTypesClient
from allen_neuro_mcp.schemas import (
    CellMetadataResponse,
    CellSearchFilters,
    CellSearchResponse,
    CellSummary,
    EphysFeatureResponse,
    ModelingBundle,
    MorphologySummary,
    Provenance,
    ReconstructionDownloadResponse,
)

from pathlib import Path

from allen_neuro_mcp.morphology.summary import compute_morphology_stats
from allen_neuro_mcp.morphology.swc import read_swc

from allen_neuro_mcp.cache import FileCache, sha256_file
from allen_neuro_mcp.schemas import ModelingBundle


def _first(record: dict[str, Any], *keys: str) -> Any:
    """
    Return the first non-None value from a raw metadata record.

    Allen metadata field names can vary slightly depending on source/version.
    This lets us normalize defensively.
    """

    for key in keys:
        value = record.get(key)
        if value is not None:
            return value
    return None

def morphology_warnings_from_metadata(raw_metadata: dict[str, Any]) -> list[str]:
    """
    Generate human-readable morphology warnings from Allen metadata.
    """

    warnings: list[str] = []

    reconstruction_type = raw_metadata.get("reconstruction_type")
    if reconstruction_type and reconstruction_type != "full":
        warnings.append(
            f"Specimen reconstruction_type is {reconstruction_type!r}; "
            "this may not represent a complete morphology."
        )

    apical = raw_metadata.get("apical")
    if apical and apical != "intact":
        warnings.append(
            f"Specimen apical dendrite status is {apical!r}."
        )

    return warnings

def normalize_cell(record: dict[str, Any]) -> CellSummary:
    """
    Convert one raw Allen-style metadata record into our public CellSummary schema.
    """

    return CellSummary(
        specimen_id=int(record["id"]),
        specimen_name=_first(record, "name", "specimen_name"),
        species=_first(record, "species", "donor_species"),
        structure_name=_first(
            record,
            "structure_name",
            "structure",
        ),
        structure_acronym=_first(
            record,
            "structure_area_abbrev",
            "structure_acronym",
            "structure_abbrev",
        ),
        structure_area_id=_first(record, "structure_area_id"),
        structure_layer_name=_first(record, "structure_layer_name"),
        dendrite_type=_first(record, "dendrite_type"),
        cre_line=_first(record, "transgenic_line", "cre_line"),
        has_reconstruction=bool(
            _first(
                record,
                "reconstruction_type",
                "has_reconstruction",
                "nr__reconstruction_type",
            )
        ),   
    )


class CellWorkflowService:
    """
    Scientific workflow layer for Allen Cell Types data.

    This layer expresses our project identity: it turns raw Allen-style records
    into compact, workflow-ready responses for MCP tools.
    """

    def __init__(
        self,
        client: AllenCellTypesClient,
        cache: FileCache | None = None,
    ) -> None:
        self.client = client
        self.cache = cache or FileCache()

    def search(self, filters: CellSearchFilters) -> CellSearchResponse:
        raw_cells = self.client.list_cells(
            species=filters.species,
            require_reconstruction=filters.require_reconstruction,
        )

        cells = [normalize_cell(record) for record in raw_cells]

        if filters.structure:
            query = filters.structure.casefold()
            cells = [
                cell
                for cell in cells
                if query in (cell.structure_name or "").casefold()
                or query in (cell.structure_acronym or "").casefold()
            ]

        if filters.dendrite_type:
            query = filters.dendrite_type.casefold()
            cells = [
                cell
                for cell in cells
                if query in (cell.dendrite_type or "").casefold()
            ]

        cells = cells[: filters.limit]

        return CellSearchResponse(
            filters=filters,
            returned=len(cells),
            cells=cells,
            provenance=Provenance(),
        )

    def metadata(self, specimen_id: int) -> CellMetadataResponse:
        raw = self.client.get_cell(specimen_id)

        return CellMetadataResponse(
            specimen_id=specimen_id,
            normalized=normalize_cell(raw),
            raw_metadata=raw,
            provenance=Provenance(specimen_id=specimen_id),
        )

    def ephys_features(self, specimen_id: int) -> EphysFeatureResponse:
        features = self.client.get_ephys_features(specimen_id)

        # Avoid duplicating specimen_id in both the top-level field and features.
        cleaned = {
            key: value
            for key, value in features.items()
            if key != "specimen_id"
        }

        return EphysFeatureResponse(
            specimen_id=specimen_id,
            feature_count=len(cleaned),
            features=cleaned,
            provenance=Provenance(specimen_id=specimen_id),
        )
    
    def download_reconstruction(self, specimen_id: int) -> ReconstructionDownloadResponse:
        """
        Download/save an Allen Cell Types morphology reconstruction as reconstruction.swc.
        """

        metadata = self.metadata(specimen_id)

        if not metadata.normalized.has_reconstruction:
            raise ValueError(
                f"Specimen {specimen_id} does not have a morphology reconstruction."
            )

        bundle_dir = self.cache.bundle_dir(specimen_id)
        reconstruction_path = bundle_dir / "reconstruction.swc"

        saved_path = self.client.save_reconstruction(
            specimen_id,
            str(reconstruction_path),
        )

        saved = reconstruction_path if reconstruction_path.exists() else Path(saved_path)

        return ReconstructionDownloadResponse(
            specimen_id=specimen_id,
            reconstruction_path=str(saved.resolve()),
            sha256=sha256_file(saved),
            provenance=Provenance(specimen_id=specimen_id),
        )
    
    def prepare_bundle(self, specimen_id: int, include_morphology: bool = False,) -> ModelingBundle:
        """
        Prepare a local modeling bundle for downstream workflows.

        v0.1:
        - metadata.json
        - ephys_features.json
        - manifest.json
        - README.md

        v0.2 with include_morphology=True:
        - reconstruction.swc
        - morphology_summary.json
        """
        metadata = self.metadata(specimen_id)
        ephys = self.ephys_features(specimen_id)

        bundle_dir = self.cache.bundle_dir(specimen_id)

        metadata_path = self.cache.write_json(
            bundle_dir / "metadata.json",
            metadata.model_dump(mode="json"),
        )

        ephys_path = self.cache.write_json(
            bundle_dir / "ephys_features.json",
            ephys.model_dump(mode="json"),
        )

        files: list[dict[str, str]] = [
            {
                "name": metadata_path.name,
                "type": "metadata",
                "sha256": sha256_file(metadata_path),
            },
            {
                "name": ephys_path.name,
                "type": "ephys_features",
                "sha256": sha256_file(ephys_path),
            },
        ]

        output_file_names = [
            metadata_path.name,
            ephys_path.name,
        ]

        warnings = morphology_warnings_from_metadata(metadata.raw_metadata)

        if include_morphology:
            reconstruction = self.download_reconstruction(specimen_id)
            morphology_summary = self.summarize_morphology(specimen_id)

            reconstruction_path = Path(reconstruction.reconstruction_path)
            morphology_summary_path = bundle_dir / "morphology_summary.json"

            files.extend(
                [
                    {
                        "name": reconstruction_path.name,
                        "type": "swc_morphology",
                        "sha256": reconstruction.sha256,
                    },
                    {
                        "name": morphology_summary_path.name,
                        "type": "morphology_summary",
                        "sha256": sha256_file(morphology_summary_path),
                    },
                ]
            )

            output_file_names.extend(
                [
                    reconstruction_path.name,
                    morphology_summary_path.name,
                ]
            )

            warnings.extend(morphology_summary.warnings)

        # Remove duplicate warnings while preserving order.
        warnings = list(dict.fromkeys(warnings))

        manifest = {
            "schema_version": "0.2",
            "bundle_type": "allen-cell-types-modeling-bundle",
            "specimen_id": specimen_id,
            "included_modalities": {
                "metadata": True,
                "ephys_features": True,
                "morphology_reconstruction": include_morphology,
                "morphology_summary": include_morphology,
                "nwb_ephys": False,
            },
            "files": files,
            "warnings": warnings,
            "provenance": metadata.provenance.model_dump(mode="json"),
        }

        manifest_path = self.cache.write_json(
            bundle_dir / "manifest.json",
            manifest,
        )

        readme = f"""# Allen Cell Types Modeling Bundle

    Specimen ID: {specimen_id}

    This bundle was generated by `allen-neuro-mcp`.

    ## Contents

    - `metadata.json`: normalized and raw Allen Cell Types metadata
    - `ephys_features.json`: Allen precomputed electrophysiology features
    - `manifest.json`: machine-readable bundle manifest
    - `README.md`: human-readable bundle notes
    """

        if include_morphology:
            readme += """
    - `reconstruction.swc`: Allen morphology reconstruction
    - `morphology_summary.json`: computed structural morphology summary
    """

        readme += f"""

    ## Included modalities

    - Metadata: yes
    - Ephys features: yes
    - Morphology reconstruction: {'yes' if include_morphology else 'no'}
    - Morphology summary: {'yes' if include_morphology else 'no'}
    - NWB ephys traces: no

    ## Warnings

    """

        if warnings:
            for warning in warnings:
                readme += f"- {warning}\n"
        else:
            readme += "- None.\n"

        readme += """
    ## Suggested next steps

    1. Review the cell metadata.
    2. Review electrophysiology features such as rheobase, input resistance, tau, vrest, sag, and adaptation.
    3. If morphology is included, inspect morphology_summary.json for cable length, branch points, terminal tips, and spatial spread.
    4. In v0.3, generate NEURON/Brian2 project scaffolds from this bundle.
    """

        readme_path = self.cache.write_text(
            bundle_dir / "README.md",
            readme,
        )

        output_file_names.extend(
            [
                manifest_path.name,
                readme_path.name,
            ]
        )

        return ModelingBundle(
            specimen_id=specimen_id,
            bundle_directory=str(bundle_dir.resolve()),
            files=output_file_names,
            next_steps=[
                "Review normalized metadata and raw Allen metadata.",
                "Review precomputed electrophysiology features.",
                "Inspect morphology summary if included.",
                "Generate simulator scaffolding in v0.3.",
            ],
            provenance=metadata.provenance,
        )
    
    def summarize_morphology(self, specimen_id: int) -> MorphologySummary:
        """
        Parse reconstruction.swc and compute compact morphology statistics.
        """

        metadata = self.metadata(specimen_id)
        download = self.download_reconstruction(specimen_id)

        reconstruction_path = Path(download.reconstruction_path)
        nodes = read_swc(reconstruction_path)
        stats = compute_morphology_stats(nodes)

        warnings = morphology_warnings_from_metadata(metadata.raw_metadata)

        summary = MorphologySummary(
            specimen_id=specimen_id,
            node_count=stats.node_count,
            edge_count=stats.edge_count,
            soma_node_count=stats.soma_node_count,
            axon_node_count=stats.axon_node_count,
            basal_dendrite_node_count=stats.basal_dendrite_node_count,
            apical_dendrite_node_count=stats.apical_dendrite_node_count,
            unknown_node_count=stats.unknown_node_count,
            total_cable_length_um=stats.total_cable_length_um,
            branch_point_count=stats.branch_point_count,
            terminal_tip_count=stats.terminal_tip_count,
            max_path_distance_um=stats.max_path_distance_um,
            bounding_box_um=stats.bounding_box_um,
            warnings=warnings,
            provenance=Provenance(specimen_id=specimen_id),
        )

        summary_path = self.cache.bundle_dir(specimen_id) / "morphology_summary.json"
        self.cache.write_json(
            summary_path,
            summary.model_dump(mode="json"),
        )

        return summary