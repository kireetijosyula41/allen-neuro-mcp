import pytest

from allen_neuro_mcp.clients.sdk import AllenSDKCellTypesClient


def test_to_allen_species_mouse() -> None:
    assert AllenSDKCellTypesClient._to_allen_species("mouse") == "Mus musculus"


def test_to_allen_species_human() -> None:
    assert AllenSDKCellTypesClient._to_allen_species("human") == "Homo Sapiens"


def test_to_allen_species_rejects_unknown_species() -> None:
    with pytest.raises(ValueError):
        AllenSDKCellTypesClient._to_allen_species("rat")