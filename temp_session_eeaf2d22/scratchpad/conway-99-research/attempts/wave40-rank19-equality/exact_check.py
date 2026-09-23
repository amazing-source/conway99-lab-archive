#!/usr/bin/env python3
"""Exact Wave 40 equality-regime calculation over F_7.

The program reconstructs the two relevant edge-local blocks, derives the
complete outside-to-block pattern universe from the SRG parameters, and
checks the quotient-syndrome obstructions for global ranks 19, 20, and 21.
It uses only integer arithmetic reduced modulo seven.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_RESULT = HERE / "exact-results.json"
FORMAT = "wave40-rank19-equality-v1"
PUBLIC_BASE_COMMIT = "6b28af70c67f062d687251494a047debe70a246f"
PRIME = 7
TARGET = {"v": 99, "k": 14, "lambda": 1, "mu": 2}
EXPECTED_INPUTS = {
    "CONJECTURE.md":
        "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "verification/2026-07-27-wave39-orchestrator.md":
        "094db8281faf23f402f5093a617c43ebe428dae6f8ce1eceae8621472fc37111",
    "verification/wave39-edge-local-rank/independent-results.json":
        "85b8d36d6ce5ebd638e957e1731864eff75f38405935f5e51ad5b629edea5966",
    "verification/wave39-edge-local-rank/run-report.yaml":
        "0c16b53a1015f2aa8cd5e96767a97736c1da5ced6691d8ad4085f6579b44cad1",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen_inputs() -> None:
    for relative, expected in EXPECTED_INPUTS.items():
        actual = sha256_file(ROOT / relative)
        require(actual == expected, f"frozen input changed: {relative}")


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value!r}")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_bytes(),
        object_pairs_hook=strict_object,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("result must be a JSON object")
    return value


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def add_edge(adjacency: list[list[int]], left: int, right: int) -> None:
    require(left != right, "loop in local graph")
    require(adjacency[left][right] == 0, "duplicate local edge")
    adjacency[left][right] = 1
    adjacency[right][left] = 1


def canonical_edge_local_graph(partition: Sequence[int]) -> list[list[int]]:
    """Build the 27-vertex edge-local normal form for ``partition``.

    Vertices are x=0, y=1, z=2, X=3,...,14, and Y=15,...,26.
    """

    require(tuple(partition) in {(2, 2, 2), (2, 4)}, "unsupported local type")
    adjacency = [[0] * 27 for _ in range(27)]
    x_vertices = list(range(3, 15))
    y_vertices = list(range(15, 27))
    for edge in ((0, 1), (0, 2), (1, 2)):
        add_edge(adjacency, *edge)
    for vertex in x_vertices:
        add_edge(adjacency, 0, vertex)
    for vertex in y_vertices:
        add_edge(adjacency, 1, vertex)

    offset = 0
    for part in partition:
        xs = x_vertices[offset : offset + 2 * part]
        ys = y_vertices[offset : offset + 2 * part]
        for index in range(part):
            x_even = xs[2 * index]
            x_odd = xs[2 * index + 1]
            y_even = ys[2 * index]
            y_odd = ys[2 * index + 1]
            next_x_even = xs[(2 * (index + 1)) % (2 * part)]
            add_edge(adjacency, x_even, x_odd)
            add_edge(adjacency, y_even, y_odd)
            add_edge(adjacency, x_odd, y_odd)
            add_edge(adjacency, y_even, next_x_even)
        offset += 2 * part
    require(offset == 12, "partition did not consume both sides")
    require([sum(row) for row in adjacency[:3]] == [14, 14, 2], "bad roots")
    require({sum(row) for row in adjacency[3:]} == {3}, "bad side degree")
    return adjacency


def transport_block(adjacency: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return K[L,L]=J-I-2A over F_7."""

    require(len(adjacency) == 27, "local block must have order 27")
    return [
        [
            (1 - int(row == column) - 2 * adjacency[row][column]) % PRIME
            for column in range(27)
        ]
        for row in range(27)
    ]


