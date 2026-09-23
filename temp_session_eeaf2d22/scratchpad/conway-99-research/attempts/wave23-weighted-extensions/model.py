#!/usr/bin/env python3
"""Exact orbit-refined order-six to order-seven extension model.

Only the Python standard library is used here.  Graphs are represented by
edge masks in lexicographic edge order.  A class representative is the least
mask over all vertex permutations.
"""

from __future__ import annotations

import math
from functools import lru_cache
from itertools import combinations, permutations
from typing import Iterable, Mapping, Sequence


N = 99
K = 14
LAMBDA = 1
MU = 2
N3 = 705
EXPECTED_LABELED_SEVEN = 394_020
EXPECTED_UNLABELED_SIX = 62
EXPECTED_UNLABELED_SEVEN = 208

# N_i -> canonical six-vertex mask.  This alignment is the frozen, exact
# Wave-21 source-table transcription.
SOURCE_N_MASKS = (
    7100, 1883, 5941, 1916, 5907, 1749, 926, 1881, 1884, 956, 922, 1880,
    920, 5905, 671, 761, 701, 762, 63, 123, 691, 663, 694, 633, 760, 126,
    693, 246, 700, 31, 61, 121, 659, 122, 692, 0, 1, 3, 36, 7, 44, 37,
    35, 15, 102, 45, 39, 106, 616, 110, 107, 47, 684, 655, 685, 617,
    656, 657, 60, 662, 120, 632,
)

# Exact source counts n_1,...,n_62 at n3=705.
SIX_COUNTS = (
    1151, 8316, 705, 1410, 20085, 90066, 41580, 164910, 40875, 81750,
    668100, 209991, 363120, 2545, 20790, 83160, 166320, 163500, 110880,
    831600, 305390, 748440, 1499700, 334050, 584940, 332640, 749850,
    334050, 1334790, 66528, 1995840, 1704075, 6981210, 6314520, 6479430,
    101286343, 275382225, 187696350, 145263960, 30351990, 95998350,
    103443990, 5072290, 2328480, 2287605, 36097080, 8816370, 37016070,
    2454630, 3573060, 3823950, 1704780, 1462206, 83160, 334050, 3573060,
    8283875, 17011860, 4991010, 1370730, 7612665, 372810,
)

# Pinned source-Hamiltonian alignment, in the same convention as Wave 22.
SOURCE_H_CHORDS: dict[int, tuple[tuple[int, int], ...]] = {
    0: (),
    1: ((6, 1),),
    2: ((5, 2),),
    3: ((0, 5), (0, 2)),
    4: ((0, 5), (0, 3)),
    5: ((0, 4), (0, 3)),
    6: ((6, 4), (1, 3)),
    7: ((6, 1), (5, 2)),
    8: ((6, 1), (0, 4)),
    9: ((6, 3), (1, 4)),
    10: ((6, 1), (6, 4), (1, 3)),
    11: ((0, 2), (0, 5), (1, 4)),
    12: ((0, 4), (0, 3), (6, 1)),
    13: ((0, 4), (0, 3), (5, 2)),
    14: ((0, 5), (0, 3), (4, 2)),
    15: ((6, 4), (1, 3), (5, 2)),
    16: ((6, 1), (5, 2), (0, 3)),
    17: ((6, 1), (5, 2), (6, 4), (1, 3)),
    18: ((6, 1), (5, 2), (0, 4), (0, 3)),
}


def edge_data(order: int) -> tuple[tuple[tuple[int, int], ...], dict[tuple[int, int], int]]:
    edges = tuple(combinations(range(order), 2))
    return edges, {edge: index for index, edge in enumerate(edges)}


@lru_cache(maxsize=None)
def permutation_data(order: int) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    edges, positions = edge_data(order)
    records = []
    for permutation in permutations(range(order)):
        bit_map = tuple(
            1 << positions[tuple(sorted((permutation[left], permutation[right])))]
            for left, right in edges
        )
        records.append((permutation, bit_map))
    return tuple(records)


def transform_mask(mask: int, bit_map: Sequence[int]) -> int:
    transformed = 0
    remaining = mask
    while remaining:
        bit = remaining & -remaining
        transformed |= bit_map[bit.bit_length() - 1]
        remaining -= bit
    return transformed


@lru_cache(maxsize=None)
def canonical_mask(mask: int, order: int) -> int:
    return min(
        transform_mask(mask, bit_map)
        for _, bit_map in permutation_data(order)
    )


