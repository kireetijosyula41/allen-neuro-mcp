from typing import Any, Protocol


class AllenCellTypesClient(Protocol):
    """
    Minimal interface required by the workflow layer.

    This is intentionally smaller than AllenSDK. The service layer should not
    know or care whether data comes from AllenSDK, a cached file, a database,
    or a fake test client.
    """

    def list_cells(self,*,species: str,require_reconstruction: bool,) -> list[dict[str, Any]]:
        """
        Return raw cell metadata records.
        """
        ...

    def get_cell(self, specimen_id: int) -> dict[str, Any]:
        """
        Return raw metadata for a single specimen.
        """
        ...

    def get_ephys_features(self, specimen_id: int) -> dict[str, Any]:
        """
        Return precomputed electrophysiology features for a single specimen.
        """
        ...
    
    def save_reconstruction(self, specimen_id: int, file_path: str) -> str:
        """
        Save the morphology reconstruction for a specimen as an SWC file.

        Returns the path where the reconstruction was saved.
        """
        ...