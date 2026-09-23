#!/usr/bin/env python3
"""Clean-room verifier for the Wave 40 endpoint rank >= 22 candidate.

This module intentionally does not import or execute discovery-side code.
It reconstructs the two needed 27-vertex principal blocks directly from the
SRG(99,14,1,2) local rules and performs all linear algebra over F_7.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence


P = 7
ROOT = Path(__file__).resolve().parents[2]
X_VERTICES = tuple(range(3, 15))
Y_VERTICES = tuple(range(15, 27))
FROZEN_INPUTS = {
    "CONJECTURE.md": "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "agents/2026-07-27-wave40-rank19-equality.md": (
        "6ae7b91df5d42fd3831b30b02e66d772aa3e56bcff28098ad7aeab8c9e70dcda"
    ),
    "attempts/wave40-rank19-equality/exact-results.json": (
        "631b36c1a3a8693ea193c21ebc0f9fa57aee68bdf5f7c52b28aa469a475e4553"
    ),
    "attempts/wave40-rank19-equality/run-report.yaml": (
        "6782793adbff657cfa3e4aaa8bf3fa53e692144741e573268c67692a46a7471a"
    ),
    "verification/wave39-edge-local-rank/independent-results.json": (
        "85b8d36d6ce5ebd638e957e1731864eff75f38405935f5e51ad5b629edea5966"
    ),
    "verification/wave39-edge-local-rank/run-report.yaml": (
        "0c16b53a1015f2aa8cd5e96767a97736c1da5ced6691d8ad4085f6579b44cad1"
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_edge(adjacency: list[list[int]], left: int, right: int) -> None:
    if left == right:
        raise ValueError("loops are forbidden")
    adjacency[left][right] = 1
    adjacency[right][left] = 1


def construct_local_adjacency(partition: Sequence[int]) -> list[list[int]]:
    """Build the edge-local graph from its three forced perfect matchings.

    The vertices are x=0, y=1, z=2, X=3..14, and Y=15..26.  Within a
    component of parameter m, the X matching, cross matching, and Y matching
    form a cycle of length 4m.
    """

    if sum(partition) != 6 or any(part < 1 for part in partition):
        raise ValueError("partition must consist of positive parts summing to six")

    adjacency = [[0] * 27 for _ in range(27)]
    for edge in ((0, 1), (0, 2), (1, 2)):
        add_edge(adjacency, *edge)
    for vertex in X_VERTICES:
        add_edge(adjacency, 0, vertex)
    for vertex in Y_VERTICES:
        add_edge(adjacency, 1, vertex)

    offset = 0
    for part in partition:
        for index in range(part):
            xa = X_VERTICES[offset + 2 * index]
            xb = X_VERTICES[offset + 2 * index + 1]
            ya = Y_VERTICES[offset + 2 * index]
            yb = Y_VERTICES[offset + 2 * index + 1]
            next_ya = Y_VERTICES[offset + 2 * ((index + 1) % part)]
            add_edge(adjacency, xa, xb)
            add_edge(adjacency, xa, ya)
            add_edge(adjacency, xb, yb)
            add_edge(adjacency, yb, next_ya)
        offset += 2 * part
    return adjacency


def local_cycle_parts(adjacency: Sequence[Sequence[int]]) -> tuple[int, ...]:
    remaining = set(X_VERTICES + Y_VERTICES)
    lengths: list[int] = []
    while remaining:
        start = min(remaining)
        stack = [start]
        component: set[int] = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            for neighbor in X_VERTICES + Y_VERTICES:
                if adjacency[vertex][neighbor] and neighbor not in component:
                    stack.append(neighbor)
        remaining -= component
        lengths.append(len(component))
    return tuple(sorted(length // 4 for length in lengths))


def validate_local_geometry(
    adjacency: Sequence[Sequence[int]], expected_partition: Sequence[int]
) -> None:
    if len(adjacency) != 27 or any(len(row) != 27 for row in adjacency):
        raise ValueError("local adjacency matrix must be 27 by 27")
    if any(adjacency[i][i] for i in range(27)):
        raise ValueError("local adjacency matrix has a loop")
    if any(adjacency[i][j] != adjacency[j][i] for i in range(27) for j in range(27)):
        raise ValueError("local adjacency matrix is not symmetric")

    expected_x = {1, 2, *X_VERTICES}
    expected_y = {0, 2, *Y_VERTICES}
    expected_z = {0, 1}
    actual_x = {j for j in range(27) if adjacency[0][j]}
    actual_y = {j for j in range(27) if adjacency[1][j]}
    actual_z = {j for j in range(27) if adjacency[2][j]}
    if actual_x != expected_x or actual_y != expected_y or actual_z != expected_z:
        raise ValueError("x, y, or z has the wrong forced local neighborhood")

    for side in (X_VERTICES, Y_VERTICES):
        degrees = [sum(adjacency[v][u] for u in side) for v in side]
        if degrees != [1] * 12:
            raise ValueError("a side does not induce a perfect matching")
    cross_x = [sum(adjacency[v][u] for u in Y_VERTICES) for v in X_VERTICES]
    cross_y = [sum(adjacency[v][u] for u in X_VERTICES) for v in Y_VERTICES]
    if cross_x != [1] * 12 or cross_y != [1] * 12:
        raise ValueError("the X--Y relation is not a perfect matching")
    if local_cycle_parts(adjacency) != tuple(sorted(expected_partition)):
        raise ValueError("the three matching union has the wrong cycle partition")


def transported_block(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            (1 - (1 if i == j else 0) - 2 * adjacency[i][j]) % P
            for j in range(27)
        ]
        for i in range(27)
    ]


def rref_mod(rows: Iterable[Sequence[int]]) -> tuple[list[list[int]], list[int]]:
    matrix = [[entry % P for entry in row] for row in rows]
    if not matrix:
        return [], []
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged matrix")

    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(width):
        selected = next(
            (row for row in range(pivot_row, len(matrix)) if matrix[row][column]),
            None,
        )
        if selected is None:
            continue
        matrix[pivot_row], matrix[selected] = matrix[selected], matrix[pivot_row]
        inverse = pow(matrix[pivot_row][column], -1, P)
        matrix[pivot_row] = [(inverse * entry) % P for entry in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                (entry - factor * pivot) % P
                for entry, pivot in zip(matrix[row], matrix[pivot_row])
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return matrix, pivot_columns


def rank_mod(rows: Iterable[Sequence[int]]) -> int:
    return len(rref_mod(rows)[1])


def kernel_basis(matrix: Sequence[Sequence[int]]) -> list[tuple[int, ...]]:
    reduced, pivots = rref_mod(matrix)
    width = len(matrix[0])
    free_columns = [column for column in range(width) if column not in pivots]
    basis: list[tuple[int, ...]] = []
    for free in free_columns:
        vector = [0] * width
        vector[free] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = (-reduced[row][free]) % P
        basis.append(tuple(vector))
    return basis


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(a * b for a, b in zip(left, right)) % P


def syndrome(kernel: Sequence[Sequence[int]], column: Sequence[int]) -> tuple[int, ...]:
    return tuple(dot(vector, column) for vector in kernel)


def normalize_line(vector: Sequence[int]) -> tuple[int, ...]:
    reduced = tuple(entry % P for entry in vector)
    first = next((entry for entry in reduced if entry), None)
    if first is None:
        raise ValueError("the zero vector has no projective line")
    inverse = pow(first, -1, P)
    return tuple((inverse * entry) % P for entry in reduced)


def row_space_key(rows: Iterable[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = rref_mod(rows)
    return tuple(tuple(reduced[index]) for index in range(len(pivots)))


def in_row_space(vector: Sequence[int], basis: Sequence[Sequence[int]]) -> bool:
    work = [entry % P for entry in vector]
    for row in basis:
        pivot = next((index for index, entry in enumerate(row) if entry), None)
        if pivot is None:
            continue
        factor = work[pivot]
        if factor:
            work = [(entry - factor * base) % P for entry, base in zip(work, row)]
    return not any(work)


def restricted_z_column(x_index: int, y_index: int) -> tuple[int, ...]:
    if x_index not in range(12) or y_index not in range(12):
        raise ValueError("pattern indices must lie in 0..11")
    column = [1] * 27
    column[2] = P - 1
    column[X_VERTICES[x_index]] = P - 1
    column[Y_VERTICES[y_index]] = P - 1
    return tuple(column)


def z_patterns(
    kernel: Sequence[Sequence[int]],
) -> list[dict[str, object]]:
    patterns: list[dict[str, object]] = []
    for x_index in range(12):
        for y_index in range(12):
            column = restricted_z_column(x_index, y_index)
            quotient = syndrome(kernel, column)
            patterns.append(
                {
                    "edge": (x_index, y_index),
                    "syndrome": quotient,
                    "line": None if not any(quotient) else normalize_line(quotient),
                }
            )
    return patterns


def maximum_matching(edges: Iterable[tuple[int, int]]) -> tuple[int, list[tuple[int, int]]]:
    adjacency: dict[int, list[int]] = {left: [] for left in range(12)}
    for left, right in sorted(set(edges)):
        adjacency[left].append(right)
    match_right: dict[int, int] = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in adjacency[left]:
            if right in seen:
                continue
            seen.add(right)
            if right not in match_right or augment(match_right[right], seen):
                match_right[right] = left
                return True
        return False

    size = sum(augment(left, set()) for left in range(12))
    matching = sorted((left, right) for right, left in match_right.items())
    return size, matching


def is_perfect_pattern_matching(edges: Iterable[tuple[int, int]]) -> bool:
    edge_list = list(edges)
    return (
        len(edge_list) == 12
        and {left for left, _ in edge_list} == set(range(12))
        and {right for _, right in edge_list} == set(range(12))
        and len(set(edge_list)) == 12
    )


def contained_edges(
    basis: Sequence[Sequence[int]], patterns: Sequence[dict[str, object]]
) -> list[tuple[int, int]]:
    return [
        tuple(pattern["edge"])
        for pattern in patterns
        if in_row_space(pattern["syndrome"], basis)
    ]


def two_space_census(
    line_groups: dict[tuple[int, ...], list[tuple[int, int]]],
    patterns: Sequence[dict[str, object]],
) -> dict[str, object]:
    lines = sorted(line_groups)
    raw_pairs = list(itertools.combinations(lines, 2))
    span_multiplicity: Counter[tuple[tuple[int, ...], ...]] = Counter(
        row_space_key(pair) for pair in raw_pairs
    )

    matching_distribution: Counter[int] = Counter()
    edge_distribution: Counter[int] = Counter()
    maximum = 0
    for basis in sorted(span_multiplicity):
        edges = contained_edges(basis, patterns)
        matching_size, _ = maximum_matching(edges)
        maximum = max(maximum, matching_size)
        matching_distribution[matching_size] += 1
        edge_distribution[len(edges)] += 1

    multiplicity_distribution = Counter(span_multiplicity.values())
    return {
        "raw_unordered_line_pairs": len(raw_pairs),
        "distinct_generated_two_spaces": len(span_multiplicity),
        "duplicate_pair_normalizations_removed": len(raw_pairs) - len(span_multiplicity),
        "pair_span_multiplicity_distribution": {
            str(key): multiplicity_distribution[key]
            for key in sorted(multiplicity_distribution)
        },
        "contained_pattern_count_distribution": {
            str(key): edge_distribution[key] for key in sorted(edge_distribution)
        },
        "matching_number_distribution": {
            str(key): matching_distribution[key]
            for key in sorted(matching_distribution)
        },
        "maximum_matching_number": maximum,
    }


def three_space_census(
    line_groups: dict[tuple[int, ...], list[tuple[int, int]]],
    patterns: Sequence[dict[str, object]],
) -> dict[str, object]:
    lines = sorted(line_groups)
    spaces: set[tuple[tuple[int, ...], ...]] = set()
    independent_raw = 0
    for triple in itertools.combinations(lines, 3):
        basis = row_space_key(triple)
        if len(basis) == 3:
            independent_raw += 1
            spaces.add(basis)

    positive: list[dict[str, object]] = []
    for basis in sorted(spaces):
        edges = contained_edges(basis, patterns)
        matching_size, matching = maximum_matching(edges)
        if matching_size == 12:
            if not is_perfect_pattern_matching(matching):
                raise AssertionError("matching routine returned a malformed witness")
            positive.append(
                {
                    "basis": [list(row) for row in basis],
                    "contained_pattern_count": len(edges),
                    "perfect_matching": [list(edge) for edge in matching],
                }
            )

    return {
        "raw_unordered_line_triples": len(list(itertools.combinations(lines, 3))),
        "raw_independent_line_triples": independent_raw,
        "distinct_generated_three_spaces": len(spaces),
        "duplicate_independent_triples_removed": independent_raw - len(spaces),
        "spaces_supporting_a_perfect_matching": len(positive),
        "canonical_first_witness": positive[0] if positive else None,
    }


def analyze_block(partition: Sequence[int], full_census: bool) -> dict[str, object]:
    adjacency = construct_local_adjacency(partition)
    validate_local_geometry(adjacency, partition)
    block = transported_block(adjacency)
    rank = rank_mod(block)
    kernel = kernel_basis(block)
    if rank + len(kernel) != 27:
        raise AssertionError("rank-nullity failed")
    patterns = z_patterns(kernel)
    zero_patterns = [
        tuple(pattern["edge"]) for pattern in patterns if not any(pattern["syndrome"])
    ]

    result: dict[str, object] = {
        "partition": list(partition),
        "cycle_component_lengths": [4 * part for part in sorted(partition)],
        "rank_F7": rank,
        "nullity_F7": len(kernel),
        "z_pattern_count": len(patterns),
        "z_patterns_in_column_space": len(zero_patterns),
    }
    if not full_census:
        return result

    line_groups: dict[tuple[int, ...], list[tuple[int, int]]] = defaultdict(list)
    for pattern in patterns:
        if pattern["line"] is None:
            continue
        line_groups[pattern["line"]].append(tuple(pattern["edge"]))
    line_multiplicities = Counter(len(edges) for edges in line_groups.values())
    result["projective_syndromes"] = {
        "line_count": len(line_groups),
        "line_pattern_multiplicity_distribution": {
            str(key): line_multiplicities[key] for key in sorted(line_multiplicities)
        },
        "maximum_patterns_on_one_line": max(map(len, line_groups.values())),
        "nonzero_scalar_multiples_per_line": P - 1,
    }
    result["two_space_census"] = two_space_census(line_groups, patterns)
    result["three_space_boundary"] = three_space_census(line_groups, patterns)
    return result


def check_frozen_inputs() -> dict[str, str]:
    observed = {path: sha256_file(ROOT / path) for path in FROZEN_INPUTS}
    if observed != FROZEN_INPUTS:
        mismatches = {
            path: {"expected": FROZEN_INPUTS[path], "observed": observed[path]}
            for path in FROZEN_INPUTS
            if observed[path] != FROZEN_INPUTS[path]
        }
        raise ValueError(f"frozen input mismatch: {mismatches}")
    return observed


def compute_results() -> dict[str, object]:
    frozen = check_frozen_inputs()
    block_222 = analyze_block((2, 2, 2), full_census=True)
    block_24 = analyze_block((2, 4), full_census=False)

    results = {
        "format": "wave40-rank19-equality-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Conditional theorem n3=4158 implies rank_F7(M)>=22 for a "
            "hypothetical srg(99,14,1,2)"
        ),
        "frozen_inputs": frozen,
        "local_geometry": {
            "derivation": [
                "For an edge xy, its unique common neighbor z completes the triangle.",
                "X=N(x)-{y,z} and Y=N(y)-{x,z} each have size 12.",
                "The lambda=1 rule makes each side a perfect matching.",
                "The mu=2 rule makes the X--Y relation a perfect matching.",
                "At the prism-free endpoint the needed cycle types are 2+2+2 and 2+4.",
            ],
            "outside_z_neighbors": {
                "count": 12,
                "outside_L": True,
                "pattern_rule": "each chooses exactly one X vertex and exactly one Y vertex",
                "forced_relation": "the twelve choices form a bijection X->Y",
                "complete_pattern_universe": 144,
            },
        },
        "rank_transfer": {
            "transported_matrix_mod_7": "K=N M N^T=J-I-2A",
            "rank_equality": "rank_F7(K)=rank_F7(M)",
            "reason": (
                "N is injective on im(M) because N^T N M=3M and 3 is "
                "invertible in F_7"
            ),
        },
        "quotient_argument": {
            "local_block": "B=K[L,L]",
            "restricted_column_space": "R=col([B C])",
            "bound": "dim(R/col(B))<=rank(K)-rank(B)",
            "syndrome_kernel": (
                "For symmetric B, col(B)=ker(B)^perp, so kernel dot products "
                "identify the quotient class"
            ),
        },
        "local_blocks": {
            "2+2+2": block_222,
            "2+4": block_24,
        },
        "case_audit": {
            "r7=19": (
                "Only type 2+2+2 is possible; quotient dimension is zero, "
                "but all 144 required Z syndromes are nonzero."
            ),
            "r7=20": (
                "Only type 2+2+2 is possible; quotient dimension is at most "
                "one, but a projective line contains at most four of the "
                "twelve distinct perfect-matching patterns."
            ),
            "r7=21_type_2+4": (
                "A type 2+4 block has rank 21, so quotient dimension is zero, "
                "but all 144 required Z syndromes are nonzero."
            ),
            "r7=21_all_2+2+2": (
                "The quotient dimension is at most two; every relevant "
                "generated two-space has bipartite matching number at most eight."
            ),
            "conclusion": "n3=4158 implies rank_F7(M)>=22",
        },
        "normalization_notes": {
            "projective_line_definition": (
                "all six nonzero F_7 scalar multiples are included"
            ),
            "two_space_count": (
                "1,923 is the number of distinct row spaces generated by "
                "pairs of the 66 observed lines; 2,145 raw unordered line "
                "pairs collapse by canonical RREF"
            ),
            "three_space_count": (
                "25,744 is the number of distinct dimension-three row spaces "
                "generated by observed-line triples, not the raw triple count"
            ),
        },
        "status_wall": {
            "conditional_endpoint_rank_floor": 22,
            "endpoint_excluded": False,
            "general_upper_bound_improved_below_4158": False,
            "strongest_general_upper_bound": "n3<=4158",
            "conway_99_status": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
            "rank_22_boundary_meaning": (
                "A local syndrome three-space can support a perfect matching; "
                "this only shows that this quotient obstruction stops, not "
                "that a global graph or rank-22 completion exists."
            ),
        },
    }
    validate_results(results)
    return results


def validate_results(results: dict[str, object]) -> None:
    if results.get("claim_label") != "VERIFIED":
        raise ValueError("the scoped candidate theorem was not promoted to VERIFIED")
    status = results["status_wall"]
    if status["conditional_endpoint_rank_floor"] != 22:
        raise ValueError("wrong conditional rank floor")
    if status["endpoint_excluded"]:
        raise ValueError("endpoint status inflation")
    if status["general_upper_bound_improved_below_4158"]:
        raise ValueError("general-bound status inflation")
    if status["strongest_general_upper_bound"] != "n3<=4158":
        raise ValueError("wrong general upper-bound status")
    if status["conway_99_status"] != "UNKNOWN":
        raise ValueError("Conway-99 status inflation")
    if status["literature_novelty"] != "UNKNOWN":
        raise ValueError("novelty status inflation")

    geometry = results["local_geometry"]["outside_z_neighbors"]
    if (
        geometry["count"] != 12
        or not geometry["outside_L"]
        or geometry["forced_relation"] != "the twelve choices form a bijection X->Y"
        or geometry["complete_pattern_universe"] != 144
    ):
        raise ValueError("outside z-neighbor geometry is malformed")

    block_222 = results["local_blocks"]["2+2+2"]
    if (
        block_222["rank_F7"] != 19
        or block_222["nullity_F7"] != 8
        or block_222["z_pattern_count"] != 144
        or block_222["z_patterns_in_column_space"] != 0
    ):
        raise ValueError("wrong 2+2+2 block data")
    lines = block_222["projective_syndromes"]
    if (
        lines["line_count"] != 66
        or lines["line_pattern_multiplicity_distribution"] != {"2": 60, "4": 6}
        or lines["maximum_patterns_on_one_line"] != 4
        or lines["nonzero_scalar_multiples_per_line"] != 6
    ):
        raise ValueError("wrong line census or scalar closure")

    two_spaces = block_222["two_space_census"]
    if (
        two_spaces["raw_unordered_line_pairs"] != 2145
        or two_spaces["distinct_generated_two_spaces"] != 1923
        or two_spaces["duplicate_pair_normalizations_removed"] != 222
        or two_spaces["matching_number_distribution"]
        != {"2": 480, "4": 1251, "6": 168, "8": 24}
        or two_spaces["maximum_matching_number"] != 8
    ):
        raise ValueError("wrong two-space census")

    three_spaces = block_222["three_space_boundary"]
    if (
        three_spaces["raw_unordered_line_triples"] != 45760
        or three_spaces["distinct_generated_three_spaces"] != 25744
        or three_spaces["spaces_supporting_a_perfect_matching"] != 32
    ):
        raise ValueError("wrong three-space boundary census")
    witness = three_spaces["canonical_first_witness"]
    if witness is None or not is_perfect_pattern_matching(
        tuple(edge) for edge in witness["perfect_matching"]
    ):
        raise ValueError("rank-22 positive-control witness is not a bijection")

    block_24 = results["local_blocks"]["2+4"]
    if (
        block_24["rank_F7"] != 21
        or block_24["nullity_F7"] != 6
        or block_24["z_pattern_count"] != 144
        or block_24["z_patterns_in_column_space"] != 0
    ):
        raise ValueError("wrong 2+4 equality obstruction")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify",
        type=Path,
        help="compare a committed JSON result byte-for-structure with a fresh run",
    )
    args = parser.parse_args()
    observed = compute_results()
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        validate_results(expected)
        if expected != observed:
            raise SystemExit("verification failed: stored and recomputed results differ")
        print(f"VERIFIED: {args.verify}")
    else:
        print(json.dumps(observed, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
