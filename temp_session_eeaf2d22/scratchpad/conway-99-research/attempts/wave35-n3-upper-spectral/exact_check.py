#!/usr/bin/env python3
"""Exact endpoint checks for the n3=4158 signed-projector relaxation.

This is a discovery-side arithmetic checker.  It does not construct a
231-by-231 matrix and it does not certify that such a matrix, an incidence
geometry, or a Conway graph exists.  Its purpose is to:

* freeze the exact endpoint algebra;
* record two new Smith/orthogonal-reflection consequences;
* replay the inherited mixed-Schur inequalities at the endpoint; and
* exhibit exact scalar and local-block controls for routes that do not
  contradict the endpoint.

Only the Python standard library is used.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


N_TRIANGLES = 231
RANK = 44
SCALE = 21
N3_ENDPOINT = 4158
Q_ENDPOINT = 12

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WAVE20_RESULTS = REPO / "attempts" / "wave20-global-obstruction" / "exact-checks.json"


class CheckError(AssertionError):
    """Raised when a frozen exact premise or consequence fails."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckError(message)


def ftext(value: Fraction | int) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def parse_affine(text: str, n3: int) -> Fraction:
    """Evaluate strings of the accepted form ``a + (b)*n3`` exactly."""

    marker = " + ("
    suffix = ")*n3"
    require(marker in text and text.endswith(suffix), f"bad affine string: {text}")
    constant, coefficient = text.split(marker, 1)
    coefficient = coefficient[: -len(suffix)]
    return Fraction(constant) + Fraction(coefficient) * n3


def determinant_bareiss(matrix: Sequence[Sequence[int]]) -> int:
    """Return an exact integer determinant using fraction-free elimination."""

    size = len(matrix)
    require(all(len(row) == size for row in matrix), "determinant matrix not square")
    work = [list(map(int, row)) for row in matrix]
    sign = 1
    previous = 1
    for column in range(size - 1):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        for row in range(column + 1, size):
            for other in range(column + 1, size):
                numerator = (
                    work[row][other] * pivot_value
                    - work[row][column] * work[column][other]
                )
                require(numerator % previous == 0, "Bareiss division was not exact")
                work[row][other] = numerator // previous
        previous = pivot_value
        for row in range(column + 1, size):
            work[row][column] = 0
    return sign * work[-1][-1]


def endpoint_profile(q_value: int = Q_ENDPOINT) -> dict[str, int]:
    """Return the fixed-triangle profile and reject a mutated endpoint."""

    require(q_value == Q_ENDPOINT, "this checker is frozen to q=12")
    profile = {
        "r0_plus": 20 + q_value,
        "r1_zero": 180 - 3 * q_value,
        "r2_minus": 3 * q_value,
        "r3_minus_two": 12 - q_value,
        "intersect_zero": 18,
    }
    require(profile == {
        "r0_plus": 32,
        "r1_zero": 144,
        "r2_minus": 36,
        "r3_minus_two": 0,
        "intersect_zero": 18,
    }, "endpoint row profile changed")
    require(4 + profile["r0_plus"] - profile["r2_minus"] == 0,
            "M row sum is not zero")
    require(
        4 * 4 + profile["r0_plus"] + profile["r2_minus"] == SCALE * 4,
        "M row norm does not match M^2=21M",
    )
    return profile


def signed_matrix_algebra(profile: dict[str, int]) -> dict[str, object]:
    """Check the formal S=M-4I two-eigenvalue algebra."""

    plus = profile["r0_plus"]
    minus = profile["r2_minus"]
    zero = profile["r1_zero"] + profile["intersect_zero"]
    require((plus, minus, zero) == (32, 36, 162), "S row alphabet changed")

    # M has eigenvalues 21^44 and 0^187.  Therefore S=M-4I has
    # eigenvalues 17^44 and (-4)^187.
    negative_multiplicity = N_TRIANGLES - RANK
    require(17 * RANK - 4 * negative_multiplicity == 0, "trace(S) is not zero")
    require(
        17 * 17 * RANK + 4 * 4 * negative_multiplicity
        == N_TRIANGLES * (plus + minus),
        "trace(S^2) does not match the row support",
    )

    # (M-4I)^2=21M-8M+16I=13S+68I.
    require(13 * (-4) + 68 == (-4) ** 2, "S polynomial fails at -4")
    require(13 * 17 + 68 == 17 ** 2, "S polynomial fails at 17")
    return {
        "definition": "S=M-4I",
        "row_profile": {"+1": plus, "-1": minus, "0": zero},
        "row_sum": plus - minus,
        "row_squared_norm": plus + minus,
        "identity": "S^2=13S+68I",
        "spectrum": {"17": RANK, "-4": negative_multiplicity},
        "absolute_determinant": str(17**RANK * 4**negative_multiplicity),
    }


