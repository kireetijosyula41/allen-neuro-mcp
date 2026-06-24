from pathlib import Path
from typing import Any

from allen_neuro_mcp.errors import CellNotFoundError, DependencyUnavailableError


class AllenSDKCellTypesClient:
    """
    AllenSDK-backed implementation of AllenCellTypesClient.

    This class adapts AllenSDK's CellTypesCache to our smaller project-specific
    interface. The workflow layer should not import AllenSDK directly.
    """

    def __init__(self, manifest_file: Path | str | None = None) -> None:
        try:
            from allensdk.core.cell_types_cache import CellTypesCache
        except ImportError as exc:
            raise DependencyUnavailableError(
                "AllenSDK is not installed. Install it with: pip install allensdk"
            ) from exc

        if manifest_file is None:
            manifest_file = Path(".cache") / "allen-neuro-mcp" / "allensdk" / "manifest.json"

        manifest_path = Path(manifest_file).expanduser()
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        self._cache = CellTypesCache(manifest_file=str(manifest_path))

    def list_cells(
        self,
        *,
        species: str,
        require_reconstruction: bool,
    ) -> list[dict[str, Any]]:
        """
        Return Allen Cell Types metadata records.

        Our public API accepts 'mouse' or 'human'. AllenSDK expects formal species
        names like 'Mus musculus' and 'Homo Sapiens'.
        """

        allen_species = self._to_allen_species(species)

        cells = self._cache.get_cells(
            species=[allen_species],
            require_reconstruction=require_reconstruction,
        )

        return [dict(cell) for cell in cells]

    def get_cell(self, specimen_id: int) -> dict[str, Any]:
        """
        Return one cell metadata record by specimen id.
        """

        cells = self._cache.get_cells()

        for cell in cells:
            if int(cell["id"]) == specimen_id:
                return dict(cell)

        raise CellNotFoundError(
            f"No Allen Cell Types specimen found for id={specimen_id}."
        )

    def get_ephys_features(self, specimen_id: int) -> dict[str, Any]:
        """
        Return precomputed electrophysiology features for one specimen.
        """

        rows = self._cache.get_ephys_features()

        for row in rows:
            if int(row["specimen_id"]) == specimen_id:
                return dict(row)

        raise CellNotFoundError(
            f"No precomputed electrophysiology features found for id={specimen_id}."
        )
    
    def save_reconstruction(self, specimen_id: int, file_path: str) -> str:
        """
        Save an Allen Cell Types morphology reconstruction as an SWC file.

        Uses AllenSDK's CellTypesCache reconstruction download path.
        """

        path = Path(file_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._cache.get_reconstruction(
                specimen_id,
                file_name=str(path),
            )
        except TypeError:
            # Fallback for AllenSDK versions where get_reconstruction does not
            # accept file_name as expected.
            self._cache.api.save_reconstruction(specimen_id, str(path))

        return str(path)

    @staticmethod
    def _to_allen_species(species: str) -> str:
        normalized = species.casefold()

        if normalized == "mouse":
            return "Mus musculus"

        if normalized == "human":
            return "Homo Sapiens"

        raise ValueError(
            f"Unsupported species: {species!r}. Expected 'mouse' or 'human'."
        )