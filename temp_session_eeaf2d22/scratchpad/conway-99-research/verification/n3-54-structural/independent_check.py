"""Independent exact audit companion for the Wave 17 n3=54 residual.

This module deliberately imports no discovery module.  It reconstructs the
finite arithmetic, graph closures, parity witness, binary-rank arithmetic,
surface link, and triangle moments used in the human audit.  It does not
claim to construct or exclude an srg(99,14,1,2).
"""

from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "agents/2026-07-23-wave17-n3-54-structural.md"
EXPECTED_HASHES = {
    "AGENTS.md": (
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3"
    ),
    "agents/2026-07-23-wave16-n3-51-structural.md": (
        "95d04a774397332417c9613718fe6699a5392ef5222fef1cfa00b12e2860af3f"
    ),
    "verification/2026-07-23-wave16-n3-51-structural-audit.md": (
        "99203a15db2646a759edbb2241eb4bd5e6001733ac862952c9db57446c58ead6"
    ),
    "verification/2026-07-23-wave15-global-lift-audit.md": (
        "edda3785d080db464028f10c22bcae5c0bf17f1e61432a8641bfa6ffdccab036"
    ),
    "verification/2026-07-23-wave15-algebraic-audit.md": (
        "b0541d05d2c1c359152b86223e2ebbdbd002b2ff42deb699f6a0b21d149a5b45"
    ),
    "attempts/wave16-n3-51-structural/exact_check.py": (
        "5aef211ea7d457543fc3f494eea125bbd0fd6fae2533fd566b475ff3f971c5cf"
    ),
    "agents/2026-07-23-wave17-n3-54-structural.md": (
        "ffae576057617b6d8e32f7df4a1cd9627c63bdfe40fb58f394fd2640d1d82d18"
    ),
}

Edge = tuple[int, int]


def canonical_edge(left: int, right: int) -> Edge:
    if left == right:
        raise ValueError("loops are not edges")
    return (left, right) if left < right else (right, left)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_provenance() -> dict[str, str]:
    observed = {}
    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        if not path.is_file():
            raise AssertionError(f"missing frozen input: {relative}")
        actual = file_sha256(path)
        if actual != expected:
            raise AssertionError(
                f"frozen input drift: {relative}: {actual} != {expected}"
            )
        observed[relative] = actual
    return observed


def profiles_sum_36() -> list[tuple[int, tuple[int, ...]]]:
    """Enumerate with combinations, not the submitted recursive partitioner."""

    rows: list[tuple[int, tuple[int, ...]]] = []
    for order in range(1, 19):
        maximum = (order - 1) // 3
        if maximum < 2:
            continue
        for values in itertools.combinations_with_replacement(
            range(2, maximum + 1), order
        ):
            if sum(values) == 36:
                rows.append((order, values))
    return rows


def k_degrees(order: int, values: Sequence[int]) -> tuple[int, ...]:
    return tuple(order - 1 - 3 * value for value in values)


def residual_profiles() -> list[tuple[int, tuple[int, ...]]]:
    return [
        (order, values)
        for order, values in profiles_sum_36()
        if min(k_degrees(order, values)) >= 4
    ]


EXPECTED_RESIDUALS = [
    (14, (2,) * 6 + (3,) * 8),
    (15, (2,) * 9 + (3,) * 6),
    (16, (2,) * 12 + (3,) * 4),
    (17, (2,) * 16 + (4,)),
    (17, (2,) * 15 + (3,) * 2),
    (18, (2,) * 18),
]


def two_sided_crossing_counts(rows: int, columns: int) -> tuple[int, ...]:
    if rows * columns > 16:
        raise ValueError("exhaustive crossing helper is intentionally small")
    counts = set()
    for mask in range(1 << (rows * columns)):
        row_degrees = [
            sum(
                (mask >> (row * columns + column)) & 1
                for column in range(columns)
            )
            for row in range(rows)
        ]
        column_degrees = [
            sum(
                (mask >> (row * columns + column)) & 1
                for row in range(rows)
            )
            for column in range(columns)
        ]
        if all(value in (0, 2) for value in row_degrees + column_degrees):
            counts.add(mask.bit_count())
    return tuple(sorted(counts))


