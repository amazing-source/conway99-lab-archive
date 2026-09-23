#!/usr/bin/env python3
"""Clean-room finite Gram matrices for rooted four-vertex flags.

This implementation was written and its output frozen before inspecting
attempts/wave45-flag-moment.  It enumerates every labelled simple graph
through order seven and removes isomorphism orbits itself; all rooted-flag
construction, overlap coefficients, controls, and exact arithmetic are
implemented here.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT_TYPES = ("vertex", "edge", "nonedge")
ROOT_ARITY = {"vertex": 1, "edge": 2, "nonedge": 2}
UNLABELLED_FLAG_ORDER = {"vertex": 3, "edge": 2, "nonedge": 2}
UNION_ORDERS = {
    "vertex": tuple(range(4, 8)),
    "edge": tuple(range(4, 7)),
    "nonedge": tuple(range(4, 7)),
}
LAMBDA_CAP = 1
MU_CAP = 2


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


def compact_json(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_compact(value: object) -> str:
    return hashlib.sha256(compact_json(value)).hexdigest()


def edge_pairs(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


def edge_index(left: int, right: int, order: int) -> int:
    require(0 <= left < right < order, "bad edge")
    return sum(order - 1 - first for first in range(left)) + right - left - 1


def adjacent(mask: int, left: int, right: int, order: int) -> bool:
    if left > right:
        left, right = right, left
    return bool(mask >> edge_index(left, right, order) & 1)


def mask_from_edges(order: int, edges: Iterable[tuple[int, int]]) -> int:
    mask = 0
    for left, right in edges:
        if left > right:
            left, right = right, left
        mask |= 1 << edge_index(left, right, order)
    return mask


@functools.lru_cache(maxsize=None)
def permutation_edge_maps(order: int) -> tuple[tuple[int, ...], ...]:
    edges = edge_pairs(order)
    maps: list[tuple[int, ...]] = []
    for permutation in itertools.permutations(range(order)):
        transformed: list[int] = []
        for left, right in edges:
            new_left, new_right = permutation[left], permutation[right]
            if new_left > new_right:
                new_left, new_right = new_right, new_left
            transformed.append(edge_index(new_left, new_right, order))
        maps.append(tuple(transformed))
    return tuple(maps)


def transform_mask(mask: int, edge_map: Sequence[int]) -> int:
    transformed = 0
    remaining = mask
    while remaining:
        low_bit = remaining & -remaining
        source_index = low_bit.bit_length() - 1
        transformed |= 1 << edge_map[source_index]
        remaining ^= low_bit
    return transformed


@functools.lru_cache(maxsize=None)
def canonical_unrooted(mask: int, order: int) -> int:
    return min(
        transform_mask(mask, edge_map)
        for edge_map in permutation_edge_maps(order)
    )


@functools.lru_cache(maxsize=None)
def rooted_edge_maps(root_arity: int) -> tuple[tuple[int, ...], ...]:
    order = 4
    edges = edge_pairs(order)
    maps: list[tuple[int, ...]] = []
    for tail in itertools.permutations(range(root_arity, order)):
        permutation = tuple(range(root_arity)) + tail
        transformed: list[int] = []
        for left, right in edges:
            new_left, new_right = permutation[left], permutation[right]
            if new_left > new_right:
                new_left, new_right = new_right, new_left
            transformed.append(edge_index(new_left, new_right, order))
        maps.append(tuple(transformed))
    return tuple(maps)


@functools.lru_cache(maxsize=None)
def canonical_rooted(mask: int, root_arity: int) -> int:
    return min(
        transform_mask(mask, edge_map)
        for edge_map in rooted_edge_maps(root_arity)
    )


def locally_admissible(mask: int, order: int) -> bool:
    rows = [0] * order
    for index, (left, right) in enumerate(edge_pairs(order)):
        if mask >> index & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    for left in range(order):
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            cap = LAMBDA_CAP if adjacent(mask, left, right, order) else MU_CAP
            if common > cap:
                return False
    return True


def induced_mask(
    mask: int,
    source_order: int,
    vertices: Sequence[int],
) -> int:
    return mask_from_edges(
        len(vertices),
        (
            (left_index, right_index)
            for left_index, left in enumerate(vertices)
            for right_index, right in enumerate(vertices)
            if left_index < right_index
            and adjacent(mask, left, right, source_order)
        ),
    )


def flag_mask(
    mask: int,
    source_order: int,
    roots: Sequence[int],
    selected: Sequence[int],
) -> int:
    require(len(roots) + len(selected) == 4, "flag does not have order four")
    return canonical_rooted(
        induced_mask(mask, source_order, tuple(roots) + tuple(sorted(selected))),
        len(roots),
    )


def root_relation_matches(mask: int, roots: Sequence[int], root_type: str) -> bool:
    if root_type == "vertex":
        return len(roots) == 1
    relation = adjacent(mask, roots[0], roots[1], 4)
    return relation if root_type == "edge" else not relation


def flag_universe(root_type: str) -> tuple[int, ...]:
    root_arity = ROOT_ARITY[root_type]
    values: set[int] = set()
    for mask in range(1 << 6):
        if not locally_admissible(mask, 4):
            continue
        roots = tuple(range(root_arity))
        if root_relation_matches(mask, roots, root_type):
            values.add(canonical_rooted(mask, root_arity))
    return tuple(sorted(values))


@functools.lru_cache(maxsize=1)
def unrooted_class_sets() -> dict[int, tuple[int, ...]]:
    result: dict[int, tuple[int, ...]] = {}
    for order in range(4, 8):
        remaining = {
            mask
            for mask in range(1 << len(edge_pairs(order)))
            if locally_admissible(mask, order)
        }
        classes: list[int] = []
        maps = permutation_edge_maps(order)
        while remaining:
            representative = next(iter(remaining))
            orbit = {
                transform_mask(representative, edge_map)
                for edge_map in maps
            }
            canonical = min(orbit)
            require(canonical in remaining, "partial isomorphism orbit")
            classes.append(canonical)
            remaining.difference_update(orbit)
        result[order] = tuple(sorted(classes))
    return result


def root_embeddings(mask: int, order: int, root_type: str) -> Iterable[tuple[int, ...]]:
    if root_type == "vertex":
        yield from ((vertex,) for vertex in range(order))
        return
    want_edge = root_type == "edge"
    for first in range(order):
        for second in range(order):
            if first != second and adjacent(mask, first, second, order) == want_edge:
                yield (first, second)


def zero_matrix(size: int) -> list[list[int]]:
    return [[0] * size for _ in range(size)]


def class_coefficient_matrix(
    mask: int,
    order: int,
    root_type: str,
    flags: Sequence[int],
) -> list[list[int]]:
    index = {flag: position for position, flag in enumerate(flags)}
    root_arity = ROOT_ARITY[root_type]
    selection_size = UNLABELLED_FLAG_ORDER[root_type]
    matrix = zero_matrix(len(flags))
    for roots in root_embeddings(mask, order, root_type):
        nonroots = tuple(vertex for vertex in range(order) if vertex not in roots)
        selections = tuple(itertools.combinations(nonroots, selection_size))
        for first_selection in selections:
            first_flag = flag_mask(mask, order, roots, first_selection)
            require(first_flag in index, "first induced flag left universe")
            first_index = index[first_flag]
            first_set = set(first_selection)
            for second_selection in selections:
                if first_set.union(second_selection) != set(nonroots):
                    continue
                second_flag = flag_mask(mask, order, roots, second_selection)
                require(second_flag in index, "second induced flag left universe")
                matrix[first_index][index[second_flag]] += 1
    require(
        all(matrix[i][j] == matrix[j][i] for i in range(len(flags)) for j in range(len(flags))),
        "coefficient matrix is not symmetric",
    )
    return matrix


def sparse_entries(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [row, column, value]
        for row, values in enumerate(matrix)
        for column, value in enumerate(values)
        if value
    ]


def coefficient_stream(
    root_type: str,
    flags: Sequence[int],
    class_sets: dict[int, tuple[int, ...]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for order in UNION_ORDERS[root_type]:
        for mask in class_sets[order]:
            records.append(
                {
                    "order": order,
                    "canonical_mask": mask,
                    "entries": sparse_entries(
                        class_coefficient_matrix(mask, order, root_type, flags)
                    ),
                }
            )
    return records


def petersen_graph() -> tuple[int, int]:
    edges: set[tuple[int, int]] = set()
    for index in range(5):
        edges.add(tuple(sorted((index, (index + 1) % 5))))
        edges.add((index, 5 + index))
        edges.add(tuple(sorted((5 + index, 5 + (index + 2) % 5))))
    return mask_from_edges(10, edges), 10


def clebsch_graph() -> tuple[int, int]:
    edges: set[tuple[int, int]] = set()
    steps = (1, 2, 4, 8, 15)
    for vertex in range(16):
        for step in steps:
            edges.add(tuple(sorted((vertex, vertex ^ step))))
    return mask_from_edges(16, edges), 16


def srg_parameters(mask: int, order: int) -> tuple[int, int, int, int]:
    rows = [0] * order
    for index, (left, right) in enumerate(edge_pairs(order)):
        if mask >> index & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    degrees = {row.bit_count() for row in rows}
    require(len(degrees) == 1, "control graph is not regular")
    lambdas: set[int] = set()
    mus: set[int] = set()
    for left in range(order):
        for right in range(order):
            if left >= right:
                continue
            common = (rows[left] & rows[right]).bit_count()
            target = lambdas if adjacent(mask, left, right, order) else mus
            target.add(common)
    require(len(lambdas) == len(mus) == 1, "control graph is not strongly regular")
    return order, next(iter(degrees)), next(iter(lambdas)), next(iter(mus))


def direct_outer_product(
    mask: int,
    order: int,
    root_type: str,
    flags: Sequence[int],
) -> list[list[int]]:
    index = {flag: position for position, flag in enumerate(flags)}
    selection_size = UNLABELLED_FLAG_ORDER[root_type]
    matrix = zero_matrix(len(flags))
    for roots in root_embeddings(mask, order, root_type):
        nonroots = tuple(vertex for vertex in range(order) if vertex not in roots)
        vector = [0] * len(flags)
        for selected in itertools.combinations(nonroots, selection_size):
            vector[index[flag_mask(mask, order, roots, selected)]] += 1
        for row, left in enumerate(vector):
            for column, right in enumerate(vector):
                matrix[row][column] += left * right
    return matrix


def induced_class_counts(
    mask: int,
    graph_order: int,
    orders: Iterable[int],
) -> dict[int, Counter[int]]:
    vertices = tuple(range(graph_order))
    counts: dict[int, Counter[int]] = {}
    for order in orders:
        counter: Counter[int] = Counter()
        for selected in itertools.combinations(vertices, order):
            submask = induced_mask(mask, graph_order, selected)
            counter[canonical_unrooted(submask, order)] += 1
        counts[order] = counter
    return counts


def evaluate_stream(
    stream: Sequence[dict[str, Any]],
    class_counts: dict[int, Counter[int]],
    dimension: int,
) -> list[list[int]]:
    matrix = zero_matrix(dimension)
    for record in stream:
        count = class_counts[record["order"]][record["canonical_mask"]]
        if not count:
            continue
        for row, column, coefficient in record["entries"]:
            matrix[row][column] += count * coefficient
    return matrix


def matrix_sum(matrix: Sequence[Sequence[int]]) -> int:
    return sum(map(sum, matrix))


def quadratic(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    return sum(
        vector[row] * matrix[row][column] * vector[column]
        for row in range(len(vector))
        for column in range(len(vector))
    )


def derive_lower_counts_from_seven(
    seven_counts: Counter[int],
    graph_order: int,
    class_sets: dict[int, tuple[int, ...]],
) -> dict[int, Counter[int]]:
    require(graph_order >= 7, "graph order must be at least seven")
    result: dict[int, Counter[int]] = {7: Counter(seven_counts)}
    for order in range(4, 7):
        numerator: Counter[int] = Counter()
        for seven_mask, count in seven_counts.items():
            require(
                seven_mask in class_sets[7] and type(count) is int and count >= 0,
                "bad seven-class count",
            )
            for selected in itertools.combinations(range(7), order):
                lower_mask = canonical_unrooted(
                    induced_mask(seven_mask, 7, selected), order
                )
                numerator[lower_mask] += count
        divisor = math.comb(graph_order - order, 7 - order)
        derived: Counter[int] = Counter()
        for mask in class_sets[order]:
            value = numerator[mask]
            require(value % divisor == 0, "nonintegral lower-order deck count")
            quotient = value // divisor
            require(quotient >= 0, "negative lower-order deck count")
            if quotient:
                derived[mask] = quotient
        require(
            sum(derived.values()) == math.comb(graph_order, order),
            "lower-order class total changed",
        )
        result[order] = derived
    return result


def control_record(
    name: str,
    graph_data: tuple[int, int],
    flag_sets: dict[str, tuple[int, ...]],
    streams: dict[str, list[dict[str, Any]]],
    class_sets: dict[int, tuple[int, ...]],
) -> dict[str, Any]:
    mask, graph_order = graph_data
    parameters = srg_parameters(mask, graph_order)
    counts = induced_class_counts(mask, graph_order, range(4, 8))
    deck_counts = derive_lower_counts_from_seven(
        counts[7], graph_order, class_sets
    )
    require(
        all(deck_counts[order] == counts[order] for order in range(4, 7)),
        f"{name} lower-order deck reconstruction failed",
    )
    roots_count = {
        "vertex": parameters[0],
        "edge": parameters[0] * parameters[1],
        "nonedge": parameters[0] * (parameters[0] - 1 - parameters[1]),
    }
    records: dict[str, Any] = {}
    for root_type in ROOT_TYPES:
        flags = flag_sets[root_type]
        direct = direct_outer_product(mask, graph_order, root_type, flags)
        linear = evaluate_stream(streams[root_type], counts, len(flags))
        require(direct == linear, f"{name} {root_type} control mismatch")
        selection_size = UNLABELLED_FLAG_ORDER[root_type]
        expected_sum = roots_count[root_type] * math.comb(
            parameters[0] - ROOT_ARITY[root_type], selection_size
        ) ** 2
        require(matrix_sum(direct) == expected_sum, "all-ones identity failed")
        hostile = tuple((index % 5) - 2 for index in range(len(flags)))
        hostile_value = quadratic(direct, hostile)
        require(hostile_value >= 0, "outer-product control became negative")
        records[root_type] = {
            "dimension": len(flags),
            "direct_equals_linear": True,
            "matrix_sha256": sha256_compact(direct),
            "all_ones_quadratic": matrix_sum(direct),
            "all_ones_expected": expected_sum,
            "hostile_integer_quadratic": hostile_value,
        }
    return {
        "name": name,
        "srg_parameters": parameters,
        "seven_class_support": len(counts[7]),
        "lower_order_deck_reconstruction": "PASS",
        "root_types": records,
    }


def compute() -> dict[str, Any]:
    class_sets = unrooted_class_sets()
    flag_sets = {root_type: flag_universe(root_type) for root_type in ROOT_TYPES}
    require(len(flag_sets["vertex"]) == 17, "vertex flag dimension is not 17")
    streams = {
        root_type: coefficient_stream(root_type, flag_sets[root_type], class_sets)
        for root_type in ROOT_TYPES
    }
    flag_payload = {
        root_type: {
            "root_arity": ROOT_ARITY[root_type],
            "unlabelled_vertices": UNLABELLED_FLAG_ORDER[root_type],
            "canonical_masks": flag_sets[root_type],
        }
        for root_type in ROOT_TYPES
    }
    class_payload = {
        str(order): masks for order, masks in sorted(class_sets.items())
    }
    coefficient_hashes = {
        root_type: sha256_compact(streams[root_type])
        for root_type in ROOT_TYPES
    }
    coefficient_hashes["combined"] = sha256_compact(streams)
    controls = [
        control_record(
            "Petersen",
            petersen_graph(),
            flag_sets,
            streams,
            class_sets,
        ),
        control_record(
            "Clebsch",
            clebsch_graph(),
            flag_sets,
            streams,
            class_sets,
        ),
    ]
    return {
        "format": "wave45-clean-room-flag-moment-v1",
        "role": "verifier",
        "status": {
            "independent_construction": "PASS",
            "discovery_inspected": False,
            "endpoint_n3_4158": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
        "definition": {
            "flag_order": 4,
            "target_local_caps": {"edge_common": 1, "nonedge_common": 2},
            "matrix": "sum over ordered roots of z_root z_root^T",
            "overlaps": "all; grouped by their unique induced union",
            "automorphism_assumption": "none",
        },
        "class_enumeration": (
            "all labelled masks through order seven, quotient by all "
            "vertex permutations"
        ),
        "flag_sets": flag_payload,
        "unrooted_class_sets": class_payload,
        "coefficient_streams": streams,
        "sha256": {
            "flag_sets": sha256_compact(flag_payload),
            "unrooted_class_sets": sha256_compact(class_payload),
            "coefficient_streams": coefficient_hashes,
        },
        "controls": controls,
        "limitations": [
            "This independent freeze has not inspected Wave45 discovery files.",
            "PSD inequalities may refute aggregate witnesses without excluding the endpoint.",
            "No endpoint infeasibility, graph construction, or strict upper bound is claimed.",
        ],
    }


def validate_record(record: dict[str, Any]) -> None:
    require(record["format"] == "wave45-clean-room-flag-moment-v1", "bad format")
    require(record["status"]["discovery_inspected"] is False, "freeze contaminated")
    require(record["status"]["endpoint_n3_4158"] == "UNKNOWN", "status inflation")
    require(
        len(record["flag_sets"]["vertex"]["canonical_masks"]) == 17,
        "vertex flag census changed",
    )
    for control in record["controls"]:
        require(
            control["lower_order_deck_reconstruction"] == "PASS",
            "deck control failed",
        )
        for root_type in ROOT_TYPES:
            require(
                control["root_types"][root_type]["direct_equals_linear"],
                "linearization control failed",
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    if arguments.verify:
        stored = arguments.verify.read_bytes()
        record = json.loads(stored)
        validate_record(record)
        replay = canonical_json(compute())
        require(replay == stored, "independent freeze replay differs")
        print(
            f"PASS {arguments.verify} "
            f"sha256={hashlib.sha256(stored).hexdigest()}"
        )
        return 0
    record = compute()
    validate_record(record)
    payload = canonical_json(record)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_bytes(payload)
        print(
            f"WROTE {arguments.output} "
            f"sha256={hashlib.sha256(payload).hexdigest()}"
        )
    else:
        print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
