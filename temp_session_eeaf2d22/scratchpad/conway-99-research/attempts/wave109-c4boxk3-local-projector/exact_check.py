"""Exact local-projector consequences of the Wave 105 C4 box K3 motif.

The calculation is conditional on a hypothetical srg(99,14,1,2) containing
the frozen 12-vertex motif.  It uses only Python's standard library and does
not construct the unknown 87-vertex outside graph.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ORDER = 87
MOTIF_ORDER = 12
PRIME = 7
GLOBAL_RANK_ROWS = tuple(range(28, 43, 2))
INPUT_MANIFESTS = {
    "attempts/wave66-spherical-code-shift/package-manifest.sha256":
        "6edc7a5eb2f4a913f9e6af4936984246a75cef8f562167b3d7a99d1a26bbec35",
    "verification/wave66-spherical-code-shift/package-manifest.sha256":
        "a6051ebcfccab0fc9b3f9698f0024cc3284549f5148c9a12a4c6bbe08c786486",
    "attempts/wave105-c4boxk3-extension/package-manifest.sha256":
        "b0fd40eda5a3677d4a835788cea20dfcb9bb3c5764719fc04536893f1b5da4a1",
    "verification/wave105-c4boxk3-extension/package-manifest.sha256":
        "2a24e3e5846558a9e93cd2f103e049816cef7f8dd4a200108643e44cc4c300ae",
    "attempts/wave107-c4boxk3-spectrum/package-manifest.sha256":
        "7e899602825d3cdf989affade8a1e5a6256f17ba911f6351ea8bfe4a3b05d2b0",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def transpose(matrix: list[list[int | Fraction]]) -> list[list[int | Fraction]]:
    return [list(column) for column in zip(*matrix)]


def matmul(
    left: list[list[int | Fraction]],
    right: list[list[int | Fraction]],
) -> list[list[int | Fraction]]:
    require(bool(left) and bool(right), "empty matrix")
    require(len(left[0]) == len(right), "matrix dimension mismatch")
    return [
        [
            sum(left[row][k] * right[k][column] for k in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def matrix_subtract(
    left: list[list[int | Fraction]],
    right: list[list[int | Fraction]],
) -> list[list[int | Fraction]]:
    return [
        [left[i][j] - right[i][j] for j in range(len(left[0]))]
        for i in range(len(left))
    ]


def determinant_bareiss(matrix: list[list[int]]) -> int:
    """Fraction-free exact determinant."""

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
            sign = -sign
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


def rank_mod(matrix: list[list[int | Fraction]], prime: int = PRIME) -> int:
    work: list[list[int]] = []
    for row in matrix:
        converted: list[int] = []
        for value in row:
            fraction = Fraction(value)
            denominator = fraction.denominator % prime
            require(denominator != 0, "denominator vanishes modulo prime")
            converted.append(
                fraction.numerator * pow(denominator, -1, prime) % prime
            )
        work.append(converted)
    rows = len(work)
    columns = len(work[0]) if work else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(pivot_row, rows)
                if work[row][column] % prime
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
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    (work[row][target] - multiplier * work[pivot_row][target])
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
    columns = len(work[0]) if work else 0
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
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            multiplier = work[row][column]
            if multiplier:
                work[row] = [
                    work[row][target] - multiplier * work[pivot_row][target]
                    for target in range(columns)
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


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
    """Independently rebuild the forced Wave 105 incidence multiset."""

    adjacency = motif_adjacency()
    patterns: list[tuple[int, ...]] = [()] * 3
    for vertex in range(MOTIF_ORDER):
        patterns.extend([(vertex,)] * 4)
    for left, right in combinations(range(MOTIF_ORDER), 2):
        internal = sum(
            adjacency[left][vertex] * adjacency[right][vertex]
            for vertex in range(MOTIF_ORDER)
        )
        target = 1 if adjacency[left][right] else 2
        multiplicity = target - internal
        require(multiplicity >= 0, "negative forced pair multiplicity")
        patterns.extend([(left, right)] * multiplicity)
    require(len(patterns) == ORDER, "outside incidence order drift")
    require(
        Counter(map(len, patterns)) == {0: 3, 1: 48, 2: 36},
        "outside incidence histogram drift",
    )
    return tuple(patterns)


def incidence_matrix() -> list[list[int]]:
    matrix = [[0] * MOTIF_ORDER for _ in range(ORDER)]
    for row, pattern in enumerate(forced_patterns()):
        for column in pattern:
            matrix[row][column] = 1
    return matrix


def q_matrix() -> list[list[int]]:
    return [[1] + row for row in incidence_matrix()]


def gram(matrix: list[list[int]]) -> list[list[int]]:
    return [
        [
            sum(matrix[row][left] * matrix[row][right] for row in range(len(matrix)))
            for right in range(len(matrix[0]))
        ]
        for left in range(len(matrix[0]))
    ]


def primitive_minor_rows() -> list[int]:
    """One empty row and one copy of every singleton pattern."""

    return [0] + [3 + 4 * vertex for vertex in range(MOTIF_ORDER)]


def lambda_basis() -> list[list[int]]:
    """Return 74 columns forming an integral basis of ker(Q^T).

    The selected 13-row Q minor consists of [1,0] and [1,e_i], so it has
    determinant one.  Every unselected coordinate therefore gives one basis
    vector with no denominators.
    """

    patterns = forced_patterns()
    pivot_rows = set(primitive_minor_rows())
    columns: list[list[int]] = []
    for free_row in range(ORDER):
        if free_row in pivot_rows:
            continue
        vector = [0] * ORDER
        vector[free_row] = 1
        vector[0] = len(patterns[free_row]) - 1
        for vertex in patterns[free_row]:
            vector[3 + 4 * vertex] = -1
        columns.append(vector)
    require(len(columns) == 74, "Lambda basis rank drift")
    return columns


def exact_results() -> dict[str, object]:
    for relative, expected in INPUT_MANIFESTS.items():
        require(sha256(ROOT / relative) == expected, f"input hash drift: {relative}")

    adjacency = motif_adjacency()
    incidence = incidence_matrix()
    q = q_matrix()
    q_gram = gram(q)
    q_determinant = determinant_bareiss(q_gram)
    expected_determinant = 2**22 * 3**10 * 5**2
    require(q_determinant == expected_determinant, "det(Q^T Q) drift")

    minor_rows = primitive_minor_rows()
    primitive_minor = [q[row] for row in minor_rows]
    require(determinant_bareiss(primitive_minor) == 1, "primitive minor drift")
    require(rank_mod(q) == 13, "Q rank modulo seven drift")

    basis_columns = lambda_basis()
    basis = transpose(basis_columns)
    orthogonality = matmul(transpose(q), basis)
    require(
        all(value == 0 for row in orthogonality for value in row),
        "Lambda basis is not in ker(Q^T)",
    )
    lambda_gram = [
        [
            sum(
                basis_columns[left][coordinate]
                * basis_columns[right][coordinate]
                for coordinate in range(ORDER)
            )
            for right in range(74)
        ]
        for left in range(74)
    ]
    require(
        determinant_bareiss(lambda_gram) == q_determinant,
        "Lambda discriminant identity drift",
    )
    require(rank_mod(lambda_gram) == 74, "Lambda degenerates modulo seven")

    discriminant_mod_seven = q_determinant % PRIME
    require(discriminant_mod_seven == 4, "mod-seven discriminant drift")
    discriminant_is_square = pow(discriminant_mod_seven, 3, PRIME) == 1
    minus_one_is_square = pow(PRIME - 1, 3, PRIME) == 1
    require(discriminant_is_square, "Lambda discriminant should be a square")
    require(not minus_one_is_square, "-1 should be nonsquare over F_7")
    # In dimension 2m, the split determinant class is (-1)^m.  Here m=37.
    require(37 % 2 == 1, "half-dimension parity drift")
    witt_type = "O^-(74,7)"
    witt_index = 36

    identity = [[int(i == j) for j in range(MOTIF_ORDER)] for i in range(MOTIF_ORDER)]
    ones_12 = [[1] * MOTIF_ORDER for _ in range(MOTIF_ORDER)]
    adjacency_square = matmul(adjacency, adjacency)
    incidence_gram = matmul(transpose(incidence), incidence)
    expected_incidence_gram = [
        [
            12 * identity[i][j]
            - adjacency[i][j]
            + 2
            - adjacency_square[i][j]
            for j in range(MOTIF_ORDER)
        ]
        for i in range(MOTIF_ORDER)
    ]
    require(incidence_gram == expected_incidence_gram, "P^T P identity drift")

    c_matrix = [
        [adjacency[i][j] + 4 * identity[i][j] for j in range(MOTIF_ORDER)]
        for i in range(MOTIF_ORDER)
    ]
    c_determinant = determinant_bareiss(c_matrix)
    require(c_determinant == 2332800, "det(H+4I) drift")
    require(c_determinant % PRIME == 1, "motif block singular modulo seven")

    c_inverse_times_g = [
        [
            3 * identity[i][j]
            - adjacency[i][j]
            + Fraction(1, 4)
            for j in range(MOTIF_ORDER)
        ]
        for i in range(MOTIF_ORDER)
    ]
    require(
        matmul(c_matrix, c_inverse_times_g) == incidence_gram,
        "C^{-1} P^T P formula drift",
    )

    motif_degrees = [sum(row) for row in incidence]
    require(Counter(motif_degrees) == {0: 3, 1: 48, 2: 36}, "degree vector drift")
    one_87 = [[1] for _ in range(ORDER)]
    s_column = [[degree] for degree in motif_degrees]
    b_one = [[18 - degree] for degree in motif_degrees]
    p_t_one = matmul(transpose(incidence), one_87)
    require(p_t_one == [[10]] * MOTIF_ORDER, "P^T one drift")
    c_inverse_p_t_one = [[Fraction(5, 4)]] * MOTIF_ORDER
    require(
        matmul(c_matrix, c_inverse_p_t_one) == p_t_one,
        "C^{-1} P^T one drift",
    )
    r_one = matrix_subtract(
        b_one, matmul(incidence, c_inverse_p_t_one)
    )
    u_rational = [[Fraction(2) - Fraction(degree, 4)] for degree in motif_degrees]
    require(r_one == [[9 * row[0]] for row in u_rational], "R one action drift")

    p_three_minus_h = matmul(
        incidence,
        [
            [3 * identity[i][j] - adjacency[i][j] for j in range(MOTIF_ORDER)]
            for i in range(MOTIF_ORDER)
        ],
    )
    b_p = [
        [2 + p_three_minus_h[row][column] for column in range(MOTIF_ORDER)]
        for row in range(ORDER)
    ]
    r_p = matrix_subtract(b_p, matmul(incidence, c_inverse_times_g))
    require(
        r_p == [[row[0]] * MOTIF_ORDER for row in u_rational],
        "R P action drift",
    )
    r_q = [r_one[row] + r_p[row] for row in range(ORDER)]
    require(rank_fraction(r_q) == 1, "R on span(Q) should have rational rank one")
    require(rank_mod(r_q) == 1, "R on span(Q) should have mod-seven rank one")

    # B=D+4I is an integral self-adjoint endomorphism of Lambda.  The global
    # identity (A+4I)^2=7(A+4I)+2J restricts to B^2=7B on Lambda.
    projector_left = {"I": 12 + 16, "A": -1 + 8, "J": 2}
    projector_right = {"I": 28, "A": 7, "J": 2}
    require(projector_left == projector_right, "global projector identity drift")
    global_t_spectrum = {18: 1, 7: 54, 0: 44}
    require(sum(global_t_spectrum.values()) == 99, "global spectrum order drift")
    global_t_rank = sum(
        multiplicity
        for eigenvalue, multiplicity in global_t_spectrum.items()
        if eigenvalue != 0
    )
    rational_schur_rank = global_t_rank - MOTIF_ORDER
    rational_rank = rational_schur_rank - rank_fraction(r_q)
    rational_nullity = 74 - rational_rank
    require((rational_rank, rational_nullity) == (42, 32), "projector dimensions drift")
    require(rational_rank + rational_nullity == 74, "projector dimensions drift")

    rows: list[dict[str, object]] = []
    for global_rank in GLOBAL_RANK_ROWS:
        local_rank = global_rank - 12
        require(local_rank <= witt_index, "Witt bound excludes imported row")
        rows.append(
            {
                "global_rank_r": global_rank,
                "local_rank_k": local_rank,
                "snf_nonzero_factors": {
                    "1": local_rank,
                    "7": rational_rank - local_rank,
                },
                "saturated_image_index_exponent":
                    rational_rank - local_rank,
                "orthogonal_gluing_index_exponent": local_rank,
                "residual_orthogonal_space":
                    f"O^-({74 - 2 * local_rank},7)",
                "excluded": False,
            }
        )
    require([row["local_rank_k"] for row in rows] == list(range(16, 31, 2)), "row transfer drift")

    return {
        "format": "wave109-c4boxk3-local-projector-v1",
        "claim_label": "DERIVED",
        "scope": (
            "Conditional on a hypothetical srg(99,14,1,2) containing the "
            "Wave 105 induced C4 Cartesian K3 motif."
        ),
        "input_manifest_sha256": INPUT_MANIFESTS,
        "incidence_lattice": {
            "P_shape": [87, 12],
            "Q_definition": "[one P]",
            "Q_shape": [87, 13],
            "rank_Q_over_Q": 13,
            "rank_Q_mod_7": 13,
            "primitive_minor_rows_zero_based": minor_rows,
            "primitive_minor_determinant": 1,
            "smith_invariant_factors_Q": [1] * 13,
            "Lambda_definition": "ker_Z(Q^T)",
            "Lambda_rank": 74,
            "Lambda_gram_determinant": q_determinant,
            "Lambda_gram_determinant_factorization": "2^22 * 3^10 * 5^2",
        },
        "mod_seven_orthogonal_space": {
            "gram_determinant_mod_7": discriminant_mod_seven,
            "gram_determinant_square": discriminant_is_square,
            "split_determinant_class": "-1, a nonsquare in F_7",
            "type": witt_type,
            "witt_index": witt_index,
            "correction": (
                "The space is non-split O^-, not split O^+: in dimension "
                "74=2*37 the split determinant class is (-1)^37=-1, "
                "which is nonsquare over F_7, while det(Lambda)=4 is square."
            ),
        },
        "local_projector": {
            "D_preserves_Lambda": True,
            "B_definition": "B=D+4I on Lambda",
            "identity": "B^2=7B",
            "rational_rank": rational_rank,
            "rational_nullity": rational_nullity,
            "image_mod_7_totally_isotropic": True,
            "motif_block_C": "H+4I",
            "motif_block_determinant": c_determinant,
            "motif_block_determinant_mod_7": c_determinant % PRIME,
        },
        "rank_transfer": {
            "global_parameter": "r=rank_F7(2A-J+I)",
            "identity": "rank_F7(B|Lambda)=r-12",
            "schur_rank_chain": [
                "rank_F7(A+4I)=r+1",
                "rank_F7(A+4I)=12+rank_F7(R)",
                "rank_F7(R)=1+rank_F7(B|Lambda)",
            ],
            "imported_global_rows": list(GLOBAL_RANK_ROWS),
            "local_rows": list(range(16, 31, 2)),
        },
        "smith_and_index_consequences": {
            "U_definition": "Lambda intersect im_Q(B)",
            "K_definition": "Lambda intersect ker_Q(B)",
            "general_nonzero_snf":
                "1^k, 7^(42-k), followed by 0^32",
            "general_saturated_image_index": "[U:B Lambda]=7^(42-k)",
            "general_gluing_index": "[Lambda:U direct_sum K]=7^k",
            "general_discriminant_relation":
                "det(U) det(K)=7^(2k) det(Lambda)",
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


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    require(args.verify or args.output is not None, "use --verify and/or --output")
    result = exact_results()
    if args.output is not None:
        write_json(args.output, result)
    if args.verify:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
