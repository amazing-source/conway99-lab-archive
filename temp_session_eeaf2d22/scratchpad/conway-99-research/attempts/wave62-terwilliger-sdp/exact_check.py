#!/usr/bin/env python3
"""Exact Wave 62 rooted signed-edge association-scheme calculations.

The hypothetical residual graph is never assumed to have scaffold symmetry.
Only matrices obtained by averaging valid PSD certificates over the rooted
scaffold group are represented in the six-dimensional orbital algebra.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable

F = Fraction

MULTIPLICITIES = [1, 6, 7, 14, 21, 35]
RELATION_NAMES = [
    "identity",
    "same_support_hamming_1",
    "same_support_hamming_2",
    "one_support_index_same_sign",
    "one_support_index_opposite_sign",
    "disjoint_supports",
]
VALENCIES = [1, 2, 1, 20, 20, 40]

# Rows are the six common eigenspaces (multiplicities above), columns are the
# six scaffold orbitals (relations above).
EIGENMATRIX = [
    [1, 2, 1, 20, 20, 40],
    [1, 2, 1, 6, 6, -16],
    [1, 0, -1, 10, -10, 0],
    [1, 2, 1, -4, -4, 4],
    [1, -2, 1, 0, 0, 0],
    [1, 0, -1, -2, 2, 0],
]

# Coefficients of the six primitive idempotents in the orbital basis.
IDEMPOTENT_COEFFICIENTS = [
    [F(1, 84), F(1, 84), F(1, 84), F(1, 84), F(1, 84), F(1, 84)],
    [F(1, 14), F(1, 14), F(1, 14), F(3, 140), F(3, 140), F(-1, 35)],
    [F(1, 12), F(0), F(-1, 12), F(1, 24), F(-1, 24), F(0)],
    [F(1, 6), F(1, 6), F(1, 6), F(-1, 30), F(-1, 30), F(1, 60)],
    [F(1, 4), F(-1, 4), F(1, 4), F(0), F(0), F(0)],
    [F(5, 12), F(0), F(-5, 12), F(-1, 24), F(1, 24), F(0)],
]


def labels() -> list[tuple[int, int, int, int]]:
    """The 84 signed edges of K_7."""
    return [
        (i, j, si, sj)
        for i, j in combinations(range(7), 2)
        for si in (-1, 1)
        for sj in (-1, 1)
    ]


def signed_coordinates(v: tuple[int, int, int, int]) -> frozenset[tuple[int, int]]:
    i, j, si, sj = v
    return frozenset(((i, si), (j, sj)))


def support(v: tuple[int, int, int, int]) -> frozenset[int]:
    return frozenset(v[:2])


def relation(
    u: tuple[int, int, int, int], v: tuple[int, int, int, int]
) -> int:
    if u == v:
        return 0
    support_overlap = len(support(u) & support(v))
    coordinate_overlap = len(signed_coordinates(u) & signed_coordinates(v))
    if support_overlap == 2:
        return 1 if coordinate_overlap == 1 else 2
    if support_overlap == 1:
        return 3 if coordinate_overlap == 1 else 4
    return 5


def fraction_text(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def affine_text(constant: F, y_coefficient: F) -> str:
    if y_coefficient == 0:
        return fraction_text(constant)
    return f"{fraction_text(constant)} + ({fraction_text(y_coefficient)})*y"


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def intersection_tensor() -> list[list[list[int]]]:
    """Return p[r][s][k] with A_r A_s = sum_k p[r][s][k] A_k."""
    vertices = labels()
    representatives: dict[int, list[list[int]]] = {}
    for u in vertices:
        for v in vertices:
            k = relation(u, v)
            counts = [[0] * 6 for _ in range(6)]
            for w in vertices:
                counts[relation(u, w)][relation(w, v)] += 1
            if k in representatives:
                if counts != representatives[k]:
                    raise AssertionError(f"relation {k} is not an orbital")
            else:
                representatives[k] = counts
    if set(representatives) != set(range(6)):
        raise AssertionError("not all six orbitals occur")
    tensor = [[[0] * 6 for _ in range(6)] for _ in range(6)]
    for k in range(6):
        for r in range(6):
            for s in range(6):
                tensor[r][s][k] = representatives[k][r][s]
    return tensor


def verify_association_scheme() -> dict[str, object]:
    vertices = labels()
    if len(vertices) != 84 or len(set(vertices)) != 84:
        raise AssertionError("signed-edge label count is not 84")
    observed_valencies = [
        sum(relation(vertices[0], v) == r for v in vertices) for r in range(6)
    ]
    if observed_valencies != VALENCIES:
        raise AssertionError((observed_valencies, VALENCIES))

    tensor = intersection_tensor()
    for r in range(6):
        for s in range(6):
            if tensor[r][s] != tensor[s][r]:
                raise AssertionError("orbital algebra is not commutative")
            for row in EIGENMATRIX:
                lhs = row[r] * row[s]
                rhs = sum(tensor[r][s][k] * row[k] for k in range(6))
                if lhs != rhs:
                    raise AssertionError(("character failure", r, s, row, lhs, rhs))

    for j, coefficients in enumerate(IDEMPOTENT_COEFFICIENTS):
        for i, row in enumerate(EIGENMATRIX):
            eigenvalue = sum(coefficients[r] * row[r] for r in range(6))
            expected = F(int(i == j))
            if eigenvalue != expected:
                raise AssertionError(("idempotent failure", i, j, eigenvalue))
        if coefficients[0] != F(MULTIPLICITIES[j], 84):
            raise AssertionError(("idempotent diagonal", j, coefficients[0]))

    for r in range(6):
        trace = sum(
            MULTIPLICITIES[i] * EIGENMATRIX[i][r] for i in range(6)
        )
        expected = 84 if r == 0 else 0
        if trace != expected:
            raise AssertionError(("trace orthogonality", r, trace))

    return {
        "order": 84,
        "relation_names": RELATION_NAMES,
        "valencies": VALENCIES,
        "multiplicities": MULTIPLICITIES,
        "eigenmatrix": EIGENMATRIX,
        "intersection_tensor_sha256": canonical_sha256(tensor),
    }


def endpoint_edge_counts(y: int) -> list[int]:
    """Counts of selected unordered residual edges in the six orbitals.

    y is the number of selected same-support/Hamming-two edges.  Wave 3's
    exact relation algebra and endpoint prism prohibition give all five
    off-diagonal counts.
    """
    if not 0 <= y <= 42:
        raise ValueError("y must be an integer in [0,42]")
    return [0, 0, y, 84, 84 - 2 * y, 336 + y]


def endpoint_probabilities(y: F) -> list[F]:
    """Orbital entry probabilities in the scaffold group average."""
    if y < 0 or y > 42:
        raise ValueError("y must lie in [0,42]")
    edge_counts = [F(0), F(0), y, F(84), F(84) - 2 * y, F(336) + y]
    orbit_edge_capacities = [F(84 * v, 2) for v in VALENCIES]
    probabilities = [F(0)]
    for r in range(1, 6):
        probabilities.append(edge_counts[r] / orbit_edge_capacities[r])
    return probabilities


def averaged_b_eigenvalues(y: F) -> list[F]:
    probabilities = endpoint_probabilities(y)
    return [
        sum(F(row[r]) * probabilities[r] for r in range(6))
        for row in EIGENMATRIX
    ]


def projector_coefficients() -> tuple[list[F], list[F]]:
    """Entry coefficients of the eigenvalue-3 and eigenvalue--4 projectors.

    B is 12,-2,0 on the first three scaffold eigenspaces.  On their
    orthogonal complement it has only eigenvalues 3 and -4.  Thus

      P3 = (B + 4I - 16E1 - 2E6 - 4E7)/7.
    """
    fixed = [
        F(4 if r == 0 else 0)
        - 16 * IDEMPOTENT_COEFFICIENTS[0][r]
        - 2 * IDEMPOTENT_COEFFICIENTS[1][r]
        - 4 * IDEMPOTENT_COEFFICIENTS[2][r]
        for r in range(6)
    ]
    p3_nonedge = [value / 7 for value in fixed]
    kernel_idempotent = [
        sum(IDEMPOTENT_COEFFICIENTS[j][r] for j in (3, 4, 5))
        for r in range(6)
    ]
    pm4_nonedge = [
        kernel_idempotent[r] - p3_nonedge[r] for r in range(6)
    ]
    return p3_nonedge, pm4_nonedge


def spectral_projector_data(y: F) -> dict[str, object]:
    beta = averaged_b_eigenvalues(y)
    q_eigenvalues = [
        EIGENMATRIX[i][1] + EIGENMATRIX[i][3] for i in range(6)
    ]
    covariance = [
        F(10) + (F(168) if i == 0 else F(0))
        - F(q_eigenvalues[i])
        - beta[i]
        - beta[i] * beta[i]
        for i in range(6)
    ]
    p3_weights = [F(0), F(0), F(0)] + [
        (beta[i] + 4) / 7 for i in (3, 4, 5)
    ]
    pm4_weights = [F(0), F(0), F(0)] + [
        1 - p3_weights[i] for i in (3, 4, 5)
    ]
    if beta[:3] != [F(12), F(-2), F(0)]:
        raise AssertionError(("fixed eigenspaces", y, beta[:3]))
    if covariance[0:3] != [F(0), F(0), F(0)]:
        raise AssertionError(("variance kernels", y, covariance[:3]))
    if any(value < 0 for value in covariance):
        raise AssertionError(("negative covariance", y, covariance))
    if any(not (0 <= value <= 1) for value in p3_weights + pm4_weights):
        raise AssertionError(("projector weight outside [0,1]", y))
    rank_trace = sum(
        MULTIPLICITIES[i] * p3_weights[i] for i in range(6)
    )
    if rank_trace != 40:
        raise AssertionError(("rank-40 trace", y, rank_trace))
    return {
        "b_bar_eigenvalues": [fraction_text(value) for value in beta],
        "variance_eigenvalues": [fraction_text(value) for value in covariance],
        "p3_weights": [fraction_text(value) for value in p3_weights],
        "pm4_weights": [fraction_text(value) for value in pm4_weights],
        "p3_trace": fraction_text(rank_trace),
    }


def affine_endpoint_probabilities() -> list[tuple[F, F]]:
    """p_r = constant + h*coefficient, where h=y/42."""
    return [
        (F(0), F(0)),
        (F(0), F(0)),
        (F(0), F(1)),
        (F(1, 10), F(0)),
        (F(1, 10), F(-1, 10)),
        (F(1, 5), F(1, 40)),
    ]


def hadamard_schur_scan(max_total_degree: int = 24) -> dict[str, object]:
    """Check an exact bounded family of symmetry-averaged Schur PSD tests.

    For each scaffold primitive idempotent E_s and a+b at most the requested
    degree, average

        E_s o P3^(o a) o P-4^(o b)

    over the scaffold group.  Every orbital coefficient and every block
    eigenvalue is affine in h=y/42, so checking h=0 and h=1 is exact for the
    entire interval.
    """
    if max_total_degree < 0:
        raise ValueError("max_total_degree must be nonnegative")
    p3_nonedge, pm4_nonedge = projector_coefficients()
    kernel_idempotent = [
        sum(IDEMPOTENT_COEFFICIENTS[j][r] for j in (3, 4, 5))
        for r in range(6)
    ]
    p3_values = [
        [p3_nonedge[r], p3_nonedge[r] + F(1, 7)] for r in range(6)
    ]
    pm4_values = [
        [
            kernel_idempotent[r] - p3_values[r][0],
            kernel_idempotent[r] - p3_values[r][1],
        ]
        for r in range(6)
    ]
    probabilities = affine_endpoint_probabilities()

    matrix_count = 0
    endpoint_inequality_count = 0
    zero_count = 0
    negative_records: list[dict[str, object]] = []
    smallest_positive: F | None = None
    smallest_positive_location: dict[str, int] | None = None

    for multiplier in range(6):
        for total_degree in range(max_total_degree + 1):
            for a in range(total_degree + 1):
                b = total_degree - a
                if multiplier == 0 and total_degree == 0:
                    continue
                matrix_count += 1
                coefficients: list[tuple[F, F]] = []
                for r in range(6):
                    values = [
                        IDEMPOTENT_COEFFICIENTS[multiplier][r]
                        * p3_values[r][edge] ** a
                        * pm4_values[r][edge] ** b
                        for edge in (0, 1)
                    ]
                    if r == 0:
                        coefficients.append((values[0], F(0)))
                    else:
                        p0, p1 = probabilities[r]
                        delta = values[1] - values[0]
                        coefficients.append((values[0] + p0 * delta, p1 * delta))

                for block, row in enumerate(EIGENMATRIX):
                    constant = sum(
                        F(row[r]) * coefficients[r][0] for r in range(6)
                    )
                    h_coefficient = sum(
                        F(row[r]) * coefficients[r][1] for r in range(6)
                    )
                    for h_endpoint in (0, 1):
                        endpoint_inequality_count += 1
                        value = constant + h_endpoint * h_coefficient
                        if value < 0:
                            negative_records.append(
                                {
                                    "multiplier": multiplier,
                                    "p3_power": a,
                                    "pm4_power": b,
                                    "block_multiplicity": MULTIPLICITIES[block],
                                    "h_endpoint": h_endpoint,
                                    "value": fraction_text(value),
                                }
                            )
                        elif value == 0:
                            zero_count += 1
                        elif smallest_positive is None or value < smallest_positive:
                            smallest_positive = value
                            smallest_positive_location = {
                                "multiplier": multiplier,
                                "p3_power": a,
                                "pm4_power": b,
                                "block_multiplicity": MULTIPLICITIES[block],
                                "h_endpoint": h_endpoint,
                            }

    if smallest_positive is None:
        raise AssertionError("scan did not produce a positive eigenvalue")
    return {
        "max_total_degree": max_total_degree,
        "primitive_idempotent_multipliers": 6,
        "averaged_matrices": matrix_count,
        "endpoint_block_inequalities": endpoint_inequality_count,
        "negative_eigenvalues": len(negative_records),
        "zero_eigenvalues": zero_count,
        "positive_eigenvalues": endpoint_inequality_count
        - zero_count
        - len(negative_records),
        "smallest_positive": fraction_text(smallest_positive),
        "smallest_positive_location": smallest_positive_location,
        "negative_records": negative_records,
        "interval_checked": "all rational h in [0,1] by affine endpoint checking",
    }


def build_result(max_total_degree: int = 24) -> dict[str, object]:
    scheme = verify_association_scheme()
    for y in range(43):
        counts = endpoint_edge_counts(y)
        if sum(counts) != 504:
            raise AssertionError(("residual edge count", y, counts))
        if 2 * counts[2] + counts[4] != 84:
            raise AssertionError(("Wave 3 orbit identity", y, counts))
        spectral_projector_data(F(y))

    p3_nonedge, pm4_nonedge = projector_coefficients()
    scan = hadamard_schur_scan(max_total_degree)
    endpoint_samples = {
        str(y): spectral_projector_data(F(y)) for y in (0, 21, 42)
    }
    return {
        "format": "wave62-rooted-terwilliger-sdp-v1",
        "role": "proof_b",
        "claim_label": "DERIVED",
        "scope": (
            "Prism-free endpoint n3=4158: scaffold-symmetry averaging of "
            "residual spectral projectors and a bounded Schur/Terwilliger family."
        ),
        "automorphism_policy": (
            "C2 wreath S7 acts only to average universally valid certificates; "
            "no automorphism of a hypothetical completed graph is assumed."
        ),
        "rooted_signed_edge_scheme": scheme,
        "endpoint_orbit_parameter": {
            "name": "y",
            "meaning": (
                "number of selected residual edges joining the two opposite "
                "signed labels on one K7 support"
            ),
            "integer_range": [0, 42],
            "relation_edge_counts": {
                "same_support_hamming_1": "0",
                "same_support_hamming_2": "y",
                "one_support_index_same_sign": "84",
                "one_support_index_opposite_sign": "84-2*y",
                "disjoint_supports": "336+y",
            },
            "known_wave3_identity_recovered": "2*y + e_opposite_sign = 84",
            "new_upper_bound_from_this_identity": False,
        },
        "linear_spectral_projector_sdp": {
            "residual_spectrum": [12, 3, 0, -2, -4],
            "fixed_scaffold_eigenspaces": {
                "multiplicity_6": "B eigenvalue -2",
                "multiplicity_7": "B eigenvalue 0",
            },
            "rank_40_projector_formula": (
                "P3=(B+4I-16E_1-2E_6-4E_7)/7"
            ),
            "p3_nonedge_or_diagonal_coefficients": [
                fraction_text(value) for value in p3_nonedge
            ],
            "pm4_nonedge_or_diagonal_coefficients": [
                fraction_text(value) for value in pm4_nonedge
            ],
            "p3_entry_table": {
                "diagonal": "10/21",
                "same_support_hamming_1": {"nonedge": "-1/21", "edge": "2/21"},
                "same_support_hamming_2": {"nonedge": "0", "edge": "1/7"},
                "one_support_index_same_sign": {
                    "nonedge": "-2/35",
                    "edge": "3/35",
                },
                "one_support_index_opposite_sign": {
                    "nonedge": "-1/105",
                    "edge": "2/15",
                },
                "disjoint_supports": {
                    "nonedge": "-2/105",
                    "edge": "13/105",
                },
            },
            "endpoint_samples": endpoint_samples,
            "exact_feasibility": (
                "The invariant PSD constraints P3_bar>=0 and "
                "E_kernel-P3_bar>=0 hold for every real y in [0,42]."
            ),
            "strict_endpoint_exclusion": False,
        },
        "bounded_hadamard_schur_scan": scan,
        "result": {
            "disposition": "EXACT_NULL_RESULT_FOR_THIS_RELAXATION",
            "strict_n3_upper_bound": "NOT_OBTAINED",
            "endpoint_n3_4158": "UNKNOWN",
            "graph_constructed": False,
            "proof_producing_reduction": (
                "The one-point invariant SDP diagonalizes into six exact "
                "rational scalar blocks; every y=0,...,42 survives."
            ),
            "next_missing_layer": (
                "two-root stabilizer blocks coupling actual edge choices, or "
                "triangle-root flags retaining prism compatibility"
            ),
        },
        "limitations": [
            "This is discovery-agent work and is not independently verified.",
            "The recovered orbit identity is already present in verified Wave 3 relation algebra.",
            "The Schur scan is exhaustive only for the declared monomial family and degree cutoff.",
            "Averaged feasibility is not a residual graph or a lift to the 99-vertex SRG.",
            "No endpoint exclusion, strict upper bound, construction, novelty, or priority claim follows.",
        ],
    }


def verify_frozen(path: Path, max_total_degree: int) -> None:
    expected = json.loads(path.read_text(encoding="utf-8"))
    actual = build_result(max_total_degree)
    if actual != expected:
        raise AssertionError("frozen exact result differs from reconstruction")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-total-degree", type=int, default=24)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.verify:
        verify_frozen(args.verify, args.max_total_degree)
        print(f"PASS: {args.verify}")
    else:
        result = build_result(args.max_total_degree)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            scan = result["bounded_hadamard_schur_scan"]
            print("PASS: exact signed-edge scheme and projector reconstruction")
            print(
                "PASS: "
                f"{scan['endpoint_block_inequalities']} affine endpoint block "
                f"inequalities, {scan['negative_eigenvalues']} negative"
            )
            print("RESULT: exact null result; endpoint and Conway-99 remain UNKNOWN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