def smith_form_of_s() -> dict[str, object]:
    """Derive the exact Smith invariants of S from endpoint data."""

    negative_multiplicity = N_TRIANGLES - RANK

    # S(S-13I)=68I, so every invariant factor divides 68.  The characteristic
    # determinant and rank_F2(S)=rank_F2(M)=44 fix the valuations.
    factors = [1] * 44 + [4] * 143 + [68] * 44
    require(len(factors) == N_TRIANGLES, "wrong Smith length")
    require(all(68 % factor == 0 for factor in factors), "Smith factor does not divide 68")
    require(all(right % left == 0 for left, right in zip(factors, factors[1:])),
            "Smith divisibility chain fails")
    require(sum(factor % 2 for factor in factors) == RANK,
            "Smith form has wrong rank modulo two")
    require(
        product(factors) == 17**RANK * 4**negative_multiplicity,
        "Smith product does not match |det S|",
    )

    # The rank_F2 input itself follows from rank_Q(M)=44 and the odd sum
    # 21^44 of all principal 44-minors.
    require((21**RANK) % 2 == 1, "top-principal-minor sum lost odd parity")
    return {
        "identity_implying_exponent": "S(S-13I)=68I",
        "rank_F2_S": RANK,
        "snf": "diag(1^44,4^143,68^44)",
        "factor_counts": {"1": 44, "4": 143, "68": 44},
        "derivation_boundary": (
            "This is forced for any endpoint S; it is not an existence "
            "certificate or a contradiction."
        ),
    }


def product(values: Iterable[int]) -> int:
    answer = 1
    for value in values:
        answer *= value
    return answer


def orthogonal_reflection(profile: dict[str, int]) -> dict[str, object]:
    """Check C=2S-13I=2M-21I and C^2=441I."""

    plus = profile["r0_plus"]
    minus = profile["r2_minus"]
    diagonal = -13
    row_sum = diagonal + 2 * plus - 2 * minus
    row_norm = diagonal * diagonal + 4 * (plus + minus)
    require(row_sum == -21, "C row sum changed")
    require(row_norm == 441, "C row norm changed")
    require((2 * 17 - 13) == 21, "C positive eigenvalue changed")
    require((2 * (-4) - 13) == -21, "C negative eigenvalue changed")
    return {
        "definition": "C=2S-13I=2M-21I",
        "identity": "C^2=441I",
        "diagonal": diagonal,
        "off_diagonal_profile": {"+2": plus, "-2": minus, "0": 162},
        "row_sum": row_sum,
        "row_squared_norm": row_norm,
        "spectrum": {"+21": RANK, "-21": N_TRIANGLES - RANK},
        "interpretation": (
            "C/21 is a rational orthogonal involution; this reformulation "
            "does not itself exclude the endpoint."
        ),
    }


def schur_power_collapse() -> dict[str, object]:
    """Check the endpoint formulas for every parity of Schur power."""

    checks: dict[str, object] = {}
    for exponent in range(1, 10):
        if exponent % 2:
            shift = 4**exponent - 4
            # Off diagonal 0,+/-1 is unchanged by an odd power.
            require(4 + shift == 4**exponent, "odd Schur diagonal mismatch")
            require(1**exponent == 1 and (-1) ** exponent == -1,
                    "odd Schur off-diagonal mismatch")
            minimum_eigenvalue = shift
            checks[str(exponent)] = {
                "formula": f"M+{shift}I",
                "eigen_on_im_M": SCALE + shift,
                "eigen_on_ker_M": shift,
                "positive_semidefinite": minimum_eigenvalue >= 0,
            }
        else:
            shift = 4**exponent - 16
            require(16 + shift == 4**exponent, "even Schur diagonal mismatch")
            require(1**exponent == 1 and (-1) ** exponent == 1,
                    "even Schur off-diagonal mismatch")
            checks[str(exponent)] = {
                "formula": f"W+{shift}I",
                "positive_semidefinite_from_W": shift >= 0,
            }
    require(checks["3"]["formula"] == "M+60I", "Schur cube did not collapse")
    require(checks["3"]["eigen_on_im_M"] == 81, "Schur-cube image eigenvalue changed")
    require(checks["3"]["eigen_on_ker_M"] == 60, "Schur-cube kernel eigenvalue changed")
    return {
        "odd_formula": "M^(o k)=M+(4^k-4)I for odd k",
        "even_formula": "M^(o k)=W+(4^k-16)I for even k>=2",
        "cube": "M^(o3)=M+60I is positive definite",
        "checks_1_through_9": checks,
    }


