#!/usr/bin/env python3
"""Independent Wave 41 verifier for the four all-odd edge types.

This file was designed and written before opening or executing the discovery
package in attempts/wave41-multiedge-rank-packing.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Iterator, Sequence


P = 7
ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
T = tuple(range(3))
X = tuple(range(3, 15))
Y = tuple(range(15, 27))
Z = tuple(range(27, 39))
ALL_ODD_TYPES = {
    "1^6": (1, 1, 1, 1, 1, 1),
    "1^3+3": (3, 1, 1, 1),
    "1+5": (5, 1),
    "3+3": (3, 3),
}
EVEN_PART_TYPES = (
    "6",
    "2+4",
    "1^2+4",
    "1+2+3",
    "2^3",
    "1^2+2^2",
    "1^4+2",
)
FROZEN_INPUTS = {
    "AGENTS.md": "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "CONJECTURE.md": "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "verification/2026-07-27-wave40-orchestrator.md": (
        "a136b971ba4e675a5edfe62780e7754b7c716ff1753507be0201eadf3042dfbf"
    ),
    "verification/wave40-exact-coupling-model/README.md": (
        "33201f7cac66df7c65f254d0c3b054cd17cfa67ae54b67cbc5032bee299b924e"
    ),
    "verification/wave40-exact-coupling-model/run-report.yaml": (
        "128bea1e5f7ff347f13e435888d62a6272ebe0968a5f8dc6a0eb2ba22fb99177"
    ),
    "verification/wave40-exact-coupling-model/independent_check.py": (
        "d87c7a5eb9377cc3095fff21eec7ff17d94445bef911e4adb092f2db6228bc6e"
    ),
    "verification/wave40-exact-coupling-model/independent-results.json": (
        "ff7916d0f5c74c47c8d7787c5cbcc84785cbccd3644d8d03d73e47b73908c0f5"
    ),
    "verification/wave40-edge-type-coupling/audit.md": (
        "3ec16bfdb7275ddfde95cf352660ec2440a029f07796f7397ba92d63859a1c79"
    ),
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_frozen_inputs() -> dict[str, str]:
    found = {name: digest(ROOT / name) for name in FROZEN_INPUTS}
    if found != FROZEN_INPUTS:
        changed = {
            name: {"expected": FROZEN_INPUTS[name], "found": found[name]}
            for name in FROZEN_INPUTS
            if found[name] != FROZEN_INPUTS[name]
        }
        raise ValueError(f"frozen inputs changed: {changed}")
    return found


def rref(
    rows: Iterable[Sequence[int]], *, modulus: int = P
) -> tuple[list[list[int]], list[int]]:
    a = [[entry % modulus for entry in row] for row in rows]
    if not a:
        return [], []
    width = len(a[0])
    if any(len(row) != width for row in a):
        raise ValueError("ragged matrix")
    pivots: list[int] = []
    next_row = 0
    for column in range(width):
        pivot_row = next(
            (row for row in range(next_row, len(a)) if a[row][column]), None
        )
        if pivot_row is None:
            continue
        a[next_row], a[pivot_row] = a[pivot_row], a[next_row]
        inv = pow(a[next_row][column], -1, modulus)
        a[next_row] = [(inv * entry) % modulus for entry in a[next_row]]
        for row in range(len(a)):
            if row == next_row:
                continue
            scale = a[row][column]
            if scale:
                a[row] = [
                    (entry - scale * lead) % modulus
                    for entry, lead in zip(a[row], a[next_row])
                ]
        pivots.append(column)
        next_row += 1
        if next_row == len(a):
            break
    return a, pivots


def rank(matrix: Iterable[Sequence[int]], *, modulus: int = P) -> int:
    return len(rref(matrix, modulus=modulus)[1])


def kernel(matrix: Sequence[Sequence[int]]) -> list[tuple[int, ...]]:
    reduced, pivots = rref(matrix)
    width = len(matrix[0])
    free_columns = [column for column in range(width) if column not in pivots]
    basis: list[tuple[int, ...]] = []
    for free in free_columns:
        vector = [0] * width
        vector[free] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free] % P
        basis.append(tuple(vector))
    return basis


def matmul(
    left: Sequence[Sequence[int]], right: Sequence[Sequence[int]]
) -> list[list[int]]:
    if not left or not right:
        return []
    if len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not conform")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right))) % P
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def solve_consistent(
    matrix: Sequence[Sequence[int]], rhs: Sequence[int]
) -> tuple[int, ...]:
    if len(matrix) != len(rhs):
        raise ValueError("right side has wrong length")
    augmented = [list(row) + [value] for row, value in zip(matrix, rhs)]
    reduced, pivots = rref(augmented)
    width = len(matrix[0])
    for row in reduced:
        if not any(row[:width]) and row[width]:
            raise ValueError("inconsistent singular system")
    solution = [0] * width
    for row_index, pivot in enumerate(pivots):
        if pivot == width:
            raise ValueError("inconsistent augmented pivot")
        solution[pivot] = reduced[row_index][width]
    if [
        sum(matrix[i][j] * solution[j] for j in range(width)) % P
        for i in range(len(matrix))
    ] != [value % P for value in rhs]:
        raise AssertionError("linear solver returned a false solution")
    return tuple(solution)


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(a * b for a, b in zip(left, right)) % P


def add_edge(graph: list[list[int]], u: int, v: int) -> None:
    if u == v or graph[u][v] or graph[v][u]:
        raise ValueError("edge is a loop or duplicate")
    graph[u][v] = graph[v][u] = 1


def standard_matching() -> tuple[tuple[int, int], ...]:
    return tuple((i, i + 1) for i in range(0, 12, 2))


def type_matching(parts: Sequence[int]) -> tuple[tuple[int, int], ...]:
    if sum(parts) != 6 or any(part <= 0 for part in parts):
        raise ValueError("parts must be a positive partition of six")
    edges: list[tuple[int, int]] = []
    first = 0
    for part in parts:
        for i in range(part):
            left = first + 2 * i + 1
            right = first + 2 * ((i + 1) % part)
            edges.append(tuple(sorted((left, right))))
        first += 2 * part
    result = tuple(sorted(edges))
    audit_matching(result)
    return result


def audit_matching(edges: Sequence[Sequence[int]]) -> None:
    flat = [vertex for edge in edges for vertex in edge]
    if len(edges) != 6 or any(len(edge) != 2 for edge in edges):
        raise ValueError("not six pairs")
    if any(a == b or a not in range(12) or b not in range(12) for a, b in edges):
        raise ValueError("invalid matching edge")
    if sorted(flat) != list(range(12)):
        raise ValueError("pairs do not partition twelve labels")


def all_matchings(vertices: tuple[int, ...] = tuple(range(12))) -> Iterator[
    tuple[tuple[int, int], ...]
]:
    if not vertices:
        yield tuple()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        remaining = vertices[1:index] + vertices[index + 1 :]
        for rest in all_matchings(remaining):
            yield ((first, second),) + rest


def matching_type(parts: Sequence[int]) -> tuple[int, ...]:
    """Return component sizes divided by four for X/Y matching union."""

    mx = standard_matching()
    my = type_matching(parts)
    adjacency = {i: [] for i in range(24)}
    for a, b in mx:
        adjacency[a].append(b)
        adjacency[b].append(a)
    for i in range(12):
        adjacency[i].append(12 + i)
        adjacency[12 + i].append(i)
    for a, b in my:
        adjacency[12 + a].append(12 + b)
        adjacency[12 + b].append(12 + a)
    unseen = set(range(24))
    answer: list[int] = []
    while unseen:
        start = min(unseen)
        stack = [start]
        component: set[int] = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(adjacency[vertex])
        unseen.difference_update(component)
        if len(component) % 4:
            raise AssertionError("three-matching component is not a multiple of four")
        answer.append(len(component) // 4)
    return tuple(sorted(answer, reverse=True))


def base_graph(parts: Sequence[int]) -> list[list[int]]:
    graph = [[0] * 39 for _ in range(39)]
    for u, v in itertools.combinations(T, 2):
        add_edge(graph, u, v)
    for root, fibre in zip(T, (X, Y, Z)):
        for vertex in fibre:
            add_edge(graph, root, vertex)
    for a, b in standard_matching():
        add_edge(graph, X[a], X[b])
    for a, b in type_matching(parts):
        add_edge(graph, Y[a], Y[b])
    for i in range(12):
        add_edge(graph, X[i], Y[i])
        add_edge(graph, X[i], Z[i])
    return graph


def complete_graph(
    parts: Sequence[int],
    yz_permutation: Sequence[int],
    z_matching: Sequence[Sequence[int]],
) -> list[list[int]]:
    if sorted(yz_permutation) != list(range(12)):
        raise ValueError("Y-Z relation is not a permutation")
    audit_matching(z_matching)
    graph = base_graph(parts)
    for zi, yi in enumerate(yz_permutation):
        add_edge(graph, Z[zi], Y[yi])
    for a, b in z_matching:
        add_edge(graph, Z[a], Z[b])
    audit_full_graph(graph)
    return graph


def audit_full_graph(graph: Sequence[Sequence[int]]) -> None:
    if len(graph) != 39 or any(len(row) != 39 for row in graph):
        raise ValueError("graph is not 39 by 39")
    if any(graph[i][i] for i in range(39)):
        raise ValueError("graph has a loop")
    if any(graph[i][j] != graph[j][i] for i in range(39) for j in range(39)):
        raise ValueError("graph is not symmetric")
    expected = [14, 14, 14] + [4] * 36
    if [sum(row) for row in graph] != expected:
        raise ValueError("wrong induced degrees")
    for fibre in (X, Y, Z):
        if [sum(graph[u][v] for v in fibre) for u in fibre] != [1] * 12:
            raise ValueError("within-fibre relation is not a perfect matching")
    for left, right in ((X, Y), (X, Z), (Y, Z)):
        if [sum(graph[u][v] for v in right) for u in left] != [1] * 12:
            raise ValueError("cross-fibre relation is not a perfect matching")
        if [sum(graph[v][u] for u in left) for v in right] != [1] * 12:
            raise ValueError("reverse cross-fibre relation is not a perfect matching")


def transported_block(graph: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            (1 - int(row == column) - 2 * graph[row][column]) % P
            for column in range(len(graph))
        ]
        for row in range(len(graph))
    ]


def local_s(parts: Sequence[int]) -> list[list[int]]:
    graph = base_graph(parts)
    return transported_block([row[:27] for row in graph[:27]])


def border_column(x_index: int, y_index: int) -> tuple[int, ...]:
    column = [1] * 27
    for vertex in (2, X[x_index], Y[y_index]):
        column[vertex] = P - 1
    return tuple(column)


def border_matrix(permutation: Sequence[int]) -> list[list[int]]:
    columns = [border_column(index, permutation[index]) for index in range(12)]
    return transpose(columns)


def zero_signature_edges(
    local_kernel: Sequence[Sequence[int]],
) -> tuple[tuple[int, int], ...]:
    return tuple(
        (x_index, y_index)
        for x_index in range(12)
        for y_index in range(12)
        if all(dot(vector, border_column(x_index, y_index)) == 0 for vector in local_kernel)
    )


def allowed_permutations(
    edges: Sequence[tuple[int, int]],
) -> Iterator[tuple[int, ...]]:
    neighborhoods = {
        left: tuple(sorted(right for a, right in edges if a == left))
        for left in range(12)
    }
    if any(not neighbors for neighbors in neighborhoods.values()):
        return

    def search(
        remaining_left: tuple[int, ...],
        used_right: frozenset[int],
        selected: dict[int, int],
    ) -> Iterator[tuple[int, ...]]:
        if not remaining_left:
            yield tuple(selected[i] for i in range(12))
            return
        left = min(
            remaining_left,
            key=lambda item: (
                sum(right not in used_right for right in neighborhoods[item]),
                item,
            ),
        )
        next_left = tuple(item for item in remaining_left if item != left)
        for right in neighborhoods[left]:
            if right in used_right:
                continue
            selected[left] = right
            yield from search(next_left, used_right | {right}, selected)
            del selected[left]

    yield from search(tuple(range(12)), frozenset(), {})


def maximum_bipartite_matching(
    edges: Sequence[tuple[int, int]],
) -> tuple[int, tuple[tuple[int, int], ...], dict[str, list[int]]]:
    """Return a maximum matching and a same-size Konig vertex-cover certificate."""

    neighborhoods = {
        left: tuple(sorted(right for a, right in set(edges) if a == left))
        for left in range(12)
    }
    right_owner: dict[int, int] = {}

    def augment(left: int, seen: set[int]) -> bool:
        for right in neighborhoods[left]:
            if right in seen:
                continue
            seen.add(right)
            if right not in right_owner or augment(right_owner[right], seen):
                right_owner[right] = left
                return True
        return False

    for left in range(12):
        augment(left, set())
    left_owner = {left: right for right, left in right_owner.items()}
    visited_left = {left for left in range(12) if left not in left_owner}
    visited_right: set[int] = set()
    frontier = list(sorted(visited_left))
    while frontier:
        left = frontier.pop()
        for right in neighborhoods[left]:
            if left_owner.get(left) == right or right in visited_right:
                continue
            visited_right.add(right)
            owner = right_owner.get(right)
            if owner is not None and owner not in visited_left:
                visited_left.add(owner)
                frontier.append(owner)
    cover_left = sorted(set(range(12)) - visited_left)
    cover_right = sorted(visited_right)
    witness = tuple(sorted((left, right) for right, left in right_owner.items()))
    if len(witness) != len(cover_left) + len(cover_right):
        raise AssertionError("matching and vertex-cover certificate sizes differ")
    if any(
        left not in cover_left and right not in cover_right for left, right in edges
    ):
        raise AssertionError("reported Konig set is not a vertex cover")
    return (
        len(witness),
        witness,
        {"left_vertices": cover_left, "right_vertices": cover_right},
    )


def schur_target(
    s: Sequence[Sequence[int]], u: Sequence[Sequence[int]]
) -> list[list[int]]:
    columns = transpose(u)
    solutions = [solve_consistent(s, column) for column in columns]
    target = [
        [dot(columns[i], solutions[j]) for j in range(12)] for i in range(12)
    ]
    if target != transpose(target):
        raise AssertionError("singular Schur target is not symmetric")
    return target


def z_block(z_matching: Sequence[Sequence[int]]) -> list[list[int]]:
    audit_matching(z_matching)
    mates = {a: b for a, b in z_matching} | {b: a for a, b in z_matching}
    return [
        [
            0 if i == j else (P - 1 if mates[i] == j else 1)
            for j in range(12)
        ]
        for i in range(12)
    ]


def residual(
    s: Sequence[Sequence[int]],
    u: Sequence[Sequence[int]],
    z_matching: Sequence[Sequence[int]],
) -> list[list[int]]:
    target = schur_target(s, u)
    w = z_block(z_matching)
    return [
        [(w[i][j] - target[i][j]) % P for j in range(12)]
        for i in range(12)
    ]


def target_matching(target: Sequence[Sequence[int]]) -> tuple[tuple[int, int], ...] | None:
    """Decode target as a legal W=J-I-2A_matching block, if possible."""

    if len(target) != 12 or any(len(row) != 12 for row in target):
        return None
    if target != transpose(target):
        return None
    if any(target[i][i] % P for i in range(12)):
        return None
    edges: list[tuple[int, int]] = []
    for i in range(12):
        negative = []
        for j in range(12):
            expected_values = {0} if i == j else {1, P - 1}
            if target[i][j] % P not in expected_values:
                return None
            if i != j and target[i][j] % P == P - 1:
                negative.append(j)
        if len(negative) != 1:
            return None
        if i < negative[0]:
            edges.append((i, negative[0]))
    try:
        audit_matching(edges)
    except ValueError:
        return None
    return tuple(edges)


def compact_kernel_vectors() -> list[tuple[int, ...]]:
    """Three fibre-constant vectors derived from the six-variable quotient."""

    vectors: list[tuple[int, ...]] = []
    for chosen in range(3):
        a = [int(i == chosen) for i in range(3)]
        a_sum = sum(a) % P
        b = [(2 * ((-a_sum) - value)) % P for value in a]
        vector = a + [b[0]] * 12 + [b[1]] * 12 + [b[2]] * 12
        vectors.append(tuple(vector))
    if rank(vectors) != 3:
        raise AssertionError("compact quotient kernel lost independence")
    return vectors


def core_laplacian(graph: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [
            ((3 if i == j else 0) - graph[3 + i][3 + j]) % P
            for j in range(36)
        ]
        for i in range(36)
    ]


def full_rank_checks(graph: Sequence[Sequence[int]]) -> dict[str, int]:
    block = transported_block(graph)
    full_rank = rank(block)
    laplacian_rank = rank(core_laplacian(graph))
    if full_rank != laplacian_rank + 1:
        raise AssertionError("rank(K39)=1+rank(3I-A_core) failed")
    for vector in compact_kernel_vectors():
        if any(dot(row, vector) for row in block):
            raise AssertionError("universal compact vector left the K39 kernel")
    return {
        "rank_F7_K39": full_rank,
        "rank_F7_3I_minus_A_core": laplacian_rank,
        "K39_nullity": 39 - full_rank,
    }


def analyze_type(label: str, parts: Sequence[int]) -> dict[str, object]:
    if any(part % 2 == 0 for part in parts):
        raise ValueError("Wave 41 scoped analyzer accepts only all-odd types")
    if matching_type(parts) != tuple(sorted(parts, reverse=True)):
        raise AssertionError("canonical normal form has the wrong component type")
    s = local_s(parts)
    s_rank = rank(s)
    s_kernel = kernel(s)
    if (s_rank, len(s_kernel)) != (25, 2):
        raise AssertionError("all-odd 27-block did not have rank 25 and nullity 2")
    zero_edges = zero_signature_edges(s_kernel)
    if len(zero_edges) != 144:
        raise AssertionError("an all-odd border column left im(S)")

    diagonal_values: Counter[int] = Counter()
    diagonal_zero_edges: list[tuple[int, int]] = []
    for x_index in range(12):
        for y_index in range(12):
            column = border_column(x_index, y_index)
            solution = solve_consistent(s, column)
            value = dot(column, solution)
            diagonal_values[value] += 1
            if value == 0:
                diagonal_zero_edges.append((x_index, y_index))
    matching_number, matching_witness, vertex_cover = maximum_bipartite_matching(
        diagonal_zero_edges
    )
    equality_candidates = (
        list(allowed_permutations(diagonal_zero_edges))
        if matching_number == 12
        else []
    )
    if len(equality_candidates) != len(set(equality_candidates)):
        raise AssertionError("rank-25 candidate enumeration has duplicates")

    decoded_targets: list[tuple[tuple[int, int], ...]] = []
    candidate_records: list[dict[str, object]] = []
    for permutation in equality_candidates:
        target = schur_target(s, border_matrix(permutation))
        decoded = target_matching(target)
        if decoded is not None:
            decoded_targets.append(decoded)
        candidate_records.append(
            {
                "permutation": list(permutation),
                "schur_target": target,
                "target_values": sorted(set(itertools.chain.from_iterable(target))),
                "target_decodes_as_internal_perfect_matching": decoded is not None,
            }
        )
    if decoded_targets:
        raise AssertionError(f"rank-25 completion found for {label}")

    all_z_matchings = tuple(all_matchings())
    if len(all_z_matchings) != 10_395 or len(set(all_z_matchings)) != 10_395:
        raise AssertionError("labelled perfect-matching enumeration is incomplete")

    # Exhaust all Z matchings for one deterministic completion as a dense
    # arithmetic control.  The rank-25 proof above does not depend on this
    # sample: it exhausted the necessary diagonal matching condition for every
    # one of the 12! possible Y-Z permutations.
    sample_permutation = tuple(range(12))
    sample_u = border_matrix(sample_permutation)
    sample_target = schur_target(s, sample_u)
    observed_ranks: Counter[int] = Counter()
    direct_crosschecks: list[dict[str, object]] = []
    for matching_index, matching in enumerate(all_z_matchings):
        w = z_block(matching)
        sample_residual = [
            [(w[i][j] - sample_target[i][j]) % P for j in range(12)]
            for i in range(12)
        ]
        schur_rank = rank(sample_residual)
        direct = s_rank + schur_rank
        observed_ranks[direct] += 1
        if matching_index in (0, 1, 10_394):
            graph = complete_graph(parts, sample_permutation, matching)
            direct_dense = rank(transported_block(graph))
            if direct_dense != direct:
                raise AssertionError("exact singular Schur rank identity failed")
            direct_crosschecks.append(
                {
                    "z_matching_index": matching_index,
                    "z_matching": [list(edge) for edge in matching],
                    "residual_rank": schur_rank,
                    **full_rank_checks(graph),
                }
            )
    if min(observed_ranks) < 26:
        raise AssertionError("sample found a rank below the proved floor")

    return {
        "partition": list(parts),
        "canonical_type_check": list(matching_type(parts)),
        "local_27_rank_F7": s_rank,
        "local_27_nullity": len(s_kernel),
        "all_144_border_columns_in_image_of_S": True,
        "schur_diagonal_value_distribution": {
            str(value): diagonal_values[value] for value in sorted(diagonal_values)
        },
        "zero_diagonal_bipartite_edges": len(diagonal_zero_edges),
        "zero_diagonal_row_degrees": [
            sum(left == row for left, _ in diagonal_zero_edges) for row in range(12)
        ],
        "zero_diagonal_matching_number": matching_number,
        "maximum_matching_witness": [list(edge) for edge in matching_witness],
        "minimum_vertex_cover_certificate": vertex_cover,
        "rank_25_candidate_permutations": len(equality_candidates),
        "enumeration_completeness": {
            "permutation_reduction": (
                "Rank 25 forces every diagonal entry of W-U^T X to vanish. "
                "Because diag(W)=0, every selected (x,y) must lie in the full "
                "144-edge Schur-quadratic zero graph."
            ),
            "permutation_method": (
                "Exact augmenting-path maximum matching plus a same-size "
                "Konig vertex-cover certificate; enumerate all perfect "
                "matchings only when the matching number is twelve."
            ),
            "internal_Z_matching_method": (
                "recursive least-unused-vertex enumeration of every labelled "
                "perfect matching"
            ),
            "labelled_internal_Z_matchings": len(all_z_matchings),
            "expected_labelled_internal_Z_matchings": 10_395,
        },
        "rank_25_schur_obstruction": {
            "diagonal_condition_has_perfect_matching": matching_number == 12,
            "perfect_diagonal_candidates_checked": len(equality_candidates),
            "candidate_targets_decoding_as_legal_Z_matchings": 0,
            "conclusion": (
                "No legal Y-Z permutation and Z internal matching can make "
                "the exact Schur residual vanish."
            ),
        },
        "rank_25_candidate_records": candidate_records,
        "identity_permutation_full_Z_rank_distribution": {
            str(value): observed_ranks[value] for value in sorted(observed_ranks)
        },
        "sample_exact_identity_crosschecks": direct_crosschecks,
        "K39_identity_crosschecks": len(direct_crosschecks),
        "scoped_rank_F7_K39_lower_bound": 26,
    }


def rank_transport_record() -> dict[str, object]:
    if (3 * pow(3, -1, P)) % P != 1:
        raise AssertionError("three is not invertible in F7")
    return {
        "field": "F_7",
        "inverse_of_3": pow(3, -1, P),
        "frozen_identities": [
            "N M N^T=J-I-2A (mod 7)",
            "N^T N M=3M (mod 7)",
        ],
        "proof": (
            "If v=Mw and Nv=0, then 0=N^T Nv=N^T N M w=3v. "
            "Since 3^-1=5 in F_7, v=0. Thus N is injective on im(M), "
            "and symmetry gives rank(NMN^T)=rank(M). A principal K39 "
            "block rank is therefore a lower bound for rank(M)."
        ),
        "conclusion": "rank_F7(N M N^T)=rank_F7(M)",
    }


def compute() -> dict[str, object]:
    frozen = check_frozen_inputs()
    matching_count = sum(1 for _ in all_matchings())
    if matching_count != 10_395:
        raise AssertionError("perfect-matching count is not 11 double factorial")
    analyses = {
        label: analyze_type(label, parts) for label, parts in ALL_ODD_TYPES.items()
    }
    result = {
        "format": "wave41-multiedge-rank-packing-independent-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED",
        "scope": (
            "For each all-odd edge type 1^6, 1^3+3, 1+5, and 3+3, "
            "every admissible third-fibre completion has rank_F7(K39)>=26."
        ),
        "frozen_inputs": frozen,
        "normalization": {
            "fixed_without_automorphism_assumption": (
                "Relabel X to put its internal matching in standard form; "
                "pull Y labels through the X-Y matching; relabel Z through "
                "the X-Z matching."
            ),
            "free_data": (
                "canonical Y internal matching for the chosen edge type, "
                "an arbitrary Y-Z permutation, and an arbitrary Z internal "
                "perfect matching"
            ),
            "labelled_perfect_matchings_on_12": matching_count,
        },
        "exact_identities": {
            "transported_block": "K39=(J-I-2A)[T union N(T)] over F_7",
            "core_laplacian": "rank_F7(K39)=1+rank_F7(3I-A_core)",
            "singular_schur": (
                "When H^T U=0, rank(K39)=rank(S)+"
                "rank(W-U^T X), where S X=U."
            ),
        },
        "rank_transport": rank_transport_record(),
        "universal_compact_kernel": {
            "dimension": 3,
            "derivation": (
                "For constants a_i on the triangle and b_i on the fibres, "
                "the K39 equations reduce to A=-B and "
                "b_i=2(B-a_i), leaving the three a_i free."
            ),
            "basis": [list(vector) for vector in compact_kernel_vectors()],
        },
        "type_results": analyses,
        "deduction": {
            "all_four_scoped_K39_lower_bounds": sorted(
                {
                    entry["scoped_rank_F7_K39_lower_bound"]
                    for entry in analyses.values()
                }
            ),
            "scoped_conclusion": (
                "An occurrence of any of the four all-odd edge types forces "
                "rank_F7(M)>=26 by principal-block monotonicity and exact "
                "rank transport."
            ),
            "universal_rank_F7_M_lower_bound": 25,
            "universal_floor_raised": False,
        },
        "status_wall": {
            "seven_even_part_types": {label: "UNKNOWN" for label in EVEN_PART_TYPES},
            "all_hypothetical_graphs_forced_to_contain_an_all_odd_type": False,
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
    if result.get("claim_label") != "VERIFIED_SCOPED":
        raise ValueError("status inflation or malformed verifier verdict")
    types = result.get("type_results")
    if not isinstance(types, dict) or set(types) != set(ALL_ODD_TYPES):
        raise ValueError("all-odd type coverage is incomplete")
    for label, record in types.items():
        if record["local_27_rank_F7"] != 25:
            raise ValueError(f"wrong local rank for {label}")
        if record["local_27_nullity"] != 2:
            raise ValueError(f"wrong local nullity for {label}")
        if not record["all_144_border_columns_in_image_of_S"]:
            raise ValueError(f"border equality changed for {label}")
        if record["rank_25_schur_obstruction"][
            "candidate_targets_decoding_as_legal_Z_matchings"
        ] != 0:
            raise ValueError(f"rank-25 completion retained for {label}")
        if record["scoped_rank_F7_K39_lower_bound"] != 26:
            raise ValueError(f"wrong scoped rank floor for {label}")
        if record["zero_diagonal_matching_number"] < 12:
            if record["rank_25_candidate_permutations"] != 0:
                raise ValueError(f"spurious rank-25 candidates for {label}")
        elif record["rank_25_candidate_permutations"] <= 0:
            raise ValueError(f"perfect diagonal candidates omitted for {label}")
    deduction = result["deduction"]
    if deduction["all_four_scoped_K39_lower_bounds"] != [26]:
        raise ValueError("scoped rank floors changed")
    if deduction["universal_rank_F7_M_lower_bound"] != 25:
        raise ValueError("universal rank floor was inflated")
    if deduction["universal_floor_raised"]:
        raise ValueError("universal floor falsely marked as raised")
    status = result["status_wall"]
    if set(status["seven_even_part_types"]) != set(EVEN_PART_TYPES):
        raise ValueError("seven-type unresolved wall is incomplete")
    if set(status["seven_even_part_types"].values()) != {"UNKNOWN"}:
        raise ValueError("an even-part type was silently promoted")
    if status["endpoint_excluded"] or status["construction_produced"]:
        raise ValueError("out-of-scope conclusion was promoted")
    if status["strongest_general_upper_bound"] != "n3<=4158":
        raise ValueError("general upper bound was inflated")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()
    computed = compute()
    if arguments.verify is not None:
        stored = json.loads(arguments.verify.read_text(encoding="utf-8"))
        validate(stored)
        if stored != computed:
            raise SystemExit("stored independent result differs from recomputation")
    if arguments.write is not None:
        arguments.write.write_text(
            json.dumps(computed, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    elif arguments.verify is None:
        print(json.dumps(computed, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
