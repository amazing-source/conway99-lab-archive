"""Exact spectral consequences of an induced C4 Cartesian K3 motif.

All computations use Python integers or fractions.  The checker is
conditional: it proves what the 87-vertex principal complement must satisfy
if an srg(99,14,1,2) containing the Wave 105 motif exists.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


ORDER = 87
TYPE_COUNTS = {0: 3, 1: 48, 2: 36}
INTEGER_EIGENVALUES = {
    -4: 32,
    -3: 2,
    -2: 2,
    -1: 1,
    0: 4,
    2: 2,
    3: 42,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def motif_adjacency() -> list[list[int]]:
    """Return H for the 12-vertex Cartesian product C4 square K3."""

    vertices = [(cycle, label) for cycle in range(4) for label in range(3)]
    matrix = [[0] * 12 for _ in range(12)]
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


def determinant(matrix: list[list[Fraction | int]]) -> Fraction:
    """Compute an exact determinant by fraction Gaussian elimination."""

    work = [[Fraction(value) for value in row] for row in matrix]
    order = len(work)
    require(all(len(row) == order for row in work), "matrix is not square")
    result = Fraction(1)
    for column in range(order):
        pivot_row = next(
            (
                row
                for row in range(column, order)
                if work[row][column] != 0
            ),
            None,
        )
        if pivot_row is None:
            return Fraction(0)
        if pivot_row != column:
            work[column], work[pivot_row] = work[pivot_row], work[column]
            result = -result
        pivot = work[column][column]
        result *= pivot
        for target_column in range(column, order):
            work[column][target_column] /= pivot
        for row in range(column + 1, order):
            multiplier = work[row][column]
            if multiplier == 0:
                continue
            for target_column in range(column, order):
                work[row][target_column] -= (
                    multiplier * work[column][target_column]
                )
    return result


def motif_characteristic_value(value: int) -> int:
    """Evaluate the proposed exact characteristic polynomial of H."""

    return (
        (value - 4)
        * (value - 2) ** 2
        * (value - 1) ** 2
        * value
        * (value + 1) ** 4
        * (value + 3) ** 2
    )


def motif_determinant_value(value: int) -> int:
    adjacency = motif_adjacency()
    matrix = [
        [
            value * int(row == column) - adjacency[row][column]
            for column in range(12)
        ]
        for row in range(12)
    ]
    result = determinant(matrix)
    require(result.denominator == 1, "integer determinant became fractional")
    return result.numerator


def residual_characteristic_value(value: int, constant: int = 46) -> int:
    """Evaluate the degree-13 residual factor for the outside graph."""

    return (
        (value * value - 9 * value - constant)
        * (value + 3) ** 2
        * (value + 2) ** 2
        * (value + 1)
        * value**4
        * (value - 2) ** 2
    )


def resolvent_residual_determinant(value: int) -> int:
    """Evaluate (x-14)det((x+1)I+H+2J/(x-14)) exactly."""

    require(value != 14, "resolvent is singular at x=14")
    adjacency = motif_adjacency()
    matrix = [
        [
            Fraction((value + 1) * int(row == column))
            + adjacency[row][column]
            + Fraction(2, value - 14)
            for column in range(12)
        ]
        for row in range(12)
    ]
    result = (value - 14) * determinant(matrix)
    require(result.denominator == 1, "residual determinant is not integral")
    return result.numerator


def quadratic_power_sums(constant: int, cutoff: int) -> dict[int, int]:
    """Power sums for roots of x^2-9x-constant."""

    sums = {0: 2, 1: 9}
    for power in range(2, cutoff + 1):
        sums[power] = 9 * sums[power - 1] + constant * sums[power - 2]
    return sums


def outside_trace(power: int, quadratic_constant: int = 46) -> int:
    quadratic = quadratic_power_sums(quadratic_constant, power)[power]
    integral = sum(
        multiplicity * eigenvalue**power
        for eigenvalue, multiplicity in INTEGER_EIGENVALUES.items()
    )
    return integral + quadratic


def forced_degree_sum() -> int:
    return sum(count * (14 - motif_degree) for motif_degree, count in TYPE_COUNTS.items())


def exact_results() -> dict[str, object]:
    degree_sum = forced_degree_sum()
    traces = {str(power): outside_trace(power) for power in range(1, 5)}
    edges = traces["2"] // 2
    degree_wedges = sum(
        count * ((14 - motif_degree) * (13 - motif_degree) // 2)
        for motif_degree, count in TYPE_COUNTS.items()
    )
    four_cycles = (traces["4"] - 2 * edges - 4 * degree_wedges) // 8
    proposed_trace_two = outside_trace(2, quadratic_constant=38)

    require(sum(TYPE_COUNTS.values()) == ORDER, "type census is not order 87")
    require(degree_sum == 1098, "outside degree sum drift")
    require(traces == {"1": 0, "2": 1098, "3": 1002, "4": 37518}, "trace drift")
    require(edges == 549, "outside edge count drift")
    require(traces["3"] % 6 == 0, "triangle trace is not divisible by six")
    require(four_cycles == 1356, "four-cycle count drift")
    require(proposed_trace_two == 1082, "refuted trace value drift")

    return {
        "format": "wave107-c4boxk3-spectrum-v1",
        "claim_label": "DERIVED",
        "scope": (
            "Conditional on an srg(99,14,1,2) containing the induced "
            "C4 Cartesian K3 motif frozen by Wave 105."
        ),
        "motif": {
            "order": 12,
            "degree": 4,
            "spectrum": {
                "-3": 2,
                "-1": 4,
                "0": 1,
                "1": 2,
                "2": 2,
                "4": 1,
            },
        },
        "resolvent": {
            "global_spectrum": {"-4": 44, "3": 54, "14": 1},
            "q": "(x-3)(x+4)",
            "principal_block": (
                "((x+1)I+H+2J/(x-14))/((x-3)(x+4))"
            ),
            "jacobi_identity_checked_exactly": True,
        },
        "outside_characteristic_polynomial": {
            "factorization": (
                "(x-3)^42 (x+4)^32 (x^2-9x-46) "
                "(x+3)^2 (x+2)^2 (x+1) x^4 (x-2)^2"
            ),
            "quadratic_roots": [
                "(9+sqrt(265))/2",
                "(9-sqrt(265))/2",
            ],
            "wrong_minus_38_factor_refuted": True,
            "wrong_factor_trace_D2": proposed_trace_two,
            "forced_trace_D2": degree_sum,
        },
        "forced_graph_invariants": {
            "degree_counts": {"12": 36, "13": 48, "14": 3},
            "edges": edges,
            "traces": traces,
            "triangles": traces["3"] // 6,
            "four_cycles": four_cycles,
            "nullity_Q_D": 4,
            "rank_Q_D_minus_3I": 45,
            "rank_Q_D_plus_4I": 55,
        },
        "two_main_eigenvalue_structure": {
            "motif_degree_vector_counts": {"0": 3, "1": 48, "2": 36},
            "D_one": "14*one-s",
            "D_s": "24*one-5*s",
            "basis_matrix_columns": [[14, 24], [-1, -5]],
            "basis_characteristic_polynomial": "x^2-9x-46",
            "perron_vector": "(rho+5)*one-s",
            "perron_vector_strictly_positive": True,
            "outside_graph_connected": True,
        },
        "status_wall": {
            "spectral_obstruction_found": False,
            "motif_excluded": False,
            "full_extension": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
    }


def verify_exact(archived_path: Path | None = None) -> dict[str, object]:
    adjacency = motif_adjacency()
    require(
        all(adjacency[row][row] == 0 for row in range(12)),
        "motif has a loop",
    )
    require(
        all(sum(row) == 4 for row in adjacency),
        "motif is not 4-regular",
    )
    require(
        all(
            adjacency[row][column] == adjacency[column][row]
            for row in range(12)
            for column in range(12)
        ),
        "motif adjacency is asymmetric",
    )

    # Both sides below are monic degree-12 polynomials.  Thirteen exact
    # evaluations therefore certify the characteristic polynomial of H.
    for value in range(-6, 7):
        require(
            motif_determinant_value(value)
            == motif_characteristic_value(value),
            f"motif characteristic polynomial mismatch at x={value}",
        )

    # Rank-one dependence on J makes the left side a degree-13 polynomial.
    # Fourteen exact evaluations certify the corrected residual factor.
    for value in range(-7, 7):
        require(
            resolvent_residual_determinant(value)
            == residual_characteristic_value(value, constant=46),
            f"Jacobi residual mismatch at x={value}",
        )

    results = exact_results()
    if archived_path is not None:
        archived = json.loads(archived_path.read_text(encoding="utf-8"))
        require(archived == results, "archived exact results drift")
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    parser.add_argument(
        "--archive",
        type=Path,
        default=Path(__file__).with_name("exact-results.json"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = verify_exact(args.archive if args.verify else None)
    print(json.dumps(results, indent=2, sort_keys=True) + "\n", end="")


if __name__ == "__main__":
    main()
