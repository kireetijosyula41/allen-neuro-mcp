from pathlib import Path

import pytest

from allen_neuro_mcp.morphology.summary import compute_morphology_stats
from allen_neuro_mcp.morphology.swc import SWCNode, read_swc


FIXTURE = Path(__file__).parent / "fixtures" / "simple.swc"


def test_compute_morphology_stats_from_fixture() -> None:
    nodes = read_swc(FIXTURE)

    stats = compute_morphology_stats(nodes)

    assert stats.node_count == 6
    assert stats.edge_count == 5

    assert stats.soma_node_count == 1
    assert stats.axon_node_count == 0
    assert stats.basal_dendrite_node_count == 4
    assert stats.apical_dendrite_node_count == 1
    assert stats.unknown_node_count == 0

    assert stats.total_cable_length_um == 50.0
    assert stats.branch_point_count == 2
    assert stats.terminal_tip_count == 3
    assert stats.max_path_distance_um == 30.0

    assert stats.bounding_box_um == {
        "x": 20.0,
        "y": 30.0,
        "z": 0.0,
    }


def test_compute_morphology_stats_handles_empty_nodes() -> None:
    stats = compute_morphology_stats([])

    assert stats.node_count == 0
    assert stats.edge_count == 0
    assert stats.total_cable_length_um == 0.0
    assert stats.branch_point_count == 0
    assert stats.terminal_tip_count == 0
    assert stats.max_path_distance_um == 0.0
    assert stats.bounding_box_um == {
        "x": 0.0,
        "y": 0.0,
        "z": 0.0,
    }


def test_compute_morphology_stats_counts_unknown_node_types() -> None:
    nodes = [
        SWCNode(1, 1, 0.0, 0.0, 0.0, 5.0, -1),
        SWCNode(2, 99, 0.0, 10.0, 0.0, 1.0, 1),
    ]

    stats = compute_morphology_stats(nodes)

    assert stats.node_count == 2
    assert stats.unknown_node_count == 1
    assert stats.total_cable_length_um == 10.0


def test_compute_morphology_stats_rejects_missing_parent() -> None:
    nodes = [
        SWCNode(1, 1, 0.0, 0.0, 0.0, 5.0, -1),
        SWCNode(2, 3, 0.0, 10.0, 0.0, 1.0, 999),
    ]

    with pytest.raises(Exception):
        compute_morphology_stats(nodes)