def mixed_schur_endpoint() -> dict[str, object]:
    """Replay every accepted primitive-projector Schur triple at n3=4158."""

    payload = json.loads(WAVE20_RESULTS.read_text(encoding="utf-8"))
    triples = payload["mixed_schur_triples"]
    evaluated = {key: parse_affine(value, N3_ENDPOINT) for key, value in triples.items()}
    require(len(evaluated) == 40, "expected forty mixed Schur triples")
    require(all(value >= 0 for value in evaluated.values()),
            "a mixed Schur triple is negative at n3=4158")
    positive = [value for value in evaluated.values() if value > 0]
    return {
        "source": WAVE20_RESULTS.relative_to(REPO).as_posix(),
        "triple_count": len(evaluated),
        "negative_count": sum(value < 0 for value in evaluated.values()),
        "zero_count": sum(value == 0 for value in evaluated.values()),
        "smallest_positive": ftext(min(positive)),
        "e000": ftext(evaluated["0,0|0"]),
        "e007": ftext(evaluated["0,0|7"]),
        "verdict": "ALL_NONNEGATIVE_NO_ENDPOINT_OBSTRUCTION",
    }


def support_compression() -> dict[str, object]:
    """Check exact projector traces and the remaining Frobenius slack for B."""

    # B=M o M-16I is the unsigned support graph of S.
    dimensions = {"18": 1, "7": 54, "0": 44, "-3": 132}
    trace_w = {
        "18": Fraction(84),
        "7": Fraction(3672, 5),
        "0": Fraction(660),
        "-3": Fraction(11088, 5),
    }
    trace_b = {
        key: trace_w[key] - 16 * dimensions[key]
        for key in dimensions
    }
    require(trace_b == {
        "18": Fraction(68),
        "7": Fraction(-648, 5),
        "0": Fraction(-44),
        "-3": Fraction(528, 5),
    }, "B projector traces changed")
    require(sum(trace_b.values()) == 0, "trace(B) is not zero")

    trace_b2 = N_TRIANGLES * 68
    cauchy_floor = sum(
        trace_b[key] ** 2 / dimensions[key]
        for key in dimensions
    )
    slack = Fraction(trace_b2) - cauchy_floor
    require(cauchy_floor == Fraction(126588, 25), "compression floor changed")
    require(slack == Fraction(266112, 25) and slack > 0,
            "compression traces unexpectedly exhaust B's Frobenius norm")

    return {
        "definition": "B=M o M-16I=S o S",
        "regular_degree": 68,
        "edge_count": N_TRIANGLES * 68 // 2,
        "trace_B2": trace_b2,
        "projector_traces": {key: ftext(value) for key, value in trace_b.items()},
        "cauchy_frobenius_floor": ftext(cauchy_floor),
        "unallocated_frobenius_slack": ftext(slack),
        "verdict": "TRACE_AND_INTERLACING_RELAXATION_FEASIBLE",
    }