def size_two_support(left_q: int, right_q: int) -> dict[str, int | bool]:
    fixed_sum = 2 * (left_q + right_q)
    compatible = fixed_sum % 4 == 0
    result: dict[str, int | bool] = {
        "fixed_sum": fixed_sum,
        "compatible": compatible,
    }
    if compatible:
        result["support_neighbors"] = fixed_sum // 4
        result["active_degree_lower"] = 4 + fixed_sum // 4
    return result


def equality_arithmetic() -> dict[str, object]:
    order = 27
    upper_twice_edges = 3 * order + Fraction(order * order, 9)
    lower_twice_edges = 6 * order
    alpha = Fraction(order, 99)
    outside_constant = (14 - 3) * alpha
    return {
        "twice_edges_lower": lower_twice_edges,
        "twice_edges_upper": upper_twice_edges,
        "edges": lower_twice_edges // 2,
        "indicator_principal_coefficient": alpha,
        "Ax_constant": outside_constant,
        "quotient": ((6, 8), (3, 11)),
        "cut_edge_count_both_sides": (27 * 8, 72 * 3),
    }


def normalize_edges(edges: Iterable[Edge]) -> tuple[Edge, ...]:
    normalized = tuple(canonical_edge(*edge) for edge in edges)
    if len(normalized) != len(set(normalized)):
        raise ValueError("parallel edge")
    return tuple(sorted(normalized))


def neighbors(order: int, edges: Iterable[Edge]) -> list[set[int]]:
    result = [set() for _ in range(order)]
    for left, right in normalize_edges(edges):
        result[left].add(right)
        result[right].add(left)
    return result


def is_triangle_free(order: int, edges: Iterable[Edge]) -> bool:
    adjacent = neighbors(order, edges)
    return not any(
        right in adjacent[left]
        for root in range(order)
        for left, right in itertools.combinations(adjacent[root], 2)
    )


def codegree(adjacent: Sequence[set[int]], left: int, right: int) -> int:
    return len(adjacent[left] & adjacent[right])


def has_nonadjacent_codegree_two(order: int, edges: Iterable[Edge]) -> bool:
    adjacent = neighbors(order, edges)
    return any(
        right not in adjacent[left]
        and codegree(adjacent, left, right) == 2
        for left, right in itertools.combinations(range(order), 2)
    )


def k33_edges(offset: int = 0) -> tuple[Edge, ...]:
    return tuple(
        (offset + left, offset + 3 + right)
        for left in range(3)
        for right in range(3)
    )


def cube_edges() -> tuple[Edge, ...]:
    return tuple(
        (vertex, vertex ^ (1 << bit))
        for vertex in range(8)
        for bit in range(3)
        if vertex < (vertex ^ (1 << bit))
    )


def petersen_edges() -> tuple[Edge, ...]:
    outer = [(index, (index + 1) % 5) for index in range(5)]
    spokes = [(index, 5 + index) for index in range(5)]
    inner = [
        (5 + index, 5 + ((index + 2) % 5))
        for index in range(5)
        if index < ((index + 2) % 5)
    ]
    # The inequality above selects only three star edges; normalize the full
    # five-edge star explicitly instead.
    inner = [(5 + index, 5 + ((index + 2) % 5)) for index in range(5)]
    return normalize_edges(outer + spokes + inner)


def component_of(
    adjacent: Sequence[set[int]], starting_vertex: int
) -> set[int]:
    seen = {starting_vertex}
    queue = deque([starting_vertex])
    while queue:
        current = queue.popleft()
        for nxt in adjacent[current]:
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def four_cycle_closures_are_k33(
    order: int, edges: Iterable[Edge]
) -> bool:
    adjacent = neighbors(order, edges)
    if any(len(row) != 3 for row in adjacent):
        return False
    if not is_triangle_free(order, edges):
        return False
    found = False
    for vertices in itertools.combinations(range(order), 4):
        if all(len(adjacent[v] & set(vertices)) == 2 for v in vertices):
            found = True
            opposite = next(
                (pair for pair in itertools.combinations(vertices, 2)
                 if pair[1] not in adjacent[pair[0]]),
                None,
            )
            assert opposite is not None
            left, right = opposite
            common = adjacent[left] & adjacent[right]
            if len(common) != 3:
                return False
            third_neighbors = {
                next(iter(adjacent[item] - {left, right}))
                for item in common
            }
            if len(third_neighbors) != 1:
                return False
            third = next(iter(third_neighbors))
            expected_component = {left, right, third, *common}
            if component_of(adjacent, left) != expected_component:
                return False
            if any(
                adjacent[side] != common
                for side in (left, right, third)
            ):
                return False
    return found


