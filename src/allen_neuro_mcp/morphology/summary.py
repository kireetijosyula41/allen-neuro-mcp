from __future__ import annotations

from dataclasses import dataclass

from allen_neuro_mcp.morphology.swc import (
    SWCNode,
    children_by_parent,
    euclidean_distance,
    nodes_by_id,
    validate_parent_links,
)


# Standard SWC node type IDs
SWC_SOMA = 1
SWC_AXON = 2
SWC_BASAL_DENDRITE = 3
SWC_APICAL_DENDRITE = 4


@dataclass(frozen=True)
class MorphologyStats:
    """
    Computed structural summary of an SWC morphology.

    This is intentionally simulator-adjacent but not simulator-specific.
    """

    node_count: int
    edge_count: int

    soma_node_count: int
    axon_node_count: int
    basal_dendrite_node_count: int
    apical_dendrite_node_count: int
    unknown_node_count: int

    total_cable_length_um: float
    branch_point_count: int
    terminal_tip_count: int
    max_path_distance_um: float

    bounding_box_um: dict[str, float]


def compute_morphology_stats(nodes: list[SWCNode]) -> MorphologyStats:
    """
    Compute morphology summary statistics from parsed SWC nodes.

    Assumes SWC coordinates are in micrometers, which is the convention used
    for Allen Cell Types morphology reconstructions.
    """

    if not nodes:
        return MorphologyStats(
            node_count=0,
            edge_count=0,
            soma_node_count=0,
            axon_node_count=0,
            basal_dendrite_node_count=0,
            apical_dendrite_node_count=0,
            unknown_node_count=0,
            total_cable_length_um=0.0,
            branch_point_count=0,
            terminal_tip_count=0,
            max_path_distance_um=0.0,
            bounding_box_um={"x": 0.0, "y": 0.0, "z": 0.0},
        )

    validate_parent_links(nodes)

    indexed = nodes_by_id(nodes)
    children = children_by_parent(nodes)

    edge_count = sum(1 for node in nodes if node.parent_id != -1)

    soma_node_count = sum(1 for node in nodes if node.node_type == SWC_SOMA)
    axon_node_count = sum(1 for node in nodes if node.node_type == SWC_AXON)
    basal_dendrite_node_count = sum(
        1 for node in nodes if node.node_type == SWC_BASAL_DENDRITE
    )
    apical_dendrite_node_count = sum(
        1 for node in nodes if node.node_type == SWC_APICAL_DENDRITE
    )

    known_types = {
        SWC_SOMA,
        SWC_AXON,
        SWC_BASAL_DENDRITE,
        SWC_APICAL_DENDRITE,
    }
    unknown_node_count = sum(1 for node in nodes if node.node_type not in known_types)

    total_cable_length_um = 0.0
    path_distance_by_node_id: dict[int, float] = {}

    # Initialize roots.
    for node in nodes:
        if node.parent_id == -1:
            path_distance_by_node_id[node.node_id] = 0.0

    # SWC files are usually topologically ordered, but this loop is robust enough
    # for simple out-of-order cases.
    unresolved = {node.node_id for node in nodes}

    while unresolved:
        progress = False

        for node_id in list(unresolved):
            node = indexed[node_id]

            if node.parent_id == -1:
                unresolved.remove(node_id)
                progress = True
                continue

            if node.parent_id not in path_distance_by_node_id:
                continue

            parent = indexed[node.parent_id]
            segment_length = euclidean_distance(parent, node)

            total_cable_length_um += segment_length
            path_distance_by_node_id[node_id] = (
                path_distance_by_node_id[node.parent_id] + segment_length
            )

            unresolved.remove(node_id)
            progress = True

        if not progress:
            # validate_parent_links should catch missing parents, so this usually
            # means a cycle or malformed parent structure.
            raise ValueError("Could not resolve SWC parent-child path distances.")

    branch_point_count = sum(
        1
        for node in nodes
        if len(children.get(node.node_id, [])) > 1
    )

    terminal_tip_count = sum(
        1
        for node in nodes
        if node.parent_id != -1 and len(children.get(node.node_id, [])) == 0
    )

    xs = [node.x for node in nodes]
    ys = [node.y for node in nodes]
    zs = [node.z for node in nodes]

    bounding_box_um = {
        "x": max(xs) - min(xs),
        "y": max(ys) - min(ys),
        "z": max(zs) - min(zs),
    }

    max_path_distance_um = max(path_distance_by_node_id.values(), default=0.0)

    return MorphologyStats(
        node_count=len(nodes),
        edge_count=edge_count,
        soma_node_count=soma_node_count,
        axon_node_count=axon_node_count,
        basal_dendrite_node_count=basal_dendrite_node_count,
        apical_dendrite_node_count=apical_dendrite_node_count,
        unknown_node_count=unknown_node_count,
        total_cable_length_um=total_cable_length_um,
        branch_point_count=branch_point_count,
        terminal_tip_count=terminal_tip_count,
        max_path_distance_um=max_path_distance_um,
        bounding_box_um=bounding_box_um,
    )