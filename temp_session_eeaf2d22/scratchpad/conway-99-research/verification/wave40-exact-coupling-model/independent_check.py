#!/usr/bin/env python3
"""Clean-room verifier for the universal characteristic-seven rank-25 claim.

Only frozen Wave 39 verified premises are consumed.  No discovery-side Wave
40 coupling code is imported or executed.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence


FIELD = 7
ROOT = Path(__file__).resolve().parents[2]
XV = tuple(range(3, 15))
YV = tuple(range(15, 27))
PARTITIONS = (
    (6,),
    (5, 1),
    (4, 2),
    (4, 1, 1),
    (3, 3),
    (3, 2, 1),
    (3, 1, 1, 1),
    (2, 2, 2),
    (2, 2, 1, 1),
    (2, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1),
)
INPUT_HASHES = {
    "CONJECTURE.md": "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "verification/2026-07-27-wave39-orchestrator.md": (
        "094db8281faf23f402f5093a617c43ebe428dae6f8ce1eceae8621472fc37111"
    ),
    "verification/wave39-edge-local-rank/README.md": (
        "ed749e5788c19a23629cee9f331cce0ef161500d9cb0d939eef3211085c0a405"
    ),
    "verification/wave39-edge-local-rank/independent-results.json": (
        "85b8d36d6ce5ebd638e957e1731864eff75f38405935f5e51ad5b629edea5966"
    ),
    "verification/wave39-edge-local-rank/run-report.yaml": (
        "0c16b53a1015f2aa8cd5e96767a97736c1da5ced6691d8ad4085f6579b44cad1"
    ),
}


def file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def freeze_inputs() -> dict[str, str]:
    actual = {name: file_digest(ROOT / name) for name in INPUT_HASHES}
    if actual != INPUT_HASHES:
        bad = {
            name: {"expected": INPUT_HASHES[name], "actual": actual[name]}
            for name in INPUT_HASHES
            if actual[name] != INPUT_HASHES[name]
        }
        raise ValueError(f"input freeze failed: {bad}")
    return actual


def connect(graph: list[list[int]], a: int, b: int) -> None:
    if a == b:
        raise ValueError("loop")
    graph[a][b] = graph[b][a] = 1


def local_graph(parts: Sequence[int]) -> list[list[int]]:
    """Construct the 27-point local graph from the three matching colors."""

    if sum(parts) != 6 or any(part <= 0 for part in parts):
        raise ValueError("expected a positive partition of six")
    graph = [[0] * 27 for _ in range(27)]
    for a, b in ((0, 1), (0, 2), (1, 2)):
        connect(graph, a, b)
    for vertex in XV:
        connect(graph, 0, vertex)
    for vertex in YV:
        connect(graph, 1, vertex)

    start = 0
    for part in parts:
        for i in range(part):
            xa, xb = XV[start + 2 * i : start + 2 * i + 2]
            ya, yb = YV[start + 2 * i : start + 2 * i + 2]
            next_ya = YV[start + 2 * ((i + 1) % part)]
            connect(graph, xa, xb)
            connect(graph, xa, ya)
            connect(graph, xb, yb)
            connect(graph, yb, next_ya)
        start += 2 * part
    audit_local_graph(graph, parts)
    return graph


def component_partition(graph: Sequence[Sequence[int]]) -> tuple[int, ...]:
    unseen = set(XV + YV)
    parts: list[int] = []
    while unseen:
        stack = [min(unseen)]
        component: set[int] = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(
                neighbor
                for neighbor in XV + YV
                if graph[vertex][neighbor] and neighbor not in component
            )
        unseen.difference_update(component)
        if len(component) % 4:
            raise ValueError("matching component length is not divisible by four")
        parts.append(len(component) // 4)
    return tuple(sorted(parts, reverse=True))


def audit_local_graph(graph: Sequence[Sequence[int]], parts: Sequence[int]) -> None:
    if len(graph) != 27 or any(len(row) != 27 for row in graph):
        raise ValueError("local graph is not 27 by 27")
    if any(graph[i][i] for i in range(27)):
        raise ValueError("local graph has a loop")
    if any(graph[i][j] != graph[j][i] for i in range(27) for j in range(27)):
        raise ValueError("local graph is not undirected")
    if {j for j in range(27) if graph[0][j]} != {1, 2, *XV}:
        raise ValueError("wrong x fibre")
    if {j for j in range(27) if graph[1][j]} != {0, 2, *YV}:
        raise ValueError("wrong y fibre")
    if {j for j in range(27) if graph[2][j]} != {0, 1}:
        raise ValueError("z has a forbidden local neighbor")
    for side in (XV, YV):
        if [sum(graph[u][v] for v in side) for u in side] != [1] * 12:
            raise ValueError("side relation is not a perfect matching")
    if [sum(graph[u][v] for v in YV) for u in XV] != [1] * 12:
        raise ValueError("X-to-Y relation is not a perfect matching")
    if [sum(graph[v][u] for u in XV) for v in YV] != [1] * 12:
        raise ValueError("Y-to-X relation is not a perfect matching")
    if component_partition(graph) != tuple(sorted(parts, reverse=True)):
        raise ValueError("wrong component partition")


def transported_principal_block(graph: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            (1 - int(row == column) - 2 * graph[row][column]) % FIELD
            for column in range(27)
        ]
        for row in range(27)
    ]


def row_reduce(rows: Iterable[Sequence[int]]) -> tuple[list[list[int]], list[int]]:
    matrix = [[value % FIELD for value in row] for row in rows]
    if not matrix:
        return [], []
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("ragged matrix")
    pivots: list[int] = []
    target = 0
    for column in range(width):
        source = next(
            (row for row in range(target, len(matrix)) if matrix[row][column]),
            None,
        )
        if source is None:
            continue
        matrix[target], matrix[source] = matrix[source], matrix[target]
        inverse = pow(matrix[target][column], -1, FIELD)
        matrix[target] = [(inverse * value) % FIELD for value in matrix[target]]
        for row in range(len(matrix)):
            coefficient = matrix[row][column]
            if row != target and coefficient:
                matrix[row] = [
                    (value - coefficient * pivot) % FIELD
                    for value, pivot in zip(matrix[row], matrix[target])
                ]
        pivots.append(column)
        target += 1
        if target == len(matrix):
            break
    return matrix, pivots


def matrix_rank(rows: Iterable[Sequence[int]]) -> int:
    return len(row_reduce(rows)[1])


def nullspace(matrix: Sequence[Sequence[int]]) -> list[tuple[int, ...]]:
    reduced, pivots = row_reduce(matrix)
    width = len(matrix[0])
    free = [column for column in range(width) if column not in pivots]
    answer: list[tuple[int, ...]] = []
    for free_column in free:
        vector = [0] * width
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = (-reduced[row][free_column]) % FIELD
        answer.append(tuple(vector))
    return answer


def inner_product(a: Sequence[int], b: Sequence[int]) -> int:
    return sum(x * y for x, y in zip(a, b)) % FIELD


def border_column(x_index: int, y_index: int) -> tuple[int, ...]:
    column = [1] * 27
    for vertex in (2, XV[x_index], YV[y_index]):
        column[vertex] = FIELD - 1
    return tuple(column)


def projected_signatures(
    kernel: Sequence[Sequence[int]],
) -> dict[tuple[int, int], tuple[int, ...]]:
    return {
        (x_index, y_index): tuple(
            inner_product(radical_vector, border_column(x_index, y_index))
            for radical_vector in kernel
        )
        for x_index in range(12)
        for y_index in range(12)
    }


def projective_representative(vector: Sequence[int]) -> tuple[int, ...]:
    first = next((value % FIELD for value in vector if value % FIELD), None)
    if first is None:
        raise ValueError("zero does not determine a projective line")
    scale = pow(first, -1, FIELD)
    return tuple((scale * value) % FIELD for value in vector)


def canonical_span(rows: Iterable[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    reduced, pivots = row_reduce(rows)
    return tuple(tuple(reduced[row]) for row in range(len(pivots)))


def belongs(vector: Sequence[int], rref_basis: Sequence[Sequence[int]]) -> bool:
    remainder = [value % FIELD for value in vector]
    for basis_vector in rref_basis:
        pivot = next(
            (index for index, value in enumerate(basis_vector) if value), None
        )
        if pivot is None:
            continue
        coefficient = remainder[pivot]
        if coefficient:
            remainder = [
                (value - coefficient * basis_value) % FIELD
                for value, basis_value in zip(remainder, basis_vector)
            ]
    return not any(remainder)


def exact_matching(edges: Iterable[tuple[int, int]]) -> tuple[int, list[tuple[int, int]]]:
    neighbors = {left: [] for left in range(12)}
    for left, right in sorted(set(edges)):
        if left not in range(12) or right not in range(12):
            raise ValueError("matching edge outside 12 by 12 universe")
        neighbors[left].append(right)
    right_owner: dict[int, int] = {}

    def augment(left: int, visited: set[int]) -> bool:
        for right in neighbors[left]:
            if right in visited:
                continue
            visited.add(right)
            if right not in right_owner or augment(right_owner[right], visited):
                right_owner[right] = left
                return True
        return False

    size = sum(augment(left, set()) for left in range(12))
    witness = sorted((left, right) for right, left in right_owner.items())
    return size, witness


def valid_permutation(edges: Iterable[tuple[int, int]]) -> bool:
    selected = list(edges)
    return (
        len(selected) == 12
        and len(set(selected)) == 12
        and {left for left, _ in selected} == set(range(12))
        and {right for _, right in selected} == set(range(12))
    )


def generated_subspaces(
    lines: Sequence[tuple[int, ...]], dimension: int
) -> tuple[int, list[tuple[tuple[int, ...], ...]]]:
    if dimension == 0:
        return 1, [tuple()]
    raw = 0
    spaces: set[tuple[tuple[int, ...], ...]] = set()
    for generators in itertools.combinations(lines, dimension):
        raw += 1
        span = canonical_span(generators)
        if len(span) == dimension:
            spaces.add(span)
    return raw, sorted(spaces)


def matching_census_for_dimension(
    signatures: dict[tuple[int, int], tuple[int, ...]],
    spaces: Sequence[tuple[tuple[int, ...], ...]],
) -> tuple[dict[str, object], dict[str, object] | None]:
    distribution: Counter[int] = Counter()
    positives = 0
    first: dict[str, object] | None = None
    for basis in spaces:
        allowed = [
            edge for edge, vector in signatures.items() if belongs(vector, basis)
        ]
        size, witness = exact_matching(allowed)
        distribution[size] += 1
        if size == 12:
            if not valid_permutation(witness):
                raise AssertionError("matching algorithm emitted a non-permutation")
            positives += 1
            if first is None:
                actual_rank = matrix_rank([signatures[edge] for edge in witness])
                first = {
                    "basis": [list(row) for row in basis],
                    "allowed_pattern_count": len(allowed),
                    "permutation": [list(edge) for edge in witness],
                    "selected_projection_rank": actual_rank,
                }
    return (
        {
            "subspaces": len(spaces),
            "matching_number_distribution": {
                str(size): distribution[size] for size in sorted(distribution)
            },
            "maximum_matching_number": max(distribution, default=0),
            "subspaces_supporting_a_permutation": positives,
        },
        first,
    )


def minimum_projection_rank(
    signatures: dict[tuple[int, int], tuple[int, ...]]
) -> dict[str, object]:
    nonzero_lines = sorted(
        {
            projective_representative(vector)
            for vector in signatures.values()
            if any(vector)
        }
    )
    dimensions: dict[str, object] = {}
    witness: dict[str, object] | None = None
    minimum: int | None = None
    for dimension in range(4):
        raw, spaces = generated_subspaces(nonzero_lines, dimension)
        census, candidate = matching_census_for_dimension(signatures, spaces)
        census["raw_generator_subsets"] = raw
        census["duplicate_or_dependent_generator_subsets_removed"] = raw - len(spaces)
        dimensions[str(dimension)] = census
        if candidate is not None:
            minimum = dimension
            witness = candidate
            break
    if minimum is None or witness is None:
        raise AssertionError("no permutation witness was found through dimension three")
    if witness["selected_projection_rank"] != minimum:
        raise AssertionError("winning subspace did not produce the claimed exact rank")
    return {
        "observed_nonzero_projective_lines": len(nonzero_lines),
        "dimensions_exhausted_through": minimum,
        "dimension_censuses": dimensions,
        "minimum_over_all_12_factorial_permutations": minimum,
        "canonical_witness": witness,
        "completeness_reason": (
            "If selected signatures span dimension d, their nonzero members "
            "generate an observed-line subspace of dimension d; all such "
            "subspaces below and at the first witness dimension were exhausted."
        ),
    }


def analyze_partition(parts: Sequence[int]) -> dict[str, object]:
    graph = local_graph(parts)
    block = transported_principal_block(graph)
    local_rank = matrix_rank(block)
    kernel = nullspace(block)
    signatures = projected_signatures(kernel)
    if local_rank + len(kernel) != 27:
        raise AssertionError("rank-nullity failure")
    if len(signatures) != 144:
        raise AssertionError("incomplete border-signature universe")
    projection = minimum_projection_rank(signatures)
    minimum = projection["minimum_over_all_12_factorial_permutations"]
    return {
        "partition": list(parts),
        "even_part_count": sum(part % 2 == 0 for part in parts),
        "local_rank_F7": local_rank,
        "kernel_dimension": len(kernel),
        "border_signature_count": len(signatures),
        "third_fibre_rule": "twelve columns indexed by a permutation X->Y",
        "projection_search": projection,
        "bordered_principal_rank_lower_bound": local_rank + 2 * minimum,
    }


def block_matrix(
    s: Sequence[Sequence[int]],
    u: Sequence[Sequence[int]],
    w: Sequence[Sequence[int]],
) -> list[list[int]]:
    n = len(s)
    m = len(w)
    if any(len(row) != n for row in s):
        raise ValueError("S is not square")
    if len(u) != n or any(len(row) != m for row in u):
        raise ValueError("U has the wrong shape")
    if any(len(row) != m for row in w):
        raise ValueError("W is not square")
    return [
        [*s[row], *u[row]] for row in range(n)
    ] + [
        [*[u[row][column] for row in range(n)], *w[column]]
        for column in range(m)
    ]


def border_lemma_terms(
    s: Sequence[Sequence[int]], u: Sequence[Sequence[int]]
) -> tuple[int, int]:
    kernel = nullspace(s)
    projected = [
        [inner_product(vector, [u[row][column] for row in range(len(u))])
         for column in range(len(u[0]))]
        for vector in kernel
    ]
    return matrix_rank(s), matrix_rank(projected)


def endpoint_rank_pair_count() -> int:
    return sum(
        (r3 + r7) % 2 == 0
        for r3 in range(12, 45)
        for r7 in range(25, 45)
    )


def compute() -> dict[str, object]:
    frozen = freeze_inputs()
    analyses = [analyze_partition(parts) for parts in PARTITIONS]
    result = {
        "format": "wave40-exact-coupling-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Universal theorem rank_F7(M)>=25 for any hypothetical "
            "srg(99,14,1,2)"
        ),
        "frozen_inputs": frozen,
        "premises": {
            "parameters": [99, 14, 1, 2],
            "transported_matrix": "N M N^T=J-I-2A over F_7",
            "rank_transfer": "rank_F7(N M N^T)=rank_F7(M)",
            "edge_local_normal_forms": "all eleven positive partitions of six",
        },
        "third_fibre": {
            "definition": "Z=N(z)-{x,y} for an edge xy with triangle mate z",
            "size": 12,
            "outside_local_block": True,
            "forced_border": (
                "lambda=1 and mu=2 force Z--X and Z--Y to be perfect "
                "matchings, hence its 12 border signatures are indexed by "
                "one permutation X->Y"
            ),
            "individual_signature_universe": 144,
        },
        "border_rank_lemma": {
            "statement": (
                "For symmetric S and arbitrary U,W, "
                "rank([[S,U],[U^T,W]]) >= rank(S)+2*rank(H^T U), "
                "where the columns of H are a basis of ker(S)."
            ),
            "proof": (
                "A congruence splits S into an invertible rank(S) block and "
                "its radical. Eliminating the border against the invertible "
                "block leaves [[0,Q],[Q^T,W']], Q=H^T U. Its kernel has "
                "dimension at most (rows(Q)-rank(Q))+(cols(Q)-rank(Q)), "
                "so its rank is at least 2*rank(Q)."
            ),
            "W_restrictions_used": "none",
        },
        "partition_results": {
            "+".join(map(str, entry["partition"])): entry for entry in analyses
        },
        "universal_deduction": {
            "minimum_bordered_principal_rank": min(
                entry["bordered_principal_rank_lower_bound"] for entry in analyses
            ),
            "all_partition_lower_bounds": sorted(
                {
                    entry["bordered_principal_rank_lower_bound"]
                    for entry in analyses
                }
            ),
            "theorem": "rank_F7(M)>=25",
        },
        "endpoint_arithmetic": {
            "inherited_ranges": "12<=r3<=44 and 25<=r7<=44",
            "parity": "r3+r7 is even",
            "remaining_rank_pairs": endpoint_rank_pair_count(),
            "if_r3_equals_12": "r7 is even and at least 26",
        },
        "status_wall": {
            "universal_rank_F7_M_lower_bound": 25,
            "endpoint_excluded": False,
            "general_upper_bound_improved_below_4158": False,
            "strongest_general_upper_bound": "n3<=4158",
            "conway_99_status": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
            "construction_produced": False,
        },
    }
    validate(result)
    return result


def validate(result: dict[str, object]) -> None:
    if result.get("claim_label") != "VERIFIED":
        raise ValueError("scoped theorem not verified")
    partitions = result["partition_results"]
    if len(partitions) != 11:
        raise ValueError("not all eleven partitions were checked")
    expected_keys = {"+".join(map(str, parts)) for parts in PARTITIONS}
    if set(partitions) != expected_keys:
        raise ValueError("partition coverage is malformed")
    for key, entry in partitions.items():
        even_parts = entry["even_part_count"]
        if entry["local_rank_F7"] != 25 - 2 * even_parts:
            raise ValueError(f"wrong local rank for {key}")
        if entry["kernel_dimension"] != 2 + 2 * even_parts:
            raise ValueError(f"wrong kernel dimension for {key}")
        if entry["border_signature_count"] != 144:
            raise ValueError(f"incomplete signatures for {key}")
        if (
            entry["projection_search"]["minimum_over_all_12_factorial_permutations"]
            != even_parts
        ):
            raise ValueError(f"wrong minimum projection rank for {key}")
        search = entry["projection_search"]
        if search["dimensions_exhausted_through"] != even_parts:
            raise ValueError(f"incomplete dimension search for {key}")
        expected_line_counts = {0: 0, 1: 6, 2: 28, 3: 66}
        if search["observed_nonzero_projective_lines"] != expected_line_counts[even_parts]:
            raise ValueError(f"wrong observed-line count for {key}")
        expected_space_counts = {
            0: (1,),
            1: (1, 6),
            2: (1, 28, 290),
            3: (1, 66, 1923, 25744),
        }
        for dimension, expected_count in enumerate(expected_space_counts[even_parts]):
            census = search["dimension_censuses"][str(dimension)]
            if census["subspaces"] != expected_count:
                raise ValueError(f"wrong dimension-{dimension} coverage for {key}")
            if sum(census["matching_number_distribution"].values()) != expected_count:
                raise ValueError(f"incomplete matching census for {key}, dimension {dimension}")
            if dimension < even_parts:
                if census["subspaces_supporting_a_permutation"] != 0:
                    raise ValueError(f"false lower-dimensional witness for {key}")
                if census["maximum_matching_number"] >= 12:
                    raise ValueError(f"false lower-dimensional perfect match for {key}")
            else:
                if census["subspaces_supporting_a_permutation"] <= 0:
                    raise ValueError(f"missing sharpness witness for {key}")
                if census["maximum_matching_number"] != 12:
                    raise ValueError(f"winning dimension lacks a perfect match for {key}")
        witness = entry["projection_search"]["canonical_witness"]
        if not valid_permutation(tuple(edge) for edge in witness["permutation"]):
            raise ValueError(f"non-bijective witness for {key}")
        if witness["selected_projection_rank"] != even_parts:
            raise ValueError(f"witness rank mismatch for {key}")
        if entry["bordered_principal_rank_lower_bound"] != 25:
            raise ValueError(f"wrong bordered rank lower bound for {key}")
    if result["universal_deduction"]["minimum_bordered_principal_rank"] != 25:
        raise ValueError("wrong universal minimum")
    if result["universal_deduction"]["all_partition_lower_bounds"] != [25]:
        raise ValueError("partition lower bounds do not all equal 25")
    if result["endpoint_arithmetic"]["remaining_rank_pairs"] != 330:
        raise ValueError("wrong endpoint rank-pair count")
    if result["endpoint_arithmetic"]["if_r3_equals_12"] != "r7 is even and at least 26":
        raise ValueError("wrong r3=12 consequence")
    wall = result["status_wall"]
    if wall["universal_rank_F7_M_lower_bound"] != 25:
        raise ValueError("wrong published rank floor")
    if wall["endpoint_excluded"]:
        raise ValueError("endpoint status inflation")
    if wall["general_upper_bound_improved_below_4158"]:
        raise ValueError("general-bound status inflation")
    if wall["strongest_general_upper_bound"] != "n3<=4158":
        raise ValueError("wrong general upper bound")
    if wall["conway_99_status"] != "UNKNOWN":
        raise ValueError("problem-status inflation")
    if wall["literature_novelty"] != "UNKNOWN":
        raise ValueError("novelty inflation")
    if wall["construction_produced"]:
        raise ValueError("construction status inflation")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    fresh = compute()
    if args.verify and args.write:
        raise SystemExit("--verify and --write are mutually exclusive")
    if args.write:
        args.write.write_text(
            json.dumps(fresh, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"WROTE: {args.write}")
    elif args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        validate(stored)
        if stored != fresh:
            raise SystemExit("stored result differs from clean-room replay")
        print(f"VERIFIED: {args.verify}")
    else:
        print(json.dumps(fresh, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
