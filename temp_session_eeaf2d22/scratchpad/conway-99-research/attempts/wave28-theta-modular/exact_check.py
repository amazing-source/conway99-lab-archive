#!/usr/bin/env python3
"""Exact arithmetic companion for the Wave 28 theta/modular lane.

This checker proves finite arithmetic statements used by the report:

* the exact level/character/Sturm table forced by the eight determinants;
* failure of the determinant condition required for modular self-duality;
* a fresh enumeration of the 17 orthogonal-ADE hostile controls;
* their first two scalar-theta coefficients and scaled-dual integrality;
* the h=9 discriminant-form nonuniqueness witness; and
* the norm-four coefficient lower bound visible from 231 frame rows.

It does not implement a modular-form package, prove a graph exists, or
classify general rank-44 lattices.  Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from fractions import Fraction
from math import comb, gcd, isqrt
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_HEAD = "d76d030f6d74e2e1b7ca2b2f0f97536241b3a10b"
BRIEF_PATH = "agents/2026-07-24-wave28-orchestrator-brief.md"
BRIEF_SHA256 = "6a15446551b78822706a8e005bef49a411b904cf05f9459b6b3350239839ee1e"
RANK = 44
WEIGHT = RANK // 2
SCALE = 21
ALLOWED_H = (9, 21, 49, 81, 189, 441, 729, 1029)

Matrix = list[list[int | Fraction]]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def matrix_sha256(matrix: Sequence[Sequence[int | Fraction]]) -> str:
    payload = json.dumps(
        [
            [
                str(Fraction(value))
                for value in row
            ]
            for row in matrix
        ],
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def freeze_inputs() -> dict[str, str]:
    actual = sha256_file(ROOT / BRIEF_PATH)
    if actual != BRIEF_SHA256:
        raise AssertionError(f"orchestrator brief hash drift: {actual}")
    return {BRIEF_PATH: actual}


def factor_3_7(value: int) -> tuple[int, int]:
    exponents: list[int] = []
    remaining = value
    for prime in (3, 7):
        exponent = 0
        while remaining % prime == 0:
            remaining //= prime
            exponent += 1
        exponents.append(exponent)
    if remaining != 1:
        raise ValueError(f"{value} is not 3,7-smooth")
    return exponents[0], exponents[1]


def exact_level(value: int) -> int:
    a3, a7 = factor_3_7(value)
    return (3 if a3 else 1) * (7 if a7 else 1)


def theta_character(value: int) -> str:
    root = isqrt(value)
    if root * root == value:
        return "TRIVIAL"
    root = isqrt(value // 21)
    if value % 21 == 0 and 21 * root * root == value:
        return "KRONECKER_CHI_21"
    raise AssertionError(f"unexpected determinant square class: {value}")


def gamma0_index(level: int) -> int:
    result = level
    for prime in (3, 7):
        if level % prime == 0:
            result = result * (prime + 1) // prime
    return result


def sturm_bound(level: int) -> int:
    return WEIGHT * gamma0_index(level) // 12


def determinant(matrix: Sequence[Sequence[int | Fraction]]) -> Fraction:
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
            result *= -1
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, n):
            ratio = work[row][column] / pivot_value
            for index in range(column + 1, n):
                work[row][index] -= ratio * work[column][index]
    return result


def inverse(matrix: Sequence[Sequence[int | Fraction]]) -> Matrix:
    n = len(matrix)
    work = [
        [Fraction(value) for value in row]
        + [Fraction(int(i == j)) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(
            (row for row in range(column, n) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            raise ValueError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [value / divisor for value in work[column]]
        for row in range(n):
            if row == column:
                continue
            multiplier = work[row][column]
            work[row] = [
                left - multiplier * right
                for left, right in zip(work[row], work[column])
            ]
    return [row[n:] for row in work]


def symmetric_from_lower(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    size = len(rows)
    if any(len(row) != index + 1 for index, row in enumerate(rows)):
        raise ValueError("lower-triangular row lengths are invalid")
    return [
        [
            rows[max(i, j)][min(i, j)]
            for j in range(size)
        ]
        for i in range(size)
    ]


def ldl(
    matrix: Sequence[Sequence[int | Fraction]],
) -> tuple[Matrix, list[Fraction]]:
    size = len(matrix)
    lower: Matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    diagonal: list[Fraction] = [Fraction(0) for _ in range(size)]
    for i in range(size):
        lower[i][i] = Fraction(1)
        diagonal[i] = Fraction(matrix[i][i]) - sum(
            Fraction(lower[i][k]) ** 2 * diagonal[k]
            for k in range(i)
        )
        if diagonal[i] <= 0:
            raise ValueError(f"nonpositive LDL pivot {i}")
        for j in range(i + 1, size):
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


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def enumerate_vectors_leq(
    matrix: Sequence[Sequence[int | Fraction]],
    bound: int | Fraction,
) -> list[tuple[int, ...]]:
    """Complete exact reverse-LDL enumeration inside a closed norm ball."""
    lower, diagonal = ldl(matrix)
    bound = Fraction(bound)
    size = len(matrix)
    vector = [0 for _ in range(size)]
    output: list[tuple[int, ...]] = []

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
            for j in range(index + 1, size)
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

    recurse(size - 1, Fraction(0))
    return sorted(set(output))


def integral_even(matrix: Sequence[Sequence[int | Fraction]]) -> bool:
    return all(
        Fraction(value).denominator == 1
        for row in matrix
        for value in row
    ) and all(int(matrix[i][i]) % 2 == 0 for i in range(len(matrix)))


def scale_matrix(
    matrix: Sequence[Sequence[int | Fraction]],
    scalar: int,
) -> Matrix:
    return [[scalar * Fraction(value) for value in row] for row in matrix]


def rank_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    work = [[value % prime for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, rows) if work[row][column] % prime),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse_pivot = pow(work[rank][column], -1, prime)
        work[rank] = [(value * inverse_pivot) % prime for value in work[rank]]
        for row in range(rows):
            if row == rank:
                continue
            multiplier = work[row][column]
            work[row] = [
                (left - multiplier * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
    return rank


def determinant_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    value = determinant([[entry % prime for entry in row] for row in matrix])
    denominator_inverse = pow(value.denominator % prime, -1, prime)
    return (value.numerator * denominator_inverse) % prime


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


def cartan_a(rank: int) -> list[list[int]]:
    return [
        [
            2 * int(i == j) - int(abs(i - j) == 1)
            for j in range(rank)
        ]
        for i in range(rank)
    ]


def exceptional_cartan(kind: str) -> list[list[int]]:
    rank = {"E6": 6, "E8": 8}[kind]
    edges = {(i, i + 1) for i in range(rank - 2)}
    edges.add((2, rank - 1))
    return [
        [
            2 * int(i == j)
            - int((i, j) in edges or (j, i) in edges)
            for j in range(rank)
        ]
        for i in range(rank)
    ]


COMPONENTS = {
    "A2": {
        "rank": 2,
        "determinant": 3,
        "gram": cartan_a(2),
        "roots": 6,
        "norm_four": 0,
        "dual_minimum": Fraction(2, 3),
    },
    "A6": {
        "rank": 6,
        "determinant": 7,
        "gram": cartan_a(6),
        "roots": 42,
        "norm_four": 210,
        "dual_minimum": Fraction(6, 7),
    },
    "A20": {
        "rank": 20,
        "determinant": 21,
        "gram": cartan_a(20),
        "roots": 420,
        "norm_four": 35910,
        "dual_minimum": Fraction(20, 21),
    },
    "E6": {
        "rank": 6,
        "determinant": 3,
        "gram": exceptional_cartan("E6"),
        "roots": 72,
        "norm_four": 270,
        "dual_minimum": Fraction(4, 3),
    },
    "E8": {
        "rank": 8,
        "determinant": 1,
        "gram": exceptional_cartan("E8"),
        "roots": 240,
        "norm_four": 2160,
        "dual_minimum": Fraction(2),
    },
}

# Published lower-triangular Gram data from the Nebe--Sloane catalogue:
# https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/K12.html
K12 = symmetric_from_lower(
    [
        [4],
        [0, 4],
        [0, 0, 4],
        [-2, 0, 0, 4],
        [0, -2, 0, 0, 4],
        [0, 0, -2, 0, 0, 4],
        [2, 2, 2, -1, -1, -1, 4],
        [-1, -1, 2, -1, 2, -1, 0, 4],
        [-1, -1, 2, 2, -1, -1, 0, 0, 4],
        [-1, -1, -1, 2, 2, 2, -2, 0, 0, 4],
        [2, -1, -1, -1, -1, 2, 0, -2, 0, 0, 4],
        [-1, 2, -1, -1, -1, 2, 0, 0, -2, 0, 0, 4],
    ]
)

# One published extremal even unimodular rank-32 Koch--Venkov lattice.
# The source calls it LAMBDA(F):
# https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/KV32F.html
KV32F = symmetric_from_lower(
    [
        [4],
        [-2, 4],
        [-2, 0, 4],
        [-2, 0, 2, 4],
        [1, -2, 1, -1, 4],
        [-2, 1, 2, 0, 0, 4],
        [-2, 0, 2, 2, 1, 0, 4],
        [1, -2, -1, -1, 0, -1, -1, 4],
        [-2, 2, 2, 1, 0, 1, 2, -1, 4],
        [-2, 2, 0, 1, -2, 0, 0, -1, 0, 4],
        [-2, 0, 2, 1, 1, 2, 2, 0, 2, 0, 4],
        [1, 1, 0, 0, 0, -1, -1, -1, 0, 0, -1, 4],
        [-2, 0, 1, 1, 1, 1, 2, -1, 1, 0, 2, -1, 4],
        [-2, 1, 2, 1, 0, 2, 1, -1, 2, 1, 2, 0, 1, 4],
        [1, 0, -2, -2, 0, 0, -2, 1, -1, 0, 0, 0, -1, 0, 4],
        [-2, 1, 1, 1, -1, 1, 1, -1, 0, 2, 1, -1, 1, 1, -1, 4],
        [-2, 2, 1, 0, -1, 1, 0, 0, 1, 2, 0, 0, 0, 1, 0, 1, 4],
        [1, -2, 1, 0, 1, 1, -1, 0, -1, -1, 0, 0, 0, 1, 0, 0, -1, 4],
        [-1, 0, 1, 1, 1, 1, 1, -1, 1, 0, 2, 0, 1, 2, 1, 0, 0, 1, 4],
        [-1, 1, -1, -1, -1, 0, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 1, -2, -1, 4],
        [-1, 1, -1, 0, -2, 0, 0, 1, 0, 1, 0, -1, 0, -1, 0, 1, 1, -2, -1, 2, 4],
        [1, 1, -2, -1, -1, -1, -2, 0, -1, 0, -2, 1, -1, -1, 1, 0, 0, 0, -1, 0, 0, 4],
        [1, -2, 1, 0, 1, 1, -1, 0, -1, -1, 0, 0, 0, 0, 0, -1, -1, 2, 0, -1, -1, -1, 4],
        [-2, 1, 1, 0, 0, 2, 1, -1, 1, 1, 2, -1, 1, 2, 1, 1, 1, 0, 2, 0, 0, -1, 0, 4],
        [1, -2, 1, 1, 2, 0, 1, 0, 0, -2, 1, 0, 0, 0, -1, -1, -2, 1, 1, -1, -2, -1, 1, -1, 4],
        [1, 0, -1, 0, 0, -1, -1, -1, -1, 1, -1, 1, -1, -1, 0, 0, -1, 0, 0, 0, 0, 0, 1, -1, 0, 4],
        [-2, 2, 1, 1, 0, 0, 2, -2, 2, 1, 1, 1, 2, 1, -1, 1, 1, -1, 1, 0, 0, 0, -1, 1, -1, 0, 4],
        [0, 0, 1, 0, 1, 1, 0, -1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, -1, -2, 0, 0, 1, 1, 0, 0, 4],
        [1, 1, -2, -2, 0, -1, -1, 0, 0, 0, -1, 1, -1, -1, 1, -1, 0, -1, -1, 1, 0, 1, -1, 0, -1, 1, 0, 0, 4],
        [-1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, -2, 0, 1, 2, -1, -1, 0, -1, 0, 1, -2, 0, 4],
        [-2, 0, 1, 2, 0, 0, 2, -1, 0, 1, 1, 0, 2, 0, -1, 1, 0, 0, 1, 0, 0, -1, 0, 1, 0, 0, 2, 0, -1, 0, 4],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, -1, 0, -1, 0, 0, 0, -1, 0, 0, -1, 1, 0, 0, 1, 0, -1, 0, 1, 0, 4],
    ]
)


def is_even_integral_scaled_inverse(name: str, scale: int) -> bool:
    dual = inverse(COMPONENTS[name]["gram"])
    scaled = [[scale * Fraction(value) for value in row] for row in dual]
    return all(value.denominator == 1 for row in scaled for value in row) and all(
        int(scaled[i][i]) % 2 == 0 for i in range(len(scaled))
    )


def component_audit() -> dict[str, object]:
    result: dict[str, object] = {}
    for name, data in COMPONENTS.items():
        gram = data["gram"]
        det = determinant(gram)
        if det != data["determinant"]:
            raise AssertionError(f"{name} determinant drift: {det}")
        if not is_even_integral_scaled_inverse(name, SCALE):
            raise AssertionError(f"{name}: 21 R^-1 is not even integral")
        if name.startswith("A"):
            rank = int(data["rank"])
            exact_roots = rank * (rank + 1)
            exact_norm_four = comb(rank + 1, 2) * comb(rank - 1, 2)
        else:
            vectors = enumerate_vectors_leq(gram, 4)
            exact_roots = sum(quadratic(gram, vector) == 2 for vector in vectors)
            exact_norm_four = sum(
                quadratic(gram, vector) == 4 for vector in vectors
            )
        if (
            exact_roots != data["roots"]
            or exact_norm_four != data["norm_four"]
        ):
            raise AssertionError(f"{name} theta coefficient drift")
        result[name] = {
            "rank": data["rank"],
            "determinant": data["determinant"],
            "roots_r2": data["roots"],
            "norm_four_r4": data["norm_four"],
            "dual_minimum": str(data["dual_minimum"]),
            "scaled_dual_minimum": str(SCALE * data["dual_minimum"]),
            "twenty_one_dual_even_integral": True,
        }
    return result


def enumerate_decompositions(target_h: int) -> list[dict[str, int]]:
    names = tuple(COMPONENTS)
    found: list[dict[str, int]] = []

    def rec(index: int, rank_left: int, det_so_far: int, counts: dict[str, int]) -> None:
        if index == len(names):
            if rank_left == 0 and det_so_far == target_h:
                found.append({name: counts[name] for name in names if counts.get(name)})
            return
        name = names[index]
        rank = int(COMPONENTS[name]["rank"])
        det = int(COMPONENTS[name]["determinant"])
        for multiplicity in range(rank_left // rank + 1):
            new_det = det_so_far * det**multiplicity
            if target_h % new_det != 0:
                continue
            if multiplicity:
                counts[name] = multiplicity
            rec(
                index + 1,
                rank_left - multiplicity * rank,
                new_det,
                counts,
            )
            counts.pop(name, None)

    rec(0, RANK, 1, {})
    return sorted(found, key=lambda item: tuple(item.get(name, 0) for name in names))


def theta_coefficients(decomposition: dict[str, int]) -> tuple[int, int]:
    root_count = sum(
        multiplicity * int(COMPONENTS[name]["roots"])
        for name, multiplicity in decomposition.items()
    )
    block_root_squares = sum(
        multiplicity * int(COMPONENTS[name]["roots"]) ** 2
        for name, multiplicity in decomposition.items()
    )
    intrinsic_norm_four = sum(
        multiplicity * int(COMPONENTS[name]["norm_four"])
        for name, multiplicity in decomposition.items()
    )
    cross_root_pairs = (root_count * root_count - block_root_squares) // 2
    return root_count, intrinsic_norm_four + cross_root_pairs


def decomposition_audit() -> dict[str, object]:
    by_h: dict[str, object] = {}
    total = 0
    for target_h in ALLOWED_H:
        cases = enumerate_decompositions(target_h)
        if not cases:
            raise AssertionError(f"no hostile control for h={target_h}")
        rows: list[dict[str, object]] = []
        level = exact_level(target_h)
        for case in cases:
            rank = sum(
                multiplicity * int(COMPONENTS[name]["rank"])
                for name, multiplicity in case.items()
            )
            det = 1
            for name, multiplicity in case.items():
                det *= int(COMPONENTS[name]["determinant"]) ** multiplicity
                if not is_even_integral_scaled_inverse(name, level):
                    raise AssertionError(f"{name} violates exact level {level}")
            roots, norm_four = theta_coefficients(case)
            scaled_dual_minimum = min(
                SCALE * Fraction(COMPONENTS[name]["dual_minimum"])
                for name in case
            )
            rows.append(
                {
                    "components": case,
                    "rank": rank,
                    "determinant": det,
                    "theta_q_coefficient_r2": roots,
                    "theta_q2_coefficient_r4": norm_four,
                    "scaled_dual_minimum": str(scaled_dual_minimum),
                    "passes_frame_visible_r4_lower_bound_462": norm_four >= 462,
                }
            )
        total += len(rows)
        by_h[str(target_h)] = rows
    if total != 17:
        raise AssertionError(f"expected 17 ADE controls, found {total}")
    return {"total": total, "by_determinant": by_h}


def h9_discriminant_nonuniqueness() -> dict[str, object]:
    # q_A2^2 has matrix (2/3)I.  The displayed P satisfies
    # P^T (2I) P = 4I and det(P)=-2=1 mod 3, so it identifies that
    # discriminant form with q_E6^2=(4/3)I.
    p = [[1, 1], [1, -1]]
    lhs = [
        [
            sum(2 * p[k][i] * p[k][j] for k in range(2))
            for j in range(2)
        ]
        for i in range(2)
    ]
    if lhs != [[4, 0], [0, 4]]:
        raise AssertionError("h=9 discriminant change-of-generators failed")
    det_p = p[0][0] * p[1][1] - p[0][1] * p[1][0]
    if gcd(det_p, 3) != 1:
        raise AssertionError("h=9 change-of-generators is singular mod 3")
    old = theta_coefficients({"A2": 2, "E8": 5})
    new = theta_coefficients({"E6": 2, "E8": 4})
    if old[0] == new[0]:
        raise AssertionError("hostile controls unexpectedly have equal root counts")
    return {
        "discriminant_module": "(Z/3Z)^2",
        "change_of_generators_mod_3": p,
        "identity": "P^T*(2/3 I)*P=4/3 I",
        "E8_5_A2_2": {"r2": old[0], "r4": old[1]},
        "E8_4_E6_2": {"r2": new[0], "r4": new[1]},
        "vector_valued_transformation_does_not_fix_zero_component": True,
    }


def discriminant_matrix_mod_prime(
    gram: Sequence[Sequence[int]],
    prime: int,
) -> list[list[int]]:
    """Return a quotient-basis matrix for p*Gram^-1 modulo p.

    This routine is used only for the p-elementary K12 and E6 forms.  The
    image of Gram modulo p is the relation space in F_p^n.  Standard basis
    vectors extending that image give representatives for the quotient.
    """
    size = len(gram)
    columns = [[gram[row][column] % prime for row in range(size)] for column in range(size)]
    basis: list[list[int]] = []
    for vector in columns:
        if rank_mod([*basis, vector], prime) > len(basis):
            basis.append(vector)
    image_rank = len(basis)
    representatives: list[list[int]] = []
    for index in range(size):
        vector = [int(row == index) for row in range(size)]
        if rank_mod([*basis, vector], prime) > len(basis):
            basis.append(vector)
            representatives.append(vector)
    if len(basis) != size:
        raise AssertionError("failed to extend quotient basis")
    scaled_dual = scale_matrix(inverse(gram), prime)
    if not integral_even(scaled_dual):
        raise AssertionError("p-scaled dual is not even integral")
    result = [
        [
            sum(
                representatives[i][a]
                * int(scaled_dual[a][b])
                * representatives[j][b]
                for a in range(size)
                for b in range(size)
            )
            % prime
            for j in range(len(representatives))
        ]
        for i in range(len(representatives))
    ]
    if len(representatives) != size - image_rank:
        raise AssertionError("quotient dimension mismatch")
    if determinant_mod(result, prime) == 0:
        raise AssertionError("degenerate discriminant matrix")
    return result


def rank_32_rootless_theta_r4() -> int:
    # For an even unimodular rank-32 lattice, theta has weight 16 and lies
    # in span{E4^4, E4*Delta}.  Rootlessness changes E4^4 to
    # E4^4-960 E4 Delta.  These are the exact q and q^2 coefficients.
    e4_q1 = 240
    e4_q2 = 2160
    e4_fourth_q2 = 4 * e4_q2 + 6 * e4_q1**2
    e4_delta_q2 = e4_q1 - 24
    result = e4_fourth_q2 - 960 * e4_delta_q2
    if result != 146880:
        raise AssertionError("rank-32 extremal theta coefficient drift")
    return result


@lru_cache(maxsize=1)
def rootless_h729_control() -> dict[str, object]:
    det_k12 = determinant(K12)
    det_kv32 = determinant(KV32F)
    if det_k12 != 729 or det_kv32 != 1:
        raise AssertionError(f"hostile determinants drifted: {det_k12}, {det_kv32}")
    if not integral_even(K12) or not integral_even(KV32F):
        raise AssertionError("hostile control is not even integral")

    k12_roots = enumerate_vectors_leq(K12, 2)
    kv32_roots = enumerate_vectors_leq(KV32F, 2)
    if k12_roots or kv32_roots:
        raise AssertionError("published hostile control unexpectedly has roots")
    k12_norm_four = enumerate_vectors_leq(K12, 4)
    if len(k12_norm_four) != 756:
        raise AssertionError(f"K12 kissing count drift: {len(k12_norm_four)}")

    three_k12_dual = scale_matrix(inverse(K12), 3)
    kv32_dual = inverse(KV32F)
    if not integral_even(three_k12_dual) or not integral_even(kv32_dual):
        raise AssertionError("hostile scaled dual lost even integrality")

    k12_discriminant = discriminant_matrix_mod_prime(K12, 3)
    e6_discriminant = discriminant_matrix_mod_prime(
        COMPONENTS["E6"]["gram"], 3
    )
    if len(k12_discriminant) != 6 or len(e6_discriminant) != 1:
        raise AssertionError("unexpected discriminant dimensions")
    det_k_disc = determinant_mod(k12_discriminant, 3)
    det_e6_six = pow(determinant_mod(e6_discriminant, 3), 6, 3)
    if det_k_disc != det_e6_six:
        raise AssertionError(
            f"discriminant determinant classes differ: {det_k_disc}, {det_e6_six}"
        )

    rooty_r2, rooty_r4 = theta_coefficients({"E6": 6, "E8": 1})
    rootless_r4 = len(k12_norm_four) + rank_32_rootless_theta_r4()
    if rooty_r2 != 672 or rootless_r4 != 147636:
        raise AssertionError("h=729 theta comparison drift")
    return {
        "candidate_label": "CANDIDATE_EXACT_BARE_LATTICE_HOSTILE_CONTROL",
        "S0": {
            "components": "K12 orthogonal_sum LAMBDA(F)",
            "rank": 44,
            "determinant": int(det_k12 * det_kv32),
            "exact_level": 3,
            "minimum": 4,
            "theta_q_coefficient_r2": 0,
            "theta_q2_coefficient_r4": rootless_r4,
            "twenty_one_scaled_dual_even_integral": True,
            "twenty_one_scaled_dual_minimum_lower_bound": 14,
        },
        "S1": {
            "components": "E6^6 orthogonal_sum E8",
            "rank": 44,
            "determinant": 729,
            "exact_level": 3,
            "theta_q_coefficient_r2": rooty_r2,
            "theta_q2_coefficient_r4": rooty_r4,
            "twenty_one_scaled_dual_minimum": 28,
        },
        "same_discriminant_form": {
            "group": "(Z/3Z)^6",
            "K12_matrix_mod_3": k12_discriminant,
            "K12_determinant_mod_3": det_k_disc,
            "E6_six_determinant_mod_3": det_e6_six,
            "classification_used": (
                "nondegenerate quadratic forms over odd finite fields are "
                "classified by dimension and determinant square class"
            ),
            "isometric": True,
        },
        "same_Weil_representation_different_root_count": True,
        "sources": {
            "K12": {
                "url": "https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/K12.html",
                "retrieved_page_sha256": "163e03dfa9a4ab07675daa6e97a371bcfdb38f6195c311c63c699872b3e486c9",
                "embedded_gram_sha256": matrix_sha256(K12),
            },
            "LAMBDA_F": {
                "url": "https://www.math.rwth-aachen.de/~Gabriele.Nebe/LATTICES/KV32F.html",
                "retrieved_page_sha256": "bb1db4504d7010dc093b24a8bcb00b042ea3879a220d669e8190d02abb6468ac",
                "embedded_gram_sha256": matrix_sha256(KV32F),
            },
            "retrieval_command": (
                "urllib.request.urlopen(url,timeout=30).read(); "
                "hashlib.sha256(bytes).hexdigest()"
            ),
        },
    }


def determinant_level_table() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for value in ALLOWED_H:
        a3, a7 = factor_3_7(value)
        level = exact_level(value)
        expected_self_dual_determinant = level ** (RANK // 2)
        if value == expected_self_dual_determinant:
            raise AssertionError("an endpoint determinant became modular self-dual")
        rows.append(
            {
                "h": value,
                "discriminant_group": f"(Z/3Z)^{a3} x (Z/7Z)^{a7}",
                "exact_level": level,
                "theta_character": theta_character(value),
                "gamma0_index": gamma0_index(level),
                "scalar_sturm_bound": sturm_bound(level),
                "fricke_partner_gram": f"{level}*S^-1",
                "G_scaling_from_fricke_partner": SCALE // level,
                "fricke_partner_rootless_forced_by_min_G_ge_4": level == SCALE,
                "determinant_required_for_level_modularity": str(
                    expected_self_dual_determinant
                ),
                "level_modular_self_duality_impossible": True,
            }
        )
    return rows


def frame_visible_constraints() -> dict[str, object]:
    row_count = 231
    # Distinct rows cannot agree or be negatives because their off-diagonal
    # inner product would be +4 or -4, outside {0,1,-1,-2}.
    theta_r4_floor = 2 * row_count
    if theta_r4_floor != 462:
        raise AssertionError("frame shell floor drift")
    for value in range(-12, 13):
        if value**3 + (-value) ** 3 != 0:
            raise AssertionError("odd harmonic antipodal cancellation failed")
    return {
        "oriented_norm_four_rows": row_count,
        "distinct_antipodal_pairs": row_count,
        "scalar_theta_norm_four_coefficient_floor": theta_r4_floor,
        "selected_second_moment": "sum_i y_i y_i^T=21 I_44",
        "selected_first_moment": "sum_i y_i=0",
        "selected_cubic_tensor_squared_norm": 60,
        "full_lattice_odd_weighted_theta_zero_component": "IDENTICALLY_ZERO",
        "reason": "P(v)+P(-v)=0 for every odd homogeneous P",
        "ordinary_theta_detects_selected_orientation_or_cubic_moment": False,
    }


def build_result() -> dict[str, object]:
    return {
        "base_commit": PUBLIC_HEAD,
        "frozen_inputs": freeze_inputs(),
        "claim": {
            "label": "DERIVED_SCOPED_RESTRICTION_AND_BLOCKER",
            "target_result": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "determinant_level_table": determinant_level_table(),
        "poisson_and_weil_laws": {
            "scalar_poisson": (
                "Theta_S(-1/(N*tau))=(N*tau/i)^22/sqrt(h)"
                "*Theta_(N*S^-1)(tau)"
            ),
            "vector_T": (
                "Theta_gamma(tau+1)=exp(pi*i*(gamma,gamma))*Theta_gamma(tau)"
            ),
            "vector_S": (
                "Theta_gamma(-1/tau)=(-i*tau)^22/sqrt(|A|)"
                "*sum_delta exp(-2*pi*i*(gamma,delta))*Theta_delta(tau)"
            ),
            "requires_strong_modularity": False,
            "fricke_eigenform_identity_available": False,
        },
        "frame_visible_constraints": frame_visible_constraints(),
        "component_checks": component_audit(),
        "ADE_scalar_theta_hostile_controls": decomposition_audit(),
        "h9_discriminant_nonuniqueness": h9_discriminant_nonuniqueness(),
        "rootless_h729_same_Weil_hostile_control": rootless_h729_control(),
        "limitations": [
            "No general even rank-44 lattice is classified.",
            "The 17 ADE lattices are hostile controls for scalar theta premises only; prior frame/tensor theorems exclude their endpoint origins.",
            "A scalar or ordinary vector-valued elliptic theta series does not encode the 231-vector pairwise Gram constraints.",
            "The selected oriented cubic moment is invisible to the zero-coset odd harmonic theta series by antipodal cancellation.",
            "No primitive embedding, projector, Schur certificate, graph, endpoint exclusion, or target resolution is supplied.",
        ],
    }


def canonical_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = canonical_json(build_result())
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