def incidence_support_bounds() -> dict[str, object]:
    """Check exact incidence profiles and a failed Frobenius-bound route."""

    # For a fixed triangle T, entries of M N^T are 4 on its three points,
    # -2 on the 36 points adjacent to one T-point, and +1 on the remaining
    # 60 points.  Subtracting 4N^T gives S N^T.
    m_profile = {"4": 3, "-2": 36, "1": 60}
    s_profile = {"0": 3, "-2": 36, "1": 60}
    require(3 * 4 + 36 * (-2) + 60 == 0, "MN^T row sum changed")
    require(36 * 4 + 60 == 204, "SN^T row norm changed")

    # For D=B N^T, the same three point classes have values
    # 0, 2, and 1+2t_x (0<=t_x<=3).  Double counting B-neighbor triangle
    # incidences gives sum t_x=36 over the 60 final points.
    t_sum = 36
    minimum_none = 36 * 3**2 + 24 * 1**2
    maximum_none = 12 * 7**2 + 48 * 1**2
    row_square_min = 36 * 2**2 + minimum_none
    row_square_max = 36 * 2**2 + maximum_none
    require((row_square_min, row_square_max) == (492, 780),
            "local support-square range changed")

    global_min = N_TRIANGLES * row_square_min
    global_max = N_TRIANGLES * row_square_max

    # Spectrally,
    # ||BN^T||_F^2=97104+10*x_7+3*x_0,
    # x_theta=tr(E_theta B^2).  Projector trace Cauchy gives the floors below.
    x7_floor = Fraction(648, 5) ** 2 / 54
    x0_floor = Fraction(44) ** 2 / 44
    spectral_floor = Fraction(97104) + 10 * x7_floor + 3 * x0_floor
    require(x7_floor == Fraction(7776, 25), "x7 floor changed")
    require(spectral_floor == Fraction(501732, 5), "incidence spectral floor changed")
    require(spectral_floor < global_min, "failed route unexpectedly contradicts endpoint")

    # An exact scalar energy allocation reaches the local lower boundary and
    # respects all three compression Cauchy floors.  It is not a matrix.
    scalar_x7 = Fraction(8208, 5)
    scalar_x0 = Fraction(44)
    scalar_xminus3 = Fraction(46992, 5)
    require(
        scalar_x7 + scalar_x0 + scalar_xminus3 == 11084,
        "scalar energy allocation has wrong nontrivial total",
    )
    require(scalar_x7 >= x7_floor, "scalar x7 violates its Cauchy floor")
    require(
        scalar_xminus3 >= Fraction(528, 5) ** 2 / 132,
        "scalar x-3 violates its Cauchy floor",
    )
    require(
        Fraction(97104) + 10 * scalar_x7 + 3 * scalar_x0 == global_min,
        "scalar energy allocation misses local lower boundary",
    )

    return {
        "MN_transpose_entry_profile": m_profile,
        "SN_transpose_entry_profile": s_profile,
        "BN_transpose_local_form": {
            "on_T": 0,
            "adjacent_to_T": 2,
            "nonadjacent_to_T": "1+2t_x, 0<=t_x<=3",
            "sum_t_x_over_60": t_sum,
        },
        "per_row_square_range": [row_square_min, row_square_max],
        "global_square_range": [global_min, global_max],
        "projector_cauchy_floor": ftext(spectral_floor),
        "gap_to_local_floor": ftext(Fraction(global_min) - spectral_floor),
        "scalar_energy_control": {
            "x7": ftext(scalar_x7),
            "x0": ftext(scalar_x0),
            "x_minus3": ftext(scalar_xminus3),
            "attained_value": global_min,
            "is_matrix_or_graph": False,
        },
        "verdict": "FROBENIUS_ROUTE_HAS_EXACT_SCALAR_SURVIVOR",
    }


def cycle_adjacency(lengths: Sequence[int]) -> list[list[int]]:
    size = sum(lengths)
    matrix = [[0] * size for _ in range(size)]
    offset = 0
    for length in lengths:
        require(length >= 4 and length % 2 == 0, "invalid bipartite cycle length")
        for index in range(length):
            left = offset + index
            right = offset + ((index + 1) % length)
            matrix[left][right] = matrix[right][left] = 1
        offset += length
    return matrix


def adjacent_vertex_blocks() -> dict[str, object]:
    """Check all cycle partitions for the adjacent-vertex incidence block."""

    partitions = ((12,), (8, 4), (6, 6), (4, 4, 4))
    determinants: dict[str, int] = {}
    for partition in partitions:
        adjacency = cycle_adjacency(partition)
        require(all(sum(row) == 2 for row in adjacency), "cycle union is not 2-regular")
        gram = [
            [4 * (row == column) - adjacency[row][column] for column in range(12)]
            for row in range(12)
        ]
        determinant = determinant_bareiss(gram)
        require(determinant > 0, "adjacent-vertex local Gram block is not positive")
        determinants["+".join(map(str, partition))] = determinant
    return {
        "cross_block": (
            "negative incidence matrix of two disjoint perfect matchings; "
            "the union is a 2-regular bipartite graph"
        ),
        "operator_norm_upper": 2,
        "local_gram_minimum_eigenvalue_lower": 2,
        "cycle_partition_determinants": determinants,
        "verdict": "ALL_ADJACENT_LOCAL_BLOCKS_SURVIVE",
    }