def rref(
    matrix: Sequence[Sequence[int]],
    *,
    column_count: int | None = None,
) -> tuple[list[list[int]], tuple[int, ...]]:
    work = [[entry % PRIME for entry in row] for row in matrix]
    columns = len(work[0]) if work else int(column_count or 0)
    require(all(len(row) == columns for row in work), "ragged matrix")
    pivot_columns: list[int] = []
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, PRIME)
        work[rank] = [(entry * inverse) % PRIME for entry in work[rank]]
        for row in range(len(work)):
            if row == rank or work[row][column] == 0:
                continue
            factor = work[row][column]
            work[row] = [
                (left - factor * right) % PRIME
                for left, right in zip(work[row], work[rank])
            ]
        pivot_columns.append(column)
        rank += 1
        if rank == len(work):
            break
    return work, tuple(pivot_columns)


def rank_mod_7(matrix: Sequence[Sequence[int]]) -> int:
    return len(rref(matrix)[1])


def nullspace_basis(
    matrix: Sequence[Sequence[int]],
    *,
    column_count: int | None = None,
) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = rref(matrix, column_count=column_count)
    columns = len(reduced[0]) if reduced else int(column_count or 0)
    free = [column for column in range(columns) if column not in pivots]
    basis: list[tuple[int, ...]] = []
    for free_column in free:
        vector = [0] * columns
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = (-reduced[row][free_column]) % PRIME
        basis.append(tuple(vector))
    return tuple(basis)


