#!/usr/bin/env python3
"""Independent exact checks for the Wave 32 indecomposable lane.

This module is standard-library only and imports no discovery code.  It
checks necessary algebraic and combinatorial consequences, plus explicit
premise-dropping controls.  It does not construct or exclude an endpoint
lattice, frame, projector, or graph.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DETERMINANTS = (9, 21, 49, 81, 189, 441, 729, 1029)
ENTRY_ALPHABET = (-2, -1, 0, 1)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)
        .encode("utf-8")
        + b"\n"
    )


def payload_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_input_freeze() -> dict[str, str]:
    result: dict[str, str] = {}
    for number, raw in enumerate(
        (HERE / "input-freeze.sha256").read_text(encoding="utf-8").splitlines(),
        1,
    ):
        if not raw:
            continue
        digest, separator, relative = raw.partition("  ")
        if (
            not separator
            or len(digest) != 64
            or any(ch not in "0123456789abcdef" for ch in digest)
            or not relative
        ):
            raise AssertionError(f"malformed freeze line {number}: {raw!r}")
        if relative in result:
            raise AssertionError(f"duplicate frozen path: {relative}")
        result[relative] = digest
    return result


def verify_input_freeze() -> dict[str, str]:
    expected = read_input_freeze()
    observed = {
        relative: file_sha256(ROOT / relative)
        for relative in expected
    }
    if observed != expected:
        raise AssertionError(
            f"frozen input drift: expected={expected}, observed={observed}"
        )
    return observed


def verify_sha256_manifest(relative_manifest: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    manifest = ROOT / relative_manifest
    for number, raw in enumerate(
        manifest.read_text(encoding="utf-8").splitlines(),
        1,
    ):
        if not raw:
            continue
        digest, separator, relative = raw.partition(" ")
        relative = relative.lstrip(" *")
        if (
            not separator
            or len(digest) != 64
            or any(ch not in "0123456789abcdef" for ch in digest)
            or not relative
        ):
            raise AssertionError(
                f"malformed {relative_manifest} line {number}: {raw!r}"
            )
        if relative in entries:
            raise AssertionError(f"duplicate manifest path: {relative}")
        observed = file_sha256(ROOT / relative)
        if observed != digest:
            raise AssertionError(
                f"manifest drift for {relative}: {observed} != {digest}"
            )
        entries[relative] = digest
    return entries


def candidate_manifest_validation() -> dict[str, object]:
    artifacts = verify_sha256_manifest(
        "attempts/wave32-indecomposable/artifact-manifest.sha256"
    )
    inputs = verify_sha256_manifest(
        "attempts/wave32-indecomposable/input-freeze.sha256"
    )
    if len(artifacts) != 7 or len(inputs) != 5:
        raise AssertionError("candidate manifest entry count drifted")
    return {
        "artifact_manifest_entries": len(artifacts),
        "input_freeze_entries": len(inputs),
        "all_hashes_match": True,
    }


def determinant(matrix: list[list[int]]) -> int:
    """Exact Bareiss determinant."""
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("determinant requires a square matrix")
    if n == 0:
        return 1
    work = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for column in range(n - 1):
        pivot = next(
            (row for row in range(column, n) if work[row][column]),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        for row in range(column + 1, n):
            for col in range(column + 1, n):
                numerator = (
                    work[row][col] * pivot_value
                    - work[row][column] * work[column][col]
                )
                if numerator % previous:
                    raise AssertionError("Bareiss division was not exact")
                work[row][col] = numerator // previous
        previous = pivot_value
    return sign * work[-1][-1]


def principal_minor_psd(matrix: list[list[int]]) -> bool:
    n = len(matrix)
    for size in range(1, n + 1):
        for indices in itertools.combinations(range(n), size):
            minor = [
                [matrix[row][column] for column in indices]
                for row in indices
            ]
            if determinant(minor) < 0:
                return False
    return True


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    if not matrix:
        return 0
    work = [[value % prime for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0])
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        work[rank] = [(inverse * value) % prime for value in work[rank]]
        for row in range(rows):
            if row == rank:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    (left - factor * right) % prime
                    for left, right in zip(work[row], work[rank])
                ]
        rank += 1
        if rank == rows:
            break
    return rank


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: list[list[int]],
    right: list[list[int]],
    modulus: int | None = None,
) -> list[list[int]]:
    right_t = transpose(right)
    product = [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]
    if modulus is not None:
        return [[value % modulus for value in row] for row in product]
    return product


def gram(rows: list[list[int]], form: list[list[int]]) -> list[list[int]]:
    return matmul(matmul(rows, form), transpose(rows))


def graph_components(matrix: list[list[int]]) -> list[list[int]]:
    unseen = set(range(len(matrix)))
    components = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        component = {start}
        stack = [start]
        while stack:
            vertex = stack.pop()
            for neighbor, value in enumerate(matrix[vertex]):
                if neighbor in unseen and value:
                    unseen.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    return components


def maximal_minor_gcd(matrix: list[list[int]]) -> int:
    rows = len(matrix)
    columns = len(matrix[0])
    values = []
    for indices in itertools.combinations(range(rows), columns):
        minor = [matrix[index][:] for index in indices]
        values.append(abs(determinant(minor)))
    return math.gcd(*values)


def primitive_row_generation() -> dict[str, object]:
    primitive = [[1, 0], [0, 1], [1, 1]]
    nonprimitive = [[2, 0], [0, 1], [2, 1]]
    primitive_index = maximal_minor_gcd(primitive)
    nonprimitive_index = maximal_minor_gcd(nonprimitive)
    if primitive_index != 1 or nonprimitive_index != 2:
        raise AssertionError("maximal-minor index control drifted")
    return {
        "criterion": (
            "for full-column-rank integral X, the row lattice im(X^T) "
            "has index equal to the gcd of the maximal minors"
        ),
        "primitive_index": primitive_index,
        "primitive_rows_generate": True,
        "nonprimitive_index": nonprimitive_index,
        "nonprimitive_missing_vector": [1, 0],
        "consequence": (
            "primitive endpoint X implies its 231 rows generate Z^44"
        ),
    }


def connectivity_and_decomposition() -> dict[str, object]:
    decomposable_form = [[4, 0], [0, 4]]
    decomposable_rows = [[1, 0], [0, 1]]
    decomposable_gram = gram(decomposable_rows, decomposable_form)

    indecomposable_form = [[4, 1], [1, 4]]
    indecomposable_rows = [[1, 0], [0, 1]]
    indecomposable_gram = gram(indecomposable_rows, indecomposable_form)

    disconnected = graph_components(decomposable_gram)
    connected = graph_components(indecomposable_gram)
    if disconnected != [[0], [1]] or connected != [[0, 1]]:
        raise AssertionError("connectivity controls drifted")
    if determinant(indecomposable_form) != 15:
        raise AssertionError("rank-two indecomposable determinant drifted")

    # If the minimum-four floor is deleted, a norm-four row may straddle
    # two orthogonal root components.
    dropped_min_form = [[2, 0], [0, 2]]
    mixed_row = [[1, 1]]
    mixed_norm = gram(mixed_row, dropped_min_form)[0][0]
    if mixed_norm != 4:
        raise AssertionError("dropped-minimum mixed-row control drifted")

    return {
        "row_graph_definition": "i~j iff i!=j and x_i^T S x_j is nonzero",
        "forward_direction": (
            "disconnected row graph plus row generation gives an integral "
            "orthogonal direct sum"
        ),
        "reverse_direction": (
            "under min(S)>=4, every norm-four row in an integral split "
            "has exactly one nonzero component"
        ),
        "decomposable_components": disconnected,
        "indecomposable_components": connected,
        "indecomposable_rank_two_determinant": 15,
        "dropped_minimum_mixed_row_norm": mixed_norm,
        "actual_incidence_consequence": (
            "Wave31 excludes a rootless integral split; therefore an "
            "actual rootless endpoint has connected row graph"
        ),
    }


def switched_values(
    edges: tuple[int, int, int],
    signs: tuple[int, int, int],
) -> tuple[int, int, int]:
    a, b, c = edges
    s0, s1, s2 = signs
    return (s0 * s1 * a, s0 * s2 * b, s1 * s2 * c)


def norm_of_signed_sum(
    edges: tuple[int, int, int],
    signs: tuple[int, int, int],
) -> int:
    a, b, c = edges
    s0, s1, s2 = signs
    return 12 + 2 * (
        s0 * s1 * a
        + s0 * s2 * b
        + s1 * s2 * c
    )


def motif_census() -> dict[str, object]:
    root_forcing = []
    for edges in itertools.product(ENTRY_ALPHABET, repeat=3):
        matrix = [
            [4, edges[0], edges[1]],
            [edges[0], 4, edges[2]],
            [edges[1], edges[2], 4],
        ]
        if not principal_minor_psd(matrix):
            continue
        witnesses = [
            signs
            for signs in itertools.product((-1, 1), repeat=3)
            if norm_of_signed_sum(edges, signs) == 2
        ]
        if witnesses:
            root_forcing.append((edges, witnesses))

    raw_edges = sorted(edges for edges, _ in root_forcing)
    expected = sorted([
        (-2, -2, -1),
        (-2, -1, -2),
        (-1, -2, -2),
    ])
    if raw_edges != expected:
        raise AssertionError(f"root-motif census drifted: {raw_edges}")

    canonical = [[4, -2, -2], [-2, 4, -1], [-2, -1, 4]]
    sign_mutation = [[4, -2, -2], [-2, 4, 1], [-2, 1, 4]]
    if determinant(canonical) != 20:
        raise AssertionError("canonical motif determinant drifted")
    if sum(sum(row) for row in canonical) != 2:
        raise AssertionError("canonical motif does not contain a norm-two sum")
    mutated_edges = (-2, -2, 1)
    mutated_norms = sorted({
        norm_of_signed_sum(mutated_edges, signs)
        for signs in itertools.product((-1, 1), repeat=3)
    })
    if 2 in mutated_norms:
        raise AssertionError("positive-sign hostile mutation still forces a root")

    switching_classes = {
        tuple(sorted(abs(value) for value in edges))
        for edges, _ in root_forcing
    }
    if switching_classes != {(1, 2, 2)}:
        raise AssertionError("motif switching class drifted")

    return {
        "raw_ordered_edge_triples": [list(row) for row in raw_edges],
        "raw_count": len(raw_edges),
        "switching_class_count": len(switching_classes),
        "canonical_gram": canonical,
        "canonical_determinant": determinant(canonical),
        "canonical_all_ones_norm": 2,
        "canonical_relation": "two -2 edges and one -1 edge",
        "sign_product_condition": "edge-sign product is negative",
        "positive_one_mutation_norms": mutated_norms,
        "rootless_consequence": "the canonical switched motif is forbidden",
    }


def adjacency(size: int, edges: Iterable[tuple[int, int]]) -> list[list[int]]:
    matrix = [[0] * size for _ in range(size)]
    for left, right in edges:
        if left == right or matrix[left][right]:
            raise AssertionError("invalid simple-graph edge")
        matrix[left][right] = 1
        matrix[right][left] = 1
    return matrix


def matrix_trace(matrix: list[list[int]]) -> int:
    return sum(matrix[index][index] for index in range(len(matrix)))


def trace_factor_two() -> dict[str, object]:
    minus_one = adjacency(3, [(0, 1)])
    minus_two = adjacency(3, [(0, 2), (1, 2)])
    product = matmul(matmul(minus_one, minus_two), minus_two)
    trace = matrix_trace(product)
    if trace != 2:
        raise AssertionError(f"motif trace factor drifted: {trace}")

    two_minus_one = adjacency(6, [(0, 1), (3, 4)])
    two_minus_two = adjacency(
        6,
        [(0, 2), (1, 2), (3, 5), (4, 5)],
    )
    double_trace = matrix_trace(
        matmul(matmul(two_minus_one, two_minus_two), two_minus_two)
    )
    if double_trace != 4:
        raise AssertionError("two-motif trace control drifted")
    return {
        "identity": (
            "tr(A_-1 A_-2^2) equals twice the number of unordered "
            "{-2,-2,-1} triangles"
        ),
        "one_motif_trace": trace,
        "two_motif_trace": double_trace,
        "factor": 2,
        "rootless_required_trace": 0,
    }


def endpoint_pair_counts() -> dict[str, object]:
    triangles = 231
    endpoint_n3 = 708
    q_sum = 2 * endpoint_n3 // 3
    ordered = {
        "plus_1": triangles * 20 + q_sum,
        "minus_1": 3 * q_sum,
        "minus_2": triangles * 12 - q_sum,
    }
    ordered["zero"] = (
        triangles * 18
        + triangles * 180
        - 3 * q_sum
    )
    if ordered != {
        "plus_1": 5092,
        "minus_1": 1416,
        "minus_2": 2300,
        "zero": 44322,
    }:
        raise AssertionError(f"endpoint ordered pair counts drifted: {ordered}")
    if sum(ordered.values()) != triangles * (triangles - 1):
        raise AssertionError("ordered pair total drifted")
    if any(value % 2 for value in ordered.values()):
        raise AssertionError("symmetric ordered counts must be even")
    unordered = {key: value // 2 for key, value in ordered.items()}
    if unordered != {
        "plus_1": 2546,
        "minus_1": 708,
        "minus_2": 1150,
        "zero": 22161,
    }:
        raise AssertionError("endpoint unordered pair counts drifted")
    return {
        "n3": endpoint_n3,
        "sum_q": q_sum,
        "ordered": ordered,
        "unordered": unordered,
        "ordered_total": sum(ordered.values()),
        "unordered_total": sum(unordered.values()),
        "same_on_all_determinant_rows": list(DETERMINANTS),
    }


def valuation(number: int, prime: int) -> int:
    result = 0
    while number % prime == 0:
        number //= prime
        result += 1
    return result


def finite_field_rank_table() -> list[dict[str, object]]:
    rows = []
    for determinant_value in DETERMINANTS:
        u = valuation(determinant_value, 3)
        v = valuation(determinant_value, 7)
        row = {
            "h": determinant_value,
            "v3": u,
            "v7": v,
            "rank_S_mod_3": 44 - u,
            "rank_G_mod_3": u,
            "rank_M_mod_3": 44 - u,
            "hull_dimension_mod_3": 44 - u,
            "code_self_orthogonal_mod_3": u == 0,
            "rank_S_mod_7": 44 - v,
            "rank_G_mod_7": v,
            "rank_M_mod_7": 44 - v,
            "hull_dimension_mod_7": 44 - v,
            "code_self_orthogonal_mod_7": v == 0,
        }
        if row["rank_S_mod_3"] + row["rank_G_mod_3"] != 44:
            raise AssertionError("3-rank complement drifted")
        if row["rank_S_mod_7"] + row["rank_G_mod_7"] != 44:
            raise AssertionError("7-rank complement drifted")
        rows.append(row)
    return rows


def finite_field_hostile_controls() -> dict[str, object]:
    isotropic_3 = [[1], [1], [1]]
    isotropic_7 = [[1], [2], [3]]
    gram_3 = matmul(transpose(isotropic_3), isotropic_3, 3)
    gram_7 = matmul(transpose(isotropic_7), isotropic_7, 7)
    if rank_mod(isotropic_3, 3) != 1 or rank_mod(gram_3, 3) != 0:
        raise AssertionError("F3 isotropic-column control drifted")
    if rank_mod(isotropic_7, 7) != 1 or rank_mod(gram_7, 7) != 0:
        raise AssertionError("F7 isotropic-column control drifted")

    nonself_3 = [[1], [0], [0]]
    nonself_7 = [[1], [0], [0]]
    if matmul(transpose(nonself_3), nonself_3, 3) != [[1]]:
        raise AssertionError("F3 non-self-orthogonal control drifted")
    if matmul(transpose(nonself_7), nonself_7, 7) != [[1]]:
        raise AssertionError("F7 non-self-orthogonal control drifted")

    return {
        "false_rank_inference": (
            "full column rank of X does not imply rank(X^T X)=rank(X) "
            "over finite fields"
        ),
        "F3_full_rank_X_gram_rank": [1, 0],
        "F7_full_rank_X_gram_rank": [1, 0],
        "false_universal_self_orthogonality": (
            "the endpoint code is self-orthogonal mod p only when "
            "rank(G mod p)=0"
        ),
        "F3_nonself_gram": [[1]],
        "F7_nonself_gram": [[1]],
    }


def symplectic_product(left: int, right: int, pairs: int = 22) -> int:
    value = 0
    for index in range(pairs):
        value ^= (
            ((left >> (2 * index)) & 1)
            & ((right >> (2 * index + 1)) & 1)
        )
        value ^= (
            ((left >> (2 * index + 1)) & 1)
            & ((right >> (2 * index)) & 1)
        )
    return value


def binary_rank(vectors: Iterable[int]) -> int:
    basis: dict[int, int] = {}
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def binary_hostile_control() -> dict[str, object]:
    rows: list[int] = []

    def quadratic_value(vector: int) -> int:
        result = 0
        for index in range(22):
            result ^= (
                ((vector >> (2 * index)) & 1)
                & ((vector >> (2 * index + 1)) & 1)
            )
        return result

    # The nine nonzero singular vectors in a four-dimensional hyperbolic
    # quadratic space have zero sum and total outer product equal to its
    # polar form.  Eleven orthogonal copies give rank 44 and 99 base rows.
    local_singular = [
        vector
        for vector in range(1, 16)
        if (
            (((vector >> 0) & 1) & ((vector >> 1) & 1))
            ^ (((vector >> 2) & 1) & ((vector >> 3) & 1))
        ) == 0
    ]
    if len(local_singular) != 9:
        raise AssertionError("four-dimensional singular census drifted")
    for block in range(11):
        rows.extend(vector << (4 * block) for vector in local_singular)

    # Doubled singular bridge rows connect the eleven four-spaces and
    # cancel in X^T X.
    for block in range(10):
        bridge = (1 << (4 * block)) | (1 << (4 * (block + 1)))
        rows.extend((bridge, bridge))

    # Fifty-six doubled filler rows reach exactly 231.
    rows.extend([1 << 0] * 112)
    if len(rows) != 231 or any(row == 0 for row in rows):
        raise AssertionError("binary control row census drifted")
    if any(quadratic_value(row) for row in rows):
        raise AssertionError("binary control contains a nonsingular row")
    row_sum = 0
    for row in rows:
        row_sum ^= row
    if row_sum:
        raise AssertionError("binary control rows do not sum to zero")

    expected_form = [[0] * 44 for _ in range(44)]
    for index in range(22):
        expected_form[2 * index][2 * index + 1] = 1
        expected_form[2 * index + 1][2 * index] = 1

    observed_gram = [[0] * 44 for _ in range(44)]
    for row in rows:
        positions = [index for index in range(44) if (row >> index) & 1]
        for left in positions:
            for right in positions:
                observed_gram[left][right] ^= 1
    if observed_gram != expected_form:
        raise AssertionError("binary control X^T X drifted")
    if binary_rank(rows) != 44:
        raise AssertionError("binary control X lost full column rank")

    projector_rows: list[int] = []
    for left in rows:
        mask = 0
        for index, right in enumerate(rows):
            if symplectic_product(left, right):
                mask |= 1 << index
        projector_rows.append(mask)

    squared_rows = []
    for mask in projector_rows:
        square = 0
        work = mask
        while work:
            bit = work & -work
            index = bit.bit_length() - 1
            square ^= projector_rows[index]
            work -= bit
        squared_rows.append(square)
    if squared_rows != projector_rows:
        raise AssertionError("binary control M is not idempotent")
    if binary_rank(projector_rows) != 44:
        raise AssertionError("binary control projector rank drifted")

    reached = 1
    frontier = 1
    while frontier:
        neighbors = 0
        work = frontier
        while work:
            bit = work & -work
            index = bit.bit_length() - 1
            neighbors |= projector_rows[index]
            work -= bit
        frontier = neighbors & ~reached
        reached |= frontier
    if reached.bit_count() != 231:
        raise AssertionError("binary control nonorthogonality graph disconnected")

    edge_count = sum(row.bit_count() for row in projector_rows) // 2
    if edge_count != 806:
        raise AssertionError(f"binary control edge count drifted: {edge_count}")

    return {
        "row_count": len(rows),
        "nonzero_row_count": sum(row != 0 for row in rows),
        "distinct_row_count": len(set(rows)),
        "base_row_count": 99,
        "padding": "66 doubled singular rows, including 10 bridge pairs",
        "all_rows_quadratically_singular": True,
        "row_sum_zero": True,
        "rank_X": binary_rank(rows),
        "gram": "22 hyperbolic 2x2 blocks",
        "projector_rank": binary_rank(projector_rows),
        "projector_idempotent": True,
        "projector_alternating": all(
            not ((projector_rows[index] >> index) & 1)
            for index in range(231)
        ),
        "projector_kills_one": all(
            row.bit_count() % 2 == 0 for row in projector_rows
        ),
        "nonorthogonality_connected": True,
        "odd_pair_count": edge_count,
        "dropped_premise": (
            "the integral entry multiplicities and positive-semidefinite "
            "integer lift are not imposed"
        ),
        "conclusion": (
            "mod-2 generation, projector rank/idempotence, and connectivity "
            "alone cannot force the signed integral motif"
        ),
    }


def pair_count_hostile_control() -> dict[str, object]:
    vertices = range(231)
    minus_two: set[tuple[int, int]] = set()
    for block in (range(48), range(48, 55), range(55, 57)):
        minus_two.update(itertools.combinations(block, 2))
    if len(minus_two) != 1150:
        raise AssertionError("minus-two hostile count drifted")

    component = {}
    for vertex in range(231):
        if vertex < 48:
            component[vertex] = 0
        elif vertex < 55:
            component[vertex] = 1
        elif vertex < 57:
            component[vertex] = 2
        else:
            component[vertex] = vertex - 54

    minus_one: set[tuple[int, int]] = set()
    for pair in itertools.combinations(vertices, 2):
        if pair in minus_two:
            continue
        if component[pair[0]] == component[pair[1]]:
            continue
        minus_one.add(pair)
        if len(minus_one) == 708:
            break
    if len(minus_one) != 708:
        raise AssertionError("minus-one hostile count drifted")

    used = minus_two | minus_one
    plus_one: set[tuple[int, int]] = set()
    for pair in itertools.combinations(vertices, 2):
        if pair in used:
            continue
        plus_one.add(pair)
        if len(plus_one) == 2546:
            break
    if len(plus_one) != 2546:
        raise AssertionError("plus-one hostile count drifted")

    minus_two_adjacency = [set() for _ in vertices]
    total_adjacency = [set() for _ in vertices]
    for left, right in minus_two:
        minus_two_adjacency[left].add(right)
        minus_two_adjacency[right].add(left)
        total_adjacency[left].add(right)
        total_adjacency[right].add(left)
    for family in (minus_one, plus_one):
        for left, right in family:
            total_adjacency[left].add(right)
            total_adjacency[right].add(left)

    motif_count = 0
    for left, right in minus_one:
        motif_count += len(
            minus_two_adjacency[left] & minus_two_adjacency[right]
        )
    if motif_count:
        raise AssertionError("pair-count hostile control contains a motif")

    seen = {0}
    stack = [0]
    while stack:
        vertex = stack.pop()
        for neighbor in total_adjacency[vertex]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    if len(seen) != 231:
        raise AssertionError("pair-count hostile control disconnected")

    zero_count = math.comb(231, 2) - len(used | plus_one)
    if zero_count != 22161:
        raise AssertionError("zero hostile count drifted")
    return {
        "vertex_count": 231,
        "connected": True,
        "unordered_counts": {
            "plus_1": len(plus_one),
            "minus_1": len(minus_one),
            "minus_2": len(minus_two),
            "zero": zero_count,
        },
        "motif_count": motif_count,
        "motif_trace": 2 * motif_count,
        "dropped_premise": (
            "no positive-semidefinite rank-44 projector/frame realization"
        ),
        "conclusion": (
            "connectivity and all endpoint pair multiplicities alone do "
            "not force the motif"
        ),
    }


def build_results() -> dict[str, object]:
    frozen = verify_input_freeze()
    endpoint_counts = endpoint_pair_counts()
    pair_control = pair_count_hostile_control()
    if pair_control["unordered_counts"] != endpoint_counts["unordered"]:
        raise AssertionError("hostile pair control does not preserve counts")
    ranks = finite_field_rank_table()
    expected_rank_rows = [
        (9, 42, 2, 44, 0),
        (21, 43, 1, 43, 1),
        (49, 44, 0, 42, 2),
        (81, 40, 4, 44, 0),
        (189, 41, 3, 43, 1),
        (441, 42, 2, 42, 2),
        (729, 38, 6, 44, 0),
        (1029, 43, 1, 41, 3),
    ]
    observed_rank_rows = [
        (
            row["h"],
            row["rank_S_mod_3"],
            row["rank_G_mod_3"],
            row["rank_S_mod_7"],
            row["rank_G_mod_7"],
        )
        for row in ranks
    ]
    if observed_rank_rows != expected_rank_rows:
        raise AssertionError(f"finite-field rank table drifted: {ranks}")
    return {
        "schema_version": 1,
        "claim_label": "VERIFIED_SCOPED_WITH_NONBLOCKING_COVERAGE_GAPS",
        "scope": (
            "independent necessary checks for a rootless integrally "
            "indecomposable rank-44 endpoint form"
        ),
        "frozen_inputs": frozen,
        "candidate_manifest_validation": candidate_manifest_validation(),
        "primitive_row_generation": primitive_row_generation(),
        "connectivity_and_decomposition": connectivity_and_decomposition(),
        "root_motif": motif_census(),
        "motif_trace": trace_factor_two(),
        "endpoint_pair_counts": endpoint_counts,
        "finite_field_rank_table": ranks,
        "finite_field_hostile_controls": finite_field_hostile_controls(),
        "binary_231_row_hostile_control": binary_hostile_control(),
        "pair_count_hostile_control": pair_control,
        "status": {
            "motif_forcing": "UNKNOWN",
            "indecomposable_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if arguments.output:
        arguments.output.write_bytes(encoded)
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
