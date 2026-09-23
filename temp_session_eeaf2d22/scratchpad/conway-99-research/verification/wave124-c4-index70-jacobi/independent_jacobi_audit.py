#!/usr/bin/env python3
"""Independent exact audit of the full-level J_{22,10} subspace.

This program intentionally uses only q^3: after elliptic reduction to
|r| <= 10, a negative-discriminant coefficient has

    n < r^2 / 40 <= 5/2.

Thus q^0, q^1, and q^2 contain representatives of every polar orbit.
The extra q^3 layer is retained as a guard coefficient.  The program does
not import or execute the Wave 124 discovery implementation.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


F = Fraction
WEIGHT = 22
INDEX = 10
QMAX = 3
Series = dict[tuple[int, int], F]


def prune(series: Series) -> Series:
    return {key: value for key, value in series.items() if value}


def plus(left: Series, right: Series, multiple: F = F(1)) -> Series:
    answer: defaultdict[tuple[int, int], F] = defaultdict(F)
    for key, value in left.items():
        answer[key] += value
    for key, value in right.items():
        answer[key] += multiple * value
    return prune(dict(answer))


def times(left: Series, right: Series, qmax: int = QMAX) -> Series:
    answer: defaultdict[tuple[int, int], F] = defaultdict(F)
    for (n1, r1), c1 in left.items():
        for (n2, r2), c2 in right.items():
            n = n1 + n2
            if n <= qmax:
                answer[n, r1 + r2] += c1 * c2
    return prune(dict(answer))


def exponentiate(base: Series, exponent: int, qmax: int = QMAX) -> Series:
    answer: Series = {(0, 0): F(1)}
    for _ in range(exponent):
        answer = times(answer, base, qmax)
    return answer


def divisor_power_sum(n: int, power: int) -> int:
    return sum(d**power for d in range(1, n + 1) if n % d == 0)


def eisenstein(weight: int) -> Series:
    multiplier, power = {4: (240, 3), 6: (-504, 5)}[weight]
    answer: Series = {(0, 0): F(1)}
    for n in range(1, QMAX + 1):
        answer[n, 0] = F(multiplier * divisor_power_sum(n, power))
    return answer


def generator_a() -> Series:
    """A=phi_{-2,1} from its Jacobi product."""

    answer: Series = {(0, -1): F(1), (0, 0): F(-2), (0, 1): F(1)}
    for n in range(1, QMAX + 1):
        inverse_eta: Series = {
            (j * n, 0): F(math.comb(j + 3, 3))
            for j in range(QMAX // n + 1)
        }
        positive: Series = {
            (0, 0): F(1),
            (n, 1): F(-2),
            (2 * n, 2): F(1),
        }
        negative: Series = {
            (0, 0): F(1),
            (n, -1): F(-2),
            (2 * n, -2): F(1),
        }
        answer = times(answer, inverse_eta)
        answer = times(answer, positive)
        answer = times(answer, negative)
    return answer


Puiseux = dict[tuple[int, int], F]


def p_times(left: Puiseux, right: Puiseux, q8max: int) -> Puiseux:
    answer: defaultdict[tuple[int, int], F] = defaultdict(F)
    for (q1, y1), c1 in left.items():
        for (q2, y2), c2 in right.items():
            if q1 + q2 <= q8max:
                answer[q1 + q2, y1 + y2] += c1 * c2
    return prune(dict(answer))


def theta(kind: int, q8max: int) -> Puiseux:
    """theta kind 2,3,4 in Q=q^(1/8), Y=y^(1/2)."""

    answer: defaultdict[tuple[int, int], F] = defaultdict(F)
    for n in range(-16, 17):
        if kind == 2:
            q8, y2, coefficient = (2 * n + 1) ** 2, 2 * n + 1, 1
        else:
            q8, y2 = 4 * n * n, 2 * n
            coefficient = 1 if kind == 3 or n % 2 == 0 else -1
        if q8 <= q8max:
            answer[q8, y2] += F(coefficient)
    return prune(dict(answer))


def theta_square_ratio(kind: int) -> Puiseux:
    """theta_j(tau,z)^2/theta_j(tau,0)^2 in Puiseux variables."""

    q8max = 8 * QMAX + 8
    numerator = p_times(theta(kind, q8max), theta(kind, q8max), q8max)
    denominator: defaultdict[int, F] = defaultdict(F)
    for (q8, _y2), coefficient in numerator.items():
        denominator[q8] += coefficient

    first = min(q8 for q8, value in denominator.items() if value)
    shifted_numerator = {
        (q8 - first, y2): value
        for (q8, y2), value in numerator.items()
    }
    shifted_denominator = {
        q8 - first: value for q8, value in denominator.items()
    }
    constant = shifted_denominator[0]
    inverse: dict[int, F] = {0: F(1) / constant}
    for degree in range(1, 8 * QMAX + 1):
        inverse[degree] = -sum(
            shifted_denominator.get(j, F(0))
            * inverse.get(degree - j, F(0))
            for j in range(1, degree + 1)
        ) / constant

    answer: defaultdict[tuple[int, int], F] = defaultdict(F)
    for (q8, y2), coefficient in shifted_numerator.items():
        for shift, inv_coefficient in inverse.items():
            if q8 + shift <= 8 * QMAX:
                answer[q8 + shift, y2] += coefficient * inv_coefficient
    return prune(dict(answer))


def generator_b() -> Series:
    """B=phi_{0,1}=4*sum_{j=2}^4 theta_j(z)^2/theta_j(0)^2."""

    combined: defaultdict[tuple[int, int], F] = defaultdict(F)
    for kind in (2, 3, 4):
        for key, value in theta_square_ratio(kind).items():
            combined[key] += 4 * value

    answer: defaultdict[tuple[int, int], F] = defaultdict(F)
    for (q8, y2), coefficient in combined.items():
        if coefficient:
            if q8 % 8 or y2 % 2:
                raise AssertionError("uncancelled fractional exponent in B")
            answer[q8 // 8, y2 // 2] += coefficient
    return prune(dict(answer))


def monomial_list() -> list[tuple[int, int, int, int]]:
    """All E4^a E6^b A^c B^d of weight 22 and index 10."""

    answer = []
    for c in range(INDEX + 1):
        d = INDEX - c
        for a in range(0, 11):
            for b in range(0, 8):
                if 4 * a + 6 * b - 2 * c == WEIGHT:
                    answer.append((a, b, c, d))
    return answer


def monomial_series() -> tuple[list[tuple[int, int, int, int]], list[Series]]:
    e4, e6, aa, bb = eisenstein(4), eisenstein(6), generator_a(), generator_b()
    labels = monomial_list()
    answer = []
    for a, b, c, d in labels:
        value: Series = {(0, 0): F(1)}
        for factor, count in ((e4, a), (e6, b), (aa, c), (bb, d)):
            value = times(value, exponentiate(factor, count))
        answer.append(value)
    return labels, answer


def rref_nullspace(rows: list[list[F]], width: int) -> list[list[F]]:
    work = [row[:] for row in rows]
    pivots: list[int] = []
    cursor = 0
    for column in range(width):
        selected = next(
            (i for i in range(cursor, len(work)) if work[i][column]),
            None,
        )
        if selected is None:
            continue
        work[cursor], work[selected] = work[selected], work[cursor]
        pivot = work[cursor][column]
        work[cursor] = [value / pivot for value in work[cursor]]
        for i in range(len(work)):
            if i != cursor and work[i][column]:
                scale = work[i][column]
                work[i] = [
                    x - scale * y
                    for x, y in zip(work[i], work[cursor], strict=True)
                ]
        pivots.append(column)
        cursor += 1
        if cursor == len(work):
            break

    free = [column for column in range(width) if column not in pivots]
    basis = []
    for free_column in free:
        vector = [F(0) for _ in range(width)]
        vector[free_column] = F(1)
        for row_index, pivot_column in enumerate(pivots):
            vector[pivot_column] = -work[row_index][free_column]
        basis.append(vector)
    return basis


def constraint_matrix(
    expansions: list[Series],
    columns: list[int],
    cusp: bool,
) -> tuple[list[tuple[int, int]], list[list[F]]]:
    keys = set().union(*(expansions[column] for column in columns))
    selected = sorted(
        (n, r)
        for n, r in keys
        if 40 * n - r * r < 0 or (cusp and 40 * n - r * r == 0)
    )
    rows = [
        [expansions[column].get(key, F(0)) for column in columns]
        for key in selected
    ]
    return selected, rows


def combine(
    expansions: list[Series], columns: list[int], vector: list[F]
) -> Series:
    answer: Series = {}
    for column, coefficient in zip(columns, vector, strict=True):
        answer = plus(answer, expansions[column], coefficient)
    return answer


def integerize(vector: list[F]) -> list[int]:
    denominator = math.lcm(*(value.denominator for value in vector))
    values = [
        value.numerator * (denominator // value.denominator)
        for value in vector
    ]
    gcd = math.gcd(*(abs(value) for value in values if value))
    values = [value // gcd for value in values]
    first = next(value for value in values if value)
    return values if first > 0 else [-value for value in values]


def audit() -> dict[str, object]:
    labels, expansions = monomial_series()
    if len(labels) != 34:
        raise AssertionError("weak-monomial enumeration changed")
    if [generator_a().get((0, r), 0) for r in (-1, 0, 1)] != [1, -2, 1]:
        raise AssertionError("A normalization")
    if [generator_b().get((0, r), 0) for r in (-1, 0, 1)] != [1, 10, 1]:
        raise AssertionError("B normalization")

    all_columns = list(range(len(labels)))
    polar_keys, polar_rows = constraint_matrix(
        expansions, all_columns, cusp=False
    )
    boundary_keys, boundary_rows = constraint_matrix(
        expansions, all_columns, cusp=True
    )
    holomorphic = rref_nullspace(polar_rows, len(all_columns))
    cusp = rref_nullspace(boundary_rows, len(all_columns))

    directions = []
    support_clean_directions = []
    for minimum_c in range(1, 6):
        columns = [
            i for i, (_a, _b, c, _d) in enumerate(labels) if c >= minimum_c
        ]
        keys, rows = constraint_matrix(expansions, columns, cusp=True)
        basis = rref_nullspace(rows, len(columns))
        target_vector = [
            combine(expansions, columns, vector).get((1, 4), F(0))
            for vector in basis
        ]
        chosen_index = next(
            (i for i, value in enumerate(target_vector) if value),
            None,
        )
        if chosen_index is None:
            raise AssertionError(f"no q^1 y^4 direction for A^{minimum_c}")
        integral = integerize(basis[chosen_index])
        form = combine(
            expansions, columns, [F(value) for value in integral]
        )
        if form.get((1, 4), F(0)) < 0:
            integral = [-value for value in integral]
            form = {key: -value for key, value in form.items()}
        directions.append(
            {
                "minimum_A_power": minimum_c,
                "cusp_dimension": len(basis),
                "constraint_count_at_q3": len(keys),
                "target_q1_r4": str(form[(1, 4)]),
                "full_34_coordinate_vector": [
                    integral[columns.index(i)] if i in columns else 0
                    for i in all_columns
                ],
                "q1_support": {
                    str(r): str(value)
                    for (n, r), value in sorted(form.items())
                    if n == 1 and value
                },
            }
        )

        clean_rows = rows + [
            [expansions[column].get((1, r), F(0)) for column in columns]
            for r in (5, 6)
        ]
        clean_basis = rref_nullspace(clean_rows, len(columns))
        clean_target_values = [
            combine(expansions, columns, vector).get((1, 4), F(0))
            for vector in clean_basis
        ]
        support_clean_directions.append(
            {
                "minimum_A_power": minimum_c,
                "cusp_dimension_after_q1_r5_r6_zeros": len(clean_basis),
                "q1_r4_functional_nonzero": any(clean_target_values),
            }
        )

    return {
        "format": "wave124-independent-jacobi-audit-v1",
        "precision": QMAX,
        "polar_completeness": (
            "elliptic reduction gives |r|<=10 and then negative "
            "discriminant implies n<5/2"
        ),
        "weak_monomial_count": len(labels),
        "weak_monomials_E4_E6_A_B": [list(label) for label in labels],
        "polar_constraint_count_at_q3": len(polar_keys),
        "cusp_constraint_count_at_q3": len(boundary_keys),
        "holomorphic_dimension": len(holomorphic),
        "cusp_dimension": len(cusp),
        "holomorphic_basis": [integerize(vector) for vector in holomorphic],
        "cusp_basis": [integerize(vector) for vector in cusp],
        "A_power_cusp_directions": directions,
        "support_clean_threshold_candidate": {
            "claim_label": "CANDIDATE",
            "constraints": "q^1 coefficients at r=5 and r=6 vanish",
            "rows": support_clean_directions,
            "exact_reason_at_A5": (
                "A^5 gives zero even Taylor moments of orders 0,2,4,6,8; "
                "after support is restricted to |r|<=4, the Vandermonde "
                "matrix on r^2 in {0,1,4,9,16} forces the whole q^1 row "
                "to vanish, including r=4"
            ),
            "interpretation": (
                "the graph support zeros plus the fifth even Taylor moment "
                "remove the published oldform escape at q_K^7 y_K^28"
            ),
        },
        "null_boundary": (
            "These full-level signed cusp directions prove only that "
            "Fricke, constants, scalar specialization, and finitely many "
            "Taylor moments do not alone bound c_K(7,28)."
        ),
    }


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    payload = canonical(audit())
    if args.write:
        args.write.write_text(payload, encoding="utf-8")
    elif args.verify:
        if args.verify.read_text(encoding="utf-8") != payload:
            raise SystemExit("independent Jacobi audit replay mismatch")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
