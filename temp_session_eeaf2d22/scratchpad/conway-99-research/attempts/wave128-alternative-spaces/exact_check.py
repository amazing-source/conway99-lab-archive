"""Exact discriminant splitting for the Wave 109 incidence-kernel lattice.

This is a discovery calculation.  It is conditional on a hypothetical
srg(99,14,1,2) containing the frozen C4 Cartesian K3 motif, and it does not
construct the unknown outside graph.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import isqrt, lcm
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ORDER = 87
MOTIF_ORDER = 12
RANK_ROWS = tuple(range(28, 43, 2))
PRIMES = (2, 3, 5, 7)
LOCAL_PRECISION = 24
INPUT_MANIFESTS = {
    "attempts/wave105-c4boxk3-extension/package-manifest.sha256":
        "b0fd40eda5a3677d4a835788cea20dfcb9bb3c5764719fc04536893f1b5da4a1",
    "verification/wave105-c4boxk3-extension/package-manifest.sha256":
        "2a24e3e5846558a9e93cd2f103e049816cef7f8dd4a200108643e44cc4c300ae",
    "attempts/wave107-c4boxk3-spectrum/package-manifest.sha256":
        "7e899602825d3cdf989affade8a1e5a6256f17ba911f6351ea8bfe4a3b05d2b0",
    "attempts/wave109-c4boxk3-local-projector/package-manifest.sha256":
        "6d54d48dbb6b1ffd3f7da845792fc12ee490471c02cc8137ebd1b03c21f5347e",
    "verification/wave109-c4boxk3-local-projector/package-manifest.sha256":
        "fcbb970eebf0b92cb012f5f2e81ccb8c6315c002c1f228f830cd1b0b082e62cd",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    require(bool(left) and bool(right), "empty matrix")
    require(len(left[0]) == len(right), "matrix dimension mismatch")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matrix_subtract(
    left: list[list[int]], right: list[list[int]]
) -> list[list[int]]:
    return [
        [left[i][j] - right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def horizontal(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    require(len(left) == len(right), "horizontal row mismatch")
    return [left[i] + right[i] for i in range(len(left))]


def identity(order: int) -> list[list[int]]:
    return [[int(i == j) for j in range(order)] for i in range(order)]


def determinant_bareiss(matrix: list[list[int]]) -> int:
    work = [row[:] for row in matrix]
    order = len(work)
    require(all(len(row) == order for row in work), "matrix is not square")
    if order == 0:
        return 1
    sign = 1
    previous = 1
    for column in range(order - 1):
        if work[column][column] == 0:
            pivot = next(
                (
                    row
                    for row in range(column + 1, order)
                    if work[row][column]
                ),
                None,
            )
            if pivot is None:
                return 0
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        for row in range(column + 1, order):
            for target in range(column + 1, order):
                numerator = (
                    work[row][target] * pivot_value
                    - work[row][column] * work[column][target]
                )
                require(numerator % previous == 0, "Bareiss division failed")
                work[row][target] = numerator // previous
            work[row][column] = 0
        previous = pivot_value
    return sign * work[-1][-1]


def solve_square(
    matrix: list[list[int]], right: list[list[int]]
) -> list[list[Fraction]]:
    order = len(matrix)
    require(all(len(row) == order for row in matrix), "left side not square")
    require(len(right) == order, "right-side row mismatch")
    augmented = [
        [Fraction(value) for value in matrix[i] + right[i]]
        for i in range(order)
    ]
    width = len(augmented[0])
    for column in range(order):
        pivot = next(
            (
                row
                for row in range(column, order)
                if augmented[row][column]
            ),
            None,
        )
        require(pivot is not None, "singular exact solve")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]
        for row in range(order):
            if row == column:
                continue
            multiplier = augmented[row][column]
            if multiplier:
                augmented[row] = [
                    augmented[row][j] - multiplier * augmented[column][j]
                    for j in range(width)
                ]
    return [row[order:] for row in augmented]


def valuation(value: int, prime: int, precision: int) -> int:
    modulus = prime**precision
    value %= modulus
    if value == 0:
        return precision
    result = 0
    while value % prime == 0:
        value //= prime
        result += 1
    return result


def local_smith_valuations(
    matrix: list[list[int]], prime: int, precision: int = LOCAL_PRECISION
) -> list[int]:
    """Return p-adic Smith valuations by exact DVR elimination mod p^N.

    Every pivot is chosen with minimum p-valuation in the remaining block.
    It therefore divides that block over Z_p.  Unit row scaling and exact
    row/column clearing expose one local invariant at a time.  The precision
    is accepted only when every row obtains a pivot strictly below N.
    """

    require(prime >= 2, "invalid prime")
    rows = len(matrix)
    columns = len(matrix[0]) if matrix else 0
    require(all(len(row) == columns for row in matrix), "ragged matrix")
    modulus = prime**precision
    work = [[value % modulus for value in row] for row in matrix]
    result: list[int] = []
    for pivot_index in range(min(rows, columns)):
        candidates = [
            (
                valuation(work[i][j], prime, precision),
                i,
                j,
            )
            for i in range(pivot_index, rows)
            for j in range(pivot_index, columns)
        ]
        pivot_valuation, pivot_row, pivot_column = min(candidates)
        require(
            pivot_valuation < precision,
            "local Smith precision exhausted before full row rank",
        )
        work[pivot_index], work[pivot_row] = (
            work[pivot_row],
            work[pivot_index],
        )
        for row in work:
            row[pivot_index], row[pivot_column] = (
                row[pivot_column],
                row[pivot_index],
            )
        prime_power = prime**pivot_valuation
        pivot = work[pivot_index][pivot_index]
        require(pivot % prime_power == 0, "pivot valuation drift")
        unit = (pivot // prime_power) % modulus
        require(unit % prime != 0, "pivot unit is not a unit")
        inverse = pow(unit, -1, modulus)
        work[pivot_index] = [
            value * inverse % modulus for value in work[pivot_index]
        ]
        require(
            work[pivot_index][pivot_index] == prime_power,
            "pivot normalization failed",
        )
        for row_index in range(rows):
            if row_index == pivot_index:
                continue
            entry = work[row_index][pivot_index]
            require(entry % prime_power == 0, "pivot does not divide column")
            quotient = (entry // prime_power) % modulus
            work[row_index] = [
                (
                    work[row_index][column]
                    - quotient * work[pivot_index][column]
                )
                % modulus
                for column in range(columns)
            ]
            require(
                work[row_index][pivot_index] == 0,
                "column clearing failed",
            )
        for column in range(columns):
            if column == pivot_index:
                continue
            entry = work[pivot_index][column]
            require(entry % prime_power == 0, "pivot does not divide row")
            quotient = (entry // prime_power) % modulus
            for row_index in range(rows):
                work[row_index][column] = (
                    work[row_index][column]
                    - quotient * work[row_index][pivot_index]
                ) % modulus
            require(work[pivot_index][column] == 0, "row clearing failed")
        result.append(pivot_valuation)
    require(len(result) == rows, "presentation lacks full row rank")
    require(all(value < precision for value in result), "precision ambiguity")
    return result


def motif_adjacency() -> list[list[int]]:
    vertices = [(cycle, label) for cycle in range(4) for label in range(3)]
    matrix = [[0] * MOTIF_ORDER for _ in range(MOTIF_ORDER)]
    for left, (cycle_left, label_left) in enumerate(vertices):
        for right, (cycle_right, label_right) in enumerate(vertices):
            same_triangle = (
                cycle_left == cycle_right and label_left != label_right
            )
            cycle_matching = (
                label_left == label_right
                and (cycle_left - cycle_right) % 4 in (1, 3)
            )
            matrix[left][right] = int(same_triangle or cycle_matching)
    return matrix


def forced_patterns() -> tuple[tuple[int, ...], ...]:
    adjacency = motif_adjacency()
    patterns: list[tuple[int, ...]] = [()] * 3
    for vertex in range(MOTIF_ORDER):
        patterns.extend([(vertex,)] * 4)
    for left, right in combinations(range(MOTIF_ORDER), 2):
        common = sum(
            adjacency[left][vertex] * adjacency[right][vertex]
            for vertex in range(MOTIF_ORDER)
        )
        target = 1 if adjacency[left][right] else 2
        multiplicity = target - common
        require(multiplicity >= 0, "negative pair multiplicity")
        patterns.extend([(left, right)] * multiplicity)
    require(len(patterns) == ORDER, "outside incidence order drift")
    return tuple(patterns)


def q_matrix() -> list[list[int]]:
    result = [[1] + [0] * MOTIF_ORDER for _ in range(ORDER)]
    for row, pattern in enumerate(forced_patterns()):
        for column in pattern:
            result[row][column + 1] = 1
    return result


def gram(matrix: list[list[int]]) -> list[list[int]]:
    return matmul(transpose(matrix), matrix)


def b_on_w_coordinates() -> list[list[int]]:
    """Matrix C satisfying B Q = Q C on W=im(Q)."""

    adjacency = motif_adjacency()
    result = [[0] * (MOTIF_ORDER + 1) for _ in range(MOTIF_ORDER + 1)]
    # B 1 = 18 1 - P 1.
    result[0][0] = 18
    for row in range(MOTIF_ORDER):
        result[row + 1][0] = -1
    # B P = 2 J + 3 P - P H.
    for column in range(MOTIF_ORDER):
        result[0][column + 1] = 2
        for row in range(MOTIF_ORDER):
            result[row + 1][column + 1] = (
                3 * int(row == column) - adjacency[row][column]
            )
    return result


def positive_valuations(values: Iterable[int]) -> list[int]:
    return [value for value in values if value]


def compressed_primary(values: Iterable[int], prime: int) -> dict[str, int]:
    return {
        str(prime**exponent): multiplicity
        for exponent, multiplicity in sorted(
            Counter(value for value in values if value).items()
        )
    }


def affine_solutions_mod_prime(
    matrix: list[list[int]], right: list[int], prime: int
) -> list[tuple[int, ...]]:
    rows = len(matrix)
    columns = len(matrix[0]) if matrix else 0
    require(len(right) == rows, "affine right-side mismatch")
    work = [
        [value % prime for value in matrix[i]] + [right[i] % prime]
        for i in range(rows)
    ]
    pivot_columns: list[int] = []
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(pivot_row, rows)
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        inverse = pow(work[pivot_row][column], -1, prime)
        work[pivot_row] = [
            value * inverse % prime for value in work[pivot_row]
        ]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            multiplier = work[row][column]
            work[row] = [
                (
                    work[row][target]
                    - multiplier * work[pivot_row][target]
                )
                % prime
                for target in range(columns + 1)
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == rows:
            break
    if any(
        all(work[row][column] == 0 for column in range(columns))
        and work[row][-1]
        for row in range(pivot_row, rows)
    ):
        return []
    free_columns = [
        column for column in range(columns) if column not in pivot_columns
    ]
    particular = [0] * columns
    for row, column in enumerate(pivot_columns):
        particular[column] = work[row][-1]
    basis = []
    for free in free_columns:
        vector = [0] * columns
        vector[free] = 1
        for row, column in enumerate(pivot_columns):
            vector[column] = -work[row][free] % prime
        basis.append(vector)
    solutions: list[tuple[int, ...]] = []
    coefficients = (
        [()] if not basis else product(range(prime), repeat=len(basis))
    )
    for coefficient in coefficients:
        solutions.append(
            tuple(
                (
                    particular[column]
                    + sum(
                        coefficient[index] * basis[index][column]
                        for index in range(len(basis))
                    )
                )
                % prime
                for column in range(columns)
            )
        )
    return solutions


def kernel_mod_prime_power(
    matrix: list[list[int]], prime: int, exponent: int
) -> list[tuple[int, ...]]:
    require(exponent >= 1, "prime-power exponent must be positive")
    columns = len(matrix[0])
    solutions = affine_solutions_mod_prime(
        matrix, [0] * len(matrix), prime
    )
    modulus = prime
    for _level in range(1, exponent):
        lifted: list[tuple[int, ...]] = []
        next_modulus = modulus * prime
        for vector in solutions:
            products = [
                sum(row[column] * vector[column] for column in range(columns))
                for row in matrix
            ]
            require(
                all(value % modulus == 0 for value in products),
                "invalid Hensel source vector",
            )
            right = [-(value // modulus) % prime for value in products]
            for correction in affine_solutions_mod_prime(
                matrix, right, prime
            ):
                lifted.append(
                    tuple(
                        (
                            vector[column] + modulus * correction[column]
                        )
                        % next_modulus
                        for column in range(columns)
                    )
                )
        solutions = lifted
        modulus = next_modulus
    return solutions


def quadratic_value_on_lambda_discriminant(
    vector: tuple[int, ...],
    prime: int,
    exponent: int,
    gram_matrix: list[list[int]],
) -> Fraction:
    """Quadratic value transported from the even complement Lambda.

    For x=a/p^e in W*, the ambient characteristic vector is one=Q e_0.
    The complementary even discriminant value is

        q_Lambda(x) = ((Gx)_0 - x^T G x)/2 mod Z.
    """

    prime_power = prime**exponent
    gram_vector = [
        sum(
            gram_matrix[row][column] * vector[column]
            for column in range(len(vector))
        )
        for row in range(len(gram_matrix))
    ]
    require(
        all(value % prime_power == 0 for value in gram_vector),
        "vector is not in the discriminant kernel",
    )
    first_dual_coordinate = gram_vector[0] // prime_power
    norm_numerator = sum(
        vector[row] * gram_vector[row] for row in range(len(vector))
    )
    value = (
        Fraction(first_dual_coordinate, 2)
        - Fraction(norm_numerator, 2 * prime_power**2)
    )
    return Fraction(value.numerator % value.denominator, value.denominator)


def smallest_prime_divisor(value: int) -> int:
    for candidate in range(2, isqrt(value) + 1):
        if value % candidate == 0:
            return candidate
    return value


def cyclotomic_reduce(coefficients: list[int]) -> list[int]:
    """Reduce a polynomial of degree below m modulo Phi_m.

    The only moduli used here are prime powers.
    """

    modulus = len(coefficients)
    prime = smallest_prime_divisor(modulus)
    power = modulus
    while power % prime == 0:
        power //= prime
    require(power == 1, "Gauss denominator is not a prime power")
    base = modulus // prime
    degree = modulus - base
    reduced = coefficients[:degree]
    for offset in range(base):
        coefficient = coefficients[degree + offset]
        if not coefficient:
            continue
        for multiple in range(prime - 1):
            reduced[offset + multiple * base] -= coefficient
    return reduced


def exact_gauss_phase(values: list[Fraction]) -> dict[str, object]:
    order = len(values)
    square_root = isqrt(order)
    require(square_root**2 == order, "module order is not a square")
    denominator = 1
    for value in values:
        denominator = lcm(denominator, value.denominator)
    counts = [0] * denominator
    for value in values:
        residue = value.numerator * (denominator // value.denominator)
        counts[residue % denominator] += 1
    if denominator == 1:
        require(order == 1 and counts == [1], "trivial Gauss module drift")
        return {
            "order": 1,
            "quadratic_denominator": 1,
            "distinct_quadratic_values": 1,
            "normalized_phase": "+1",
            "cyclotomic_remainder_sha256": hashlib.sha256(b"[1]\n").hexdigest(),
        }
    reduced = cyclotomic_reduce(counts)
    candidates: dict[str, list[int]] = {}
    for label, coefficient, exponent in (
        ("+1", square_root, 0),
        ("-1", -square_root, 0),
    ):
        target = [0] * denominator
        target[exponent] = coefficient
        candidates[label] = cyclotomic_reduce(target)
    if denominator % 4 == 0:
        for label, exponent in (
            ("+i", denominator // 4),
            ("-i", 3 * denominator // 4),
        ):
            target = [0] * denominator
            target[exponent] = square_root
            candidates[label] = cyclotomic_reduce(target)
    matches = [
        label for label, target in candidates.items() if target == reduced
    ]
    require(len(matches) == 1, "Gauss phase was not certified uniquely")
    reduced_bytes = canonical_json(reduced).encode("ascii")
    return {
        "order": order,
        "quadratic_denominator": denominator,
        "distinct_quadratic_values": len(set(values)),
        "normalized_phase": matches[0],
        "cyclotomic_remainder_sha256": hashlib.sha256(
            reduced_bytes
        ).hexdigest(),
    }


def finite_quadratic_gauss_profiles(
    gram_matrix: list[list[int]], action: list[list[int]]
) -> dict[str, object]:
    order = len(gram_matrix)
    result: dict[str, object] = {"U": {}, "K": {}}
    for component in ("U", "K"):
        operator = [
            [
                action[i][j]
                - (7 if component == "U" and i == j else 0)
                for j in range(order)
            ]
            for i in range(order)
        ]
        for prime, exponent in ((2, 8), (3, 2), (5, 1)):
            presentation = gram_matrix + operator
            vectors = kernel_mod_prime_power(
                presentation, prime, exponent
            )
            values = [
                quadratic_value_on_lambda_discriminant(
                    vector, prime, exponent, gram_matrix
                )
                for vector in vectors
            ]
            result[component][str(prime)] = exact_gauss_phase(values)
    expected = {
        "U": {"2": "-i", "3": "-1", "5": "-1"},
        "K": {"2": "+1", "3": "-1", "5": "+1"},
    }
    for component, profiles in expected.items():
        for prime, phase in profiles.items():
            require(
                result[component][prime]["normalized_phase"] == phase,
                f"{component} p={prime} Gauss phase drift",
            )
    result["non_seven_phase"] = {"U": "-i", "K": "-1"}
    result["milgram_forced_seven_phase"] = {"U": "-1", "K": "-1"}
    result["seven_determinant_legendre_symbol"] = "(-1)^(k/2+1)"
    result["seven_primary_type"] = {"U": "O^-(k,7)", "K": "O^-(k,7)"}
    return result


def exact_primary_profiles(
    gram_matrix: list[list[int]], action_transpose: list[list[int]]
) -> dict[str, object]:
    order = len(gram_matrix)
    seven_identity_minus_action = [
        [
            7 * int(i == j) - action_transpose[i][j]
            for j in range(order)
        ]
        for i in range(order)
    ]
    result: dict[str, object] = {}
    for prime in PRIMES:
        total = local_smith_valuations(gram_matrix, prime)
        # On the p-primary discriminant group for p != 7,
        # E=C^T/7 is an idempotent.  Quotienting by im(1-E) leaves A_U;
        # quotienting by im(E) leaves A_K.
        u_component = local_smith_valuations(
            horizontal(gram_matrix, seven_identity_minus_action), prime
        )
        k_component = local_smith_valuations(
            horizontal(gram_matrix, action_transpose), prime
        )
        result[str(prime)] = {
            "ambient_valuations": positive_valuations(total),
            "ambient_group": compressed_primary(total, prime),
            "U_valuations": positive_valuations(u_component),
            "U_group": compressed_primary(u_component, prime),
            "K_valuations": positive_valuations(k_component),
            "K_group": compressed_primary(k_component, prime),
            "valuation_check": (
                sum(u_component) + sum(k_component) == sum(total)
            ),
        }
    return result


def verify_inputs() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in INPUT_MANIFESTS.items():
        path = ROOT / relative
        require(path.is_file(), f"missing input manifest: {relative}")
        digest = sha256(path)
        require(digest == expected, f"input manifest hash drift: {relative}")
        observed[relative] = digest
    return observed


def build_results(verify_imports: bool = True) -> dict[str, object]:
    patterns = forced_patterns()
    q = q_matrix()
    gram_q = gram(q)
    determinant = determinant_bareiss(gram_q)
    require(
        Counter(map(len, patterns)) == {0: 3, 1: 48, 2: 36},
        "pattern histogram drift",
    )
    require(determinant == 6_191_736_422_400, "Gram determinant drift")

    action = b_on_w_coordinates()
    action_transpose = transpose(action)
    require(
        matmul(gram_q, action) == matmul(action_transpose, gram_q),
        "B is not self-adjoint on W",
    )

    induced_polynomial = matrix_subtract(
        matmul(action_transpose, action_transpose),
        [[7 * value for value in row] for row in action_transpose],
    )
    quotient = solve_square(gram_q, induced_polynomial)
    require(
        all(value.denominator == 1 for row in quotient for value in row),
        "C^T(C^T-7I) does not vanish modulo G Z^13",
    )
    quotient_integer = [
        [int(value) for value in row]
        for row in quotient
    ]
    require(
        matmul(gram_q, quotient_integer) == induced_polynomial,
        "induced polynomial certificate replay failed",
    )

    profiles = exact_primary_profiles(gram_q, action_transpose)
    gauss_profiles = finite_quadratic_gauss_profiles(gram_q, action)
    expected = {
        "2": {
            "ambient_valuations": [2, 3, 3, 3, 3, 8],
            "U_valuations": [2, 8],
            "K_valuations": [3, 3, 3, 3],
        },
        "3": {
            "ambient_valuations": [1, 1, 1, 1, 2, 2, 2],
            "U_valuations": [1, 1, 2, 2],
            "K_valuations": [1, 1, 2],
        },
        "5": {
            "ambient_valuations": [1, 1],
            "U_valuations": [1, 1],
            "K_valuations": [],
        },
        "7": {
            "ambient_valuations": [],
            "U_valuations": [],
            "K_valuations": [],
        },
    }
    for prime, rows in expected.items():
        for key, value in rows.items():
            require(profiles[prime][key] == value, f"{prime}:{key} drift")
        require(profiles[prime]["valuation_check"], f"{prime}-split mismatch")

    rows = []
    non_seven_u = 2**10 * 3**6 * 5**2
    non_seven_k = 2**12 * 3**4
    for global_rank in RANK_ROWS:
        local_rank = global_rank - 12
        determinant_u = non_seven_u * 7**local_rank
        determinant_k = non_seven_k * 7**local_rank
        require(
            determinant_u * determinant_k
            == 7 ** (2 * local_rank) * determinant,
            "orthogonal determinant product drift",
        )
        rows.append(
            {
                "global_rank_r": global_rank,
                "local_mod7_rank_k": local_rank,
                "det_U": determinant_u,
                "det_K": determinant_k,
                "U_7_primary": f"(Z/7)^{local_rank}",
                "K_7_primary": f"(Z/7)^{local_rank}",
                "index_U_over_BLambda": f"7^{42 - local_rank}",
                "index_K_over_7IminusB_Lambda": f"7^{32 - local_rank}",
                "excluded": False,
            }
        )

    input_hashes = verify_inputs() if verify_imports else INPUT_MANIFESTS
    return {
        "format": "wave128-alternative-spaces-v1",
        "claim_label": "DERIVED",
        "scope": (
            "Conditional on a hypothetical srg(99,14,1,2) containing "
            "the frozen Wave 105 induced C4 Cartesian K3 motif."
        ),
        "input_manifest_sha256": input_hashes,
        "incidence_kernel": {
            "Lambda_definition": "ker_Z(Q^T)",
            "W_definition": "im_Z(Q)",
            "rank_Lambda": 74,
            "rank_W": 13,
            "det_Lambda_equals_det_QtQ": determinant,
            "det_factorization": "2^22 * 3^10 * 5^2",
            "outside_pattern_histogram": {
                str(weight): count
                for weight, count in sorted(Counter(map(len, patterns)).items())
            },
        },
        "discriminant_action": {
            "presentation": "A_W = Z^13 / (Q^T Q) Z^13",
            "action": "C^T, where BQ=QC and B=D+4I",
            "self_adjoint_certificate": "Q^TQ C = C^T Q^TQ",
            "projector_relation": "(C^T)^2-7C^T=0 on A_W",
            "projector_quotient_integral": True,
            "projector_quotient_max_abs": max(
                abs(value) for row in quotient_integer for value in row
            ),
        },
        "primary_split": profiles,
        "finite_quadratic_gauss": gauss_profiles,
        "eigenlattices": {
            "U_definition": "Lambda intersect eig_Q(D,3)",
            "K_definition": "Lambda intersect eig_Q(D,-4)",
            "ranks": {"U": 42, "K": 32},
            "rootless": {
                "U_minimum_at_least": 4,
                "K_minimum_at_least": 4,
                "reason": (
                    "Every norm-2 vector of Lambda is +/- (e_i-e_j); "
                    "the i-coordinate of D(e_i-e_j) is -D_ij in {0,-1}, "
                    "which is neither 3 nor -4."
                ),
            },
            "non_seven_discriminant_groups": {
                "U": (
                    "Z/256 + Z/4 + (Z/9)^2 + (Z/3)^2 + (Z/5)^2"
                ),
                "K": "(Z/8)^4 + Z/9 + (Z/3)^2",
            },
            "determinant_formulas": {
                "U": "2^10 * 3^6 * 5^2 * 7^k",
                "K": "2^12 * 3^4 * 7^k",
            },
            "seven_primary_certificate": {
                "gluing_index": "[Lambda:U direct_sum K]=7^k",
                "equal_orders": (
                    "Lambda is 7-unimodular, so A_U,7 and A_K,7 are "
                    "anti-isometric and both have order 7^k"
                ),
                "U_map": "B Lambda = 7 U* over Z_7",
                "K_map": "(7I-B) Lambda = 7 K* over Z_7",
            },
            "seven_primary_exponent": 7,
            "rows": rows,
        },
        "status_wall": {
            "any_rank_row_excluded": False,
            "motif_excluded": False,
            "full_extension": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
    }


def canonical_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--skip-input-hash-check", action="store_true")
    arguments = parser.parse_args()
    data = build_results(not arguments.skip_input_hash_check)
    rendered = canonical_json(data)
    if arguments.verify:
        require(arguments.verify.read_text(encoding="utf-8") == rendered,
                "frozen exact-results.json drift")
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    if not arguments.output and not arguments.verify:
        print(rendered, end="")


if __name__ == "__main__":
    main()
