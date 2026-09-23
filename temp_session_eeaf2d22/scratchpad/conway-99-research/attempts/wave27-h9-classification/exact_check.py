#!/usr/bin/env python3
"""Exact checks for the Wave 27 determinant-nine A2-free survivor.

This module uses only Python's standard library.  It constructs an
E8^4 + E6^2 scaled-dual form and a coupled even form Q, verifies all
coordinate-lattice/endomorphism identities inherited at n3=708, and
certifies the exact local E6 trace minimum used in the report.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_BASE_COMMIT = "2ac11809fafee7ab752965ae49a96e922859b5ee"

INPUTS = {
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave24-n3-708-index/2026-07-23T204222Z-audit.md":
        "958b9b2d13d697c281ba490d21b170f453d059bfaa952f8e92a9709b6c8d3cd8",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md":
        "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
    "verification/wave26-a2-frame-obstruction/2026-07-23T225015Z-audit.md":
        "5ec6b1924fb9ca2ab9295808178684751b6a90e43315d00cbf232ba8d9fe84a3",
    "verification/wave26-a2-cubic-obstruction/2026-07-23T231001Z-audit.md":
        "883f48e70336b87955f5c2a115ac8b137169310c6f5ef91fe4581cb1b6c10465",
}

Matrix = list[list[int | Fraction]]


E8: list[list[int]] = [
    [2, -1, 0, 0, 0, 0, 0, 0],
    [-1, 2, -1, 0, 0, 0, 0, 0],
    [0, -1, 2, -1, 0, 0, 0, -1],
    [0, 0, -1, 2, -1, 0, 0, 0],
    [0, 0, 0, -1, 2, -1, 0, 0],
    [0, 0, 0, 0, -1, 2, -1, 0],
    [0, 0, 0, 0, 0, -1, 2, 0],
    [0, 0, -1, 0, 0, 0, 0, 2],
]

E6: list[list[int]] = [
    [2, -1, 0, 0, 0, 0],
    [-1, 2, -1, 0, 0, 0],
    [0, -1, 2, -1, 0, -1],
    [0, 0, -1, 2, -1, 0],
    [0, 0, 0, -1, 2, 0],
    [0, 0, -1, 0, 0, 2],
]

A2: list[list[int]] = [[2, -1], [-1, 2]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_inputs() -> dict[str, dict[str, str | bool]]:
    result: dict[str, dict[str, str | bool]] = {}
    for relative, expected in INPUTS.items():
        actual = sha256(ROOT / relative)
        result[relative] = {
            "expected": expected,
            "actual": actual,
            "matches": actual == expected,
        }
        if actual != expected:
            raise AssertionError(f"frozen input changed: {relative}")
    return result


def identity(n: int) -> list[list[int]]:
    return [[int(i == j) for j in range(n)] for i in range(n)]


def transpose(a: Sequence[Sequence[int | Fraction]]) -> Matrix:
    return [list(row) for row in zip(*a)]


def matmul(
    a: Sequence[Sequence[int | Fraction]],
    b: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    columns = list(zip(*b))
    return [
        [sum(Fraction(x) * Fraction(y) for x, y in zip(row, col))
         for col in columns]
        for row in a
    ]


def matscale(
    scalar: int | Fraction,
    a: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return [[Fraction(scalar) * Fraction(x) for x in row] for row in a]


def matadd(
    a: Sequence[Sequence[int | Fraction]],
    b: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return [
        [Fraction(x) + Fraction(y) for x, y in zip(left, right)]
        for left, right in zip(a, b)
    ]


def matsub(
    a: Sequence[Sequence[int | Fraction]],
    b: Sequence[Sequence[int | Fraction]],
) -> Matrix:
    return [
        [Fraction(x) - Fraction(y) for x, y in zip(left, right)]
        for left, right in zip(a, b)
    ]


def trace(a: Sequence[Sequence[int | Fraction]]) -> Fraction:
    return sum((Fraction(a[i][i]) for i in range(len(a))), Fraction(0))


def trace_product(
    a: Sequence[Sequence[int | Fraction]],
    b: Sequence[Sequence[int | Fraction]],
) -> Fraction:
    return sum(
        (
            Fraction(a[i][j]) * Fraction(b[j][i])
            for i in range(len(a))
            for j in range(len(a))
        ),
        Fraction(0),
    )


def determinant(a: Sequence[Sequence[int | Fraction]]) -> Fraction:
    work = [[Fraction(x) for x in row] for row in a]
    n = len(work)
    result = Fraction(1)
    for col in range(n):
        pivot = next(
            (row for row in range(col, n) if work[row][col]),
            None,
        )
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            result = -result
        pivot_value = work[col][col]
        result *= pivot_value
        work[col] = [x / pivot_value for x in work[col]]
        for row in range(col + 1, n):
            factor = work[row][col]
            if factor:
                work[row] = [
                    x - factor * y
                    for x, y in zip(work[row], work[col])
                ]
    return result


def inverse(a: Sequence[Sequence[int | Fraction]]) -> Matrix:
    n = len(a)
    work = [
        [Fraction(x) for x in row]
        + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(a)
    ]
    for col in range(n):
        pivot = next(
            (row for row in range(col, n) if work[row][col]),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
        pivot_value = work[col][col]
        work[col] = [x / pivot_value for x in work[col]]
        for row in range(n):
            if row == col:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [
                    x - factor * y
                    for x, y in zip(work[row], work[col])
                ]
    return [row[n:] for row in work]


def rank(a: Sequence[Sequence[int | Fraction]]) -> int:
    work = [[Fraction(x) for x in row] for row in a]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    result = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(result, rows) if work[row][col]),
            None,
        )
        if pivot is None:
            continue
        work[result], work[pivot] = work[pivot], work[result]
        pivot_value = work[result][col]
        work[result] = [x / pivot_value for x in work[result]]
        for row in range(rows):
            if row == result:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [
                    x - factor * y
                    for x, y in zip(work[row], work[result])
                ]
        result += 1
        if result == rows:
            break
    return result


def block_diagonal(
    blocks: Iterable[Sequence[Sequence[int | Fraction]]],
) -> Matrix:
    materialized = list(blocks)
    n = sum(len(block) for block in materialized)
    out: Matrix = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    offset = 0
    for block in materialized:
        size = len(block)
        for i in range(size):
            for j in range(size):
                out[offset + i][offset + j] = Fraction(block[i][j])
        offset += size
    return out


def is_integral(a: Sequence[Sequence[int | Fraction]]) -> bool:
    return all(Fraction(x).denominator == 1 for row in a for x in row)


def as_integer(a: Sequence[Sequence[int | Fraction]]) -> list[list[int]]:
    if not is_integral(a):
        raise AssertionError("matrix is not integral")
    return [[int(Fraction(x)) for x in row] for row in a]


def is_symmetric(a: Sequence[Sequence[int | Fraction]]) -> bool:
    return [list(row) for row in a] == transpose(a)


def is_even_integral_form(
    a: Sequence[Sequence[int | Fraction]],
) -> bool:
    return (
        is_integral(a)
        and is_symmetric(a)
        and all(int(Fraction(a[i][i])) % 2 == 0 for i in range(len(a)))
    )


def positive_definite(a: Sequence[Sequence[int | Fraction]]) -> bool:
    return all(
        determinant([list(row[:size]) for row in a[:size]]) > 0
        for size in range(1, len(a) + 1)
    )


def quadratic(
    vector: Sequence[int | Fraction],
    gram: Sequence[Sequence[int | Fraction]],
) -> Fraction:
    return sum(
        (
            Fraction(vector[i])
            * Fraction(gram[i][j])
            * Fraction(vector[j])
            for i in range(len(vector))
            for j in range(len(vector))
        ),
        Fraction(0),
    )


def matrix_digest(a: Sequence[Sequence[int | Fraction]]) -> str:
    encoded = [
        [
            (
                str(Fraction(x).numerator)
                if Fraction(x).denominator == 1
                else f"{Fraction(x).numerator}/{Fraction(x).denominator}"
            )
            for x in row
        ]
        for row in a
    ]
    payload = json.dumps(
        encoded,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def congruent_identity_mod_two(
    a: Sequence[Sequence[int | Fraction]],
) -> bool:
    if not is_integral(a):
        return False
    return all(
        (int(Fraction(a[i][j])) - int(i == j)) % 2 == 0
        for i in range(len(a))
        for j in range(len(a))
    )


def rank_mod_prime(a: Sequence[Sequence[int]], prime: int) -> int:
    work = [[x % prime for x in row] for row in a]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    result = 0
    for col in range(cols):
        pivot = next(
            (row for row in range(result, rows) if work[row][col]),
            None,
        )
        if pivot is None:
            continue
        work[result], work[pivot] = work[pivot], work[result]
        scale = pow(work[result][col], -1, prime)
        work[result] = [(scale * x) % prime for x in work[result]]
        for row in range(rows):
            if row == result:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [
                    (x - factor * y) % prime
                    for x, y in zip(work[row], work[result])
                ]
        result += 1
    return result


def simple_root_orbit(cartan: Sequence[Sequence[int]]) -> set[tuple[int, ...]]:
    """Enumerate the Weyl orbit generated by simple reflections."""
    n = len(cartan)
    roots: set[tuple[int, ...]] = set()
    queue: list[tuple[int, ...]] = []
    for i in range(n):
        for sign in (-1, 1):
            root = tuple(sign * int(i == j) for j in range(n))
            if root not in roots:
                roots.add(root)
                queue.append(root)
    cursor = 0
    while cursor < len(queue):
        root = queue[cursor]
        cursor += 1
        pairings = [
            sum(cartan[i][j] * root[j] for j in range(n))
            for i in range(n)
        ]
        for i, pairing in enumerate(pairings):
            reflected = list(root)
            reflected[i] -= pairing
            candidate = tuple(reflected)
            if candidate not in roots:
                if quadratic(candidate, cartan) != 2:
                    raise AssertionError("simple reflection changed root norm")
                roots.add(candidate)
                queue.append(candidate)
    return roots


def e6_dual_minimum() -> dict[str, object]:
    h = inverse(E6)
    four_i_minus_e6 = matsub(matscale(4, identity(6)), E6)
    if not positive_definite(four_i_minus_e6):
        raise AssertionError("lambda_max(E6)<4 certificate failed")

    candidates: list[tuple[Fraction, tuple[int, ...]]] = []
    for vector in itertools.product(range(-2, 3), repeat=6):
        euclidean_square = sum(x * x for x in vector)
        if not vector or euclidean_square == 0 or euclidean_square > 5:
            continue
        candidates.append((quadratic(vector, h), vector))
    minimum, witness = min(candidates)
    if minimum != Fraction(4, 3):
        raise AssertionError("E6 dual minimum changed")
    return {
        "minimum": "4/3",
        "witness": list(witness),
        "vectors_checked": len(candidates),
        "completion_argument":
            "4I-E6 is positive definite, so any vector below 4/3 has "
            "Euclidean square below 16/3 and is in the enumerated set",
    }


def discriminant_module_check() -> dict[str, object]:
    h6 = inverse(E6)
    h2 = inverse(A2)
    if determinant(E6) != 3 or rank_mod_prime(E6, 3) != 5:
        raise AssertionError("E6 discriminant group is not cyclic of order 3")
    if determinant(A2) != 3 or rank_mod_prime(A2, 3) != 1:
        raise AssertionError("A2 discriminant group is not cyclic of order 3")
    if h6[0][0] != Fraction(4, 3):
        raise AssertionError("chosen E6 discriminant generator changed")
    if h2[0][0] != Fraction(2, 3):
        raise AssertionError("chosen A2 discriminant generator changed")

    # Over F_3, P has determinant one.  Before reduction modulo 3,
    # (2/3)||Px||^2 = (4/3)||x||^2 exactly.
    p = [[1, 1], [1, -1]]
    if round(determinant(p)) % 3 != 1:
        raise AssertionError("discriminant isometry is singular modulo 3")
    for x in itertools.product(range(3), repeat=2):
        y = [
            sum(p[i][j] * x[j] for j in range(2))
            for i in range(2)
        ]
        source = Fraction(4, 3) * sum(t * t for t in x)
        target = Fraction(2, 3) * sum(t * t for t in y)
        if source != target:
            raise AssertionError("discriminant quadratic values changed")
    return {
        "group": "(Z/3Z)^2",
        "E6_squared_diagonal_values": ["4/3", "4/3"],
        "A2_squared_diagonal_values": ["2/3", "2/3"],
        "isometry_mod_3": p,
        "conclusion":
            "the two rank-44 forms have isometric discriminant modules",
    }


def local_e6_package() -> dict[str, Matrix | list[int] | Fraction]:
    h = inverse(E6)
    v = [Fraction(-1), 0, 1, 0, 0, -1]
    v_h = [
        sum(v[i] * Fraction(h[i][j]) for i in range(6))
        for j in range(6)
    ]
    denominator = sum(v_h[i] * v[i] for i in range(6))
    if denominator != Fraction(4, 3):
        raise AssertionError("projector vector norm changed")
    projector = [
        [v[i] * v_h[j] / denominator for j in range(6)]
        for i in range(6)
    ]
    b = matadd(identity(6), matscale(8, projector))
    q = matmul(h, b)
    c = matscale(Fraction(1, 2), matsub(b, identity(6)))
    g = matscale(21, h)
    return {
        "H": h,
        "v": v,
        "vH": v_h,
        "projector_denominator": denominator,
        "P": projector,
        "B": b,
        "C": c,
        "Q": q,
        "G": g,
    }


def verify_local_e6_package() -> dict[str, object]:
    package = local_e6_package()
    h = package["H"]
    p = package["P"]
    b = package["B"]
    c = package["C"]
    q = package["Q"]
    g = package["G"]
    assert isinstance(h, list)
    assert isinstance(p, list)
    assert isinstance(b, list)
    assert isinstance(c, list)
    assert isinstance(q, list)
    assert isinstance(g, list)

    if matmul(p, p) != p or trace(p) != 1:
        raise AssertionError("rank-one projector identity failed")
    if rank(p) != 1:
        raise AssertionError("projector rank changed")
    if not is_integral(b) or not congruent_identity_mod_two(b):
        raise AssertionError("B6 integrality/parity failed")
    if not is_even_integral_form(q) or not positive_definite(q):
        raise AssertionError("Q6 form checks failed")
    if not is_even_integral_form(g) or not positive_definite(g):
        raise AssertionError("G6 form checks failed")
    if matmul(E6, q) != b:
        raise AssertionError("E6*Q6=B6 failed")
    if matmul(g, b) != matscale(21, q):
        raise AssertionError("G6*B6=21Q6 failed")
    if matmul(E6, g) != matscale(21, identity(6)):
        raise AssertionError("E6*G6=21I failed")
    if matmul(matsub(b, identity(6)), matsub(b, matscale(9, identity(6)))) != [
        [Fraction(0) for _ in range(6)] for _ in range(6)
    ]:
        raise AssertionError("B6 spectral polynomial failed")
    if (
        determinant(E6) != 3
        or determinant(q) != 3
        or determinant(b) != 9
        or trace(b) != 14
        or trace(c) != 4
        or trace(matmul(c, c)) != 16
    ):
        raise AssertionError("local determinant/trace data changed")

    return {
        "v": [int(x) for x in package["v"]],
        "v_H_norm": "4/3",
        "P_rank": 1,
        "P_squared_equals_P": True,
        "B": as_integer(b),
        "Q": as_integer(q),
        "det_B": int(determinant(b)),
        "det_Q": int(determinant(q)),
        "trace_B": int(trace(b)),
        "trace_C": int(trace(c)),
        "trace_C_squared": int(trace(matmul(c, c))),
        "B_minimal_polynomial_divides": "(t-1)(t-9)",
        "B_spectrum": ["9", "1", "1", "1", "1", "1"],
        "Q_even_integral_positive_definite": True,
        "B_integral_and_identity_mod_two": True,
    }


def local_trace_floor_certificate() -> dict[str, object]:
    """Return the exact scalar certificate behind min tr(E6 Q)=14."""
    # If T <= 8, AM-GM gives det(B) <= (8/6)^6 = 4096/729 < 9,
    # contradicting det(B)=3 det(Q) >= 9.
    if not 4096 < 9 * 729:
        raise AssertionError("AM-GM integer comparison failed")

    # At T=10, after the trace-square-two idempotent case is excluded,
    # tr(B^2)>=30.  The KKT boundary candidates for six positive
    # eigenvalues with sum 10 and square sum 30 have k=1,2,3 large roots.
    # Their products are respectively 5,
    # (4625-1000sqrt(10))/729, and 125/729.
    # The middle term is <5 already from sqrt(10)>1.
    if not 4625 - 1000 < 5 * 729:
        raise AssertionError("k=2 radical comparison failed")
    if not 125 < 5 * 729:
        raise AssertionError("k=3 rational comparison failed")

    return {
        "congruence": "T=tr(E6 Q) is 2 mod 4",
        "determinant_floor": "det(E6 Q)=3 det(Q)>=9",
        "AM_GM": {
            "T_at_most_8_upper_numerator": 4096,
            "denominator": 729,
            "strictly_below_9": True,
        },
        "trace_10_gate": {
            "C_trace": 2,
            "C_trace_square_floor_before_idempotent_obstruction": 2,
            "rank_four_even_unimodular_kernel_if_equality": "impossible",
            "C_trace_square_after_obstruction": 4,
            "B_trace_square_floor": 30,
            "KKT_boundary_products": {
                "k=1": "5",
                "k=2": "(4625-1000*sqrt(10))/729 < 5",
                "k=3": "125/729 < 5",
            },
            "det_B_upper": 5,
            "contradicts_det_B_at_least_9": True,
        },
        "unrestricted_minimum": 14,
        "attained_by_explicit_Q6": True,
    }


def full_package() -> dict[str, Matrix]:
    e8_inverse = inverse(E8)
    local = local_e6_package()
    q6 = local["Q"]
    assert isinstance(q6, list)
    s = block_diagonal([E8] * 4 + [E6] * 2)
    q = block_diagonal([e8_inverse] * 4 + [q6] * 2)
    h = inverse(s)
    g = matscale(21, h)
    b = matmul(s, q)
    c = matscale(Fraction(1, 2), matsub(b, identity(44)))
    return {"S": s, "Q": q, "H": h, "G": g, "B": b, "C": c}


def verify_full_package() -> dict[str, object]:
    package = full_package()
    s, q, h, g, b, c = (
        package["S"],
        package["Q"],
        package["H"],
        package["G"],
        package["B"],
        package["C"],
    )
    for name, matrix in (("S", s), ("Q", q), ("G", g)):
        if not is_even_integral_form(matrix) or not positive_definite(matrix):
            raise AssertionError(f"{name} form checks failed")
    if not is_integral(b) or not congruent_identity_mod_two(b):
        raise AssertionError("B form checks failed")
    if matmul(s, h) != identity(44):
        raise AssertionError("H=S^-1 failed")
    if matmul(s, g) != matscale(21, identity(44)):
        raise AssertionError("SG=21I failed")
    if matmul(s, q) != b:
        raise AssertionError("SQ=B failed")
    if matmul(g, b) != matscale(21, q):
        raise AssertionError("GB=21Q failed")
    if (
        determinant(s) != 9
        or determinant(q) != 9
        or determinant(b) != 81
        or determinant(g) != Fraction(21**44, 9)
    ):
        raise AssertionError("full determinant data changed")
    if (
        trace(b) != 60
        or trace(c) != 8
        or trace(matmul(c, c)) != 32
        or rank(c) != 2
    ):
        raise AssertionError("full trace/rank data changed")
    if rank_mod_prime(as_integer(s), 3) != 42:
        raise AssertionError("S discriminant rank changed")
    if not is_even_integral_form(matscale(3, h)):
        raise AssertionError("3-elementary scaled dual check failed")

    h8 = inverse(E8)
    if not is_even_integral_form(h8) or min(
        int(h8[i][i]) for i in range(8)
    ) != 2:
        raise AssertionError("E8 dual minimum witness failed")
    e6_minimum = e6_dual_minimum()

    return {
        "rank": 44,
        "decomposition": "E8^4 orthogonal_sum E6^2",
        "det_S": int(determinant(s)),
        "det_Q": int(determinant(q)),
        "det_B": int(determinant(b)),
        "det_G": f"21^44/9",
        "trace_B": int(trace(b)),
        "trace_C": int(trace(c)),
        "trace_C_squared": int(trace(matmul(c, c))),
        "rank_C": rank(c),
        "S_Q_G_even_integral_positive_definite": True,
        "B_integral_positive_and_identity_mod_two": True,
        "SG_equals_21I": True,
        "SQ_equals_B": True,
        "GB_equals_21Q": True,
        "S_minimum": 2,
        "E8_dual_minimum": 2,
        "E6_dual_minimum": e6_minimum,
        "G_minimum": 28,
        "rank_mod_3_S": rank_mod_prime(as_integer(s), 3),
        "discriminant_group": "(Z/3Z)^2",
        "matrix_sha256": {
            name: matrix_digest(matrix)
            for name, matrix in package.items()
        },
    }


def root_component_check() -> dict[str, object]:
    a2_roots = simple_root_orbit(A2)
    e6_roots = simple_root_orbit(E6)
    e8_roots = simple_root_orbit(E8)
    if (len(a2_roots), len(e6_roots), len(e8_roots)) != (6, 72, 240):
        raise AssertionError("root orbit counts changed")
    return {
        "root_counts": {"A2": 6, "E6": 72, "E8": 240},
        "candidate_root_components": ["E8", "E8", "E8", "E8", "E6", "E6"],
        "candidate_root_count": 4 * 240 + 2 * 72,
        "old_A2_survivor_root_components":
            ["E8", "E8", "E8", "E8", "E8", "A2", "A2"],
        "old_A2_survivor_root_count": 5 * 240 + 2 * 6,
        "orthogonal_A2_summand": False,
        "reason":
            "each connected simple-root diagram spans its block; an "
            "orthogonal splitting must preserve these root components",
    }


def build_result() -> dict[str, object]:
    result = {
        "claim_label": "DERIVED",
        "public_base_commit": PUBLIC_BASE_COMMIT,
        "scope": (
            "A2-free exact survivor of the h=9 n3=708 "
            "coordinate-lattice and coupled S,Q,G,B identities only; "
            "no 231-row projector, Schur-square, or graph origin"
        ),
        "frozen_inputs": verify_inputs(),
        "discriminant_module": discriminant_module_check(),
        "roots": root_component_check(),
        "local_E6_trace_floor": local_trace_floor_certificate(),
        "local_E6_equality_package": verify_local_e6_package(),
        "full_rank_44_package": verify_full_package(),
        "conclusions": {
            "determinant_minimum_scaled_dual_force_A2": False,
            "coupled_S_Q_G_B_identities_force_A2": False,
            "all_h9_forms_classified": False,
            "projector_or_Schur_origin_constructed": False,
            "n3_708_excluded": False,
            "Conway_99_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_result()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
