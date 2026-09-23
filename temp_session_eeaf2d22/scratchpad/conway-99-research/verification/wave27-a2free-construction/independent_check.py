"""Independent exact verifier for the Wave 27 A2-summand-free control.

This module intentionally uses only the Python standard library.  It rebuilds
the matrices from Cartan edges and a single E6 vector, rather than importing
the construction checker or trusting its serialized matrices.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUBLIC_BASE_COMMIT = "2ac11809fafee7ab752965ae49a96e922859b5ee"

DISCOVERY_HASHES = {
    "agents/2026-07-23-wave27-a2free-construction.md":
        "3e80a13c71f227d394dbbbd5e82d2d9afa781b60a523f7470d6c6d74c3b6dbe9",
    "attempts/wave27-a2free-construction/exact_check.py":
        "1bd20f820a5d4467f29860a03a93c4ef3192bb9df4b1c87901080ffa8b793f1e",
    "attempts/wave27-a2free-construction/exact-results.json":
        "3b1d30b6110d937f1bd4bb9ff570419625063afc5c0915382baa2466d349946d",
    "attempts/wave27-a2free-construction/failed-routes.md":
        "724e2daf4604cd7fb779b686acc9bdf5b6a1398ed020846bcbebc0968482e120",
    "attempts/wave27-a2free-construction/input-freeze.sha256":
        "19beda0a2cfd430bde00d39c9371b9f76df36b7e3ee9ee612b73db21bae43f93",
    "attempts/wave27-a2free-construction/run-report.yaml":
        "249078954019aad3256456470a2a677e4b85f3b7c734bad80c0f29a4effa05d7",
    "attempts/wave27-a2free-construction/test_exact_check.py":
        "7693d905bd142c34e8552f93c87b253621dfc6e6f94e1beec65e8b688eb8568d",
}

Matrix = list[list[Fraction]]
IntMatrix = list[list[int]]
Vector = tuple[int, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def fractions(matrix: Sequence[Sequence[int | Fraction]]) -> Matrix:
    return [[Fraction(value) for value in row] for row in matrix]


def identity(n: int) -> Matrix:
    return [
        [Fraction(int(i == j)) for j in range(n)]
        for i in range(n)
    ]


def transpose(matrix: Sequence[Sequence[int | Fraction]]) -> Matrix:
    if not matrix:
        return []
    return [
        [Fraction(matrix[i][j]) for i in range(len(matrix))]
        for j in range(len(matrix[0]))
    ]


def matmul(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    if not left or not right:
        return []
    rows = len(left)
    middle = len(right)
    columns = len(right[0])
    if len(left[0]) != middle:
        raise ValueError("matrix dimension mismatch")
    right_t = transpose(right)
    return [
        [
            sum(
                (Fraction(left[i][k]) * right_t[j][k] for k in range(middle)),
                Fraction(0),
            )
            for j in range(columns)
        ]
        for i in range(rows)
    ]


def matadd(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return [
        [Fraction(a) + Fraction(b) for a, b in zip(row_a, row_b)]
        for row_a, row_b in zip(left, right)
    ]


def matsub(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return [
        [Fraction(a) - Fraction(b) for a, b in zip(row_a, row_b)]
        for row_a, row_b in zip(left, right)
    ]


def matscale(
    scalar: int | Fraction,
    matrix: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    factor = Fraction(scalar)
    return [[factor * Fraction(value) for value in row] for row in matrix]


def outer(
    left: Sequence[int | Fraction],
    right: Sequence[int | Fraction],
) -> Matrix:
    return [
        [Fraction(a) * Fraction(b) for b in right]
        for a in left
    ]


def matrix_equal(
    left: Sequence[Sequence[int | Fraction]],
    right: Sequence[Sequence[int | Fraction]],
) -> bool:
    return fractions(left) == fractions(right)


def as_integers(matrix: Sequence[Sequence[int | Fraction]]) -> IntMatrix:
    result: IntMatrix = []
    for row in matrix:
        out_row: list[int] = []
        for value in row:
            exact = Fraction(value)
            if exact.denominator != 1:
                raise AssertionError(f"nonintegral matrix entry {exact}")
            out_row.append(exact.numerator)
        result.append(out_row)
    return result


def block_diagonal(blocks: Sequence[Sequence[Sequence[int | Fraction]]]) -> Matrix:
    total = sum(len(block) for block in blocks)
    result = [[Fraction(0) for _ in range(total)] for _ in range(total)]
    start = 0
    for block in blocks:
        size = len(block)
        if any(len(row) != size for row in block):
            raise ValueError("blocks must be square")
        for i in range(size):
            for j in range(size):
                result[start + i][start + j] = Fraction(block[i][j])
        start += size
    return result


def trace(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    return sum(
        (Fraction(matrix[i][i]) for i in range(len(matrix))),
        Fraction(0),
    )


def determinant(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
    work = fractions(matrix)
    n = len(work)
    if any(len(row) != n for row in work):
        raise ValueError("determinant requires a square matrix")
    sign = 1
    value = Fraction(1)
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        value *= pivot_value
        for row in range(column + 1, n):
            if not work[row][column]:
                continue
            factor = work[row][column] / pivot_value
            for j in range(column + 1, n):
                work[row][j] -= factor * work[column][j]
            work[row][column] = Fraction(0)
    return sign * value


def inverse(matrix: Sequence[Sequence[int | Fraction]]) -> Matrix:
    left = fractions(matrix)
    n = len(left)
    if any(len(row) != n for row in left):
        raise ValueError("inverse requires a square matrix")
    augmented = [
        left[i] + identity(n)[i]
        for i in range(n)
    ]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if augmented[row][column]),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        augmented[column], augmented[pivot] = (
            augmented[pivot],
            augmented[column],
        )
        pivot_value = augmented[column][column]
        augmented[column] = [
            value / pivot_value for value in augmented[column]
        ]
        for row in range(n):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_entry
                    for value, pivot_entry
                    in zip(augmented[row], augmented[column])
                ]
    return [row[n:] for row in augmented]


def rank_exact(matrix: Sequence[Sequence[int | Fraction]]) -> int:
    work = fractions(matrix)
    if not work:
        return 0
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def rank_mod_prime(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[value % prime for value in row] for row in matrix]
    if not work:
        return 0
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse_pivot = pow(work[pivot_row][column], -1, prime)
        work[pivot_row] = [
            value * inverse_pivot % prime for value in work[pivot_row]
        ]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    (value - factor * pivot_value) % prime
                    for value, pivot_value
                    in zip(work[row], work[pivot_row])
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def ldl(matrix: Sequence[Sequence[int | Fraction]]) -> tuple[Matrix, list[Fraction]]:
    source = fractions(matrix)
    n = len(source)
    if any(len(row) != n for row in source):
        raise ValueError("LDL requires a square matrix")
    if source != transpose(source):
        raise ValueError("LDL requires symmetry")
    lower = identity(n)
    diagonal: list[Fraction] = [Fraction(0) for _ in range(n)]
    for i in range(n):
        diagonal[i] = source[i][i] - sum(
            (
                lower[i][k] * lower[i][k] * diagonal[k]
                for k in range(i)
            ),
            Fraction(0),
        )
        if diagonal[i] == 0:
            raise ValueError("zero LDL pivot")
        for j in range(i + 1, n):
            numerator = source[j][i] - sum(
                (
                    lower[j][k] * lower[i][k] * diagonal[k]
                    for k in range(i)
                ),
                Fraction(0),
            )
            lower[j][i] = numerator / diagonal[i]
    return lower, diagonal


def is_positive_definite(
    matrix: Sequence[Sequence[int | Fraction]],
) -> bool:
    try:
        _, pivots = ldl(matrix)
    except ValueError:
        return False
    return all(pivot > 0 for pivot in pivots)


def is_even_integral_form(
    matrix: Sequence[Sequence[int | Fraction]],
) -> bool:
    try:
        integer_matrix = as_integers(matrix)
    except AssertionError:
        return False
    return (
        integer_matrix == as_integers(transpose(integer_matrix))
        and all(integer_matrix[i][i] % 2 == 0 for i in range(len(matrix)))
    )


def qform(
    matrix: Sequence[Sequence[int | Fraction]],
    vector: Sequence[int],
) -> Fraction:
    return sum(
        (
            Fraction(vector[i])
            * Fraction(matrix[i][j])
            * Fraction(vector[j])
            for i in range(len(vector))
            for j in range(len(vector))
        ),
        Fraction(0),
    )


def bilinear(
    matrix: Sequence[Sequence[int | Fraction]],
    left: Sequence[int],
    right: Sequence[int],
) -> Fraction:
    return sum(
        (
            Fraction(left[i])
            * Fraction(matrix[i][j])
            * Fraction(right[j])
            for i in range(len(left))
            for j in range(len(right))
        ),
        Fraction(0),
    )


def ceil_sqrt_fraction(value: Fraction) -> int:
    if value < 0:
        raise ValueError("square root of negative value")
    base = isqrt(value.numerator // value.denominator)
    if Fraction(base * base) < value:
        base += 1
    return base


def enumerate_vectors_at_most(
    matrix: Sequence[Sequence[int | Fraction]],
    limit: int | Fraction,
) -> list[Vector]:
    """Complete reverse-LDL enumeration of nonzero integer vectors."""

    source = fractions(matrix)
    n = len(source)
    lower, diagonal = ldl(source)
    if not all(value > 0 for value in diagonal):
        raise ValueError("enumeration requires positive definiteness")
    cutoff = Fraction(limit)
    coordinates = [0 for _ in range(n)]
    found: list[Vector] = []

    def descend(index: int, spent: Fraction) -> None:
        if index < 0:
            vector = tuple(coordinates)
            if any(vector) and qform(source, vector) <= cutoff:
                found.append(vector)
            return
        remaining = cutoff - spent
        if remaining < 0:
            return
        shift = sum(
            (
                lower[j][index] * coordinates[j]
                for j in range(index + 1, n)
            ),
            Fraction(0),
        )
        radius = ceil_sqrt_fraction(remaining / diagonal[index])
        center_floor = (-shift).numerator // (-shift).denominator
        for value in range(
            center_floor - radius - 1,
            center_floor + radius + 2,
        ):
            contribution = diagonal[index] * (Fraction(value) + shift) ** 2
            if contribution <= remaining:
                coordinates[index] = value
                descend(index - 1, spent + contribution)
        coordinates[index] = 0

    descend(n - 1, Fraction(0))
    unique = sorted(set(found))
    for vector in unique:
        if qform(source, vector) > cutoff:
            raise AssertionError("enumerator emitted an out-of-range vector")
    return unique


def minimum_certificate(
    matrix: Sequence[Sequence[int | Fraction]],
    witness_limit: int | Fraction,
) -> dict[str, object]:
    vectors = enumerate_vectors_at_most(matrix, witness_limit)
    if not vectors:
        raise AssertionError("no nonzero vectors at witness limit")
    values = {vector: qform(matrix, vector) for vector in vectors}
    minimum = min(values.values())
    minimizers = sorted(
        vector for vector, value in values.items() if value == minimum
    )
    return {
        "minimum": fraction_text(minimum),
        "minimal_vector_count": len(minimizers),
        "minimal_vectors": [list(vector) for vector in minimizers],
        "minimal_vectors_sha256": canonical_sha256(minimizers),
        "enumeration_cutoff": fraction_text(Fraction(witness_limit)),
        "enumerated_nonzero_count": len(vectors),
    }


def component_sizes(
    matrix: Sequence[Sequence[int | Fraction]],
    vectors: Sequence[Vector],
) -> list[int]:
    remaining = set(range(len(vectors)))
    sizes: list[int] = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        queue: deque[int] = deque([seed])
        size = 0
        while queue:
            current = queue.popleft()
            size += 1
            neighbors = [
                candidate
                for candidate in sorted(remaining)
                if bilinear(matrix, vectors[current], vectors[candidate]) != 0
            ]
            for candidate in neighbors:
                remaining.remove(candidate)
                queue.append(candidate)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def cartan(rank: int, edges: Iterable[tuple[int, int]]) -> IntMatrix:
    result = [[0 for _ in range(rank)] for _ in range(rank)]
    for i in range(rank):
        result[i][i] = 2
    for i, j in edges:
        result[i][j] = -1
        result[j][i] = -1
    return result


def prime_valuation(value: int, prime: int) -> int:
    if value <= 0:
        raise ValueError("valuation expects a positive integer")
    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent


def build_matrices() -> dict[str, object]:
    e8 = cartan(
        8,
        (
            (0, 1), (1, 2), (2, 3), (3, 4),
            (4, 5), (5, 6), (2, 7),
        ),
    )
    e6 = cartan(
        6,
        ((0, 1), (1, 2), (2, 3), (3, 4), (2, 5)),
    )
    h8 = inverse(e8)
    h6 = inverse(e6)
    seed = (1, 0, -1, 0, 0, 1)
    hv = [
        sum(
            (h6[i][j] * seed[j] for j in range(6)),
            Fraction(0),
        )
        for i in range(6)
    ]
    dual_norm = sum(
        (Fraction(seed[i]) * hv[i] for i in range(6)),
        Fraction(0),
    )
    projector = matscale(
        Fraction(1, 1) / dual_norm,
        outer(seed, hv),
    )
    b6 = matadd(identity(6), matscale(8, projector))
    q6 = matmul(h6, b6)
    g8 = matscale(21, h8)
    g6 = matscale(21, h6)

    s = block_diagonal([e8] * 4 + [e6] * 2)
    q = block_diagonal([h8] * 4 + [q6] * 2)
    g = block_diagonal([g8] * 4 + [g6] * 2)
    b = matmul(s, q)
    c = matscale(Fraction(1, 2), matsub(b, identity(44)))

    return {
        "E8": e8,
        "E6": e6,
        "H8": as_integers(h8),
        "H6": [[fraction_text(value) for value in row] for row in h6],
        "seed": list(seed),
        "seed_dual_norm": fraction_text(dual_norm),
        "projector": [
            [fraction_text(value) for value in row] for row in projector
        ],
        "B6": as_integers(b6),
        "Q6": as_integers(q6),
        "G8": as_integers(g8),
        "G6": as_integers(g6),
        "S": as_integers(s),
        "Q": as_integers(q),
        "G": as_integers(g),
        "B": as_integers(b),
        "C": as_integers(c),
    }


def matrix_summary(matrix: IntMatrix, form: bool) -> dict[str, object]:
    row: dict[str, object] = {
        "rank": rank_exact(matrix),
        "determinant": int(determinant(matrix)),
        "trace": int(trace(matrix)),
        "sha256_canonical_json": canonical_sha256(matrix),
    }
    if form:
        _, pivots = ldl(matrix)
        row.update({
            "symmetric": matrix_equal(matrix, transpose(matrix)),
            "integral": True,
            "even": is_even_integral_form(matrix),
            "positive_definite": all(pivot > 0 for pivot in pivots),
            "ldl_pivots": [fraction_text(pivot) for pivot in pivots],
        })
    return row


def independent_results() -> dict[str, object]:
    actual_hashes = {
        path: sha256_file(ROOT / path)
        for path in DISCOVERY_HASHES
    }
    if actual_hashes != DISCOVERY_HASHES:
        raise AssertionError("discovery artifacts changed after freeze")

    built = build_matrices()
    e8 = built["E8"]
    e6 = built["E6"]
    h8 = built["H8"]
    h6 = [
        [Fraction(value) for value in row]
        for row in built["H6"]
    ]
    q6 = built["Q6"]
    g8 = built["G8"]
    g6 = built["G6"]
    s = built["S"]
    q = built["Q"]
    g = built["G"]
    b = built["B"]
    c = built["C"]
    b6 = built["B6"]

    if determinant(e8) != 1 or determinant(e6) != 3:
        raise AssertionError("unexpected Cartan determinant")
    if built["seed_dual_norm"] != "4/3":
        raise AssertionError("unexpected E6 dual norm")
    for name in ("S", "Q", "G"):
        if not is_even_integral_form(built[name]):
            raise AssertionError(f"{name} is not even integral")
        if not is_positive_definite(built[name]):
            raise AssertionError(f"{name} is not positive definite")

    projector = [
        [Fraction(value) for value in row]
        for row in built["projector"]
    ]
    if not matrix_equal(matmul(projector, projector), projector):
        raise AssertionError("rank-one operator is not idempotent")
    if rank_exact(projector) != 1:
        raise AssertionError("projector rank changed")
    if not matrix_equal(matmul(e6, q6), b6):
        raise AssertionError("local B6=E6 Q6 failed")
    if not matrix_equal(matmul(s, q), b):
        raise AssertionError("B=S Q failed")
    if not matrix_equal(matmul(s, g), matscale(21, identity(44))):
        raise AssertionError("S G=21 I failed")
    if not matrix_equal(matmul(g, b), matscale(21, q)):
        raise AssertionError("G B=21 Q failed")
    if not matrix_equal(matmul(transpose(b), g), matmul(g, b)):
        raise AssertionError("B is not G-self-adjoint")
    if any(
        (b[i][j] - int(i == j)) % 2
        for i in range(44)
        for j in range(44)
    ):
        raise AssertionError("B is not congruent to I modulo two")

    n6 = matsub(b6, identity(6))
    if not matrix_equal(
        matmul(n6, matsub(n6, matscale(8, identity(6)))),
        [[0] * 6 for _ in range(6)],
    ):
        raise AssertionError("local spectral polynomial failed")
    if rank_exact(n6) != 1:
        raise AssertionError("local eigenvalue-nine multiplicity changed")
    n = matsub(b, identity(44))
    if not matrix_equal(
        matmul(n, matsub(n, matscale(8, identity(44)))),
        [[0] * 44 for _ in range(44)],
    ):
        raise AssertionError("global spectral polynomial failed")
    if rank_exact(n) != 2:
        raise AssertionError("global eigenvalue-nine multiplicity changed")
    if not matrix_equal(matmul(c, c), matscale(4, c)):
        raise AssertionError("C^2=4C failed")

    e8_roots = enumerate_vectors_at_most(e8, 2)
    e6_roots = enumerate_vectors_at_most(e6, 2)
    h8_roots = enumerate_vectors_at_most(h8, 2)
    q6_roots = enumerate_vectors_at_most(q6, 2)
    for name, form, vectors, expected in (
        ("E8", e8, e8_roots, 240),
        ("E6", e6, e6_roots, 72),
        ("E8_inverse", h8, h8_roots, 240),
        ("Q6", q6, q6_roots, 72),
    ):
        if len(vectors) != expected:
            raise AssertionError(f"{name} root count {len(vectors)}")
        if {qform(form, vector) for vector in vectors} != {Fraction(2)}:
            raise AssertionError(f"{name} enumeration contains non-roots")

    e8_components = component_sizes(e8, e8_roots)
    e6_components = component_sizes(e6, e6_roots)
    h8_components = component_sizes(h8, h8_roots)
    q6_components = component_sizes(q6, q6_roots)
    if (
        e8_components != [240]
        or e6_components != [72]
        or h8_components != [240]
        or q6_components != [72]
    ):
        raise AssertionError("a unique-block root graph is disconnected")

    h6_min = minimum_certificate(h6, Fraction(4, 3))
    g6_min = minimum_certificate(g6, 28)
    g8_min = minimum_certificate(g8, 42)
    if h6_min["minimum"] != "4/3" or h6_min["minimal_vector_count"] != 54:
        raise AssertionError("E6 dual minimum certificate changed")
    if g6_min["minimum"] != "28/1" or g6_min["minimal_vector_count"] != 54:
        raise AssertionError("G6 minimum certificate changed")
    if g8_min["minimum"] != "42/1" or g8_min["minimal_vector_count"] != 240:
        raise AssertionError("G8 minimum certificate changed")

    s_components = sorted([240] * 4 + [72] * 2, reverse=True)
    q_components = sorted([240] * 4 + [72] * 2, reverse=True)
    if 6 in s_components or 6 in q_components:
        raise AssertionError("unexpected six-root component")

    determinant_s = int(determinant(s))
    determinant_q = int(determinant(q))
    determinant_g = int(determinant(g))
    determinant_b = int(determinant(b))
    mod_ranks = {
        "S_mod_3": rank_mod_prime(s, 3),
        "Q_mod_3": rank_mod_prime(q, 3),
        "G_mod_3": rank_mod_prime(g, 3),
        "G_mod_7": rank_mod_prime(g, 7),
    }
    if (determinant_s, determinant_q, determinant_b) != (9, 9, 81):
        raise AssertionError("endpoint determinants changed")
    if determinant_g != 21 ** 44 // 9:
        raise AssertionError("G determinant changed")
    if mod_ranks != {
        "S_mod_3": 42,
        "Q_mod_3": 42,
        "G_mod_3": 2,
        "G_mod_7": 0,
    }:
        raise AssertionError("modular ranks changed")

    smith = {
        "S": [1] * 42 + [3, 3],
        "Q": [1] * 42 + [3, 3],
        "G": [7, 7] + [21] * 42,
    }
    determinants = {"S": determinant_s, "Q": determinant_q, "G": determinant_g}
    for name, factors in smith.items():
        product = 1
        for factor in factors:
            product *= factor
        if product != determinants[name]:
            raise AssertionError(f"{name} Smith product mismatch")
        if any(b_factor % a_factor for a_factor, b_factor in zip(factors, factors[1:])):
            raise AssertionError(f"{name} Smith ordering mismatch")

    summaries = {
        name: matrix_summary(built[name], name in ("S", "Q", "G"))
        for name in ("S", "Q", "G", "B", "C")
    }
    b_square = matmul(b, b)
    c_square = matmul(c, c)
    summaries["B"].update({
        "trace_square": int(trace(b_square)),
        "congruent_to_identity_mod_2": True,
        "euclidean_symmetric": matrix_equal(b, transpose(b)),
        "G_self_adjoint": True,
        "spectrum": {"1": 42, "9": 2},
        "spectral_certificate": "(B-I)(B-9I)=0 and rank(B-I)=2",
    })
    summaries["C"].update({
        "trace_square": int(trace(c_square)),
        "square_equals_four_times_self": True,
    })
    if (
        summaries["B"]["trace"],
        summaries["B"]["trace_square"],
        summaries["C"]["rank"],
        summaries["C"]["trace"],
        summaries["C"]["trace_square"],
    ) != (60, 204, 2, 8, 32):
        raise AssertionError("endpoint moments changed")

    root_certificates = {
        "unique_blocks": {
            "S_E8": {
                "minimum": 2,
                "root_count": len(e8_roots),
                "root_vectors": [list(vector) for vector in e8_roots],
                "root_vectors_sha256": canonical_sha256(e8_roots),
                "component_sizes": e8_components,
            },
            "S_E6": {
                "minimum": 2,
                "root_count": len(e6_roots),
                "root_vectors": [list(vector) for vector in e6_roots],
                "root_vectors_sha256": canonical_sha256(e6_roots),
                "component_sizes": e6_components,
            },
            "Q_E8_inverse": {
                "minimum": 2,
                "root_count": len(h8_roots),
                "root_vectors": [list(vector) for vector in h8_roots],
                "root_vectors_sha256": canonical_sha256(h8_roots),
                "component_sizes": h8_components,
            },
            "Q_Q6": {
                "minimum": 2,
                "root_count": len(q6_roots),
                "root_vectors": [list(vector) for vector in q6_roots],
                "root_vectors_sha256": canonical_sha256(q6_roots),
                "component_sizes": q6_components,
            },
            "E6_dual": h6_min,
            "G_E6": g6_min,
            "G_E8": g8_min,
        },
        "full_forms": {
            "S": {
                "minimum": 2,
                "root_count": 4 * len(e8_roots) + 2 * len(e6_roots),
                "component_sizes": s_components,
                "has_orthogonal_A2_direct_summand": False,
            },
            "Q": {
                "minimum": 2,
                "root_count": 4 * len(h8_roots) + 2 * len(q6_roots),
                "component_sizes": q_components,
                "has_orthogonal_A2_direct_summand": False,
            },
            "G": {
                "minimum": 28,
                "minimal_vector_count": 2 * 54,
                "root_count": 0,
                "component_sizes": [],
                "has_orthogonal_A2_direct_summand": False,
            },
        },
        "direct_sum_completeness": (
            "Each block is even positive definite with minimum two (or, for "
            "G, at least 28). Thus a full norm-two vector has one root block "
            "and zero in every other block; cross-block root edges vanish."
        ),
        "A2_summand_obstruction": (
            "In an even orthogonal decomposition A2 plus R, every norm-two "
            "vector lies in one summand, so the six connected A2 roots form "
            "a whole six-vertex nonorthogonality component. No such component "
            "occurs here."
        ),
        "embedded_A2_control": {
            "present": True,
            "E6_simple_root_indices": [0, 1],
            "Gram": [[2, -1], [-1, 2]],
            "meaning": "embedded root subsystem, not orthogonal direct summand",
        },
    }

    discriminants = {
        "S": {
            "determinant": determinant_s,
            "rank_mod_3": mod_ranks["S_mod_3"],
            "v3_determinant": prime_valuation(determinant_s, 3),
            "smith_invariants": smith["S"],
            "group": "(Z/3Z)^2",
        },
        "Q": {
            "determinant": determinant_q,
            "rank_mod_3": mod_ranks["Q_mod_3"],
            "v3_determinant": prime_valuation(determinant_q, 3),
            "smith_invariants": smith["Q"],
            "group": "(Z/3Z)^2",
        },
        "G": {
            "determinant": determinant_g,
            "rank_mod_3": mod_ranks["G_mod_3"],
            "rank_mod_7": mod_ranks["G_mod_7"],
            "v3_determinant": prime_valuation(determinant_g, 3),
            "v7_determinant": prime_valuation(determinant_g, 7),
            "smith_invariants": smith["G"],
            "group": "(Z/7Z)^2 direct_sum (Z/21Z)^42",
        },
        "certificate_logic": (
            "For each relevant prime, nullity modulo p counts Smith factors "
            "divisible by p. It equals the determinant p-valuation here, so "
            "each such factor contains exactly one p. The determinant has no "
            "other primes, and Smith divisibility ordering fixes the pairing."
        ),
    }

    submitted = json.loads(
        (ROOT / "attempts/wave27-a2free-construction/exact-results.json")
        .read_text(encoding="utf-8")
    )
    submitted_matrices = submitted["construction"]["matrices"]
    comparison = {
        name: submitted_matrices[name] == built[name]
        for name in ("S", "Q", "G", "B", "C")
    }
    comparison["E6"] = submitted["construction"]["blocks"]["E6"] == e6
    comparison["E8"] = submitted["construction"]["blocks"]["E8"] == e8
    comparison["Q6"] = submitted["construction"]["blocks"]["Q6"] == q6
    comparison["B6"] = submitted["construction"]["blocks"]["B6"] == b6
    if not all(comparison.values()):
        raise AssertionError("submitted matrices differ from independent rebuild")

    return {
        "schema_version": 1,
        "status": {
            "verdict": "PASS_SCOPED_CANDIDATE",
            "claim_label": "VERIFIED",
            "verified_object_label": "CANDIDATE",
            "abstract_coupled_package": "VERIFIED_AS_EXPLICIT_OBJECT",
            "projector_or_schur_origin": "NOT_ESTABLISHED",
            "n3_708": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "frozen_discovery": {
            "public_base_commit": PUBLIC_BASE_COMMIT,
            "sha256": actual_hashes,
        },
        "scope": {
            "verified": [
                "The displayed E8^4 orthogonal-sum E6^2 form is even, "
                "positive definite, rank 44, determinant nine, and has no "
                "orthogonal A2 direct summand.",
                "The independently rebuilt S,Q,G,B,C satisfy the stated "
                "abstract h=9, n3=708 arithmetic/lattice identities.",
                "The E6 dual and G minima, root data, and discriminant groups "
                "are exact.",
            ],
            "not_verified_or_claimed": [
                "No primitive embedding into Z^231.",
                "No 231-row projector frame.",
                "No Schur-square or cubic-tensor origin.",
                "No classification of determinant-nine forms.",
                "No graph or strongly regular graph realization.",
            ],
        },
        "construction": built,
        "matrix_invariants": summaries,
        "coupled_identities": {
            "B_equals_SQ": True,
            "SG_equals_21I": True,
            "GB_equals_21Q": True,
            "B_transpose_G_equals_GB": True,
            "B_congruent_I_mod_2": True,
            "C_equals_B_minus_I_over_2": True,
            "C_square_equals_4C": True,
        },
        "root_and_minimum_certificates": root_certificates,
        "discriminant_groups": discriminants,
        "submitted_matrix_comparison": comparison,
        "defects": [],
        "conclusion": {
            "naive_all_h9_forms_have_A2_summand":
                "REFUTED_BY_THIS_EXPLICIT_FORM",
            "abstract_h9_arithmetic_lattice_relaxation": "HAS_THIS_SURVIVOR",
            "full_projector_schur_realizability": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "conway_99": "UNKNOWN",
        },
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("ascii")
    path.write_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE / "independent-results.json",
    )
    arguments = parser.parse_args()
    results = independent_results()
    write_json(arguments.output, results)
    print(json.dumps({
        "verdict": results["status"]["verdict"],
        "matrix_hashes": {
            name: row["sha256_canonical_json"]
            for name, row in results["matrix_invariants"].items()
        },
        "S_root_components": results["root_and_minimum_certificates"][
            "full_forms"
        ]["S"]["component_sizes"],
        "output": str(arguments.output),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
