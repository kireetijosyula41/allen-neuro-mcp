import pytest

from allen_neuro_mcp.errors import CellNotFoundError
from allen_neuro_mcp.schemas import CellSearchFilters
from allen_neuro_mcp.services.cells import CellWorkflowService, normalize_cell

import json

from allen_neuro_mcp.cache import FileCache

from pathlib import Path

from allen_neuro_mcp.cache import FileCache


def test_normalize_cell_maps_raw_record_to_cell_summary(fake_client) -> None:
    raw = fake_client.get_cell(1)

    summary = normalize_cell(raw)

    assert summary.specimen_id == 1
    assert summary.specimen_name == "Mouse VISp spiny specimen"
    assert summary.structure_acronym == "VISp"
    assert summary.dendrite_type == "spiny"
    assert summary.cre_line == "Rbp4-Cre_KL100"
    assert summary.has_reconstruction is True


def test_search_filters_by_mouse_species(fake_client) -> None:
    service = CellWorkflowService(fake_client)

    response = service.search(
        CellSearchFilters(
            species="mouse",
            limit=10,
        )
    )

    assert response.returned == 2
    assert {cell.specimen_id for cell in response.cells} == {1, 2}


def test_search_filters_by_structure_acronym(fake_client) -> None:
    service = CellWorkflowService(fake_client)

    response = service.search(
        CellSearchFilters(
            species="mouse",
            structure="VISp",
            limit=10,
        )
    )

    assert response.returned == 1
    assert response.cells[0].specimen_id == 1
    assert response.cells[0].structure_acronym == "VISp"


def test_search_filters_by_structure_name_fragment(fake_client) -> None:
    service = CellWorkflowService(fake_client)

    response = service.search(
        CellSearchFilters(
            species="mouse",
            structure="motor",
            limit=10,
        )
    )

    assert response.returned == 1
    assert response.cells[0].specimen_id == 2
    assert response.cells[0].structure_acronym == "MOp"


def test_search_filters_by_dendrite_type(fake_client) -> None:
    service = CellWorkflowService(fake_client)

    response = service.search(
        CellSearchFilters(
            species="mouse",
            dendrite_type="aspiny",
            limit=10,
        )
    )

    assert response.returned == 1
    assert response.cells[0].specimen_id == 2
    assert response.cells[0].dendrite_type == "aspiny"


def test_search_can_require_reconstruction(fake_client) -> None:
    service = CellWorkflowService(fake_client)

    response = service.search(
        CellSearchFilters(
            species="mouse",
            require_reconstruction=True,
            limit=10,
        )
    )

    assert response.returned == 1
    assert response.cells[0].specimen_id == 1
    assert response.cells[0].has_reconstruction is True


def test_search_respects_limit(fake_client) -> None:
    service = CellWorkflowService(fake_client)

    response = service.search(
        CellSearchFilters(
            species="mouse",
            limit=1,
        )
    )

    assert response.returned == 1
    assert len(response.cells) == 1


def test_metadata_returns_normalized_and_raw_metadata(fake_client) -> None:
    service = CellWorkflowService(fake_client)

    response = service.metadata(1)

    assert response.specimen_id == 1
    assert response.normalized.structure_acronym == "VISp"
    assert response.raw_metadata["name"] == "Mouse VISp spiny specimen"
    assert response.provenance.specimen_id == 1


def test_ephys_features_removes_duplicate_specimen_id(fake_client) -> None:
    service = CellWorkflowService(fake_client)

    response = service.ephys_features(1)

    assert response.specimen_id == 1
    assert response.feature_count == 4
    assert "specimen_id" not in response.features
    assert response.features["adaptation"] == 0.12
    assert response.provenance.specimen_id == 1


def test_missing_cell_raises_clear_error(fake_client) -> None:
    service = CellWorkflowService(fake_client)

    with pytest.raises(CellNotFoundError):
        service.metadata(999)

def test_prepare_bundle_writes_modeling_artifact(fake_client, tmp_path: Path) -> None:
    service = CellWorkflowService(
        fake_client,
        cache=FileCache(tmp_path),
    )

    bundle = service.prepare_bundle(1)

    bundle_dir = Path(bundle.bundle_directory)

    assert bundle.specimen_id == 1
    assert bundle_dir.exists()

    assert (bundle_dir / "metadata.json").exists()
    assert (bundle_dir / "ephys_features.json").exists()
    assert (bundle_dir / "manifest.json").exists()
    assert (bundle_dir / "README.md").exists()

    assert set(bundle.files) == {
        "metadata.json",
        "ephys_features.json",
        "manifest.json",
        "README.md",
    }

def test_fake_client_saves_reconstruction(fake_client, tmp_path: Path) -> None:
    output_path = tmp_path / "reconstruction.swc"

    saved_path = fake_client.save_reconstruction(1, str(output_path))

    assert saved_path == str(output_path)
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").startswith("# simple test morphology")

import json
from pathlib import Path

from allen_neuro_mcp.cache import FileCache