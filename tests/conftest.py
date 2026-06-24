from typing import Any

from pathlib import Path
import shutil

import pytest

from allen_neuro_mcp.clients.base import AllenCellTypesClient
from allen_neuro_mcp.errors import CellNotFoundError


class FakeAllenClient(AllenCellTypesClient):
    """
    Fake Allen client for service-layer tests.

    This gives us stable, deterministic records without calling AllenSDK or the
    network.
    """

    cells = [
        {
            "id": 1,
            "name": "Mouse VISp spiny specimen",
            "species": "Mus musculus",
            "structure_name": "Primary visual area",
            "structure_area_abbrev": "VISp",
            "dendrite_type": "spiny",
            "transgenic_line": "Rbp4-Cre_KL100",
            "reconstruction_type": "full",
        },
        {
            "id": 2,
            "name": "Mouse MOp aspiny specimen",
            "species": "Mus musculus",
            "structure_name": "Primary motor area",
            "structure_area_abbrev": "MOp",
            "dendrite_type": "aspiny",
            "transgenic_line": None,
            "reconstruction_type": None,
        },
        {
            "id": 3,
            "name": "Human temporal cortex specimen",
            "species": "Homo Sapiens",
            "structure_name": "Middle temporal gyrus",
            "structure_area_abbrev": "MTG",
            "dendrite_type": "spiny",
            "transgenic_line": None,
            "reconstruction_type": "full",
        },
    ]

    def list_cells(
        self,
        *,
        species: str,
        require_reconstruction: bool,
    ) -> list[dict[str, Any]]:
        if species == "mouse":
            species_name = "Mus musculus"
        elif species == "human":
            species_name = "Homo Sapiens"
        else:
            species_name = species

        rows = [
            row
            for row in self.cells
            if row["species"] == species_name
        ]

        if require_reconstruction:
            rows = [
                row
                for row in rows
                if row["reconstruction_type"] is not None
            ]

        return rows

    def get_cell(self, specimen_id: int) -> dict[str, Any]:
        for row in self.cells:
            if row["id"] == specimen_id:
                return row

        raise CellNotFoundError(
            f"No fake specimen found for id={specimen_id}."
        )

    def get_ephys_features(self, specimen_id: int) -> dict[str, Any]:
        if specimen_id not in {1, 2, 3}:
            raise CellNotFoundError(
                f"No fake ephys features found for id={specimen_id}."
            )

        return {
            "specimen_id": specimen_id,
            "rheobase_sweep_number": 12,
            "adaptation": 0.12,
            "avg_isi": 42.5,
            "input_resistance_mohm": 180.0,
        }
    
    def save_reconstruction(self, specimen_id: int, file_path: str) -> str:
        """
        Fake reconstruction download.

        Copies tests/fixtures/simple.swc into the requested output path.
        """

        # Make sure the specimen exists.
        self.get_cell(specimen_id)

        source = Path(__file__).parent / "fixtures" / "simple.swc"
        destination = Path(file_path)

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)

        return str(destination)


@pytest.fixture
def fake_client() -> FakeAllenClient:
    return FakeAllenClient()