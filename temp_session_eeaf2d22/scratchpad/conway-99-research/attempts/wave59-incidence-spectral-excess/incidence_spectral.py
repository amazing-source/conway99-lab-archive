#!/usr/bin/env python3
"""Exact discovery calculations for Wave 59.

All calculations are conditional on the frozen prism-free target parameters.
No target graph is constructed and no discovery result is self-verifying.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
from fractions import Fraction
from pathlib import Path
from typing import Iterable


Spectrum = tuple[tuple[int, int], ...]
Polynomial = tuple[Fraction, ...]


def free_memory_percent() -> float:
    if os.name == "nt":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.dwLength = ctypes.sizeof(MemoryStatus)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return 100.0 * status.ullAvailPhys / status.ullTotalPhys

    info: dict[str, int] = {}
    with open("/proc/meminfo", encoding="ascii") as handle:
        for line in handle:
            key, value = line.split(":", 1)
            info[key] = int(value.strip().split()[0])
    return 100.0 * info["MemAvailable"] / info["MemTotal"]


def require_memory(floor: float = 15.0) -> float:
    observed = free_memory_percent()
    if observed < floor:
        raise MemoryError(
            f"free physical memory {observed:.2f}% is below floor {floor:.2f}%"
        )
    return observed


def trim(poly: Iterable[Fraction]) -> Polynomial:
    values = list(poly)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    return trim(
        (left[index] if index < len(left) else Fraction(0))
        + (right[index] if index < len(right) else Fraction(0))
        for index in range(size)
    )


def poly_scale(poly: Polynomial, scalar: Fraction) -> Polynomial:
    return trim(value * scalar for value in poly)


def poly_eval(poly: Polynomial, value: int | Fraction) -> Fraction:
    result = Fraction(0)
    for coefficient in reversed(poly):
        result = result * value + coefficient
    return result


def spectrum_inner(
    left: Polynomial, right: Polynomial, spectrum: Spectrum
) -> Fraction:
    order = sum(multiplicity for _, multiplicity in spectrum)
    return sum(
        Fraction(multiplicity, order)
        * poly_eval(left, eigenvalue)
        * poly_eval(right, eigenvalue)
        for eigenvalue, multiplicity in spectrum
    )


def predistance_polynomials(spectrum: Spectrum) -> tuple[Polynomial, ...]:
    valency = spectrum[0][0]
    polynomials: list[Polynomial] = []
    for degree in range(len(spectrum)):
        q: Polynomial = tuple(
            Fraction(int(index == degree)) for index in range(degree + 1)
        )
        for previous in polynomials:
            coefficient = spectrum_inner(q, previous, spectrum) / spectrum_inner(
                previous, previous, spectrum
            )
            q = poly_add(q, poly_scale(previous, -coefficient))
        norm = spectrum_inner(q, q, spectrum)
        scale = poly_eval(q, valency) / norm
        p = poly_scale(q, scale)
        if spectrum_inner(p, p, spectrum) != poly_eval(p, valency):
            raise AssertionError("predistance normalization failed")
        polynomials.append(p)
    return tuple(polynomials)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def polynomial_record(poly: Polynomial) -> dict[str, object]:
    return {
        "coefficients_low_to_high": [fraction_text(value) for value in poly],
        "degree": len(poly) - 1,
    }


def triangle_relations() -> dict[str, object]:
    total_lines = 231
    root = 1
    relation_k = 3 * 6
    disjoint = total_lines - root - relation_k

    # There are 36 edges from the root triangle to outside points. Each
    # outside endpoint lies in six additional triangles, producing 216
    # cross-edge/line incidences.
    cross_edge_incidences = 3 * 12 * 6

    # Between each two of the three 12-point neighbor sectors there is a
    # perfect matching, because mu=2 supplies one common neighbor in addition
    # to the third root point. Prism-freeness makes the resulting 36 edges
    # belong to 36 distinct B triangles.
    relation_b = 3 * 12
    relation_c = cross_edge_incidences - 2 * relation_b
    relation_d = disjoint - relation_b - relation_c

    if (relation_k, relation_b, relation_c, relation_d) != (18, 36, 144, 32):
        raise AssertionError("triangle relation census failed")
    return {
        "valencies": {
            "I": root,
            "K": relation_k,
            "B": relation_b,
            "C": relation_c,
            "D": relation_d,
        },
        "disjoint_total": disjoint,
        "cross_edge_incidences": cross_edge_incidences,
        "cross_edge_equation": "2*B + C = 216",
        "B_derivation": "three 12-edge cross-sector perfect matchings",
        "automorphism_assumed": False,
    }


def incidence_graph_record() -> dict[str, object]:
    relation = triangle_relations()["valencies"]
    point_layers = [1, 7, 14, 84, 84, 140]
    line_layers = [1, 3, 18, 36, 180, 60, 32]

    point_edge_balances = [
        point_layers[0] * 7 == point_layers[1] * 1,
        point_layers[1] * 2 == point_layers[2] * 1,
        point_layers[2] * 6 == point_layers[3] * 1,
        point_layers[3] * 2 == point_layers[4] * 2,
        point_layers[4] * 5 == point_layers[5] * 3,
    ]
    line_edge_balances = [
        line_layers[0] * 3 == line_layers[1] * 1,
        line_layers[1] * 6 == line_layers[2] * 1,
        line_layers[2] * 2 == line_layers[3] * 1,
        line_layers[3] * 6
        == relation["B"] * 2 + relation["C"] * 1,
        relation["B"] * 1 + relation["C"] * 2
        == line_layers[5] * Fraction(27, 5),
        line_layers[5] * Fraction(8, 5) == line_layers[6] * 3,
    ]
    if not all(point_edge_balances + line_edge_balances):
        raise AssertionError("distance-layer edge balance failed")

    incidence_spectrum = [
        {"eigenvalue": "sqrt(21)", "multiplicity": 1},
        {"eigenvalue": "sqrt(10)", "multiplicity": 54},
        {"eigenvalue": "sqrt(3)", "multiplicity": 44},
        {"eigenvalue": "0", "multiplicity": 132},
        {"eigenvalue": "-sqrt(3)", "multiplicity": 44},
        {"eigenvalue": "-sqrt(10)", "multiplicity": 54},
        {"eigenvalue": "-sqrt(21)", "multiplicity": 1},
    ]
    trace_square = 2 * (21 + 54 * 10 + 44 * 3)
    if trace_square != 2 * 693:
        raise AssertionError("incidence spectrum trace-square failed")

    return {
        "bipartition": {
            "points": 99,
            "triangles": 231,
            "point_degree": 7,
            "triangle_degree": 3,
            "incidences": 693,
        },
        "matrix_identity": "N*N^T = A + 7I",
        "connected": True,
        "spectrum": incidence_spectrum,
        "zero_multiplicity": 132,
        "trace_square": trace_square,
        "girth": 8,
        "diameter": 6,
        "point_root": {
            "distance_layers": point_layers,
            "eccentricity": 5,
            "intersection_array": {
                "b": [7, 2, 6, 2, 5],
                "c": [1, 1, 1, 2, 3],
            },
            "distance_regular_around_every_point": True,
        },
        "triangle_root": {
            "distance_layers": line_layers,
            "line_relations_at_distance_4": {
                "B": relation["B"],
                "C": relation["C"],
            },
            "distance_4_predecessors": {"B": 2, "C": 1},
            "distance_5_average_predecessors": "27/5",
            "distance_5_average_successors": "8/5",
            "distance_regular_around_triangle": False,
        },
        "distance_biregular": False,
        "fiol_theorem_6_case": {
            "case": "c",
            "d": 6,
            "d_plus_1_distinct_eigenvalues": 7,
            "larger_part_size": 231,
            "smaller_part_size": 99,
            "m_zero": 132,
            "larger_minus_smaller": 132,
            "ordinary_regular_spectral_excess_applied_to_L": False,
        },
    }


def line_graph_record() -> dict[str, object]:
    spectrum: Spectrum = ((18, 1), (7, 54), (0, 44), (-3, 132))
    polynomials = predistance_polynomials(spectrum)
    expected_p3 = (
        Fraction(25, 2),
        Fraction(19, 12),
        Fraction(-35, 36),
        Fraction(1, 18),
    )
    if polynomials[3] != expected_p3:
        raise AssertionError(
            f"unexpected p3 {polynomials[3]} != {expected_p3}"
        )

    relation = triangle_relations()["valencies"]
    k2_entries = {"I": 18, "K": 5, "B": 2, "C": 1, "D": 0}
    ntan_entries = {"I": 6, "K": 4, "B": 2, "C": 1, "D": 0}
    k3_entries = {
        label: 4 * ntan_entries[label]
        + 25 * int(label == "K")
        + 48 * int(label == "I")
        + 18
        for label in ("I", "K", "B", "C", "D")
    }
    expected_k3 = {"I": 90, "K": 59, "B": 26, "C": 22, "D": 18}
    if k3_entries != expected_k3:
        raise AssertionError("third-walk table failed")

    p3_entries = {}
    for label in ("I", "K", "B", "C", "D"):
        p3_entries[label] = (
            Fraction(k3_entries[label], 18)
            - Fraction(35 * k2_entries[label], 36)
            + Fraction(19 * int(label == "K"), 12)
            + Fraction(25 * int(label == "I"), 2)
        )
    expected_p3_entries = {
        "I": Fraction(0),
        "K": Fraction(0),
        "B": Fraction(-1, 2),
        "C": Fraction(1, 4),
        "D": Fraction(1),
    }
    if p3_entries != expected_p3_entries:
        raise AssertionError("p3 relation entries failed")

    p2_entries = {}
    for label in ("I", "K", "B", "C", "D"):
        p2_entries[label] = (
            Fraction(-27 * int(label == "I"), 2)
            - Fraction(15 * int(label == "K"), 4)
            + Fraction(3 * k2_entries[label], 4)
        )
    expected_p2_entries = {
        "I": Fraction(0),
        "K": Fraction(0),
        "B": Fraction(3, 2),
        "C": Fraction(3, 4),
        "D": Fraction(0),
    }
    if p2_entries != expected_p2_entries:
        raise AssertionError("p2 relation entries failed")

    spectral_excess = poly_eval(polynomials[3], 18)
    actual_excess = Fraction(relation["D"])
    gap = spectral_excess - actual_excess
    if (spectral_excess, actual_excess, gap) != (
        Fraction(50),
        Fraction(32),
        Fraction(18),
    ):
        raise AssertionError("spectral-excess values failed")

    # Normalized Frobenius scalar product: n^{-1} trace(XY).
    p3_norm_squared = sum(
        Fraction(relation[label]) * p3_entries[label] ** 2
        for label in ("I", "K", "B", "C", "D")
    )
    d_norm_squared = Fraction(relation["D"])
    p3_d_inner = Fraction(relation["D"])
    defect_norm_squared = (
        p3_norm_squared + d_norm_squared - 2 * p3_d_inner
    )
    if (
        p3_norm_squared,
        d_norm_squared,
        p3_d_inner,
        defect_norm_squared,
    ) != (Fraction(50), Fraction(32), Fraction(32), Fraction(18)):
        raise AssertionError("defect norms failed")

    projection_scale = p3_d_inner / p3_norm_squared
    projection_residual_norm = (
        d_norm_squared - p3_d_inner**2 / p3_norm_squared
    )
    if (projection_scale, projection_residual_norm) != (
        Fraction(16, 25),
        Fraction(288, 25),
    ):
        raise AssertionError("adjacency-algebra projection failed")

    defect_entries = {
        label: p3_entries[label] - int(label == "D")
        for label in p3_entries
    }
    defect_row_sum = sum(
        Fraction(relation[label]) * defect_entries[label]
        for label in defect_entries
    )
    if defect_row_sum != 18:
        raise AssertionError("defect row sum failed")

    signed_defect = {
        "formula": "F = A_C - 2*A_B = 4*(p3(K)-A_D)",
        "relation_entries": {"I": 0, "K": 0, "B": -2, "C": 1, "D": 0},
        "row_sum": 72,
        "trace": 0,
        "trace_square": 231 * (36 * 4 + 144),
        "has_eigenvalue": 72,
        "psd": False,
        "psd_failure_reason": (
            "F is nonzero with trace zero and has the positive eigenvalue 72"
        ),
        "orthogonal_to": ["I", "K", "K^2"],
    }
    pair_gram_trace = 231 * 153
    pair_gram_trace_square = 231 * (153**2 + 18 * 10**2 + 36)

    return {
        "definition": "K = N^T*N - 3I",
        "order": 231,
        "valency": 18,
        "connected": True,
        "diameter": 3,
        "distance_layers": [1, 18, 180, 32],
        "spectrum": [
            {"eigenvalue": eigenvalue, "multiplicity": multiplicity}
            for eigenvalue, multiplicity in spectrum
        ],
        "minimal_polynomial_identity": "K^3 - 4*K^2 - 21*K = 18*J",
        "predistance_polynomials": [
            polynomial_record(poly) for poly in polynomials
        ],
        "p3_formula": "x^3/18 - 35*x^2/36 + 19*x/12 + 25/2",
        "spectral_excess": fraction_text(spectral_excess),
        "actual_excess": fraction_text(actual_excess),
        "spectral_excess_gap": fraction_text(gap),
        "distance_regular": False,
        "walk_tables": {
            "K_squared": k2_entries,
            "N_transpose_A_N": ntan_entries,
            "K_cubed": k3_entries,
            "K_cubed_identity": "4*N^T*A*N + 25*K + 48*I + 18*J",
        },
        "p3_relation_entries": {
            label: fraction_text(value) for label, value in p3_entries.items()
        },
        "p2_relation_entries": {
            label: fraction_text(value) for label, value in p2_entries.items()
        },
        "defect": {
            "formula": "p3(K)-A_D = (A_C-2*A_B)/4",
            "distance_transfer_identity": (
                "p2(K)-A_distance_2 = -(p3(K)-A_D)"
            ),
            "relation_entries": {
                label: fraction_text(value)
                for label, value in defect_entries.items()
            },
            "row_sum": fraction_text(defect_row_sum),
            "normalized_frobenius_norm_squared": fraction_text(
                defect_norm_squared
            ),
            "signed_integral_form": signed_defect,
        },
        "distance_matrix_projection": {
            "polynomial_adjacency_algebra_dimension": 4,
            "projection": "(16/25)*p3(K)",
            "normalized_residual_norm_squared": fraction_text(
                projection_residual_norm
            ),
            "angle_cosine": "4/5",
        },
        "gram_constraints": {
            "common_K_neighbor_pair_gram": (
                "binom(K^2 entry,2) = 153*I + 10*K + A_B is PSD"
            ),
            "common_K_neighbor_pair_gram_trace": pair_gram_trace,
            "common_K_neighbor_pair_gram_trace_square": (
                pair_gram_trace_square
            ),
            "positive_definite_lower_bound": (
                "lambda_min >= 153 - 30 - 36 = 87"
            ),
            "rank": 231,
            "rank_or_psd_contradiction": False,
        },
    }


def quadratic_power_sum(root_sum: int, root_product: int, exponent: int) -> int:
    if exponent == 0:
        return 2
    if exponent == 1:
        return root_sum
    previous_previous = 2
    previous = root_sum
    for _ in range(2, exponent + 1):
        current = root_sum * previous - root_product * previous_previous
        previous_previous, previous = previous, current
    return previous


def nonbacktracking_record() -> dict[str, object]:
    # Bass: det(I-uH)=(1-u^2)^(m-n)det(I-uL+u^2(D-I)).
    # A singular-value block with square lambda contributes
    # 1+(8-lambda)u^2+12u^4.
    singular_square_spectrum = ((21, 1), (10, 54), (3, 44))
    moments: dict[str, int] = {}
    for half_length in range(1, 8):
        power_sum = 363 + 132 * ((-2) ** half_length)
        for singular_square, multiplicity in singular_square_spectrum:
            root_sum = singular_square - 8
            power_sum += multiplicity * quadratic_power_sum(
                root_sum, 12, half_length
            )
        trace = 2 * power_sum
        moments[str(2 * half_length)] = trace

    expected = {
        "2": 0,
        "4": 0,
        "6": 0,
        "8": 33264,
        "10": 665280,
        "12": 6020784,
        "14": 69854400,
    }
    if moments != expected:
        raise AssertionError(f"nonbacktracking moments failed: {moments}")

    cycle_counts = {
        length: moments[str(length)] // (2 * length)
        for length in (8, 10, 12, 14)
    }
    expected_cycles = {
        8: 2079,
        10: 33264,
        12: 250866,
        14: 2494800,
    }
    if cycle_counts != expected_cycles:
        raise AssertionError("short-cycle counts failed")
    if cycle_counts[8] != 4158 // 2:
        raise AssertionError("8-cycle/nonedge control failed")

    return {
        "oriented_edge_matrix": "H",
        "oriented_edge_count": 1386,
        "bass_determinant": (
            "(1-u^2)^363 (1+2u^2)^132 "
            "(1-13u^2+12u^4) "
            "(1-2u^2+12u^4)^54 "
            "(1+5u^2+12u^4)^44"
        ),
        "trace_H_powers": moments,
        "simple_cycle_counts": {
            str(length): count for length, count in cycle_counts.items()
        },
        "simple_cycle_scope": (
            "Lengths 8,10,12,14 are below twice the girth, so a closed "
            "tailless nonbacktracking walk is a simple cycle."
        ),
        "contradiction": False,
    }


def cage_record() -> dict[str, object]:
    return {
        "biregular_girth_8_Moore_lower_bound": {
            "points": 39,
            "lines": 91,
            "total": 130,
            "edge_root_tree": {
                "points": "1 + 2 + 12 + 24",
                "lines": "1 + 6 + 12 + 72",
            },
        },
        "target_incidence_order": {
            "points": 99,
            "lines": 231,
            "total": 330,
        },
        "excess_over_bound": {
            "points": 60,
            "lines": 140,
            "total": 200,
        },
        "generalized_quadrangle_equality_case": (
            "The Moore equality geometry would have order (2,6); L is "
            "strictly larger and has diameter 6 rather than 4."
        ),
        "contradiction": False,
    }


def build_result() -> dict[str, object]:
    observed = require_memory()
    result = {
        "schema_version": 1,
        "role": "proof_b",
        "claim_label": "DERIVED",
        "scope": (
            "Conditional point-triangle incidence, triangle-halved-graph, "
            "spectral-excess, and nonbacktracking constraints at the "
            "prism-free endpoint"
        ),
        "triangle_relations": triangle_relations(),
        "incidence_graph": incidence_graph_record(),
        "triangle_line_graph": line_graph_record(),
        "nonbacktracking": nonbacktracking_record(),
        "cage_comparison": cage_record(),
        "status": {
            "new_exact_smaller_obstruction": (
                "The regular triangle graph has spectral excess 50, actual "
                "excess 32, and exact distance-matrix projection residual "
                "norm squared 288/25."
            ),
            "incidence_distance_biregular": False,
            "point_root_distance_regular": True,
            "triangle_root_distance_regular": False,
            "strict_n3_upper_bound": "NOT_OBTAINED",
            "endpoint_excluded": False,
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "All results are conditional on the hypothetical prism-free target.",
            "The ordinary spectral-excess theorem is applied only to the regular triangle graph.",
            "Strict spectral-excess inequality certifies non-distance-regularity, not nonexistence.",
            "Cycle counts and PSD Gram constraints are exact but consistent.",
            "No target automorphism, graph construction, endpoint exclusion, or strict n3 bound follows.",
            "Discovery cannot independently verify itself.",
        ],
        "resources": {
            "minimum_free_memory_percent": 15.0,
            "observed_free_memory_percent": round(observed, 2),
            "floor_passed": observed >= 15.0,
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()

    result = build_result()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.verify is not None:
        if args.verify.read_text(encoding="utf-8") != encoded:
            # Resource observations are expected to vary. Compare after
            # replacing the current observation with the stored one.
            stored = json.loads(args.verify.read_text(encoding="utf-8"))
            result["resources"]["observed_free_memory_percent"] = stored[
                "resources"
            ]["observed_free_memory_percent"]
            encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
            if args.verify.read_text(encoding="utf-8") != encoded:
                raise SystemExit("stored exact result does not reproduce")
        print(f"VERIFIED {args.verify}")
    elif args.output is not None:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
        print(args.output)
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