def allowed_component_order_partitions(total: int = 18) -> tuple[tuple[int, ...], ...]:
    allowed = (6,) + tuple(range(10, total + 1, 2))
    result = []
    for length in range(1, total // 6 + 1):
        for parts in itertools.combinations_with_replacement(allowed, length):
            if sum(parts) == total:
                result.append(parts)
    return tuple(result)


def line_neighbors(edges: Sequence[Edge]) -> list[set[int]]:
    result = [set() for _ in edges]
    for left, right in itertools.combinations(range(len(edges)), 2):
        if set(edges[left]) & set(edges[right]):
            result[left].add(right)
            result[right].add(left)
    return result


def r_neighbors(order: int, r_edges: Iterable[Edge]) -> list[set[int]]:
    return neighbors(order, r_edges)


def k33_line_plus_disjoint_cycle() -> dict[str, object]:
    f_edges = k33_edges()
    # Cells (row,column) in this order form a 9-cycle whose consecutive
    # cells differ in both coordinates, hence represent disjoint F-edges.
    cycle = (0, 4, 8, 1, 5, 6, 2, 3, 7)
    r_edges = tuple(
        canonical_edge(cycle[index], cycle[(index + 1) % len(cycle)])
        for index in range(len(cycle))
    )
    line = line_neighbors(f_edges)
    support = r_neighbors(len(f_edges), r_edges)
    return {
        "line_degrees": tuple(map(len, line)),
        "R_degrees": tuple(map(len, support)),
        "edge_disjoint": all(not (line[v] & support[v]) for v in range(9)),
        "union_degrees": tuple(
            len(line[v] | support[v]) for v in range(9)
        ),
        "R_pairs_are_disjoint_F_edges": all(
            not (set(f_edges[left]) & set(f_edges[right]))
            for left, right in r_edges
        ),
    }


def incidence_rectangle_product(
    f_edges: Sequence[Edge],
    r_edges: Iterable[Edge],
    label_count: int,
) -> tuple[tuple[int, ...], ...]:
    product = [[0 for _ in range(label_count)] for _ in range(label_count)]
    for left_index, right_index in r_edges:
        left_edge = f_edges[left_index]
        right_edge = f_edges[right_index]
        for left_label in left_edge:
            for right_label in right_edge:
                product[left_label][right_label] += 1
                product[right_label][left_label] += 1
    return tuple(tuple(row) for row in product)


def independent_cross_matching(
    f_edges: Sequence[Edge],
    r_edges: Iterable[Edge],
    label_pair: Edge,
) -> bool:
    covers = []
    for r_edge in r_edges:
        first, second = (f_edges[index] for index in r_edge)
        if (
            label_pair[0] in first and label_pair[1] in second
        ) or (
            label_pair[1] in first and label_pair[0] in second
        ):
            covers.append(set(r_edge))
    return len(covers) == 2 and not (covers[0] & covers[1])


def matrix_scope_checks() -> dict[str, object]:
    f_edges = ((0, 2), (1, 3), (0, 4), (1, 5))
    r_edges = ((0, 1), (2, 3))
    product = incidence_rectangle_product(f_edges, r_edges, 6)

    adjacent_f = ((0, 1), (0, 2))
    adjacent_product = incidence_rectangle_product(
        adjacent_f, ((0, 1),), 3
    )

    shared_cover_f = ((0, 2), (1, 3), (1, 4))
    shared_cover_r = ((0, 1), (0, 2))
    shared_product = incidence_rectangle_product(
        shared_cover_f, shared_cover_r, 5
    )
    return {
        "independent_pair_entry": product[0][1],
        "diagonal_zero_for_disjoint_R": all(
            product[index][index] == 0 for index in range(6)
        ),
        "F_edge_entries_zero": all(
            product[left][right] == 0 for left, right in f_edges
        ),
        "adjacent_R_mutation_diagonal": adjacent_product[0][0],
        "identity_does_not_imply_matching_entry": shared_product[0][1],
        "identity_does_not_imply_matching": not independent_cross_matching(
            shared_cover_f, shared_cover_r, (0, 1)
        ),
    }


def incidence_rows(order: int, edges: Sequence[Edge]) -> list[int]:
    rows = [0] * order
    for index, (left, right) in enumerate(edges):
        rows[left] |= 1 << index
        rows[right] |= 1 << index
    return rows


def gf2_rank(rows: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for value in rows:
        current = value
        while current:
            pivot = current.bit_length() - 1
            if pivot in basis:
                current ^= basis[pivot]
            else:
                basis[pivot] = current
                break
    return len(basis)


def cycle_edges(length: int) -> tuple[Edge, ...]:
    return tuple(
        canonical_edge(index, (index + 1) % length)
        for index in range(length)
    )


def cycle_adjacency_nullity(length: int) -> int:
    rows = []
    for vertex in range(length):
        rows.append(
            (1 << ((vertex - 1) % length))
            | (1 << ((vertex + 1) % length))
        )
    return length - gf2_rank(rows)


def parity_witness_for_k33_block() -> dict[str, object]:
    f_edges = k33_edges()
    incidence = incidence_rows(6, f_edges)
    block_constraints = []
    for left_vertex in range(6):
        for right_vertex in range(6):
            row = 0
            for left_edge in range(9):
                if not ((incidence[left_vertex] >> left_edge) & 1):
                    continue
                for right_edge in range(9):
                    if (incidence[right_vertex] >> right_edge) & 1:
                        row ^= 1 << (9 * left_edge + right_edge)
            block_constraints.append(row)

    # Sum the constraint entries indexed by one bipartition class on each
    # side.  Every K3,3 edge meets each selected class once, so the resulting
    # functional is parity of all 81 M_AB entries.
    witness = 0
    for left_vertex in range(3):
        for right_vertex in range(3):
            witness ^= block_constraints[6 * left_vertex + right_vertex]
    all_entries = (1 << 81) - 1

    x_ab = (18 + 18 - 18) // 2
    return {
        "incidence_rank": gf2_rank(incidence),
        "all_entry_parity_is_constraint_combination": witness == all_entries,
        "forced_cross_component_edge_counts": (x_ab, x_ab, x_ab),
        "forced_count_is_odd": bool(x_ab & 1),
        "parity_contradiction": witness == all_entries and bool(x_ab & 1),
    }


def binary_rank_checks() -> dict[str, object]:
    cycle_nullities = {
        length: cycle_adjacency_nullity(length)
        for length in range(3, 28)
    }
    return {
        "K33_incidence_rank": gf2_rank(
            incidence_rows(6, k33_edges())
        ),
        "Petersen_incidence_rank": gf2_rank(
            incidence_rows(10, petersen_edges())
        ),
        "cycle_nullities": cycle_nullities,
        "all_cycle_nullities_match_parity": all(
            nullity == (1 if length % 2 else 2)
            for length, nullity in cycle_nullities.items()
        ),
        "component_lower_bounds": {
            1: {
                "c_R_min": 5 - 1,
                "adjacency_nullity_min": 9 - 2,
            },
            2: {
                "c_R_min": 5 - 2,
                "adjacency_nullity_min": 9 - 4,
            },
        },
    }


def link_is_single_cycle(
    pairings: Iterable[tuple[str, str]]
) -> bool:
    adjacent: dict[str, list[str]] = {}
    for left, right in pairings:
        adjacent.setdefault(left, []).append(right)
        adjacent.setdefault(right, []).append(left)
    if not adjacent or any(len(row) != 2 for row in adjacent.values()):
        return False
    seen = set()
    queue = deque([next(iter(adjacent))])
    while queue:
        current = queue.popleft()
        if current in seen:
            continue
        seen.add(current)
        queue.extend(adjacent[current])
    return seen == set(adjacent)


def simple_triangle_free_cycle_partitions(
    edge_count: int,
) -> tuple[tuple[int, ...], ...]:
    result = []
    for component_count in range(1, edge_count // 4 + 1):
        for lengths in itertools.combinations_with_replacement(
            range(4, edge_count + 1), component_count
        ):
            if sum(lengths) == edge_count:
                result.append(lengths)
    return tuple(result)


def surface_checks() -> dict[str, object]:
    correct_link = (
        ("ac", "ad"),
        ("ad", "bd"),
        ("bd", "bc"),
        ("bc", "ac"),
    )
    broken_link = correct_link[:-1]
    characteristic = 27 - 54 + 18
    return {
        "correct_link_is_circle": link_is_single_cycle(correct_link),
        "deleted_corner_breaks_link": not link_is_single_cycle(broken_link),
        "six_edge_side_graph_cycle_partitions": (
            simple_triangle_free_cycle_partitions(6)
        ),
        "euler_characteristic": characteristic,
        "orientable_total_would_be_even": characteristic % 2 == 0,
        "nonorientable_component_forced": characteristic % 2 != 0,
    }


def triangle_moments(c_triangles_of_R: int) -> dict[str, object]:
    c = c_triangles_of_R
    types = {
        0: 105 - c,
        1: 81 + 3 * c,
        2: 27 - 3 * c,
        3: 18 + c,
    }
    inactive = {
        0: types[0],
        1: types[1],
        2: types[2],
        3: c,
    }
    return {
        "types": types,
        "total_triangles": sum(types.values()),
        "outside_triples_with_R_edge": types[2],
        "outside_triples_independent": 72 - types[2],
        "inactive_count": sum(inactive.values()),
        "inactive_first_moment": sum(
            count * 2 * x_count
            for x_count, count in inactive.items()
        ),
        "inactive_second_moment": sum(
            count * (2 * x_count) ** 2
            for x_count, count in inactive.items()
        ),
        "all_triangle_second_moment": (
            sum(
                count * (2 * x_count) ** 2
                for x_count, count in inactive.items()
            )
            + 18 * 3**2
        ),
    }


def status_boundary() -> dict[str, bool]:
    text = REPORT.read_text(encoding="utf-8")
    return {
        "explicit_not_excluded": (
            "Verdict: **`n3=54` is not excluded.**" in text
        ),
        "conditional_unknown": (
            "conditional_n3_54_exclusion: UNKNOWN" in text
        ),
        "conway_unknown": "conway_99_target: UNKNOWN" in text,
        "novelty_unknown": "novelty: UNKNOWN" in text,
        "unsat_unproved": (
            "UNSAT_WITHOUT_PROOF_CERTIFICATE" in text
            and "neither solver status is evidence" in text
        ),
        "timeout_nonevidentiary": (
            "TIMEOUT_AFTER_60_SECONDS_NON_EVIDENTIARY" in text
        ),
        "no_wave14_size_cap": "No Wave 14 size cap" in text,
        "no_global_H_degree_import": (
            "global\n`H`-degree restriction is imported" in text
        ),
        "surface_not_promoted": (
            "nonorientability, not impossibility" in text
        ),
    }


def build_result() -> dict[str, object]:
    provenance = verify_provenance()
    raw = profiles_sum_36()
    residuals = residual_profiles()
    size_two = {
        f"{left}{right}": size_two_support(left, right)
        for left, right in itertools.combinations_with_replacement(
            (2, 3, 4), 2
        )
    }
    equality = equality_arithmetic()
    component_examples = {
        "K33": {
            "cubic": all(
                len(row) == 3 for row in neighbors(6, k33_edges())
            ),
            "triangle_free": is_triangle_free(6, k33_edges()),
            "has_codegree_two": has_nonadjacent_codegree_two(
                6, k33_edges()
            ),
            "four_cycle_closes": four_cycle_closures_are_k33(
                6, k33_edges()
            ),
        },
        "cube_mutation": {
            "cubic": all(
                len(row) == 3 for row in neighbors(8, cube_edges())
            ),
            "triangle_free": is_triangle_free(8, cube_edges()),
            "has_codegree_two": has_nonadjacent_codegree_two(
                8, cube_edges()
            ),
        },
        "Petersen": {
            "cubic": all(
                len(row) == 3
                for row in neighbors(10, petersen_edges())
            ),
            "triangle_free": is_triangle_free(10, petersen_edges()),
            "has_codegree_two": has_nonadjacent_codegree_two(
                10, petersen_edges()
            ),
        },
    }
    moments = {c: triangle_moments(c) for c in range(10)}
    result = {
        "schema": "conway99-wave17-n3-54-independent-structural-audit-v1",
        "provenance": provenance,
        "profile_census": {
            "raw_count": len(raw),
            "order_histogram": dict(
                sorted(Counter(order for order, _ in raw).items())
            ),
            "residual_count": len(residuals),
            "residuals": [
                {
                    "r": order,
                    "q": list(values),
                    "d_K": list(k_degrees(order, values)),
                    "X_upper": 3 * order // 2,
                }
                for order, values in residuals
            ],
            "includes_q4_boundary_profile": (
                (17, (2,) * 16 + (4,)) in residuals
            ),
            "omitting_q4_changes_residual_count": (
                len(
                    [
                        row
                        for row in residuals
                        if max(row[1]) <= 3
                    ]
                )
                != len(residuals)
            ),
        },
        "crossing_and_degree": {
            "meeting_one_by_four_counts": list(
                two_sided_crossing_counts(1, 4)
            ),
            "disjoint_two_by_four_counts": list(
                two_sided_crossing_counts(2, 4)
            ),
            "global_three_by_three_countercontrol": list(
                two_sided_crossing_counts(3, 3)
            ),
            "size_two_types": size_two,
            "size_four_triangle_neighbors": 8,
        },
        "equality": {
            key: (
                str(value) if isinstance(value, Fraction) else value
            )
            for key, value in equality.items()
        },
        "point_graph": {
            "examples": component_examples,
            "component_order_options": [
                list(parts) for parts in allowed_component_order_partitions()
            ],
            "line_plus_R": k33_line_plus_disjoint_cycle(),
        },
        "matrix_scope": matrix_scope_checks(),
        "three_K33_parity": parity_witness_for_k33_block(),
        "binary_rank": binary_rank_checks(),
        "surface": surface_checks(),
        "moments": moments,
        "status_boundary": status_boundary(),
        "hostile_mutations": {
            "q4_omission_rejected": (
                (17, (2,) * 16 + (4,)) in residuals
            ),
            "global_H_degree_zero_or_four_rejected": (
                6 in two_sided_crossing_counts(3, 3)
            ),
            "point_size_cap_rejected": 2 * 4 >= 6,
            "support_degree_equals_point_size_rejected": (
                size_two["24"]["support_neighbors"] != 2
            ),
            "adjacent_R_pair_rejected_by_diagonal": (
                matrix_scope_checks()["adjacent_R_mutation_diagonal"] != 0
            ),
            "matrix_identity_not_matching_rule": (
                matrix_scope_checks()[
                    "identity_does_not_imply_matching"
                ]
            ),
            "cube_codegree_two_rejected": component_examples[
                "cube_mutation"
            ]["has_codegree_two"],
            "deleted_surface_corner_rejected": surface_checks()[
                "deleted_corner_breaks_link"
            ],
            "all_status_boundaries_conservative": all(
                status_boundary().values()
            ),
        },
        "claim_label": "VERIFIED_RESIDUAL_NOT_EXCLUSION",
        "conditional_n3_54_exclusion": "UNKNOWN",
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
    }
    semantic = {
        key: value
        for key, value in result.items()
        if key not in {"provenance"}
    }
    result["semantic_sha256"] = hashlib.sha256(
        json.dumps(
            semantic, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    return result


def main() -> None:
    result = build_result()
    assert result["profile_census"]["raw_count"] == 23
    assert residual_profiles() == EXPECTED_RESIDUALS
    assert result["crossing_and_degree"][
        "meeting_one_by_four_counts"
    ] == [0]
    assert result["crossing_and_degree"][
        "disjoint_two_by_four_counts"
    ] == [0, 4]
    assert 6 in result["crossing_and_degree"][
        "global_three_by_three_countercontrol"
    ]
    assert equality_arithmetic()["twice_edges_lower"] == (
        equality_arithmetic()["twice_edges_upper"]
    )
    assert result["three_K33_parity"]["parity_contradiction"]
    assert result["binary_rank"]["all_cycle_nullities_match_parity"]
    assert result["surface"]["nonorientable_component_forced"]
    assert all(
        row["inactive_first_moment"] == 270
        and row["inactive_second_moment"] == 756
        and row["all_triangle_second_moment"] == 918
        for row in result["moments"].values()
    )
    assert all(result["status_boundary"].values())
    assert all(result["hostile_mutations"].values())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