@lru_cache(maxsize=None)
def adjacency_rows(mask: int, order: int) -> tuple[int, ...]:
    edges, _ = edge_data(order)
    rows = [0] * order
    for index, (left, right) in enumerate(edges):
        if mask >> index & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def locally_admissible(mask: int, order: int) -> bool:
    edges, positions = edge_data(order)
    adjacency = adjacency_rows(mask, order)
    for left, right in edges:
        common = (adjacency[left] & adjacency[right]).bit_count()
        bound = LAMBDA if mask >> positions[(left, right)] & 1 else MU
        if common > bound:
            return False
    return True


@lru_cache(maxsize=None)
def admissible_labeled_masks(order: int) -> tuple[int, ...]:
    edge_count = order * (order - 1) // 2
    return tuple(
        mask for mask in range(1 << edge_count)
        if locally_admissible(mask, order)
    )


@lru_cache(maxsize=None)
def locally_admissible_classes(order: int) -> tuple[int, ...]:
    remaining = set(admissible_labeled_masks(order))
    classes: list[int] = []
    maps = tuple(bit_map for _, bit_map in permutation_data(order))
    while remaining:
        representative = next(iter(remaining))
        orbit = {transform_mask(representative, bit_map) for bit_map in maps}
        canonical = min(orbit)
        if canonical not in remaining:
            raise AssertionError("partially removed isomorphism orbit")
        classes.append(canonical)
        remaining.difference_update(orbit)
    return tuple(sorted(classes))


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    old_edges, _ = edge_data(order)
    _, new_positions = edge_data(order - 1)
    remaining = [vertex for vertex in range(order) if vertex != deleted]
    relabel = {old: new for new, old in enumerate(remaining)}
    result = 0
    for edge_index, (left, right) in enumerate(old_edges):
        if left == deleted or right == deleted or not (mask >> edge_index & 1):
            continue
        edge = tuple(sorted((relabel[left], relabel[right])))
        result |= 1 << new_positions[edge]
    return result


@lru_cache(maxsize=None)
def canonicalizing_permutation(mask: int, order: int) -> tuple[int, ...]:
    canonical = canonical_mask(mask, order)
    for permutation, bit_map in permutation_data(order):
        if transform_mask(mask, bit_map) == canonical:
            return permutation
    raise AssertionError("canonicalizing permutation not found")


def _orbits(items: Iterable[tuple[int, ...]], actions: Sequence[Sequence[int]]) -> tuple[tuple[tuple[int, ...], ...], ...]:
    remaining = set(items)
    result = []
    while remaining:
        seed = min(remaining)
        orbit = {
            tuple(sorted(action[vertex] for vertex in seed))
            for action in actions
        }
        result.append(tuple(sorted(orbit)))
        remaining.difference_update(orbit)
    return tuple(sorted(result))


@lru_cache(maxsize=None)
def automorphisms(mask: int, order: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        permutation
        for permutation, bit_map in permutation_data(order)
        if transform_mask(mask, bit_map) == mask
    )


@lru_cache(maxsize=None)
def vertex_orbits(mask: int, order: int) -> tuple[tuple[int, ...], ...]:
    actions = automorphisms(mask, order)
    raw = _orbits(((vertex,) for vertex in range(order)), actions)
    return tuple(tuple(item[0] for item in orbit) for orbit in raw)


@lru_cache(maxsize=None)
def pair_orbits(mask: int, order: int) -> tuple[tuple[tuple[int, int], ...], ...]:
    return _orbits(combinations(range(order), 2), automorphisms(mask, order))


def c7_mask(chords: Iterable[tuple[int, int]]) -> int:
    _, positions = edge_data(7)
    edges = {
        tuple(sorted((vertex, (vertex + 1) % 7)))
        for vertex in range(7)
    }
    edges.update(tuple(sorted(edge)) for edge in chords)
    return sum(1 << positions[edge] for edge in edges)


@lru_cache(maxsize=1)
def source_h_masks() -> tuple[int, ...]:
    return tuple(
        canonical_mask(c7_mask(SOURCE_H_CHORDS[index]), 7)
        for index in range(19)
    )