def nonadjacent_control_block() -> dict[str, object]:
    """Give an exact 7x7 control for the nonadjacent-vertex local constraints."""

    cross = [[0] * 7 for _ in range(7)]
    negative = ((0, 1), (1, 0), (0, 2), (1, 3), (4, 0), (5, 1))
    positive = ((2, 2), (3, 3), (4, 2), (4, 4), (5, 3), (5, 5), (6, 6))
    for row, column in negative:
        cross[row][column] = -1
    for row, column in positive:
        require(cross[row][column] == 0, "control entry assigned twice")
        cross[row][column] = 1

    row_sums = [sum(row) for row in cross]
    column_sums = [sum(cross[row][column] for row in range(7)) for column in range(7)]
    require(row_sums == [-2, -2, 1, 1, 1, 1, 1], "control row sums changed")
    require(column_sums == [-2, -2, 1, 1, 1, 1, 1], "control column sums changed")
    require(cross[0][0] == cross[1][1] == 0, "shared-neighbor zero cells changed")
    require(cross[0][1] == cross[1][0] == -1, "forced two-cross-edge cells changed")
    frobenius_square = sum(value * value for row in cross for value in row)
    require(frobenius_square == 13 and frobenius_square < 16,
            "control no longer certifies ||C||_2<4")

    # For [[4I,C],[C^T,4I]], ||C||_2<=||C||_F<4 proves positive definiteness.
    return {
        "matrix": cross,
        "row_sums": row_sums,
        "column_sums": column_sums,
        "frobenius_squared": frobenius_square,
        "operator_norm_strictly_below": 4,
        "block_gram": "[[4I,C],[C^T,4I]] is positive definite",
        "scope": (
            "This is a local incidence/PSD control only.  It does not satisfy "
            "the global M^2=21M equations and is not a partial graph."
        ),
    }


def principal_minor_target() -> dict[str, object]:
    """Record the exact 45-row obstruction target supplied by rank 44."""

    require(RANK + 1 == 45, "principal-minor target size changed")
    require(4 - 3 > 0, "Gershgorin sufficient condition changed")
    return {
        "universal_endpoint_fact": (
            "Every 45x45 principal submatrix M[X] is singular, equivalently "
            "S[X] has eigenvalue -4."
        ),
        "sufficient_contradiction_target": (
            "Find 45 triangle indices with maximum internal absolute S-degree "
            "at most 3; then 4I+S[X] is strictly diagonally dominant and "
            "positive definite."
        ),
        "status": "TARGET_NOT_CONSTRUCTED",
    }


def build_results() -> dict[str, object]:
    profile = endpoint_profile()
    return {
        "schema_version": 1,
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": (
            "Exact consequences and failed obstruction routes for the "
            "conditional endpoint n3=4158"
        ),
        "parameters": {
            "n3": N3_ENDPOINT,
            "q_per_triangle": Q_ENDPOINT,
            "triangle_count": N_TRIANGLES,
            "rank_M": RANK,
            "M_scale": SCALE,
        },
        "endpoint_profile": profile,
        "signed_matrix": signed_matrix_algebra(profile),
        "smith_form_S": smith_form_of_s(),
        "orthogonal_reflection": orthogonal_reflection(profile),
        "schur_power_collapse": schur_power_collapse(),
        "mixed_schur_endpoint": mixed_schur_endpoint(),
        "support_compression": support_compression(),
        "incidence_support_bounds": incidence_support_bounds(),
        "adjacent_vertex_blocks": adjacent_vertex_blocks(),
        "nonadjacent_control_block": nonadjacent_control_block(),
        "principal_minor_target": principal_minor_target(),
        "conclusion": {
            "endpoint_excluded": False,
            "upper_bound_improved_below_4158": False,
            "strongest_rigorous_general_upper_bound": 4158,
            "next_exact_target": (
                "Use global incidence compatibility to force a forbidden "
                "45-row principal block or another nonlocal obstruction."
            ),
            "target_status": "UNKNOWN",
        },
        "limitations": [
            "No 231x231 endpoint matrix is constructed.",
            "No scalar or local control is a graph or partial graph.",
            "The Smith and reflection identities restrict a putative endpoint but do not exclude it.",
            "This discovery-side checker does not self-certify its mathematical interpretation.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    arguments = parser.parse_args()

    results = build_results()
    rendered = json.dumps(results, indent=2, sort_keys=True) + "\n"
    if arguments.verify is not None:
        expected = arguments.verify.read_text(encoding="utf-8")
        require(expected == rendered, "verification artifact differs from exact regeneration")
    if arguments.output is not None:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    elif arguments.verify is None:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