def canonical_span(vectors: Iterable[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    rows = [tuple(entry % PRIME for entry in vector) for vector in vectors]
    reduced, pivots = rref(rows, column_count=8)
    return tuple(tuple(reduced[row]) for row in range(len(pivots)))


def projective_representative(vector: Sequence[int]) -> tuple[int, ...]:
    reduced = tuple(entry % PRIME for entry in vector)
    require(any(reduced), "zero vector has no projective representative")
    first = next(entry for entry in reduced if entry)
    inverse = pow(first, -1, PRIME)
    return tuple((entry * inverse) % PRIME for entry in reduced)


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(a * b for a, b in zip(left, right)) % PRIME


def span_checks(
    basis: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    """Return equations cutting out the row span of ``basis`` in F_7^8."""

    return nullspace_basis(basis, column_count=8)


def in_span(vector: Sequence[int], checks: Sequence[Sequence[int]]) -> bool:
    return all(dot(vector, check) == 0 for check in checks)


def pattern_vertices(
    adjacent_to_z: int,
    x_indices: Sequence[int],
    y_indices: Sequence[int],
) -> frozenset[int]:
    require(adjacent_to_z in (0, 1), "z flag must be binary")
    require(len(x_indices) == len(y_indices) == 2 - adjacent_to_z, "bad side sizes")
    vertices = {3 + index for index in x_indices}
    vertices.update(15 + index for index in y_indices)
    if adjacent_to_z:
        vertices.add(2)
    return frozenset(vertices)


def outside_patterns(adjacent_to_z: int) -> list[dict[str, Any]]:
    """Enumerate the complete SRG-count pattern universe relative to L.

    For w outside L, w is nonadjacent to x and y.  The mu=2 equations for
    (w,x) and (w,y) are

        a_z + |N(w) intersect X| = 2,
        a_z + |N(w) intersect Y| = 2.
    """

    choose = 2 - adjacent_to_z
    patterns: list[dict[str, Any]] = []
    for x_indices in itertools.combinations(range(12), choose):
        for y_indices in itertools.combinations(range(12), choose):
            patterns.append(
                {
                    "adjacent_to_z": adjacent_to_z,
                    "X_indices": tuple(x_indices),
                    "Y_indices": tuple(y_indices),
                    "vertices": pattern_vertices(
                        adjacent_to_z, x_indices, y_indices
                    ),
                }
            )
    expected = 144 if adjacent_to_z else 4_356
    require(len(patterns) == expected, "outside pattern universe is incomplete")
    return patterns


def affine_k_column(pattern: dict[str, Any]) -> tuple[int, ...]:
    """Return K[L,w]: 1 for a nonedge and -1=6 for an edge."""

    adjacent = pattern["vertices"]
    return tuple(6 if vertex in adjacent else 1 for vertex in range(27))


def adjacency_indicator_column(pattern: dict[str, Any]) -> tuple[int, ...]:
    """A deliberately wrong control: A[L,w], not K[L,w]."""

    adjacent = pattern["vertices"]
    return tuple(int(vertex in adjacent) for vertex in range(27))


def local_common_neighbor_cap(
    adjacency: Sequence[Sequence[int]],
    pattern: dict[str, Any],
) -> bool:
    """Check a necessary lambda=1 condition visible entirely inside L.

    If w is adjacent to a side vertex u, the known common neighbors of w,u
    inside L cannot already exceed one.
    """

    adjacent = pattern["vertices"]
    for vertex in adjacent:
        if vertex < 3:
            continue
        known = sum(
            adjacency[vertex][other]
            for other in adjacent
            if other >= 3
        )
        if known > 1:
            return False
    return True


def syndrome(
    column: Sequence[int],
    local_kernel: Sequence[Sequence[int]],
) -> tuple[int, ...]:
    """Coordinate the quotient F_7^L / col(B) using ker(B).

    B is symmetric, so col(B)=ker(B)^perp.  The syndrome is zero exactly
    when the column lies in col(B).
    """

    return tuple(dot(kernel_vector, column) for kernel_vector in local_kernel)


def bipartite_matching(
    edges: Iterable[tuple[int, int]],
) -> tuple[int, list[list[int]]]:
    adjacency = [[] for _ in range(12)]
    for left, right in edges:
        adjacency[left].append(right)
    order = sorted(range(12), key=lambda left: len(adjacency[left]))
    matched_left = [-1] * 12

    def augment(left: int, seen: list[bool]) -> bool:
        for right in adjacency[left]:
            if seen[right]:
                continue
            seen[right] = True
            if matched_left[right] < 0 or augment(matched_left[right], seen):
                matched_left[right] = left
                return True
        return False

    size = sum(augment(left, [False] * 12) for left in order)
    pairs = sorted(
        [[left, right] for right, left in enumerate(matched_left) if left >= 0]
    )
    return size, pairs


def maximum_bipartite_matching(
    edges: Iterable[tuple[int, int]],
) -> int:
    return bipartite_matching(edges)[0]


def z_pattern_syndromes(
    local_kernel: Sequence[Sequence[int]],
) -> dict[tuple[int, int], tuple[int, ...]]:
    result: dict[tuple[int, int], tuple[int, ...]] = {}
    for pattern in outside_patterns(1):
        pair = (pattern["X_indices"][0], pattern["Y_indices"][0])
        result[pair] = syndrome(affine_k_column(pattern), local_kernel)
    require(len(result) == 144, "z-neighbor pattern map lost an edge")
    return result


def two_space_census(
    z_syndromes: dict[tuple[int, int], tuple[int, ...]],
) -> dict[str, Any]:
    require(all(any(value) for value in z_syndromes.values()), "zero z syndrome")
    line_counts = Counter(
        projective_representative(value) for value in z_syndromes.values()
    )
    lines = sorted(line_counts)
    require(len(lines) == 66, "projective z-syndrome line count changed")

    spaces = {
        canonical_span((lines[left], lines[right]))
        for left in range(len(lines))
        for right in range(left + 1, len(lines))
    }
    require(all(len(space) == 2 for space in spaces), "line pair did not span a plane")
    require(len(spaces) == 1_923, "two-space census changed")

    matching_distribution: Counter[int] = Counter()
    edge_distribution: Counter[int] = Counter()
    for space in spaces:
        checks = span_checks(space)
        edges = [
            pair
            for pair, value in z_syndromes.items()
            if in_span(value, checks)
        ]
        edge_distribution[len(edges)] += 1
        matching_distribution[maximum_bipartite_matching(edges)] += 1

    require(max(matching_distribution) == 8, "two-space matching maximum changed")
    return {
        "projective_line_count": len(lines),
        "line_pattern_multiplicity_distribution": {
            str(count): multiplicity
            for count, multiplicity in sorted(Counter(line_counts.values()).items())
        },
        "maximum_patterns_on_one_line": max(line_counts.values()),
        "two_space_count": len(spaces),
        "two_space_edge_count_distribution": {
            str(count): multiplicity
            for count, multiplicity in sorted(edge_distribution.items())
        },
        "two_space_matching_number_distribution": {
            str(count): multiplicity
            for count, multiplicity in sorted(matching_distribution.items())
        },
        "maximum_matching_in_a_two_space": max(matching_distribution),
    }


def three_space_positive_control(
    z_syndromes: dict[tuple[int, int], tuple[int, ...]],
) -> dict[str, Any]:
    """Show exactly why the quotient argument stops at global rank 22."""

    lines = sorted(
        {
            projective_representative(value)
            for value in z_syndromes.values()
        }
    )
    two_spaces = {
        canonical_span((lines[left], lines[right]))
        for left in range(len(lines))
        for right in range(left + 1, len(lines))
    }
    three_spaces = sorted(
        {
            canonical_span((*space, line))
            for space in two_spaces
            for line in lines
            if len(canonical_span((*space, line))) == 3
        }
    )
    require(len(three_spaces) == 25_744, "three-space census changed")

    perfect_space_count = 0
    witness: dict[str, Any] | None = None
    for space in three_spaces:
        checks = span_checks(space)
        edges = sorted(
            pair
            for pair, value in z_syndromes.items()
            if in_span(value, checks)
        )
        matching_size, matching = bipartite_matching(edges)
        if matching_size == 12:
            perfect_space_count += 1
            if witness is None:
                witness = {
                    "basis": [list(row) for row in space],
                    "contained_edge_count": len(edges),
                    "perfect_matching": matching,
                }

    require(perfect_space_count == 32, "rank-22 positive-control count changed")
    require(witness is not None, "rank-22 positive control disappeared")
    return {
        "three_space_count": len(three_spaces),
        "three_spaces_supporting_a_perfect_matching": perfect_space_count,
        "canonical_first_witness": witness,
        "meaning": (
            "A quotient of dimension three can contain all twelve forced Z "
            "patterns, so this local argument does not exclude r7=22."
        ),
    }


def local_block_record(partition: tuple[int, ...]) -> dict[str, Any]:
    adjacency = canonical_edge_local_graph(partition)
    block = transport_block(adjacency)
    rank = rank_mod_7(block)
    kernel = nullspace_basis(block)
    require(len(kernel) == 27 - rank, "rank-nullity failed")
    z_syndromes = z_pattern_syndromes(kernel)
    zero_z = sum(not any(value) for value in z_syndromes.values())
    result: dict[str, Any] = {
        "partition": list(partition),
        "rank_F7": rank,
        "nullity_F7": len(kernel),
        "z_neighbor_pattern_count": len(z_syndromes),
        "z_neighbor_columns_in_local_column_space": zero_z,
    }
    if partition == (2, 2, 2):
        non_z = outside_patterns(0)
        admitted = [
            pattern
            for pattern in non_z
            if local_common_neighbor_cap(adjacency, pattern)
        ]
        all_patterns = outside_patterns(1) + non_z
        column_space_survivors = [
            pattern
            for pattern in all_patterns
            if not any(syndrome(affine_k_column(pattern), kernel))
        ]
        wrong_column_survivors = [
            pattern
            for pattern in all_patterns
            if not any(syndrome(adjacency_indicator_column(pattern), kernel))
        ]
        require(len(non_z) == 4_356, "non-z universe count changed")
        require(len(admitted) == 4_116, "visible lambda filter changed")
        require(len(column_space_survivors) == 36, "rank-19 survivor count changed")
        require(
            {pattern["adjacent_to_z"] for pattern in column_space_survivors} == {0},
            "a z-neighbor column entered the local column space",
        )
        result.update(
            {
                "non_z_pattern_count": len(non_z),
                "non_z_patterns_passing_visible_lambda_cap": len(admitted),
                "combined_outside_pattern_count": len(all_patterns),
                "columns_in_local_column_space": len(column_space_survivors),
                "column_space_survivors_by_z_flag": dict(
                    sorted(
                        Counter(
                            str(pattern["adjacent_to_z"])
                            for pattern in column_space_survivors
                        ).items()
                    )
                ),
                "wrong_adjacency_indicator_survivor_count": len(
                    wrong_column_survivors
                ),
                "quotient_census_for_z_neighbors": two_space_census(z_syndromes),
                "rank_22_positive_control": three_space_positive_control(
                    z_syndromes
                ),
            }
        )
    return result


def rank_completion_lemma() -> dict[str, Any]:
    return {
        "block_form": "K=[[B,C],[C^T,D]] with B=K[L,L]",
        "restriction_space": (
            "R=col([B,C]) is the restriction to L of the full column space"
        ),
        "dimension_bounds": "col(B) subseteq R and dim(R)<=rank(K)",
        "quotient_bound": "dim(R/col(B))<=rank(K)-rank(B)",
        "equality_case": (
            "If rank(K)=rank(B), every outside restricted column K[L,w] "
            "lies in col(B)."
        ),
        "syndrome_identification": (
            "Because B is symmetric, col(B)=ker(B)^perp; the eight (or six) "
            "kernel dot products identify F_7^L/col(B)."
        ),
    }


def geometry_record() -> dict[str, Any]:
    return {
        "local_set": "L={x,y,z} union X union Y",
        "sizes": {"L": 27, "X": 12, "Y": 12, "outside": 72},
        "outside_vertex_equations": [
            "w is nonadjacent to x and y",
            "a_z+|N(w) intersect X|=mu=2",
            "a_z+|N(w) intersect Y|=mu=2",
        ],
        "complete_pattern_counts": {
            "a_z=1": "12*12=144",
            "a_z=0": "binom(12,2)^2=4356",
        },
        "triangle_mate_set": (
            "Z=N(z)-{x,y} has size 12 and lies outside L, because z has no "
            "neighbor in X or Y."
        ),
        "forced_perfect_matching": (
            "For each u in X, the nonedge uz has common neighbor x and one "
            "further common neighbor in Z; similarly for Y. Hence the twelve "
            "Z patterns form a perfect matching X--Y."
        ),
        "distinctness": (
            "The perfect-matching property already makes the twelve patterns "
            "distinct; alternatively, equal patterns would give two vertices "
            "at least three common neighbors, contradicting lambda=1 or mu=2."
        ),
        "restricted_column": "K[L,w]=1-2*A[L,w], i.e. 1 on nonedges and 6 on edges",
    }


@lru_cache(maxsize=1)
def _exact_record_cached() -> dict[str, Any]:
    block_222 = local_block_record((2, 2, 2))
    block_24 = local_block_record((2, 4))
    require(block_222["rank_F7"] == 19, "2+2+2 local rank changed")
    require(block_24["rank_F7"] == 21, "2+4 local rank changed")
    require(
        block_24["z_neighbor_columns_in_local_column_space"] == 0,
        "a 2+4 equality completion survived",
    )

    return {
        "format": FORMAT,
        "role": "proof_a",
        "claim_label": "CANDIDATE",
        "git_commit": PUBLIC_BASE_COMMIT,
        "scope": (
            "Conditional characteristic-seven equality-regime obstruction at "
            "the prism-free endpoint n3=4158"
        ),
        "frozen_inputs": EXPECTED_INPUTS,
        "premises": {
            "endpoint": "n3=4158, equivalently no induced triangular prism",
            "matrix": "K=N M N^T=J-I-2A over F_7",
            "identities": ["K^2=0", "rank_F7(K)=rank_F7(M)=r7"],
            "verified_endpoint_local_types": {
                "2+2+2": 19,
                "2+4": 21,
                "3+3": 25,
                "6": 23,
            },
        },
        "outside_geometry": geometry_record(),
        "rank_completion": rank_completion_lemma(),
        "local_blocks": {
            "2+2+2": block_222,
            "2+4": block_24,
        },
        "case_analysis": {
            "r7=19": {
                "forced_edge_types": ["2+2+2"],
                "quotient_dimension_at_most": 0,
                "contradiction": (
                    "All outside columns would lie in col(B), but none of the "
                    "144 required z-neighbor columns does."
                ),
            },
            "r7=20": {
                "forced_edge_types": ["2+2+2"],
                "quotient_dimension_at_most": 1,
                "contradiction": (
                    "The twelve distinct Z patterns would lie on one quotient "
                    "line, but every line contains at most four patterns."
                ),
            },
            "r7=21": {
                "possible_edge_types": ["2+2+2", "2+4"],
                "type_2+4_branch": (
                    "If a 2+4 edge exists, rank(B)=rank(K)=21, yet none of "
                    "its 144 required z-neighbor columns lies in col(B)."
                ),
                "all_2+2+2_branch": (
                    "Otherwise every edge is 2+2+2. The twelve Z patterns "
                    "must form a perfect matching inside a quotient subspace "
                    "of dimension at most two. All 1,923 two-spaces have "
                    "matching number at most eight."
                ),
            },
        },
        "candidate_theorem": {
            "statement": (
                "If n3=4158 for a hypothetical srg(99,14,1,2), then "
                "rank_F7(M)>=22."
            ),
            "previous_verified_endpoint_floor": 19,
            "new_conditional_floor": 22,
            "endpoint_excluded": False,
            "general_upper_bound_improved_below_4158": False,
        },
        "limitations": [
            "Discovery cannot verify itself; independent verification is required.",
            "The theorem is conditional on the prism-free endpoint.",
            "Ranks 22 through 44 are not excluded.",
            "No graph, endpoint contradiction, or upper bound below 4158 is produced.",
            "K^2=0 is a frozen consistency identity but is not needed by this obstruction.",
            "Literature novelty and priority remain UNKNOWN.",
        ],
        "target_status": "UNKNOWN",
        "novelty_status": "UNKNOWN",
    }


def exact_record() -> dict[str, Any]:
    return copy.deepcopy(_exact_record_cached())


def validate_record(record: dict[str, Any]) -> None:
    expected = exact_record()
    require(record == expected, "stored record differs from exact regeneration")
    require(record["claim_label"] == "CANDIDATE", "discovery status inflated")
    theorem = record["candidate_theorem"]
    require(theorem["endpoint_excluded"] is False, "endpoint status inflated")
    require(
        theorem["general_upper_bound_improved_below_4158"] is False,
        "general upper-bound status inflated",
    )
    require(record["target_status"] == "UNKNOWN", "target status inflated")
    require(record["novelty_status"] == "UNKNOWN", "novelty status inflated")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--output", type=Path)
    modes.add_argument("--verify", type=Path)
    args = parser.parse_args()

    verify_frozen_inputs()
    record = exact_record()
    if args.verify:
        loaded = load_json(args.verify)
        validate_record(loaded)
        require(args.verify.read_bytes() == canonical_json(record), "JSON is not canonical")
        print(f"PASS: {args.verify} matches exact regeneration")
        return 0

    output = args.output or DEFAULT_RESULT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(canonical_json(record))
    print(f"WROTE: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