def published_hamiltonian_counts(n3: int, h11: int) -> tuple[int, ...]:
    if h11 % 4:
        raise ValueError("h11 must be divisible by four")
    common = N * K * (K - 2)
    b = common * (K - 4)
    values = (
        b * (2 * K**2 - 30 * K + 133) // 14 - 10 * n3 - h11,
        common * (2 * K**2 - 25 * K + 68) // 2 + 16 * n3 + 3 * h11 // 2,
        b * (K - 8) + 12 * n3 + 5 * h11 // 2,
        b - 2 * n3 - h11 // 2,
        b - 4 * n3,
        b // 2 - h11 // 2,
        b - 8 * n3,
        b // 2 - 3 * h11 // 2,
        2 * b - 8 * n3 - 2 * h11,
        b - 2 * n3 - 3 * h11 // 2,
        2 * n3,
        h11,
        (common - 4 * n3 + h11) // 4,
        h11 // 2,
        4 * n3,
        2 * n3,
        h11 - 2 * n3,
        common // 4 - n3,
        (4 * n3 - h11) // 4,
    )
    if any(value < 0 for value in values):
        raise ValueError("negative published Hamiltonian count")
    return values


def hamiltonian_affine_counts(n3: int) -> tuple[tuple[int, int], ...]:
    """Return ``(intercept, slope)`` in ``h_i=intercept+slope*z``.

    Here ``z=h11/4``.  The interpolation deliberately uses two admissible
    values instead of evaluating the source formulas at inadmissible h11=0.
    """
    lower_h11 = ((2 * n3 + 3) // 4) * 4
    left = published_hamiltonian_counts(n3, lower_h11)
    right = published_hamiltonian_counts(n3, lower_h11 + 4)
    slopes = tuple(rvalue - lvalue for lvalue, rvalue in zip(left, right))
    z0 = lower_h11 // 4
    return tuple(
        (value - slope * z0, slope)
        for value, slope in zip(left, slopes)
    )


def row_key(record: Mapping[str, object]) -> tuple[object, ...]:
    return (
        record["kind"],
        record["source_index"],
        record.get("orbit_index", -1),
    )


@lru_cache(maxsize=None)
def build_transition(order: int) -> dict[str, object]:
    """Build all orbit-refined ``order -> order+1`` coefficient rows.

    Unlike :func:`build_extension_model`, this generic constructor uses
    canonical-mask order on both sides and has no source-table dependency.
    """
    if not 1 <= order <= 6:
        raise ValueError("transition order must lie in 1,...,6")
    lower = locally_admissible_classes(order)
    upper = locally_admissible_classes(order + 1)
    lower_index = {mask: index for index, mask in enumerate(lower)}
    row_records: list[dict[str, object]] = []
    rows: list[list[int]] = []
    lookup: dict[tuple[object, ...], int] = {}

    for index, mask in enumerate(lower):
        adjacency = adjacency_rows(mask, order)
        positions = edge_data(order)[1]
        records: list[dict[str, object]] = [
            {
                "kind": "deletion",
                "lower_index": index,
                "lower_mask": mask,
                "orbit_index": 0,
                "orbit_size": 1,
                "rhs_multiplier": N - order,
            }
        ]
        for orbit_index, orbit in enumerate(vertex_orbits(mask, order)):
            degree = adjacency[orbit[0]].bit_count()
            records.append(
                {
                    "kind": "vertex",
                    "lower_index": index,
                    "lower_mask": mask,
                    "orbit_index": orbit_index,
                    "orbit": list(orbit),
                    "orbit_size": len(orbit),
                    "internal_degree": degree,
                    "rhs_multiplier": len(orbit) * (K - degree),
                }
            )
        for orbit_index, orbit in enumerate(pair_orbits(mask, order)):
            left, right = orbit[0]
            is_edge = bool(mask >> positions[(left, right)] & 1)
            common = (adjacency[left] & adjacency[right]).bit_count()
            target = LAMBDA if is_edge else MU
            records.append(
                {
                    "kind": "pair",
                    "lower_index": index,
                    "lower_mask": mask,
                    "orbit_index": orbit_index,
                    "orbit": [list(pair) for pair in orbit],
                    "orbit_size": len(orbit),
                    "is_edge": is_edge,
                    "internal_common_neighbors": common,
                    "rhs_multiplier": len(orbit) * (target - common),
                }
            )
        for record in records:
            key = (
                record["kind"],
                record["lower_index"],
                record["orbit_index"],
            )
            lookup[key] = len(row_records)
            row_records.append(record)
            rows.append([0] * len(upper))

    for column, upper_mask in enumerate(upper):
        upper_adjacency = adjacency_rows(upper_mask, order + 1)
        for root in range(order + 1):
            raw_card = delete_vertex(upper_mask, order + 1, root)
            canonical_card = canonical_mask(raw_card, order)
            lower_i = lower_index[canonical_card]
            permutation = canonicalizing_permutation(raw_card, order)
            mask = lower[lower_i]
            v_orbits = vertex_orbits(mask, order)
            p_orbits = pair_orbits(mask, order)
            vertex_to_orbit = {
                vertex: orbit_i
                for orbit_i, orbit in enumerate(v_orbits)
                for vertex in orbit
            }
            pair_to_orbit = {
                pair: orbit_i
                for orbit_i, orbit in enumerate(p_orbits)
                for pair in orbit
            }
            rows[lookup[("deletion", lower_i, 0)]][column] += 1
            remaining = [vertex for vertex in range(order + 1) if vertex != root]
            root_neighbors: list[int] = []
            for raw_vertex, old_vertex in enumerate(remaining):
                if upper_adjacency[root] >> old_vertex & 1:
                    canonical_vertex = permutation[raw_vertex]
                    root_neighbors.append(canonical_vertex)
                    orbit_i = vertex_to_orbit[canonical_vertex]
                    rows[lookup[("vertex", lower_i, orbit_i)]][column] += 1
            for pair in combinations(sorted(root_neighbors), 2):
                orbit_i = pair_to_orbit[pair]
                rows[lookup[("pair", lower_i, orbit_i)]][column] += 1

    return {
        "order": order,
        "lower_classes": lower,
        "upper_classes": upper,
        "row_records": tuple(row_records),
        "matrix_rows": tuple(tuple(row) for row in rows),
    }


def transition_rhs(
    transition: Mapping[str, object],
    lower_counts: Sequence[int],
) -> tuple[int, ...]:
    lower = transition["lower_classes"]
    records = transition["row_records"]
    if len(lower_counts) != len(lower):
        raise ValueError("lower count vector has the wrong length")
    result = []
    for record in records:
        lower_index = int(record["lower_index"])
        result.append(
            int(record["rhs_multiplier"]) * int(lower_counts[lower_index])
        )
    return tuple(result)


@lru_cache(maxsize=1)
def build_extension_model() -> dict[str, object]:
    classes6 = locally_admissible_classes(6)
    classes7 = locally_admissible_classes(7)
    if len(classes6) != EXPECTED_UNLABELED_SIX:
        raise AssertionError(f"expected 62 six-classes, got {len(classes6)}")
    if len(admissible_labeled_masks(7)) != EXPECTED_LABELED_SEVEN:
        raise AssertionError("unexpected labeled seven-census")
    if len(classes7) != EXPECTED_UNLABELED_SEVEN:
        raise AssertionError(f"expected 208 seven-classes, got {len(classes7)}")
    if len(set(SOURCE_N_MASKS)) != 62 or set(SOURCE_N_MASKS) != set(classes6):
        raise AssertionError("source N alignment is not a six-class bijection")
    h_masks = source_h_masks()
    if len(set(h_masks)) != 19 or not set(h_masks).issubset(classes7):
        raise AssertionError("source H alignment does not identify 19 seven-classes")

    source_index = {mask: index for index, mask in enumerate(SOURCE_N_MASKS)}
    row_records: list[dict[str, object]] = []
    row_vectors: list[list[int]] = []
    rhs: list[int] = []
    row_lookup: dict[tuple[object, ...], int] = {}

    for index, (mask, count) in enumerate(zip(SOURCE_N_MASKS, SIX_COUNTS)):
        adjacency = adjacency_rows(mask, 6)
        positions = edge_data(6)[1]
        v_orbits = vertex_orbits(mask, 6)
        p_orbits = pair_orbits(mask, 6)

        records: list[tuple[dict[str, object], int]] = [
            (
                {
                    "kind": "deletion",
                    "source_index": index,
                    "source_mask": mask,
                    "orbit_index": 0,
                    "orbit": [],
                },
                (N - 6) * count,
            )
        ]
        for orbit_index, orbit in enumerate(v_orbits):
            degree = adjacency[orbit[0]].bit_count()
            if any(adjacency[vertex].bit_count() != degree for vertex in orbit):
                raise AssertionError("vertex orbit has mixed degrees")
            records.append(
                (
                    {
                        "kind": "vertex",
                        "source_index": index,
                        "source_mask": mask,
                        "orbit_index": orbit_index,
                        "orbit": list(orbit),
                        "orbit_size": len(orbit),
                        "internal_degree": degree,
                    },
                    len(orbit) * (K - degree) * count,
                )
            )
        for orbit_index, orbit in enumerate(p_orbits):
            left, right = orbit[0]
            is_edge = bool(mask >> positions[(left, right)] & 1)
            common = (adjacency[left] & adjacency[right]).bit_count()
            if any(
                bool(mask >> positions[pair] & 1) != is_edge
                or (adjacency[pair[0]] & adjacency[pair[1]]).bit_count() != common
                for pair in orbit
            ):
                raise AssertionError("pair orbit has mixed local data")
            target = LAMBDA if is_edge else MU
            records.append(
                (
                    {
                        "kind": "pair",
                        "source_index": index,
                        "source_mask": mask,
                        "orbit_index": orbit_index,
                        "orbit": [list(pair) for pair in orbit],
                        "orbit_size": len(orbit),
                        "is_edge": is_edge,
                        "internal_common_neighbors": common,
                    },
                    len(orbit) * (target - common) * count,
                )
            )

        for record, right_side in records:
            key = row_key(record)
            row_lookup[key] = len(row_records)
            row_records.append(record)
            row_vectors.append([0] * len(classes7))
            rhs.append(right_side)

    # Each seven-class contributes once for every distinguished deletion root.
    for column, mask7 in enumerate(classes7):
        adjacency7 = adjacency_rows(mask7, 7)
        remaining_by_root = [
            [vertex for vertex in range(7) if vertex != root]
            for root in range(7)
        ]
        for root in range(7):
            raw_card = delete_vertex(mask7, 7, root)
            canonical_card = canonical_mask(raw_card, 6)
            index = source_index[canonical_card]
            permutation = canonicalizing_permutation(raw_card, 6)
            mask6 = SOURCE_N_MASKS[index]
            v_orbits = vertex_orbits(mask6, 6)
            p_orbits = pair_orbits(mask6, 6)
            vertex_to_orbit = {
                vertex: orbit_index
                for orbit_index, orbit in enumerate(v_orbits)
                for vertex in orbit
            }
            pair_to_orbit = {
                pair: orbit_index
                for orbit_index, orbit in enumerate(p_orbits)
                for pair in orbit
            }
            row_vectors[row_lookup[("deletion", index, 0)]][column] += 1

            root_neighbors: set[int] = set()
            remaining = remaining_by_root[root]
            for raw_vertex, old_vertex in enumerate(remaining):
                if adjacency7[root] >> old_vertex & 1:
                    canonical_vertex = permutation[raw_vertex]
                    root_neighbors.add(canonical_vertex)
                    orbit_index = vertex_to_orbit[canonical_vertex]
                    row_vectors[row_lookup[("vertex", index, orbit_index)]][column] += 1

            for left, right in combinations(sorted(root_neighbors), 2):
                orbit_index = pair_to_orbit[(left, right)]
                row_vectors[row_lookup[("pair", index, orbit_index)]][column] += 1

    # Internal consistency identities catch all normalization mistakes.
    for index, mask in enumerate(SOURCE_N_MASKS):
        deletion = row_vectors[row_lookup[("deletion", index, 0)]]
        vertex_rows = [
            row_vectors[row_lookup[("vertex", index, orbit_index)]]
            for orbit_index in range(len(vertex_orbits(mask, 6)))
        ]
        pair_rows = [
            row_vectors[row_lookup[("pair", index, orbit_index)]]
            for orbit_index in range(len(pair_orbits(mask, 6)))
        ]
        for column, mask7 in enumerate(classes7):
            rooted_degrees = 0
            rooted_choose2 = 0
            for root in range(7):
                if canonical_mask(delete_vertex(mask7, 7, root), 6) == mask:
                    degree = adjacency_rows(mask7, 7)[root].bit_count()
                    rooted_degrees += degree
                    rooted_choose2 += math.comb(degree, 2)
            if sum(row[column] for row in vertex_rows) != rooted_degrees:
                raise AssertionError("vertex-orbit rows do not partition rooted degree")
            if sum(row[column] for row in pair_rows) != rooted_choose2:
                raise AssertionError("pair-orbit rows do not partition rooted neighbor pairs")
            if deletion[column] < 0 or deletion[column] > 7:
                raise AssertionError("invalid deletion coefficient")

    return {
        "classes6": classes6,
        "classes7": classes7,
        "h_masks": h_masks,
        "h_columns": tuple(classes7.index(mask) for mask in h_masks),
        "row_records": tuple(row_records),
        "matrix_rows": tuple(tuple(row) for row in row_vectors),
        "rhs": tuple(rhs),
        "row_lookup": row_lookup,
    }
