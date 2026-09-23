"""Independent verification of the conditional Wave 109 local projector.

This file does not import or execute discovery code.  It reconstructs the
motif incidence matrix from the SRG common-neighbor equations and checks the
integer, rational, and characteristic-seven consequences exactly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
P7 = 7
OUTSIDE_ORDER = 87
MOTIF_ORDER = 12
GLOBAL_RANK_ROWS = tuple(range(28, 43, 2))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def frozen_inputs() -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in (PACKAGE / "input-freeze.sha256").read_text(
        encoding="utf-8"
    ).splitlines():
        if not raw.strip():
            continue
        digest, relative = raw.split(maxsplit=1)
        result[relative] = digest
    return result


def verify_input_freeze() -> dict[str, str]:
    frozen = frozen_inputs()
    require(len(frozen) == 10, "input-freeze entry count drift")
    for relative, expected in frozen.items():
        actual = file_sha256(ROOT / relative)
        require(actual == expected, f"frozen input changed: {relative}")
    require(
        frozen[
            "attempts/wave109-c4boxk3-local-projector/"
            "package-manifest.sha256"
        ]
        == "6d54d48dbb6b1ffd3f7da845792fc12ee490471c02cc8137ebd1b03c21f5347e",
        "sealed package hash drift",
    )
    return frozen


def transpose(matrix: list[list[object]]) -> list[list[object]]:
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: list[list[int | Fraction]],
    right: list[list[int | Fraction]],
) -> list[list[int | Fraction]]:
    require(bool(left) and bool(right), "matrix must be nonempty")
    require(len(left[0]) == len(right), "matrix dimension mismatch")
    return [
        [
            sum(left[i][k] * right[k][j] for k in range(len(right)))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matrix_subtract(
    left: list[list[int | Fraction]],
    right: list[list[int | Fraction]],
) -> list[list[int | Fraction]]:
    require(len(left) == len(right), "row dimension mismatch")
    require(len(left[0]) == len(right[0]), "column dimension mismatch")
    return [
        [left[i][j] - right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


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
                    if work[row][column] != 0
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
                require(numerator % previous == 0, "nonexact Bareiss step")
                work[row][target] = numerator // previous
            work[row][column] = 0
        previous = pivot_value
    return sign * work[-1][-1]


def determinant_mod(matrix: list[list[int]], prime: int) -> int:
    work = [[value % prime for value in row] for row in matrix]
    order = len(work)
    require(all(len(row) == order for row in work), "matrix is not square")
    result = 1
    for column in range(order):
        pivot = next(
            (
                row
                for row in range(column, order)
                if work[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result = result * pivot_value % prime
        inverse = pow(pivot_value, -1, prime)
        for row in range(column + 1, order):
            factor = work[row][column] * inverse % prime
            if factor:
                work[row] = [
                    (work[row][target] - factor * work[column][target]) % prime
                    for target in range(order)
                ]
    return result % prime


def rank_mod(
    matrix: list[list[int | Fraction]],
    prime: int = P7,
) -> int:
    work: list[list[int]] = []
    for row in matrix:
        converted: list[int] = []
        for entry in row:
            value = Fraction(entry)
            denominator = value.denominator % prime
            require(denominator != 0, "denominator vanishes modulo prime")
            converted.append(
                value.numerator * pow(denominator, -1, prime) % prime
            )
        work.append(converted)
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(pivot_row, rows)
                if work[row][column] != 0
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
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    (work[row][target] - factor * work[pivot_row][target])
                    % prime
                    for target in range(columns)
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def rank_fraction(matrix: list[list[int | Fraction]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
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
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [
            value / pivot_value for value in work[pivot_row]
        ]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    work[row][target]
                    - factor * work[pivot_row][target]
                    for target in range(columns)
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def inverse_fraction(
    matrix: list[list[int]],
) -> list[list[Fraction]]:
    order = len(matrix)
    require(all(len(row) == order for row in matrix), "matrix is not square")
    unit = identity(order)
    work = [
        [Fraction(value) for value in matrix[row]]
        + [Fraction(value) for value in unit[row]]
        for row in range(order)
    ]
    for column in range(order):
        pivot = next(
            (
                row
                for row in range(column, order)
                if work[row][column]
            ),
            None,
        )
        require(pivot is not None, "singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        pivot_value = work[column][column]
        work[column] = [value / pivot_value for value in work[column]]
        for row in range(order):
            if row == column:
                continue
            factor = work[row][column]
            if factor:
                work[row] = [
                    work[row][target] - factor * work[column][target]
                    for target in range(2 * order)
                ]
    return [row[order:] for row in work]


def motif_adjacency() -> list[list[int]]:
    vertices = [
        (cycle_coordinate, triangle_coordinate)
        for cycle_coordinate in range(4)
        for triangle_coordinate in range(3)
    ]
    result = [[0] * MOTIF_ORDER for _ in range(MOTIF_ORDER)]
    for i, (cycle_i, triangle_i) in enumerate(vertices):
        for j, (cycle_j, triangle_j) in enumerate(vertices):
            cycle_edge = (
                triangle_i == triangle_j
                and (cycle_i - cycle_j) % 4 in {1, 3}
            )
            triangle_edge = cycle_i == cycle_j and triangle_i != triangle_j
            result[i][j] = int(cycle_edge or triangle_edge)
    return result


def forced_patterns() -> list[tuple[int, ...]]:
    """Derive the 87 outside rows from degrees and common-neighbor deficits."""

    h = motif_adjacency()
    pairs: list[tuple[int, ...]] = []
    pair_incidence = [0] * MOTIF_ORDER
    for left in range(MOTIF_ORDER):
        for right in range(left + 1, MOTIF_ORDER):
            common_inside = sum(
                h[left][vertex] * h[right][vertex]
                for vertex in range(MOTIF_ORDER)
            )
            required_common = 1 if h[left][right] else 2
            multiplicity = required_common - common_inside
            require(
                multiplicity in {0, 1, 2},
                "unexpected outside pair multiplicity",
            )
            for _ in range(multiplicity):
                pairs.append((left, right))
                pair_incidence[left] += 1
                pair_incidence[right] += 1

    singletons: list[tuple[int, ...]] = []
    for vertex in range(MOTIF_ORDER):
        outside_degree = 14 - sum(h[vertex])
        multiplicity = outside_degree - pair_incidence[vertex]
        require(multiplicity >= 0, "negative singleton multiplicity")
        singletons.extend([(vertex,)] * multiplicity)

    zero_count = OUTSIDE_ORDER - len(singletons) - len(pairs)
    require(zero_count >= 0, "negative zero-pattern multiplicity")
    patterns = [()] * zero_count + singletons + pairs
    require(
        (zero_count, len(singletons), len(pairs)) == (3, 48, 36),
        "forced incidence histogram drift",
    )
    return patterns


def incidence_matrix() -> list[list[int]]:
    result: list[list[int]] = []
    for pattern in forced_patterns():
        row = [0] * MOTIF_ORDER
        for vertex in pattern:
            row[vertex] = 1
        result.append(row)
    return result


def q_matrix() -> list[list[int]]:
    return [[1] + row for row in incidence_matrix()]


def gram(matrix: list[list[int]]) -> list[list[int]]:
    return matmul(transpose(matrix), matrix)  # type: ignore[arg-type,return-value]


def independently_find_unit_minor(q: list[list[int]]) -> tuple[list[int], int]:
    """Search row contents for a unimodular minor; use no claimed row list."""

    selected: list[int] = []
    desired = [[0] * MOTIF_ORDER]
    desired.extend(
        [[int(i == j) for j in range(MOTIF_ORDER)] for i in range(MOTIF_ORDER)]
    )
    for tail in desired:
        row = next(
            (
                index
                for index, candidate in enumerate(q)
                if candidate[1:] == tail and index not in selected
            ),
            None,
        )
        require(row is not None, f"missing unit-minor row {tail}")
        selected.append(row)
    minor = [q[row] for row in selected]
    value = determinant_bareiss(minor)
    require(abs(value) == 1, "independently found minor is not unimodular")
    return selected, value


def integral_kernel_basis(
    q: list[list[int]],
    pivot_rows: list[int],
) -> list[list[int]]:
    """Build a complete Z-basis of ker(Q^T) using the unit minor."""

    pivot_matrix_transpose = transpose([q[row] for row in pivot_rows])
    inverse = inverse_fraction(pivot_matrix_transpose)  # type: ignore[arg-type]
    pivot_set = set(pivot_rows)
    free_rows = [row for row in range(len(q)) if row not in pivot_set]
    basis_columns: list[list[int]] = []
    for free_row in free_rows:
        right = [[-entry] for entry in q[free_row]]
        coefficients = matmul(inverse, right)
        require(
            all(value[0].denominator == 1 for value in coefficients),
            "unit minor produced nonintegral kernel coordinate",
        )
        vector = [0] * len(q)
        vector[free_row] = 1
        for index, row in enumerate(pivot_rows):
            vector[row] = int(coefficients[index][0])
        basis_columns.append(vector)
    require(len(basis_columns) == 74, "kernel basis rank drift")
    basis = transpose(basis_columns)
    require(
        all(
            entry == 0
            for row in matmul(transpose(q), basis)
            for entry in row
        ),
        "kernel basis is not orthogonal to Q",
    )
    return basis  # 87 rows by 74 columns


def legendre_symbol(value: int, prime: int = P7) -> int:
    residue = pow(value % prime, (prime - 1) // 2, prime)
    if residue == prime - 1:
        return -1
    return residue


def coefficient_matrix_for_dq(h: list[list[int]]) -> list[list[int]]:
    """E such that the conditional SRG block equations give DQ=QE."""

    result = [[0] * 13 for _ in range(13)]
    result[0][0] = 14
    for row in range(MOTIF_ORDER):
        result[row + 1][0] = -1
    for column in range(MOTIF_ORDER):
        result[0][column + 1] = 2
        for row in range(MOTIF_ORDER):
            result[row + 1][column + 1] = -(
                int(row == column) + h[row][column]
            )
    return result


def exact_verification() -> dict[str, object]:
    frozen = verify_input_freeze()
    h = motif_adjacency()
    require(all(sum(row) == 4 for row in h), "motif is not 4-regular")
    p = incidence_matrix()
    q = [[1] + row for row in p]

    pivot_rows, unit_minor = independently_find_unit_minor(q)
    require(rank_fraction(q) == 13, "Q lacks full rational column rank")
    q_gram = gram(q)
    q_gram_determinant = determinant_bareiss(q_gram)
    factorized_determinant = 2**22 * 3**10 * 5**2
    require(
        q_gram_determinant == factorized_determinant,
        "det(Q^T Q) factorization drift",
    )

    lambda_basis = integral_kernel_basis(q, pivot_rows)
    lambda_gram = matmul(transpose(lambda_basis), lambda_basis)
    lambda_gram_int = [
        [int(value) for value in row] for row in lambda_gram
    ]
    lambda_determinant = determinant_bareiss(lambda_gram_int)
    require(
        lambda_determinant == q_gram_determinant,
        "kernel-lattice determinant mismatch",
    )

    determinant_mod_7 = determinant_mod(lambda_gram_int, P7)
    require(determinant_mod_7 == 4, "Lambda discriminant mod 7 drift")
    require(rank_mod(lambda_gram_int, P7) == 74, "Lambda mod 7 degenerates")
    determinant_character = legendre_symbol(determinant_mod_7)
    split_class = pow(-1, 37, P7)
    split_character = legendre_symbol(split_class)
    require(determinant_character == 1, "Lambda determinant is nonsquare")
    require(split_character == -1, "split determinant class should be nonsquare")
    require(
        determinant_character != split_character,
        "orthogonal type should be non-split",
    )
    witt_index = 36

    ptp = matmul(transpose(p), p)
    h_squared = matmul(h, h)
    expected_ptp = [
        [
            12 * int(i == j) - h[i][j] + 2 - h_squared[i][j]
            for j in range(MOTIF_ORDER)
        ]
        for i in range(MOTIF_ORDER)
    ]
    require(ptp == expected_ptp, "P^T P block identity drift")

    c = [
        [h[i][j] + 4 * int(i == j) for j in range(MOTIF_ORDER)]
        for i in range(MOTIF_ORDER)
    ]
    c_determinant = determinant_bareiss(c)
    require(c_determinant == 2332800, "det(H+4I) drift")
    require(c_determinant % P7 == 1, "motif block singular modulo 7")
    c_inverse = inverse_fraction(c)

    e = coefficient_matrix_for_dq(h)
    d_q = matmul(q, e)
    row_sums_p = [sum(row) for row in p]
    expected_d_one = [[14 - degree] for degree in row_sums_p]
    require(
        [[row[0]] for row in d_q] == expected_d_one,
        "D one block action drift",
    )
    expected_dp = [
        [
            2
            - p[row][column]
            - sum(p[row][j] * h[j][column] for j in range(MOTIF_ORDER))
            for column in range(MOTIF_ORDER)
        ]
        for row in range(OUTSIDE_ORDER)
    ]
    require(
        [row[1:] for row in d_q] == expected_dp,
        "DP block action drift",
    )
    # The SRG identity is A^2=12I-A+2J.  Expanding T=A+4I gives
    # T^2=28I+7A+2J=7T+2J.  Since D preserves Lambda, the restriction to
    # (0,Lambda) is exactly B^2=7B.
    expanded_t_squared = {"I": 12 + 16, "A": -1 + 8, "J": 2}
    seven_t_plus_two_j = {"I": 28, "A": 7, "J": 2}
    require(
        expanded_t_squared == seven_t_plus_two_j,
        "global projector polynomial drift",
    )

    e_plus_4 = [
        [e[i][j] + 4 * int(i == j) for j in range(13)]
        for i in range(13)
    ]
    b_q = matmul(q, e_plus_4)
    ptq = matmul(transpose(p), q)
    correction = matmul(p, matmul(c_inverse, ptq))
    r_q = matrix_subtract(b_q, correction)
    rank_r_on_w_q = rank_fraction(r_q)
    rank_r_on_w_7 = rank_mod(r_q, P7)
    require(
        (rank_r_on_w_q, rank_r_on_w_7) == (1, 1),
        "Schur complement does not have rank one on W",
    )

    # Independently derive the global rational T=A+4I spectrum.
    multiplicity_3 = 54
    multiplicity_minus_4 = 44
    require(
        multiplicity_3 + multiplicity_minus_4 == 98,
        "restricted multiplicities do not sum to 98",
    )
    require(
        14 + 3 * multiplicity_3 - 4 * multiplicity_minus_4 == 0,
        "adjacency trace equation fails",
    )
    rank_t_over_q = 1 + multiplicity_3
    rank_r_over_q = rank_t_over_q - MOTIF_ORDER
    rank_b_on_lambda_q = rank_r_over_q - rank_r_on_w_q
    nullity_b_on_lambda_q = 74 - rank_b_on_lambda_q
    require(
        (rank_b_on_lambda_q, nullity_b_on_lambda_q) == (42, 32),
        "rational projector dimensions drift",
    )

    # In F_7, 2T=S+J, S1=0, and 99=1.  Therefore rank(T)=r+1.
    require((2 * 14 - 99 + 1) % P7 == 0, "S does not kill one")
    require(99 % P7 == 1, "one is unexpectedly isotropic")
    rank_rows: list[dict[str, object]] = []
    for global_rank in GLOBAL_RANK_ROWS:
        rank_t_7 = global_rank + 1
        rank_r_7 = rank_t_7 - MOTIF_ORDER
        local_rank = rank_r_7 - rank_r_on_w_7
        require(local_rank == global_rank - 12, "rank transfer drift")
        require(local_rank <= witt_index, "Witt index excludes a row")

        residual_dimension = 74 - 2 * local_rank
        residual_half_dimension = residual_dimension // 2
        residual_det_character = (
            determinant_character
            * legendre_symbol(pow(-1, local_rank, P7))
        )
        residual_split_character = legendre_symbol(
            pow(-1, residual_half_dimension, P7)
        )
        require(
            residual_det_character != residual_split_character,
            "residual orthogonal type changed from minus",
        )

        ones = local_rank
        sevens = rank_b_on_lambda_q - local_rank
        require(ones >= 0 and sevens >= 0, "invalid Smith exponents")
        rank_rows.append(
            {
                "global_rank_r": global_rank,
                "rank_T_mod_7": rank_t_7,
                "rank_R_mod_7": rank_r_7,
                "local_rank_k": local_rank,
                "witt_capacity": witt_index,
                "excluded": False,
                "snf_nonzero": {"1": ones, "7": sevens},
                "index_U_over_BLambda": f"7^{sevens}",
                "index_Lambda_over_U_plus_K": f"7^{ones}",
                "det_U_times_det_K": (
                    f"7^{2 * ones} * 2^22 * 3^10 * 5^2"
                ),
                "residual_space": f"O^-({residual_dimension},7)",
            }
        )

    # B^2=7B and self-adjointness imply <Bx,By>=7<x,By>, so im(B mod 7)
    # is totally isotropic.  The Smith and index statements below then follow
    # for any integral conditional B with the proved rational dimensions.
    require(
        all(row["local_rank_k"] <= witt_index for row in rank_rows),
        "isotropic dimension overflow",
    )

    return {
        "format": "wave109-independent-verification-v1",
        "verdict": "VERIFIED_SCOPED",
        "scope": (
            "Conditional algebra assuming a hypothetical srg(99,14,1,2) "
            "contains the induced C4 Cartesian K3 motif."
        ),
        "frozen_discovery_inputs": frozen,
        "incidence_lattice": {
            "pattern_histogram": {"0": 3, "1": 48, "2": 36},
            "P_shape": [87, 12],
            "Q_shape": [87, 13],
            "rank_Q_over_Q": 13,
            "unit_minor_rows_found_independently": pivot_rows,
            "unit_minor_determinant": unit_minor,
            "smith_invariant_factors_Q": [1] * 13,
            "Lambda_rank": 74,
            "det_QtQ": q_gram_determinant,
            "det_Lambda": lambda_determinant,
            "factorization": "2^22 * 3^10 * 5^2",
        },
        "orthogonal_space_mod_7": {
            "determinant_mod_7": determinant_mod_7,
            "determinant_legendre_symbol": determinant_character,
            "split_determinant_class_mod_7": split_class,
            "split_class_legendre_symbol": split_character,
            "type": "O^-(74,7)",
            "witt_index": witt_index,
        },
        "conditional_projector": {
            "D_preserves_Lambda": True,
            "reason": "DQ=QE for an exact integral 13 by 13 matrix E",
            "B_squared_equals_7B": True,
            "global_polynomial_check": expanded_t_squared,
            "image_mod_7_totally_isotropic": True,
            "det_H_plus_4I": c_determinant,
            "det_H_plus_4I_mod_7": c_determinant % P7,
            "rank_R_on_W_over_Q": rank_r_on_w_q,
            "rank_R_on_W_mod_7": rank_r_on_w_7,
            "rank_B_on_Lambda_over_Q": rank_b_on_lambda_q,
            "nullity_B_on_Lambda_over_Q": nullity_b_on_lambda_q,
        },
        "rank_transfer": {
            "formula": "rank_F7(B|Lambda)=r-12",
            "rows": rank_rows,
        },
        "smith_index_formulas": {
            "nonzero_snf": "1^k, 7^(42-k), then 0^32",
            "index_U_over_BLambda": "7^(42-k)",
            "index_Lambda_over_U_plus_K": "7^k",
            "determinant_product": (
                "det(U) det(K)=7^(2k) det(Lambda)"
            ),
            "justification": (
                "7U is contained in B Lambda, which is contained in U; "
                "the map x -> Bx mod 7U has kernel U direct_sum K; "
                "U and K are rationally orthogonal."
            ),
        },
        "additional_obstruction_search": {
            "tests": [
                "Witt-index capacity",
                "residual orthogonal sign after removing k hyperbolic planes",
                "nonnegative Smith exponents",
                "conditional determinant/index compatibility",
            ],
            "new_obstruction_found": False,
        },
        "status_wall": {
            "motif_occurrence": "UNKNOWN",
            "full_extension": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
            "rank_rows_excluded": [],
        },
    }


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    require(args.verify or args.output is not None, "choose --verify or --output")
    result = exact_verification()
    if args.output is not None:
        write_json(args.output, result)
    if args.verify:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
