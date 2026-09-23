#!/usr/bin/env python3
"""Exact Wave 27 checks for orthogonal ADE summands and cubic tensors.

The main finite calculation is an exact affine-lattice sphere enumeration.
For an orthogonal rank-six summand R of the scaled-dual form, the projected
row coordinates z_i have second moment

    sum_i z_i z_i^T = 21 R^-1.

If P_abc=sum_i z_ia z_ib z_ic, then

    P_aab = (21 R^-1)_ab (mod 2).

The fully symmetric coordinate tensor P has squared norm in the exact
S^(tensor 3) metric.  Fraction-valued LDL decomposition and integer interval
bounds enumerate every tensor in the forced parity coset below a stated
norm cap.  No floating-point pruning is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from functools import lru_cache
from itertools import combinations_with_replacement, product, permutations
from math import isqrt
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_BASE = "2ac11809fafee7ab752965ae49a96e922859b5ee"
FRAME_SCALE = 21
GLOBAL_CUBIC_TRACE = 60
AMBIENT_ROWS = 231
LATTICE_RANK = 44

INPUTS = {
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave25-n3-708-strictness/"
    "2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
    "verification/wave26-a2-frame-obstruction/"
    "2026-07-23T225015Z-audit.md":
        "5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3",
    "verification/wave26-a2-cubic-obstruction/"
    "2026-07-23T231001Z-audit.md":
        "883f48e70336b87955f5c2a115ac8b137169310c6f5ef91fe4581cb1b6c10465",
}

Number = int | Fraction
Matrix = list[list[Number]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def hash_payload(payload: object) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def validate_frozen_inputs(root: Path | None = None) -> dict[str, str]:
    root = ROOT if root is None else root
    observed: dict[str, str] = {}
    for relative, expected in INPUTS.items():
        digest = sha256(root / relative)
        if digest != expected:
            raise AssertionError(
                f"frozen input changed: {relative}: {digest} != {expected}"
            )
        observed[relative] = digest
    return observed


def identity(n: int) -> Matrix:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    columns = list(zip(*right))
    return [
        [sum(a * b for a, b in zip(row, column)) for column in columns]
        for row in left
    ]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[i][j] + right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def scale(matrix: Matrix, scalar: Number) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


def trace(matrix: Matrix) -> Number:
    return sum(matrix[i][i] for i in range(len(matrix)))


def determinant(matrix: Matrix) -> Fraction:
    work = [[Fraction(value) for value in row] for row in matrix]
    n = len(work)
    result = Fraction(1)
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, n):
            multiplier = work[row][column] / pivot_value
            for col in range(column + 1, n):
                work[row][col] -= multiplier * work[column][col]
    return result


def inverse(matrix: Matrix) -> Matrix:
    n = len(matrix)
    work = [
        [Fraction(value) for value in matrix[row]]
        + [Fraction(int(row == column)) for column in range(n)]
        for row in range(n)
    ]
    for column in range(n):
        pivot = next(
            row for row in range(column, n) if work[row][column] != 0
        )
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(n):
            if row == column or work[row][column] == 0:
                continue
            multiplier = work[row][column]
            work[row] = [
                work[row][col] - multiplier * work[column][col]
                for col in range(2 * n)
            ]
    return [row[n:] for row in work]


def as_integer_matrix(matrix: Matrix) -> list[list[int]]:
    result: list[list[int]] = []
    for row in matrix:
        converted: list[int] = []
        for value in row:
            fraction = Fraction(value)
            if fraction.denominator != 1:
                raise AssertionError(f"nonintegral matrix entry: {value}")
            converted.append(fraction.numerator)
        result.append(converted)
    return result


def is_symmetric(matrix: Matrix) -> bool:
    return matrix == transpose(matrix)


def is_even(matrix: Matrix) -> bool:
    return all(Fraction(matrix[i][i]).denominator == 1
               and int(matrix[i][i]) % 2 == 0
               for i in range(len(matrix)))


def is_positive_definite(matrix: Matrix) -> bool:
    return all(
        determinant([row[:size] for row in matrix[:size]]) > 0
        for size in range(1, len(matrix) + 1)
    )


def cartan_a(rank: int) -> list[list[int]]:
    return [
        [
            2 * int(i == j) - int(abs(i - j) == 1)
            for j in range(rank)
        ]
        for i in range(rank)
    ]


def cartan_d(rank: int) -> list[list[int]]:
    if rank < 4:
        raise ValueError("D rank must be at least four")
    edges = {(i, i + 1) for i in range(rank - 2)}
    edges.add((rank - 3, rank - 1))
    return [
        [
            2 * int(i == j)
            - int((i, j) in edges or (j, i) in edges)
            for j in range(rank)
        ]
        for i in range(rank)
    ]


def exceptional_cartan(kind: str) -> list[list[int]]:
    ranks = {"E6": 6, "E7": 7, "E8": 8}
    rank = ranks[kind]
    chain_end = rank - 2
    edges = {(i, i + 1) for i in range(chain_end)}
    edges.add((2, rank - 1))
    return [
        [
            2 * int(i == j)
            - int((i, j) in edges or (j, i) in edges)
            for j in range(rank)
        ]
        for i in range(rank)
    ]


E6 = exceptional_cartan("E6")
A6 = cartan_a(6)
E8 = exceptional_cartan("E8")


def ade_discriminant_screen() -> dict[str, object]:
    candidates: list[tuple[str, Matrix]] = []
    candidates.extend((f"A{rank}", cartan_a(rank)) for rank in range(1, 45))
    candidates.extend((f"D{rank}", cartan_d(rank)) for rank in range(4, 45))
    candidates.extend(
        (kind, exceptional_cartan(kind)) for kind in ("E6", "E7", "E8")
    )

    allowed: list[dict[str, object]] = []
    rejected: list[str] = []
    for name, matrix in candidates:
        dual = scale(inverse(matrix), FRAME_SCALE)
        if all(Fraction(value).denominator == 1
               for row in dual for value in row):
            allowed.append(
                {
                    "type": name,
                    "rank": len(matrix),
                    "determinant": int(determinant(matrix)),
                }
            )
        else:
            rejected.append(name)

    expected = [
        {"type": "A2", "rank": 2, "determinant": 3},
        {"type": "A6", "rank": 6, "determinant": 7},
        {"type": "A20", "rank": 20, "determinant": 21},
        {"type": "E6", "rank": 6, "determinant": 3},
        {"type": "E8", "rank": 8, "determinant": 1},
    ]
    if allowed != expected:
        raise AssertionError(f"unexpected ADE screen: {allowed}")
    return {
        "necessary_integrality": "21*R^-1 is integral",
        "rank_range_checked": [1, 44],
        "allowed_irreducible_components": allowed,
        "rejected_component_count": len(rejected),
        "rejected_components": rejected,
    }


def symmetric_triples(rank: int) -> list[tuple[int, int, int]]:
    return list(combinations_with_replacement(range(rank), 3))


def ordered_orbit(triple: tuple[int, int, int]) -> tuple[tuple[int, int, int], ...]:
    return tuple(sorted(set(permutations(triple))))


def symmetric_cubic_gram(form: Matrix) -> tuple[
    list[tuple[int, int, int]], list[list[int]]
]:
    triples = symmetric_triples(len(form))
    orbits = [ordered_orbit(triple) for triple in triples]
    gram: list[list[int]] = []
    for left in orbits:
        row: list[int] = []
        for right in orbits:
            row.append(
                sum(
                    int(form[a][d]) * int(form[b][e]) * int(form[c][f])
                    for a, b, c in left
                    for d, e, f in right
                )
            )
        gram.append(row)
    return triples, gram


def ldl(matrix: list[list[int]]) -> tuple[
    list[list[Fraction]], list[Fraction]
]:
    """Return exact G=L D L^T with unit lower-triangular L."""
    n = len(matrix)
    lower = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    diagonal = [Fraction(0) for _ in range(n)]
    for i in range(n):
        lower[i][i] = Fraction(1)
        diagonal[i] = Fraction(matrix[i][i]) - sum(
            lower[i][k] * lower[i][k] * diagonal[k]
            for k in range(i)
        )
        if diagonal[i] <= 0:
            raise AssertionError(f"nonpositive LDL pivot at {i}")
        for j in range(i + 1, n):
            lower[j][i] = (
                Fraction(matrix[j][i])
                - sum(
                    lower[j][k] * lower[i][k] * diagonal[k]
                    for k in range(i)
                )
            ) / diagonal[i]
    return lower, diagonal


def reconstruct_ldl(
    lower: list[list[Fraction]], diagonal: list[Fraction]
) -> Matrix:
    n = len(diagonal)
    return [
        [
            sum(lower[i][k] * diagonal[k] * lower[j][k]
                for k in range(n))
            for j in range(n)
        ]
        for i in range(n)
    ]


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def frame_parity_coset(
    form: Matrix, scale_value: int = FRAME_SCALE
) -> tuple[list[tuple[int, int, int]], list[int], list[int], Matrix]:
    triples = symmetric_triples(len(form))
    moment = scale(inverse(form), scale_value)
    moment_integer = as_integer_matrix(moment)
    moduli: list[int] = []
    residues: list[int] = []
    for a, b, c in triples:
        if a == b:
            moduli.append(2)
            residues.append(moment_integer[a][c] % 2)
        elif b == c:
            moduli.append(2)
            residues.append(moment_integer[b][a] % 2)
        else:
            moduli.append(1)
            residues.append(0)
    return triples, moduli, residues, moment_integer


def enumerate_affine_sphere(
    form: Matrix, bound: int, scale_value: int = FRAME_SCALE
) -> dict[str, object]:
    """Exhaust the frame-parity tensor coset through an exact norm cap.

    The natural lexicographic symmetric-triple basis is fixed.  For
    G=L D L^T,

        x^T G x = sum_i D_i (x_i + sum_{j>i} L_{j,i} x_j)^2.

    At depth i all x_j with j>i are fixed.  Multiplying the rational center
    denominator through the remaining inequality gives an exact integer
    square bound, evaluated with isqrt.  The congruence progression then
    visits every and only admissible integer x_i.
    """
    triples, gram = symmetric_cubic_gram(form)
    lower, diagonal = ldl(gram)
    if reconstruct_ldl(lower, diagonal) != [
        [Fraction(value) for value in row] for row in gram
    ]:
        raise AssertionError("LDL reconstruction failed")

    _, moduli, residues, moment = frame_parity_coset(form, scale_value)
    dimension = len(triples)
    vector = [0] * dimension
    accepted_nodes = 0
    complete_leaves = 0
    witness: tuple[int, ...] | None = None

    def recurse(index: int, remaining: Fraction) -> bool:
        nonlocal accepted_nodes, complete_leaves, witness
        if index < 0:
            complete_leaves += 1
            witness = tuple(vector)
            return True

        center = sum(
            lower[j][index] * vector[j]
            for j in range(index + 1, dimension)
        )
        radius_squared = remaining / diagonal[index]
        center_num = center.numerator
        center_den = center.denominator
        integer_radius = isqrt(
            (
                radius_squared.numerator
                * center_den
                * center_den
            ) // radius_squared.denominator
        )
        low = ceil_div(-center_num - integer_radius, center_den)
        high = (-center_num + integer_radius) // center_den

        modulus = moduli[index]
        residue = residues[index]
        first = low + ((residue - low) % modulus)
        for value in range(first, high + 1, modulus):
            term = diagonal[index] * (Fraction(value) + center) ** 2
            if term > remaining:
                continue
            accepted_nodes += 1
            vector[index] = value
            if recurse(index - 1, remaining - term):
                return True
        vector[index] = 0
        return False

    found = recurse(dimension - 1, Fraction(bound))
    witness_norm: int | None = None
    if found:
        assert witness is not None
        witness_norm = sum(
            witness[i] * gram[i][j] * witness[j]
            for i in range(dimension)
            for j in range(dimension)
        )
        if witness_norm > bound:
            raise AssertionError("enumerator returned an out-of-ball witness")

    gram_payload = {
        "triples": [list(triple) for triple in triples],
        "gram": gram,
    }
    ldl_payload = {
        "lower": [
            [str(value) for value in row] for row in lower
        ],
        "diagonal": [str(value) for value in diagonal],
    }
    return {
        "dimension": dimension,
        "bound": bound,
        "scale": scale_value,
        "basis_order": "lexicographic combinations_with_replacement",
        "recursion_order": "indices descending",
        "arithmetic": "fractions.Fraction plus exact integer isqrt bounds",
        "gram_sha256": hash_payload(gram_payload),
        "ldl_sha256": hash_payload(ldl_payload),
        "ldl_reconstruction": "PASS",
        "modulus_counts": {
            str(modulus): moduli.count(modulus)
            for modulus in sorted(set(moduli))
        },
        "odd_repeated_coordinate_count": sum(residues),
        "second_moment": moment,
        "accepted_partial_nodes": accepted_nodes,
        "complete_leaves": complete_leaves,
        "found_tensor_in_closed_ball": found,
        "witness_norm": witness_norm,
    }


@lru_cache(maxsize=None)
def e6_tensor_search() -> dict[str, object]:
    result = enumerate_affine_sphere(E6, 18)
    if result["found_tensor_in_closed_ball"]:
        raise AssertionError("E6 parity coset met the norm-18 ball")
    if result["accepted_partial_nodes"] != 10011:
        raise AssertionError(f"E6 search drifted: {result}")
    return result


@lru_cache(maxsize=None)
def a6_tensor_search() -> dict[str, object]:
    result = enumerate_affine_sphere(A6, GLOBAL_CUBIC_TRACE)
    if result["found_tensor_in_closed_ball"]:
        raise AssertionError("A6 parity coset met the norm-60 ball")
    if result["accepted_partial_nodes"] != 105185:
        raise AssertionError(f"A6 search drifted: {result}")
    return result


def cubic_energy_divisibility() -> dict[str, object]:
    residues = {
        value: (value ** 3 - value) % 6 for value in range(6)
    }
    if set(residues.values()) != {0}:
        raise AssertionError("k^3-k divisibility failed")
    return {
        "identity": (
            "||sum_i z_i^(tensor 3)||^2 "
            "= sum_(i,j)<z_i,z_j>^3"
        ),
        "congruence": (
            "energy is congruent modulo 6 to "
            "||sum_i z_i||^2"
        ),
        "all_integer_proof": (
            "k^3-k=k(k-1)(k+1), a product of three consecutive integers "
            "and therefore divisible by both 2 and 3"
        ),
        "projector_zero_sum": (
            "M*1=0 and full column rank imply sum_i z_i=0 "
            "on every transported orthogonal summand"
        ),
        "conclusion": "every actual local pure-cubic energy is in 6*Z",
        "complete_residue_check_modulo_6": [0, 1, 2, 3, 4, 5],
    }


def rank_one_projection_block() -> dict[str, object]:
    """Exact trace-14 E6 block refuting a naive algebraic trace floor."""
    form = E6
    dual = inverse(form)
    vector = [-1, 0, 1, 0, 0, -1]
    dual_row = [
        sum(vector[i] * dual[i][j] for i in range(6))
        for j in range(6)
    ]
    denominator = sum(dual_row[j] * vector[j] for j in range(6))
    projection = [
        [
            Fraction(vector[i]) * dual_row[j] / denominator
            for j in range(6)
        ]
        for i in range(6)
    ]
    b_matrix = add(identity(6), scale(projection, 8))
    q_matrix = matmul(dual, b_matrix)
    b_integer = as_integer_matrix(b_matrix)
    q_integer = as_integer_matrix(q_matrix)

    if matmul(form, q_integer) != b_integer:
        raise AssertionError("S*Q=B failed")
    if matmul(projection, projection) != projection:
        raise AssertionError("rank-one projection is not idempotent")
    if any(
        b_integer[i][j] % 2 != int(i == j)
        for i in range(6)
        for j in range(6)
    ):
        raise AssertionError("B is not the identity modulo two")
    if not is_symmetric(q_integer) or not is_even(q_integer):
        raise AssertionError("Q is not an even symmetric integral form")
    if not is_positive_definite(q_integer):
        raise AssertionError("Q is not positive definite")

    expected_q = [
        [2, 1, 0, 0, 0, 1],
        [1, 4, 6, 4, 2, 2],
        [0, 6, 12, 8, 4, 3],
        [0, 4, 8, 6, 3, 2],
        [0, 2, 4, 3, 2, 1],
        [1, 2, 3, 2, 1, 2],
    ]
    if q_integer != expected_q:
        raise AssertionError("trace-14 E6 block changed")

    return {
        "E6_cartan": form,
        "H_equals_E6_inverse": [
            [str(value) for value in row] for row in dual
        ],
        "v": vector,
        "vT_H_v": str(denominator),
        "P_squared_equals_P": True,
        "B_equals_I_plus_8P": b_integer,
        "B_mod_2": "identity",
        "B_spectrum": {"9": 1, "1": 5},
        "trace_B": int(trace(b_integer)),
        "det_B": int(determinant(b_integer)),
        "Q_equals_HB": q_integer,
        "Q_integral_even_positive_definite": True,
        "det_Q": int(determinant(q_integer)),
        "status": (
            "VALID_ALGEBRAIC_BLOCK_BUT_REFUTED_AS_PROJECTOR_SCHUR_ORIGIN"
        ),
        "refutation": (
            "compression trace 14 is below the verified E6 pure-cubic "
            "floor 24"
        ),
    }


def component_tensor_floors() -> dict[str, object]:
    e6 = e6_tensor_search()
    a6 = a6_tensor_search()
    divisibility = cubic_energy_divisibility()
    return {
        "general_compression": (
            "tr(R*Q_RR) >= ||sum_i z_i^(tensor 3)||^2"
        ),
        "global_complement_budget": (
            "a rank-r orthogonal summand has compression trace at most "
            "60-(44-r)=r+16 because the complementary compression has "
            "positive integral determinant and trace at least 44-r"
        ),
        "parity_identity": (
            "P_aab congruent to (21*R^-1)_ab modulo 2"
        ),
        "zero_sum_energy_divisibility": divisibility,
        "E6": {
            "parity_coset_closed_ball_cap": 18,
            "closed_ball_empty": not e6["found_tensor_in_closed_ball"],
            "actual_energy_floor": 24,
            "compression_trace_floor": 24,
            "global_complement_upper_bound": 22,
            "orthogonal_E6_summand": "REFUTED",
            "enumeration": e6,
        },
        "A6": {
            "parity_coset_closed_ball_cap": 60,
            "closed_ball_empty": not a6["found_tensor_in_closed_ball"],
            "actual_energy_floor": 66,
            "compression_trace_floor": 66,
            "global_trace": GLOBAL_CUBIC_TRACE,
            "orthogonal_A6_summand": "REFUTED",
            "enumeration": a6,
        },
    }


def a2_frame_capacity() -> dict[str, object]:
    rank = 2
    oriented_roots = 6
    energy = FRAME_SCALE * rank
    incident_rows = energy // 2
    fiber_cap = 3
    capacity = oriented_roots * fiber_cap
    if incident_rows <= capacity:
        raise AssertionError("A2 frame capacity did not contradict")
    return {
        "energy": energy,
        "forced_root_incident_rows": incident_rows,
        "oriented_roots": oriented_roots,
        "same_oriented_root_fiber_cap": fiber_cap,
        "capacity": capacity,
        "status": "REFUTED_AS_ORTHOGONAL_SUMMAND",
    }


COMPONENTS = [
    ("A2", 2, 3),
    ("A6", 6, 7),
    ("A20", 20, 21),
    ("E6", 6, 3),
    ("E8", 8, 1),
]
SURVIVING_H = [9, 21, 49, 81, 189, 441, 729, 1029]


def full_ade_decompositions() -> dict[int, list[dict[str, int]]]:
    rows: dict[int, list[dict[str, int]]] = {
        value: [] for value in SURVIVING_H
    }
    ranges = [range(LATTICE_RANK // rank + 1)
              for _, rank, _ in COMPONENTS]
    for counts in product(*ranges):
        rank = sum(
            counts[i] * COMPONENTS[i][1] for i in range(len(COMPONENTS))
        )
        if rank != LATTICE_RANK:
            continue
        determinant_value = 1
        for i, count in enumerate(counts):
            determinant_value *= COMPONENTS[i][2] ** count
        if determinant_value not in rows:
            continue
        rows[determinant_value].append(
            {
                COMPONENTS[i][0]: count
                for i, count in enumerate(counts)
                if count
            }
        )
    for value in rows:
        rows[value].sort(key=canonical_json)
    return rows


def even_amgm_floor(rank: int, determinant_product_floor: int) -> int:
    trace_floor = 2
    while (
        trace_floor ** rank
        < (rank ** rank) * determinant_product_floor
    ):
        trace_floor += 2
    return trace_floor


def classify_full_ade_cases() -> dict[str, object]:
    decompositions = full_ade_decompositions()
    expected_counts = {
        9: 2,
        21: 2,
        49: 1,
        81: 2,
        189: 3,
        441: 2,
        729: 4,
        1029: 1,
    }
    if {key: len(value) for key, value in decompositions.items()} != expected_counts:
        raise AssertionError("rank-44 ADE decomposition census drifted")

    baseline = {
        "A20": even_amgm_floor(20, 21),
        "E8": even_amgm_floor(8, 1),
    }
    if baseline != {"A20": 24, "E8": 8}:
        raise AssertionError(f"AM-GM baseline drifted: {baseline}")

    classified: list[dict[str, object]] = []
    survivors: list[dict[str, object]] = []
    for h in SURVIVING_H:
        for components in decompositions[h]:
            if components.get("A2", 0):
                status = "EXCLUDED_BY_A2_FRAME_CAPACITY"
                floor: int | None = None
            elif components.get("A6", 0):
                status = "EXCLUDED_BY_A6_CUBIC_FLOOR_66"
                floor = None
            elif components.get("E6", 0):
                status = "EXCLUDED_BY_E6_LOCAL_FLOOR_24_VS_GLOBAL_CAP_22"
                floor = None
            else:
                floor = (
                    baseline["E8"] * components.get("E8", 0)
                    + baseline["A20"] * components.get("A20", 0)
                )
                status = (
                    "EXCLUDED_BY_ORTHOGONAL_COMPRESSION_BUDGET"
                    if floor > GLOBAL_CUBIC_TRACE
                    else "SURVIVES_THIS_CONDITIONAL_SCREEN"
                )
            row = {
                "h": h,
                "components": components,
                "local_trace_floor": floor,
                "status": status,
            }
            classified.append(row)
            if status == "SURVIVES_THIS_CONDITIONAL_SCREEN":
                survivors.append(row)

    expected_survivors = [
        {
            "h": 21,
            "components": {"A20": 1, "E8": 3},
            "local_trace_floor": 48,
            "status": "SURVIVES_THIS_CONDITIONAL_SCREEN",
        }
    ]
    if survivors != expected_survivors:
        raise AssertionError(f"unexpected full-ADE survivors: {survivors}")

    return {
        "assumption": (
            "the entire rank-44 scaled-dual form is an orthogonal direct "
            "sum of irreducible ADE root lattices"
        ),
        "decompositions": {str(key): value for key, value in decompositions.items()},
        "component_rules": {
            "A2": "excluded by the 21-versus-18 projector-frame capacity",
            "A6": "excluded because its pure-cubic floor is 66 > 60",
            "E6": (
                "excluded: local tensor floor 24 exceeds the global "
                "complement upper bound 22"
            ),
            "E8": "AM-GM baseline at least 8",
            "A20": "AM-GM even-trace baseline at least 24",
        },
        "classified_cases": classified,
        "survivors_of_this_screen": survivors,
        "conditional_conclusion": (
            "only h=21 with S isometric to A20 orthogonal_sum E8^3 "
            "survives this full-ADE screen"
        ),
    }


def general_capacity_inequality() -> dict[str, object]:
    return {
        "setup": (
            "R is an orthogonal even root-lattice summand; n2 and n4 count "
            "rows whose R-projection has norm two and four"
        ),
        "energy_identity": "2*n2 + 4*n4 = 21*rank(R)",
        "root_fiber_bound": (
            "each oriented root supports at most three norm-two projection "
            "rows under the off-diagonal alphabet {-2,-1,0,1}"
        ),
        "norm_four_code": (
            "alpha4(R) is the maximum number of norm-four vectors having "
            "all mutual inner products in {-2,-1,0,1}"
        ),
        "necessary_capacity": (
            "21*rank(R) <= 6*number_of_oriented_roots(R) + 4*alpha4(R)"
        ),
        "A2_specialization": "42 <= 36 is false because alpha4(A2)=0",
        "warning": (
            "for A3 and larger, norm-four projections exist and the A2 "
            "incidence count cannot be copied without alpha4(R)"
        ),
    }


def hostile_controls() -> dict[str, object]:
    trace_block = rank_one_projection_block()
    e6_even_scale = frame_parity_coset(E6, 18)
    a6_even_scale = frame_parity_coset(A6, 14)
    if any(e6_even_scale[2]) or any(a6_even_scale[2]):
        raise AssertionError("even-scale zero-tensor control failed")
    return {
        "naive_E6_algebraic_trace_floor": {
            "proposed_floor": 18,
            "counterexample_trace": trace_block["trace_B"],
            "counterexample": trace_block,
            "status": "REFUTED",
        },
        "replace_frame_scale_21_by_18_for_E6": {
            "all_repeated_tensor_parities_even": True,
            "zero_tensor_allowed_by_congruence_relaxation": True,
            "status": "ODD_SCALE_IS_ACTIVE",
        },
        "replace_frame_scale_21_by_14_for_A6": {
            "all_repeated_tensor_parities_even": True,
            "zero_tensor_allowed_by_congruence_relaxation": True,
            "status": "ODD_SCALE_IS_ACTIVE",
        },
        "omit_second_moment": {
            "zero_tensor_allowed": True,
            "status": "FRAME_IDENTITY_IS_ACTIVE",
        },
        "nonorthogonal_root_subsystem": {
            "warning": (
                "projection coordinates can lie in a dual/glue coset and "
                "need not satisfy sum z_i z_i^T=21*R^-1"
            ),
            "status": "NO_CLAIM",
        },
        "norm_four_vectors": {
            "warning": (
                "A3 and larger root lattices contain norm-four vectors, so "
                "the A2 root-only incidence proof does not generalize"
            ),
            "tensor_parity_method_uses_norm_four_vectors_safely": True,
        },
    }


def build_results(root: Path | None = None) -> dict[str, object]:
    root = ROOT if root is None else root
    floors = component_tensor_floors()
    return {
        "base_commit": PUBLIC_BASE,
        "claim": {
            "label": "DERIVED",
            "primary": (
                "a full endpoint projector/Schur origin cannot have an "
                "orthogonal E6 summand: its local tensor floor is 24 while "
                "the rank-38 complement forces a local upper bound of 22"
            ),
            "corollary": (
                "an orthogonal A6 summand is impossible because its local "
                "pure-cubic floor is at least 66 while the global trace is 60"
            ),
            "full_ADE_conditional": (
                "if the full scaled-dual lattice is an orthogonal ADE root "
                "lattice, only h=21 and A20 orthogonal_sum E8^3 survives "
                "the current component screen"
            ),
            "endpoint_status": "UNKNOWN",
            "novelty_status": "UNKNOWN",
        },
        "frozen_inputs": validate_frozen_inputs(root),
        "ADE_discriminant_screen": ade_discriminant_screen(),
        "general_frame_capacity": general_capacity_inequality(),
        "tensor_component_floors": floors,
        "trace_14_E6_hostile_block": rank_one_projection_block(),
        "full_rank_44_ADE_screen": classify_full_ade_cases(),
        "hostile_controls": hostile_controls(),
        "limitations": [
            "The component theorems require an orthogonal integral summand, "
            "not merely a nonorthogonal root subsystem.",
            "The full-ADE census is conditional on the entire scaled-dual "
            "form being an orthogonal sum of irreducible ADE root lattices.",
            "A20 orthogonal_sum E8^3 survives this screen; no row frame, "
            "Schur certificate, primitive embedding, or graph is constructed.",
            "The parity sphere searches use necessary conditions only. "
            "Their empty balls prove lower bounds; a nonempty ball would "
            "not by itself construct projected rows.",
            "No surviving arithmetic h row is excluded without the stated "
            "root-lattice decomposition assumptions.",
            "n3=708, Conway-99 existence, and literature novelty remain UNKNOWN.",
        ],
    }


def write_results(path: Path, payload: object) -> None:
    path.write_text(canonical_json(payload), encoding="utf-8", newline="\n")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("exact-results.json"),
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_results()
    write_results(args.output, payload)
    print(canonical_json(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
