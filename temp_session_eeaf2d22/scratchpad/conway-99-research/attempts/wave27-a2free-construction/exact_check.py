#!/usr/bin/env python3
"""Exact Wave 27 A2-summand-free hostile-control certificate.

The construction is deliberately restricted.  It produces one exact
rank-44 determinant-nine form and one coupled (S,Q,G,B,C) arithmetic
package.  It does not enumerate all determinant-nine forms, all Q, any
231-row projector frames, or any graphs.

Only the Python standard library is used.  All matrix arithmetic,
positive-definiteness checks, lattice-vector enumeration, determinants,
and modular ranks are exact.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_BASE_COMMIT = "2ac11809fafee7ab752965ae49a96e922859b5ee"
INPUT_HASHES = {
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave24-n3-708-index/survivor-certificate.json":
        "a217ec7211128f51e684030a7fe8d3c60ac80935f356ba5193dc34d36d4077a2",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
    "verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md":
        "5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3",
    "verification/wave26-a2-cubic-obstruction/2026-07-23T231001Z-audit.md":
        "883f48e70336b87955f5c2a115ac8b137169310c6f5ef91fe4581cb1b6c10465",
}

RANK = 44
SCALE = 21

# The same E8 simple-root Gram matrix used by the frozen Wave 24 checker.
E8 = [
    [2, -1, 0, 0, 0, 0, 0, 0],
    [-1, 2, -1, 0, 0, 0, 0, 0],
    [0, -1, 2, -1, 0, 0, 0, -1],
    [0, 0, -1, 2, -1, 0, 0, 0],
    [0, 0, 0, -1, 2, -1, 0, 0],
    [0, 0, 0, 0, -1, 2, -1, 0],
    [0, 0, 0, 0, 0, -1, 2, 0],
    [0, 0, -1, 0, 0, 0, 0, 2],
]

# E6 with central node 2 and edge set
# (0,1),(1,2),(2,3),(3,4),(2,5).
E6 = [
    [2, -1, 0, 0, 0, 0],
    [-1, 2, -1, 0, 0, 0],
    [0, -1, 2, -1, 0, -1],
    [0, 0, -1, 2, -1, 0],
    [0, 0, 0, -1, 2, 0],
    [0, 0, -1, 0, 0, 2],
]

# The sign-canonical rank-one seed.  Its negative defines the same projector.
E6_SEED = (1, 0, -1, 0, 0, 1)


Matrix = list[list[int | Fraction]]
Vector = tuple[int, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def identity(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(matrix: Sequence[Sequence[int | Fraction]]) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    right_t = transpose(right)
    return [
        [sum(Fraction(x) * Fraction(y) for x, y in zip(row, col))
         for col in right_t]
        for row in left
    ]


def matscale(
    scalar: int | Fraction,
    matrix: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return [[Fraction(scalar) * Fraction(x) for x in row] for row in matrix]


def matadd(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return [
        [Fraction(x) + Fraction(y) for x, y in zip(row_left, row_right)]
        for row_left, row_right in zip(left, right)
    ]


def block_diag(blocks: Sequence[Sequence[Sequence[int | Fraction]]]) -> Matrix:
    size = sum(len(block) for block in blocks)
    out: Matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    offset = 0
    for block in blocks:
        width = len(block)
        if any(len(row) != width for row in block):
            raise ValueError("blocks must be square")
        for i in range(width):
            for j in range(width):
                out[offset + i][offset + j] = Fraction(block[i][j])
        offset += width
    return out


def as_integer_matrix(matrix: Sequence[Sequence[int | Fraction]]) -> list[list[int]]:
    out = []
    for row in matrix:
        integer_row = []
        for value in row:
            value = Fraction(value)
            if value.denominator != 1:
                raise ValueError(f"nonintegral matrix entry {value}")
            integer_row.append(value.numerator)
        out.append(integer_row)
    return out


def determinant(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("determinant requires a square matrix")
    work = [[Fraction(x) for x in row] for row in matrix]
    result = Fraction(1)
    for col in range(n):
        pivot = next((row for row in range(col, n) if work[row][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result = -result
        pivot_value = work[col][col]
        result *= pivot_value
        for row in range(col + 1, n):
            scale = work[row][col] / pivot_value
            if scale:
                for j in range(col, n):
                    work[row][j] -= scale * work[col][j]
    return result


def inverse(matrix: Sequence[Sequence[int | Fraction]]) -> Matrix:
    n = len(matrix)
    work = [
        [Fraction(x) for x in row]
        + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for col in range(n):
        pivot = next((row for row in range(col, n) if work[row][col]), None)
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
        pivot_value = work[col][col]
        work[col] = [x / pivot_value for x in work[col]]
        for row in range(n):
            if row == col:
                continue
            scale = work[row][col]
            if scale:
                work[row] = [
                    x - scale * y for x, y in zip(work[row], work[col])
                ]
    return [row[n:] for row in work]


def rank_exact(matrix: Sequence[Sequence[int | Fraction]]) -> int:
    if not matrix:
        return 0
    work = [[Fraction(x) for x in row] for row in matrix]
    rows = len(work)
    cols = len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][col]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][col]
        work[pivot_row] = [x / pivot_value for x in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            scale = work[row][col]
            if scale:
                work[row] = [
                    x - scale * y
                    for x, y in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    if not matrix:
        return 0
    work = [[x % prime for x in row] for row in matrix]
    rows = len(work)
    cols = len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][col]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse_pivot = pow(work[pivot_row][col], -1, prime)
        work[pivot_row] = [
            (x * inverse_pivot) % prime for x in work[pivot_row]
        ]
        for row in range(rows):
            if row == pivot_row:
                continue
            scale = work[row][col]
            if scale:
                work[row] = [
                    (x - scale * y) % prime
                    for x, y in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def ldl_decomposition(
    matrix: Sequence[Sequence[int | Fraction]],
) -> tuple[Matrix, list[Fraction]]:
    """Return exact A=L D L^T with unit lower-triangular L."""
    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("LDL requires a square matrix")
    if list(map(list, matrix)) != transpose(matrix):
        raise ValueError("LDL requires a symmetric matrix")
    lower: Matrix = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    diagonal = [Fraction(0) for _ in range(n)]
    for i in range(n):
        lower[i][i] = Fraction(1)
        diagonal[i] = Fraction(matrix[i][i]) - sum(
            Fraction(lower[i][k]) ** 2 * diagonal[k] for k in range(i)
        )
        if diagonal[i] == 0:
            raise ValueError("zero LDL pivot")
        for j in range(i + 1, n):
            lower[j][i] = (
                Fraction(matrix[j][i])
                - sum(
                    Fraction(lower[j][k])
                    * Fraction(lower[i][k])
                    * diagonal[k]
                    for k in range(i)
                )
            ) / diagonal[i]
    return lower, diagonal


def positive_definite(matrix: Sequence[Sequence[int | Fraction]]) -> bool:
    try:
        _, diagonal = ldl_decomposition(matrix)
    except ValueError:
        return False
    return all(value > 0 for value in diagonal)


def quadratic(
    matrix: Sequence[Sequence[int | Fraction]],
    vector: Sequence[int],
) -> Fraction:
    return sum(
        Fraction(vector[i])
        * Fraction(matrix[i][j])
        * Fraction(vector[j])
        for i in range(len(vector))
        for j in range(len(vector))
    )


def inner(
    matrix: Sequence[Sequence[int | Fraction]],
    left: Sequence[int],
    right: Sequence[int],
) -> Fraction:
    return sum(
        Fraction(left[i])
        * Fraction(matrix[i][j])
        * Fraction(right[j])
        for i in range(len(left))
        for j in range(len(right))
    )


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def enumerate_vectors_leq(
    matrix: Sequence[Sequence[int | Fraction]],
    bound: int | Fraction,
) -> list[Vector]:
    """Completely enumerate nonzero integer x with x^T A x <= bound.

    The exact LDL identity

        x^T A x = sum_i D_i (x_i + sum_{j>i} L[j,i] x_j)^2

    gives a finite interval for each coordinate once the higher coordinates
    are fixed.  Candidate intervals are deliberately enlarged and then
    filtered by exact rational comparison, so no floating-point cutoff is
    present.
    """
    lower, diagonal = ldl_decomposition(matrix)
    if any(value <= 0 for value in diagonal):
        raise ValueError("enumeration requires positive definiteness")
    bound = Fraction(bound)
    n = len(matrix)
    vector = [0 for _ in range(n)]
    output: list[Vector] = []

    def recurse(index: int, used: Fraction) -> None:
        if index < 0:
            if any(vector):
                output.append(tuple(vector))
            return
        remaining = bound - used
        if remaining < 0:
            return
        center = sum(
            Fraction(lower[j][index]) * vector[j]
            for j in range(index + 1, n)
        )
        radius_square = remaining / diagonal[index]
        integer_ceiling = (
            radius_square.numerator + radius_square.denominator - 1
        ) // radius_square.denominator
        radius_cap = isqrt(integer_ceiling) + 2
        low = floor_fraction(-center) - radius_cap
        high = ceil_fraction(-center) + radius_cap
        for candidate in range(low, high + 1):
            term = diagonal[index] * (Fraction(candidate) + center) ** 2
            if term <= remaining:
                vector[index] = candidate
                recurse(index - 1, used + term)
        vector[index] = 0

    recurse(n - 1, Fraction(0))
    return sorted(set(output))


def connected_components(
    matrix: Sequence[Sequence[int | Fraction]],
    vectors: Sequence[Vector],
) -> list[list[int]]:
    unseen = set(range(len(vectors)))
    components: list[list[int]] = []
    while unseen:
        start = min(unseen)
        unseen.remove(start)
        stack = [start]
        component: list[int] = []
        while stack:
            current = stack.pop()
            component.append(current)
            neighbors = [
                other
                for other in sorted(unseen)
                if inner(matrix, vectors[current], vectors[other]) != 0
            ]
            for other in neighbors:
                unseen.remove(other)
                stack.append(other)
        components.append(sorted(component))
    return sorted(components, key=lambda component: component[0])


def fraction_text(value: int | Fraction) -> str:
    value = Fraction(value)
    return f"{value.numerator}/{value.denominator}"


def fraction_matrix_text(
    matrix: Sequence[Sequence[int | Fraction]],
) -> list[list[str]]:
    return [[fraction_text(x) for x in row] for row in matrix]


def matrix_sha256(matrix: Sequence[Sequence[int]]) -> str:
    payload = json.dumps(
        matrix,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def prime_valuation(value: int, prime: int) -> int:
    value = abs(value)
    exponent = 0
    while value and value % prime == 0:
        exponent += 1
        value //= prime
    return exponent


def trace(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    return sum(Fraction(matrix[i][i]) for i in range(len(matrix)))


def matrix_equal(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> bool:
    return [
        [Fraction(x) for x in row] for row in left
    ] == [
        [Fraction(x) for x in row] for row in right
    ]


def even_integral_form(matrix: Sequence[Sequence[int | Fraction]]) -> bool:
    return (
        matrix_equal(matrix, transpose(matrix))
        and all(
            Fraction(value).denominator == 1
            for row in matrix
            for value in row
        )
        and all(Fraction(matrix[i][i]).numerator % 2 == 0
                for i in range(len(matrix)))
    )


def root_block_summary(
    label: str,
    matrix: Sequence[Sequence[int]],
    witness_bound: int,
) -> dict[str, object]:
    vectors = enumerate_vectors_leq(matrix, witness_bound)
    norms = [quadratic(matrix, vector) for vector in vectors]
    minimum = min(norms)
    minimal_vectors = [
        vector for vector, norm in zip(vectors, norms) if norm == minimum
    ]
    root_vectors = [
        vector for vector, norm in zip(vectors, norms) if norm == 2
    ]
    components = connected_components(matrix, root_vectors)
    return {
        "label": label,
        "enumeration_bound": witness_bound,
        "enumeration_method": "exact_reverse_LDL_branch_and_bound",
        "enumerated_nonzero_vector_count": len(vectors),
        "minimum": int(minimum),
        "minimal_vector_count": len(minimal_vectors),
        "minimal_vectors": [list(vector) for vector in minimal_vectors],
        "root_count": len(root_vectors),
        "root_vectors": [list(vector) for vector in root_vectors],
        "root_span_rank": rank_exact(root_vectors),
        "nonorthogonality_component_sizes": [
            len(component) for component in components
        ],
    }


def projection_package(
    e6: Sequence[Sequence[int]],
    seed: Sequence[int],
) -> dict[str, object]:
    h6 = inverse(e6)
    h_seed = [
        sum(Fraction(h6[i][j]) * seed[j] for j in range(6))
        for i in range(6)
    ]
    seed_norm = sum(Fraction(seed[i]) * h_seed[i] for i in range(6))
    projector = [
        [
            Fraction(seed[i]) * h_seed[j] / seed_norm
            for j in range(6)
        ]
        for i in range(6)
    ]
    b6 = matadd(identity(6), matscale(8, projector))
    q6 = matmul(h6, b6)
    return {
        "H6": h6,
        "seed": tuple(seed),
        "seed_norm": seed_norm,
        "P6": projector,
        "B6": b6,
        "Q6": q6,
    }


def valid_seed(seed: Sequence[int]) -> bool:
    package = projection_package(E6, seed)
    try:
        b6 = as_integer_matrix(package["B6"])  # type: ignore[arg-type]
        q6 = as_integer_matrix(package["Q6"])  # type: ignore[arg-type]
    except ValueError:
        return False
    return (
        all(
            (b6[i][j] - int(i == j)) % 2 == 0
            for i in range(6)
            for j in range(6)
        )
        and even_integral_form(q6)
        and positive_definite(q6)
        and determinant(q6) == 3
        and trace(b6) == 14
    )


def bounded_seed_search() -> dict[str, object]:
    seeds = []
    for seed in itertools.product((-1, 0, 1), repeat=6):
        if not any(seed):
            continue
        # Quotient by the harmless sign symmetry P(v)=P(-v).
        if next(value for value in seed if value) != 1:
            continue
        if valid_seed(seed):
            package = projection_package(E6, seed)
            seeds.append({
                "seed": list(seed),
                "H6_norm": fraction_text(package["seed_norm"]),
            })
    return {
        "ansatz": (
            "fixed E6 coordinates; v in {-1,0,1}^6 modulo sign; "
            "P=v(v^T E6^-1)/(v^T E6^-1 v); B6=I+8P; Q6=E6^-1 B6"
        ),
        "complete_within_stated_box_and_ansatz": True,
        "classification_of_all_forms_or_Q": False,
        "assumed_automorphism": None,
        "valid_sign_canonical_seed_count": len(seeds),
        "valid_sign_canonical_seeds": seeds,
        "selected_seed": list(E6_SEED),
    }


def construct() -> dict[str, object]:
    e8_inverse = as_integer_matrix(inverse(E8))
    projection = projection_package(E6, E6_SEED)
    h6 = projection["H6"]
    p6 = projection["P6"]
    b6 = as_integer_matrix(projection["B6"])  # type: ignore[arg-type]
    q6 = as_integer_matrix(projection["Q6"])  # type: ignore[arg-type]
    g8 = as_integer_matrix(matscale(SCALE, e8_inverse))
    g6 = as_integer_matrix(matscale(SCALE, h6))  # type: ignore[arg-type]

    s = as_integer_matrix(block_diag([E8] * 4 + [E6] * 2))
    q = as_integer_matrix(block_diag([e8_inverse] * 4 + [q6] * 2))
    g = as_integer_matrix(block_diag([g8] * 4 + [g6] * 2))
    b = as_integer_matrix(matmul(s, q))
    c_fraction = [
        [
            Fraction(b[i][j] - int(i == j), 2)
            for j in range(RANK)
        ]
        for i in range(RANK)
    ]
    c = as_integer_matrix(c_fraction)

    return {
        "blocks": {
            "E8": E8,
            "E8_inverse": e8_inverse,
            "E6": E6,
            "E6_inverse": fraction_matrix_text(h6),  # type: ignore[arg-type]
            "E6_seed": list(E6_SEED),
            "E6_seed_norm": fraction_text(projection["seed_norm"]),
            "P6": fraction_matrix_text(p6),  # type: ignore[arg-type]
            "Q6": q6,
            "B6": b6,
            "G8": g8,
            "G6": g6,
        },
        "matrices": {
            "S": s,
            "Q": q,
            "G": g,
            "B": b,
            "C": c,
        },
    }


def build_results() -> dict[str, object]:
    actual_hashes = {
        path: sha256_file(ROOT / path) for path in INPUT_HASHES
    }
    if actual_hashes != INPUT_HASHES:
        raise AssertionError(("frozen input hash mismatch", actual_hashes))

    construction = construct()
    blocks = construction["blocks"]
    matrices = construction["matrices"]
    s = matrices["S"]
    q = matrices["Q"]
    g = matrices["G"]
    b = matrices["B"]
    c = matrices["C"]
    e8_inverse = blocks["E8_inverse"]
    q6 = blocks["Q6"]
    g8 = blocks["G8"]
    g6 = blocks["G6"]
    p6 = [
        [Fraction(value) for value in row] for row in blocks["P6"]
    ]
    b6 = blocks["B6"]

    i44 = identity(RANK)
    twenty_one_i = matscale(SCALE, i44)
    twenty_one_q = matscale(SCALE, q)
    c_square = matmul(c, c)
    b_square = matmul(b, b)

    if not matrix_equal(matmul(p6, p6), p6):
        raise AssertionError("P6 is not idempotent")
    if rank_exact(p6) != 1:
        raise AssertionError("P6 is not rank one")
    if not matrix_equal(matmul(s, g), twenty_one_i):
        raise AssertionError("S G != 21 I")
    if not matrix_equal(matmul(s, q), b):
        raise AssertionError("B != S Q")
    if not matrix_equal(matmul(g, b), twenty_one_q):
        raise AssertionError("G B != 21 Q")
    if not matrix_equal(matmul(transpose(b), g), matmul(g, b)):
        raise AssertionError("B is not G-self-adjoint")
    if not matrix_equal(c_square, matscale(4, c)):
        raise AssertionError("C^2 != 4 C")

    determinant_s = int(determinant(s))
    determinant_q = int(determinant(q))
    determinant_g = int(determinant(g))
    determinant_b = int(determinant(b))
    if (determinant_s, determinant_q, determinant_b) != (9, 9, 81):
        raise AssertionError("unexpected coupled determinants")
    if determinant_g != SCALE ** RANK // 9:
        raise AssertionError("unexpected determinant of G")

    matrix_invariants = {
        "S": {
            "rank": rank_exact(s),
            "determinant": determinant_s,
            "symmetric": matrix_equal(s, transpose(s)),
            "integral": True,
            "even": even_integral_form(s),
            "positive_definite": positive_definite(s),
            "ldl_pivots": [
                fraction_text(value) for value in ldl_decomposition(s)[1]
            ],
            "sha256_canonical_json": matrix_sha256(s),
        },
        "Q": {
            "rank": rank_exact(q),
            "determinant": determinant_q,
            "determinant_mod_4": determinant_q % 4,
            "symmetric": matrix_equal(q, transpose(q)),
            "integral": True,
            "even": even_integral_form(q),
            "positive_definite": positive_definite(q),
            "ldl_pivots": [
                fraction_text(value) for value in ldl_decomposition(q)[1]
            ],
            "sha256_canonical_json": matrix_sha256(q),
        },
        "G": {
            "rank": rank_exact(g),
            "determinant": determinant_g,
            "symmetric": matrix_equal(g, transpose(g)),
            "integral": True,
            "even": even_integral_form(g),
            "positive_definite": positive_definite(g),
            "ldl_pivots": [
                fraction_text(value) for value in ldl_decomposition(g)[1]
            ],
            "sha256_canonical_json": matrix_sha256(g),
        },
        "B": {
            "rank": rank_exact(b),
            "determinant": determinant_b,
            "trace": int(trace(b)),
            "trace_square": int(trace(b_square)),
            "integral": True,
            "euclidean_symmetric": matrix_equal(b, transpose(b)),
            "G_self_adjoint": matrix_equal(
                matmul(transpose(b), g), matmul(g, b)
            ),
            "congruent_to_identity_mod_2": all(
                (b[i][j] - int(i == j)) % 2 == 0
                for i in range(RANK)
                for j in range(RANK)
            ),
            "spectrum_from_squarefree_polynomial": {
                "minimal_polynomial_divides": "(t-1)(t-9)",
                "eigenvalue_1_multiplicity": 42,
                "eigenvalue_9_multiplicity": 2,
                "positive": True,
            },
            "sha256_canonical_json": matrix_sha256(b),
        },
        "C": {
            "rank": rank_exact(c),
            "determinant": int(determinant(c)),
            "trace": int(trace(c)),
            "trace_square": int(trace(c_square)),
            "integral": True,
            "identity": "C=(B-I)/2",
            "polynomial_identity": "C^2=4C",
            "sha256_canonical_json": matrix_sha256(c),
        },
    }

    expected_scalar_facts = {
        "S": (RANK, 9, True, True),
        "Q": (RANK, 9, True, True),
        "G": (RANK, SCALE ** RANK // 9, True, True),
    }
    for name, expected in expected_scalar_facts.items():
        row = matrix_invariants[name]
        actual = (
            row["rank"],
            row["determinant"],
            row["even"],
            row["positive_definite"],
        )
        if actual != expected:
            raise AssertionError((name, actual, expected))
    if (
        matrix_invariants["B"]["trace"],
        matrix_invariants["B"]["trace_square"],
        matrix_invariants["C"]["rank"],
        matrix_invariants["C"]["trace"],
        matrix_invariants["C"]["trace_square"],
    ) != (60, 204, 2, 8, 32):
        raise AssertionError("unexpected B/C moments")

    block_vector_certificates = {
        "S_E8": root_block_summary("S E8 block", E8, 2),
        "S_E6": root_block_summary("S E6 block", E6, 2),
        "Q_E8_inverse": root_block_summary(
            "Q E8-inverse block", e8_inverse, 2
        ),
        "Q_Q6": root_block_summary("Q Q6 block", q6, 2),
        "G_G8": root_block_summary("G 21*E8^-1 block", g8, 42),
        "G_G6": root_block_summary("G 21*E6^-1 block", g6, 28),
    }

    expected_block_facts = {
        "S_E8": (2, 240, [240], 8),
        "S_E6": (2, 72, [72], 6),
        "Q_E8_inverse": (2, 240, [240], 8),
        "Q_Q6": (2, 72, [72], 6),
        "G_G8": (42, 0, [], 0),
        "G_G6": (28, 0, [], 0),
    }
    for name, expected in expected_block_facts.items():
        row = block_vector_certificates[name]
        actual = (
            row["minimum"],
            row["root_count"],
            row["nonorthogonality_component_sizes"],
            row["root_span_rank"],
        )
        if actual != expected:
            raise AssertionError((name, actual, expected))

    s_component_sizes = [240] * 4 + [72] * 2
    q_component_sizes = [240] * 4 + [72] * 2
    embedded_a2_vectors = [
        [1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
    ]
    embedded_a2_gram = [
        [
            int(inner(E6, left, right))
            for right in embedded_a2_vectors
        ]
        for left in embedded_a2_vectors
    ]
    if embedded_a2_gram != [[2, -1], [-1, 2]]:
        raise AssertionError("embedded A2 control was lost")

    root_and_minimum = {
        "block_vector_certificates": block_vector_certificates,
        "S": {
            "minimum": 2,
            "root_count": 4 * 240 + 2 * 72,
            "root_system": "E8^4 orthogonal_sum E6^2",
            "nonorthogonality_component_sizes": s_component_sizes,
            "contains_embedded_A2_root_subsystems": True,
            "embedded_A2_control_vectors_in_one_E6_block":
                embedded_a2_vectors,
            "embedded_A2_control_gram": embedded_a2_gram,
            "has_orthogonal_A2_direct_summand": False,
            "direct_summand_test": (
                "In an even orthogonal decomposition A2+R, every norm-two "
                "vector lies wholly in one summand; the six A2 roots must "
                "therefore be a size-six nonorthogonality component.  The "
                "complete exact root enumeration has only components of "
                "sizes 240 and 72."
            ),
        },
        "Q": {
            "minimum": 2,
            "root_count": 4 * 240 + 2 * 72,
            "root_system": "E8^4 orthogonal_sum E6^2",
            "nonorthogonality_component_sizes": q_component_sizes,
            "has_orthogonal_A2_direct_summand": False,
            "direct_summand_test": (
                "The same even-root-component criterion; complete exact "
                "root components have sizes 240 and 72, never six."
            ),
        },
        "G": {
            "minimum": 28,
            "minimal_vector_count": 2 * 54,
            "root_count": 0,
            "root_system": "empty",
            "has_orthogonal_A2_direct_summand": False,
            "direct_summand_test": (
                "An A2 direct summand contains norm-two vectors, while G "
                "has exact minimum 28."
            ),
        },
    }

    s_rank_mod_3 = rank_mod_prime(s, 3)
    q_rank_mod_3 = rank_mod_prime(q, 3)
    g_rank_mod_3 = rank_mod_prime(g, 3)
    g_rank_mod_7 = rank_mod_prime(g, 7)
    if (s_rank_mod_3, q_rank_mod_3, g_rank_mod_3, g_rank_mod_7) != (
        42, 42, 2, 0
    ):
        raise AssertionError("unexpected modular ranks")

    discriminant_groups = {
        "S": {
            "determinant": determinant_s,
            "rank_mod_3": s_rank_mod_3,
            "v3_determinant": prime_valuation(determinant_s, 3),
            "smith_invariants": [1] * 42 + [3, 3],
            "nontrivial_invariant_factors": [3, 3],
            "group": "(Z/3Z)^2",
        },
        "Q": {
            "determinant": determinant_q,
            "rank_mod_3": q_rank_mod_3,
            "v3_determinant": prime_valuation(determinant_q, 3),
            "smith_invariants": [1] * 42 + [3, 3],
            "nontrivial_invariant_factors": [3, 3],
            "group": "(Z/3Z)^2",
        },
        "G": {
            "determinant": determinant_g,
            "rank_mod_3": g_rank_mod_3,
            "rank_mod_7": g_rank_mod_7,
            "v3_determinant": prime_valuation(determinant_g, 3),
            "v7_determinant": prime_valuation(determinant_g, 7),
            "smith_invariants": [7, 7] + [21] * 42,
            "nontrivial_invariant_factors": [7, 7] + [21] * 42,
            "group": "(Z/7Z)^2 direct_sum (Z/21Z)^42",
        },
        "inference_rule": (
            "For each relevant prime p, rank modulo p counts Smith factors "
            "not divisible by p.  Here each determinant valuation equals "
            "the number of divisible factors, so no factor contains p^2; "
            "divisibility ordering fixes the displayed invariant factors."
        ),
    }
    for name in ("S", "Q", "G"):
        row = discriminant_groups[name]
        product = 1
        for invariant in row["smith_invariants"]:
            product *= invariant
        if product != row["determinant"]:
            raise AssertionError((name, "Smith product mismatch"))

    search = bounded_seed_search()
    if search["valid_sign_canonical_seed_count"] != 27:
        raise AssertionError("bounded seed count changed")
    if list(E6_SEED) not in [
        row["seed"] for row in search["valid_sign_canonical_seeds"]
    ]:
        raise AssertionError("selected seed absent from bounded search")

    wrong_convention_seed = (1, 1, 0, -1, 0, 0)
    wrong_norm = projection_package(E6, wrong_convention_seed)["seed_norm"]
    naive_q_equals_s_trace = int(trace(matmul(s, s)))
    if wrong_norm != Fraction(10, 3):
        raise AssertionError("coordinate-mismatch hostile control changed")
    if naive_q_equals_s_trace == 60:
        raise AssertionError("naive Q=S unexpectedly met endpoint trace")

    coupled_identities = {
        "n3_parameter_used_only_for_trace_target": 708,
        "h_equals_detS": determinant_s,
        "detQ": determinant_q,
        "detB": determinant_b,
        "detB_equals_h_times_detQ": (
            determinant_b == determinant_s * determinant_q
        ),
        "traceB": int(trace(b)),
        "B_equals_SQ": matrix_equal(matmul(s, q), b),
        "SG_equals_21I": matrix_equal(matmul(s, g), twenty_one_i),
        "GB_equals_21Q": matrix_equal(matmul(g, b), twenty_one_q),
        "B_congruent_I_mod_2": matrix_invariants["B"][
            "congruent_to_identity_mod_2"
        ],
        "C_equals_B_minus_I_over_2": True,
        "C_square_equals_4C": matrix_equal(c_square, matscale(4, c)),
        "C_rank": rank_exact(c),
        "traceC": int(trace(c)),
        "traceC2": int(trace(c_square)),
        "B_spectrum": {"1": 42, "9": 2},
        "G_minimum_at_least_4": root_and_minimum["G"]["minimum"] >= 4,
    }
    if not all(
        coupled_identities[key]
        for key in (
            "detB_equals_h_times_detQ",
            "B_equals_SQ",
            "SG_equals_21I",
            "GB_equals_21Q",
            "B_congruent_I_mod_2",
            "C_square_equals_4C",
            "G_minimum_at_least_4",
        )
    ):
        raise AssertionError("coupled identity failed")

    return {
        "schema_version": 1,
        "status": {
            "claim_label": "CANDIDATE",
            "construction_result": (
                "Exact A2-orthogonal-summand-free hostile control for the "
                "h=9 coupled arithmetic/lattice relaxation"
            ),
            "n3_708_excluded": False,
            "n3_708_status": "UNKNOWN",
            "conway_99_status": "UNKNOWN",
            "novelty_status": "UNKNOWN",
            "independent_verification": "PENDING",
        },
        "frozen_inputs": {
            "public_base_commit": PUBLIC_BASE_COMMIT,
            "sha256": actual_hashes,
        },
        "scope": {
            "proved_by_certificate": [
                "One explicit even positive-definite rank-44 determinant-nine "
                "form S has no orthogonal A2 direct summand.",
                "The displayed complete S,Q,G,B,C matrices satisfy the h=9 "
                "n3=708 coupled arithmetic/lattice identities.",
                "The control survives the Wave 26 A2-summand obstruction "
                "because S has no such summand.",
            ],
            "not_proved": [
                "No primitive embedding in Z^231.",
                "No 231-row norm-four projector frame.",
                "No Schur-square W=M o M origin.",
                "No classification of rank-44 determinant-nine forms.",
                "No completeness outside the explicitly bounded seed ansatz.",
                "No graph and no srg(99,14,1,2).",
            ],
            "terminology": (
                "A2-free means no orthogonal A2 direct summand here.  S does "
                "contain embedded A2 root subsystems."
            ),
        },
        "search": {
            **search,
            "global_restrictions": [
                "S fixed to E8^4 orthogonal_sum E6^2.",
                "Q fixed block diagonal with E8-inverse blocks and two "
                "identical rank-one-projector E6 blocks.",
                "The same E6 seed is repeated in both blocks.",
                "No cross-block Q entries are searched.",
                "No target automorphism is assumed.",
            ],
            "hostile_controls": {
                "wrong_E6_coordinate_seed": list(wrong_convention_seed),
                "wrong_E6_coordinate_seed_norm": fraction_text(wrong_norm),
                "naive_Q_equals_S_traceB": naive_q_equals_s_trace,
                "required_traceB": 60,
            },
        },
        "construction": construction,
        "matrix_invariants": matrix_invariants,
        "root_and_minimum_certificates": root_and_minimum,
        "discriminant_groups": discriminant_groups,
        "coupled_identities": coupled_identities,
        "conclusion": {
            "naive_all_h9_forms_have_A2_summand": "REFUTED_BY_EXPLICIT_FORM",
            "wave26_specific_E8_5_A2_2_survivor_refutation": "UNCHANGED",
            "abstract_h9_relaxation": "STILL_SURVIVES",
            "projector_or_schur_origin_of_new_control": "NOT_ESTABLISHED",
            "n3_708": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("exact-results.json"),
    )
    args = parser.parse_args()
    results = build_results()
    write_json(args.output, results)
    print(json.dumps({
        "status": results["status"],
        "matrix_hashes": {
            name: row["sha256_canonical_json"]
            for name, row in results["matrix_invariants"].items()
        },
        "output": str(args.output),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
