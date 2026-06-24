from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from pathlib import Path


class SWCParseError(ValueError):
    """Raised when an SWC file contains an invalid row."""


@dataclass(frozen=True)
class SWCNode:
    """
    One node/compartment sample from an SWC morphology file.

    Standard SWC columns:
    node_id node_type x y z radius parent_id
    """

    node_id: int
    node_type: int
    x: float
    y: float
    z: float
    radius: float
    parent_id: int


def read_swc(path: Path | str) -> list[SWCNode]:
    """
    Read an SWC file into a list of SWCNode objects.

    Blank lines and comment lines beginning with '#' are ignored.
    """

    swc_path = Path(path)
    nodes: list[SWCNode] = []

    for line_number, raw_line in enumerate(
        swc_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        parts = line.split()

        if len(parts) != 7:
            raise SWCParseError(
                f"Invalid SWC row at line {line_number}: expected 7 columns, "
                f"found {len(parts)}. Row: {raw_line!r}"
            )

        try:
            node = SWCNode(
                node_id=int(parts[0]),
                node_type=int(parts[1]),
                x=float(parts[2]),
                y=float(parts[3]),
                z=float(parts[4]),
                radius=float(parts[5]),
                parent_id=int(parts[6]),
            )
        except ValueError as exc:
            raise SWCParseError(
                f"Invalid numeric value in SWC row at line {line_number}: {raw_line!r}"
            ) from exc

        nodes.append(node)

    return nodes

def nodes_by_id(nodes: list[SWCNode]) -> dict[int, SWCNode]:
    """
    Return nodes indexed by node_id.

    Raises SWCParseError if duplicate node IDs exist.
    """

    indexed: dict[int, SWCNode] = {}

    for node in nodes:
        if node.node_id in indexed:
            raise SWCParseError(f"Duplicate SWC node_id found: {node.node_id}")
        indexed[node.node_id] = node

    return indexed


def children_by_parent(nodes: list[SWCNode]) -> dict[int, list[int]]:
    """
    Return child node IDs grouped by parent node ID.
    """

    children: dict[int, list[int]] = {}

    for node in nodes:
        children.setdefault(node.parent_id, [])

        if node.parent_id != -1:
            children.setdefault(node.parent_id, []).append(node.node_id)

    return children


def euclidean_distance(a: SWCNode, b: SWCNode) -> float:
    """
    Compute Euclidean distance between two SWC nodes in 3D space.
    """

    return sqrt(
        (a.x - b.x) ** 2
        + (a.y - b.y) ** 2
        + (a.z - b.z) ** 2
    )


def validate_parent_links(nodes: list[SWCNode]) -> None:
    """
    Validate that every non-root parent_id points to an existing node.

    SWC root nodes conventionally have parent_id = -1.
    """

    indexed = nodes_by_id(nodes)

    for node in nodes:
        if node.parent_id == -1:
            continue

        if node.parent_id not in indexed:
            raise SWCParseError(
                f"Node {node.node_id} references missing parent_id {node.parent_id}."
            )