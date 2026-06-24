from pathlib import Path

import pytest

from allen_neuro_mcp.morphology.swc import (
    SWCNode,
    SWCParseError,
    children_by_parent,
    euclidean_distance,
    nodes_by_id,
    read_swc,
    validate_parent_links,
)


FIXTURE = Path(__file__).parent / "fixtures" / "simple.swc"


def test_read_swc_parses_nodes() -> None:
    nodes = read_swc(FIXTURE)

    assert len(nodes) == 6

    first = nodes[0]
    assert first == SWCNode(
        node_id=1,
        node_type=1,
        x=0.0,
        y=0.0,
        z=0.0,
        radius=5.0,
        parent_id=-1,
    )


def test_nodes_by_id_indexes_nodes() -> None:
    nodes = read_swc(FIXTURE)

    indexed = nodes_by_id(nodes)

    assert indexed[1].node_type == 1
    assert indexed[3].parent_id == 2
    assert indexed[6].node_type == 4


def test_children_by_parent_groups_child_ids() -> None:
    nodes = read_swc(FIXTURE)

    children = children_by_parent(nodes)

    assert children[1] == [2, 6]
    assert children[2] == [3]
    assert children[3] == [4, 5]


def test_euclidean_distance_between_connected_nodes() -> None:
    nodes = nodes_by_id(read_swc(FIXTURE))

    assert euclidean_distance(nodes[1], nodes[2]) == 10.0
    assert euclidean_distance(nodes[3], nodes[4]) == 10.0


def test_validate_parent_links_accepts_valid_fixture() -> None:
    nodes = read_swc(FIXTURE)

    validate_parent_links(nodes)


def test_read_swc_rejects_invalid_column_count(tmp_path: Path) -> None:
    bad = tmp_path / "bad.swc"
    bad.write_text("1 1 0 0 0 5\n", encoding="utf-8")

    with pytest.raises(SWCParseError, match="expected 7 columns"):
        read_swc(bad)


def test_read_swc_rejects_invalid_numeric_value(tmp_path: Path) -> None:
    bad = tmp_path / "bad_numeric.swc"
    bad.write_text("1 1 0 0 nope 5 -1\n", encoding="utf-8")

    with pytest.raises(SWCParseError, match="Invalid numeric value"):
        read_swc(bad)


def test_nodes_by_id_rejects_duplicate_node_ids() -> None:
    nodes = [
        SWCNode(1, 1, 0.0, 0.0, 0.0, 5.0, -1),
        SWCNode(1, 3, 0.0, 10.0, 0.0, 1.0, 1),
    ]

    with pytest.raises(SWCParseError, match="Duplicate"):
        nodes_by_id(nodes)


def test_validate_parent_links_rejects_missing_parent() -> None:
    nodes = [
        SWCNode(1, 1, 0.0, 0.0, 0.0, 5.0, -1),
        SWCNode(2, 3, 0.0, 10.0, 0.0, 1.0, 999),
    ]

    with pytest.raises(SWCParseError, match="missing parent_id"):
        validate_parent_links(nodes)