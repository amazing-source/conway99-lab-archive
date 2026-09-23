#!/usr/bin/env python3
"""Clean-room exact verifier for the sealed Wave 59 claim surface.

This module is intentionally self-contained.  It does not import, execute, or
inspect the Wave 59 discovery implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Mapping, Sequence


K_SPECTRUM = ((18, 1), (7, 54), (0, 44), (-3, 132))
RELATIONS = ("I", "K", "B", "C", "D")
RELATION_VALENCIES = {"I": 1, "K": 18, "B": 36, "C": 144, "D": 32}
K2_TABLE = {"I": 18, "K": 5, "B": 2, "C": 1, "D": 0}
N_T_A_N_TABLE = {"I": 6, "K": 4, "B": 2, "C": 1, "D": 0}
DISCOVERY_RESULT_SHA256 = (
    "7954daa92f8cb4a400ae8f9f5bfb4d4edb10ad42361872178eb538d35edc1d81"
)
SOURCE_METADATA_SHA256 = (
    "1772cf48f52b3945c5d3bb5dafd63bf94baad0741d231b6d094e4daf9c1b8cb9"
)
PRIMARY_PDF_SHA256 = (
    "1ba19437e449bbc75474242ce0f52f24d9934dc02912d67a46c16afb6151c038"
)


def frac_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def polynomial_trim(poly: Sequence[Fraction]) -> tuple[Fraction, ...]:
    values = list(poly)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def polynomial_add(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    size = max(len(left), len(right))
    return polynomial_trim(
        [
            (left[index] if index < len(left) else Fraction(0))
            + (right[index] if index < len(right) else Fraction(0))
            for index in range(size)
        ]
    )


def polynomial_scale(
    scalar: Fraction, poly: Sequence[Fraction]
) -> tuple[Fraction, ...]:
    return polynomial_trim([scalar * value for value in poly])


def polynomial_evaluate(poly: Sequence[Fraction], x: int) -> Fraction:
    total = Fraction(0)
    for coefficient in reversed(poly):
        total = total * x + coefficient
    return total


def spectral_inner_product(
    left: Sequence[Fraction], right: Sequence[Fraction]
) -> Fraction:
    numerator = sum(
        multiplicity
        * polynomial_evaluate(left, eigenvalue)
        * polynomial_evaluate(right, eigenvalue)
        for eigenvalue, multiplicity in K_SPECTRUM
    )
    return numerator / 231


def predistance_polynomials() -> tuple[tuple[Fraction, ...], ...]:
    """Perform exact Gram--Schmidt with ||p_i||^2 = p_i(18)."""

    result: list[tuple[Fraction, ...]] = []
    for degree in range(4):
        candidate: tuple[Fraction, ...] = (
            (Fraction(0),) * degree + (Fraction(1),)
        )
        for prior in result:
            coefficient = (
                spectral_inner_product(candidate, prior)
                / spectral_inner_product(prior, prior)
            )
            candidate = polynomial_add(
                candidate, polynomial_scale(-coefficient, prior)
            )
        norm = spectral_inner_product(candidate, candidate)
        at_valency = polynomial_evaluate(candidate, 18)
        candidate = polynomial_scale(at_valency / norm, candidate)
        assert spectral_inner_product(candidate, candidate) == polynomial_evaluate(
            candidate, 18
        )
        result.append(candidate)
    return tuple(result)


def relation_polynomial_entries(
    coefficients: Sequence[Fraction],
    k2_table: Mapping[str, int],
    k3_table: Mapping[str, int],
) -> dict[str, Fraction]:
    output: dict[str, Fraction] = {}
    for relation in RELATIONS:
        powers = {
            0: 1 if relation == "I" else 0,
            1: 1 if relation == "K" else 0,
            2: k2_table[relation],
            3: k3_table[relation],
        }
        output[relation] = sum(
            coefficient * powers[degree]
            for degree, coefficient in enumerate(coefficients)
        )
    return output


def relation_norm_squared(entries: Mapping[str, Fraction | int]) -> Fraction:
    return sum(
        RELATION_VALENCIES[relation] * Fraction(entries[relation]) ** 2
        for relation in RELATIONS
    )


def polynomial_multiply_truncated(
    left: Sequence[Fraction], right: Sequence[Fraction], maximum_degree: int
) -> tuple[Fraction, ...]:
    output = [Fraction(0)] * (
        min(maximum_degree, len(left) + len(right) - 2) + 1
    )
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            if i + j <= maximum_degree:
                output[i + j] += left_value * right_value
    return polynomial_trim(output)


def polynomial_power_truncated(
    base: Sequence[Fraction], exponent: int, maximum_degree: int
) -> tuple[Fraction, ...]:
    output: tuple[Fraction, ...] = (Fraction(1),)
    current = tuple(base)
    remaining = exponent
    while remaining:
        if remaining & 1:
            output = polynomial_multiply_truncated(
                output, current, maximum_degree
            )
        remaining >>= 1
        if remaining:
            current = polynomial_multiply_truncated(
                current, current, maximum_degree
            )
    return output


def formal_logarithm(
    polynomial: Sequence[Fraction], maximum_degree: int
) -> tuple[Fraction, ...]:
    assert polynomial[0] == 1
    x = list(polynomial)
    x[0] -= 1
    output = [Fraction(0)] * (maximum_degree + 1)
    power: tuple[Fraction, ...] = tuple(x)
    for exponent in range(1, maximum_degree + 1):
        sign = Fraction(1 if exponent % 2 else -1, exponent)
        for degree, coefficient in enumerate(power):
            if degree <= maximum_degree:
                output[degree] += sign * coefficient
        power = polynomial_multiply_truncated(power, x, maximum_degree)
    return tuple(output)


def ihara_bass_data(maximum_degree: int = 14) -> dict[str, object]:
    """Expand the independently specialized Bass determinant exactly."""

    factors: tuple[tuple[tuple[Fraction, ...], int], ...] = (
        ((Fraction(1), Fraction(0), Fraction(-1)), 363),
        ((Fraction(1), Fraction(0), Fraction(2)), 132),
        (
            (
                Fraction(1),
                Fraction(0),
                Fraction(-13),
                Fraction(0),
                Fraction(12),
            ),
            1,
        ),
        (
            (
                Fraction(1),
                Fraction(0),
                Fraction(-2),
                Fraction(0),
                Fraction(12),
            ),
            54,
        ),
        (
            (
                Fraction(1),
                Fraction(0),
                Fraction(5),
                Fraction(0),
                Fraction(12),
            ),
            44,
        ),
    )
    determinant: tuple[Fraction, ...] = (Fraction(1),)
    for factor, exponent in factors:
        determinant = polynomial_multiply_truncated(
            determinant,
            polynomial_power_truncated(factor, exponent, maximum_degree),
            maximum_degree,
        )
    log_determinant = formal_logarithm(determinant, maximum_degree)
    traces = {
        degree: -degree * log_determinant[degree]
        for degree in range(1, maximum_degree + 1)
    }
    for trace in traces.values():
        assert trace.denominator == 1
    girth = 8
    simple_cycles = {
        degree: traces[degree] / (2 * degree)
        for degree in range(girth, 2 * girth)
        if degree % 2 == 0
    }
    for count in simple_cycles.values():
        assert count.denominator == 1
    return {
        "determinant_factorization": (
            "(1-u^2)^363 (1+2u^2)^132 "
            "(1-13u^2+12u^4) "
            "(1-2u^2+12u^4)^54 "
            "(1+5u^2+12u^4)^44"
        ),
        "oriented_edges": 1386,
        "trace_H_powers": {
            str(degree): int(traces[degree])
            for degree in (2, 4, 6, 8, 10, 12, 14)
        },
        "simple_cycle_counts": {
            str(degree): int(simple_cycles[degree])
            for degree in (8, 10, 12, 14)
        },
        "simple_cycle_justification": (
            "For length ell < 2*girth, a tailless nonbacktracking closed "
            "walk with a repeated vertex would split into two closed "
            "nonbacktracking walks of length at least girth; a repeated "
            "traversal also has length at least 2*girth. Thus division by "
            "2*ell counts simple unoriented cycles for ell=8,10,12,14."
        ),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compute_result() -> dict[str, object]:
    # SRG arithmetic and point--triangle incidence.
    v, degree, lam, mu = 99, 14, 1, 2
    edge_count = v * degree // 2
    triangle_count = edge_count // 3
    triangles_per_point = degree // 2
    assert (edge_count, triangle_count, triangles_per_point) == (693, 231, 7)

    # For an arbitrary root triangle, relation counts follow without
    # transitivity: K=3(7-1), 2B+C=36*6, B=3*12 at the prism-free endpoint.
    relation_k = 3 * (triangles_per_point - 1)
    disjoint = triangle_count - 1 - relation_k
    cross_edge_incidences = 3 * (degree - 2) * (
        triangles_per_point - 1
    )
    relation_b = 3 * (degree - 2)
    relation_c = cross_edge_incidences - 2 * relation_b
    relation_d = disjoint - relation_b - relation_c
    independently_counted_valencies = {
        "I": 1,
        "K": relation_k,
        "B": relation_b,
        "C": relation_c,
        "D": relation_d,
    }
    assert independently_counted_valencies == RELATION_VALENCIES

    # The K^3 table follows from the spectral minimal-polynomial identity
    # K^3 - 4K^2 - 21K = 18J.
    k3_table = {
        relation: 4 * K2_TABLE[relation]
        + 21 * (1 if relation == "K" else 0)
        + 18
        for relation in RELATIONS
    }
    assert k3_table == {"I": 90, "K": 59, "B": 26, "C": 22, "D": 18}
    assert {
        relation: N_T_A_N_TABLE[relation]
        + (1 if relation == "K" else 0)
        + 12 * (1 if relation == "I" else 0)
        for relation in RELATIONS
    } == K2_TABLE

    polynomials = predistance_polynomials()
    expected_polynomials = (
        (Fraction(1),),
        (Fraction(0), Fraction(1)),
        (Fraction(-27, 2), Fraction(-15, 4), Fraction(3, 4)),
        (
            Fraction(25, 2),
            Fraction(19, 12),
            Fraction(-35, 36),
            Fraction(1, 18),
        ),
    )
    assert polynomials == expected_polynomials
    p2_entries = relation_polynomial_entries(polynomials[2], K2_TABLE, k3_table)
    p3_entries = relation_polynomial_entries(polynomials[3], K2_TABLE, k3_table)
    distance_3_entries = {
        relation: Fraction(1 if relation == "D" else 0)
        for relation in RELATIONS
    }
    defect_entries = {
        relation: p3_entries[relation] - distance_3_entries[relation]
        for relation in RELATIONS
    }
    assert defect_entries == {
        "I": 0,
        "K": 0,
        "B": Fraction(-1, 2),
        "C": Fraction(1, 4),
        "D": 0,
    }
    p3_norm = relation_norm_squared(p3_entries)
    distance_3_norm = relation_norm_squared(distance_3_entries)
    defect_norm = relation_norm_squared(defect_entries)
    inner_p3_distance_3 = sum(
        RELATION_VALENCIES[relation]
        * p3_entries[relation]
        * distance_3_entries[relation]
        for relation in RELATIONS
    )
    projection_coefficient = inner_p3_distance_3 / p3_norm
    projection_residual_norm = (
        distance_3_norm
        - inner_p3_distance_3 * inner_p3_distance_3 / p3_norm
    )
    angle_cosine_squared = (
        inner_p3_distance_3 * inner_p3_distance_3
        / (p3_norm * distance_3_norm)
    )

    pair_gram_entries = {
        relation: Fraction(
            K2_TABLE[relation] * (K2_TABLE[relation] - 1), 2
        )
        for relation in RELATIONS
    }
    assert pair_gram_entries == {
        "I": 153,
        "K": 10,
        "B": 1,
        "C": 0,
        "D": 0,
    }
    pair_gram_trace = 231 * pair_gram_entries["I"]
    pair_gram_trace_square = 231 * relation_norm_squared(pair_gram_entries)
    pair_gram_lower_bound = 153 + 10 * (-3) - 36

    point_layers = (1, 7, 14, 84, 84, 140)
    triangle_layers = (1, 3, 18, 36, 180, 60, 32)
    assert sum(point_layers[::2]) == 99
    assert sum(point_layers[1::2]) == 231
    assert sum(triangle_layers[::2]) == 231
    assert sum(triangle_layers[1::2]) == 99

    # Edge-root Moore tree for girth 8.  Equality has GQ order (s,t)=(2,6).
    moore_points = 1 + 2 + 12 + 24
    moore_lines = 1 + 6 + 12 + 72

    result: dict[str, object] = {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Finite conditional consequences of a prism-free hypothetical "
            "srg(99,14,1,2); no existence, nonexistence, endpoint, upper-bound, "
            "or novelty promotion."
        ),
        "assumptions": {
            "graph": "finite simple undirected srg(99,14,1,2)",
            "additional": (
                "No two disjoint graph triangles have three cross edges "
                "(prism-free endpoint)."
            ),
            "automorphism_or_transitivity": False,
        },
        "base_arithmetic": {
            "edges": edge_count,
            "triangles": triangle_count,
            "triangles_per_point": triangles_per_point,
            "A_spectrum": [
                {"eigenvalue": 14, "multiplicity": 1},
                {"eigenvalue": 3, "multiplicity": 54},
                {"eigenvalue": -4, "multiplicity": 44},
            ],
        },
        "incidence_matrix_N": {
            "shape": [99, 231],
            "identity": "N*N^T=A+7I",
            "rank": 99,
            "nonzero_squared_singular_values": [
                {"value": 21, "multiplicity": 1},
                {"value": 10, "multiplicity": 54},
                {"value": 3, "multiplicity": 44},
            ],
        },
        "incidence_graph_L": {
            "order": 330,
            "bipartition": {"points": 99, "triangles": 231},
            "degrees": {"point": 7, "triangle": 3},
            "edges": 693,
            "connected": True,
            "spectrum": (
                "+/-sqrt(21)^1, +/-sqrt(10)^54, "
                "+/-sqrt(3)^44, 0^132"
            ),
            "zero_multiplicity": 132,
            "trace_square": 1386,
            "girth": 8,
            "diameter": 6,
            "point_root": {
                "distance_layers": list(point_layers),
                "intersection_array": {
                    "b": [7, 2, 6, 2, 5],
                    "c": [1, 1, 1, 2, 3],
                },
                "equitable_for_every_point": True,
            },
            "triangle_root": {
                "distance_layers": list(triangle_layers),
                "distance_4_predecessors": {"B": 2, "C": 1},
                "distance_5_average_predecessors": "27/5",
                "distance_5_average_successors": "8/5",
                "equitable": False,
            },
            "distance_biregular": False,
            "semiregular_spectral_excess_source_check": {
                "theorem": "Fiol (2013), Theorem 6",
                "source_case": "c",
                "d": 6,
                "m_zero": 132,
                "larger_minus_smaller": 132,
                "ordinary_regular_theorem_applied_to_L": False,
            },
        },
        "triangle_relations": {
            "definitions": {
                "K": "share one point",
                "B": "disjoint with two cross edges",
                "C": "disjoint with one cross edge",
                "D": "disjoint with no cross edge",
            },
            "valencies": independently_counted_valencies,
            "disjoint_total": disjoint,
            "cross_edge_incidence_equation": "2*B+C=216",
            "B_count_basis": (
                "For each of the three pairs of 12-point root sectors, "
                "mu=2 induces a perfect matching. Prism-freeness prevents "
                "the matching-edge triangle from having a third root cross "
                "edge, giving 3*12 distinct B triangles."
            ),
        },
        "triangle_graph_K": {
            "definition": "K=N^T*N-3I",
            "order": 231,
            "valency": 18,
            "connected": True,
            "diameter": 3,
            "distance_layers": [1, 18, 180, 32],
            "spectrum": [
                {"eigenvalue": 18, "multiplicity": 1},
                {"eigenvalue": 7, "multiplicity": 54},
                {"eigenvalue": 0, "multiplicity": 44},
                {"eigenvalue": -3, "multiplicity": 132},
            ],
            "minimal_polynomial_identity": "K^3-4K^2-21K=18J",
            "spectral_excess_theorem_hypotheses": {
                "connected": True,
                "regular": True,
                "distinct_eigenvalues": 4,
                "diameter": 3,
                "conclusion_scope": (
                    "Equality of average and spectral excess characterizes "
                    "distance-regularity; strict inequality is not a "
                    "nonexistence condition."
                ),
            },
            "predistance_polynomials_low_to_high": [
                [frac_text(value) for value in polynomial]
                for polynomial in polynomials
            ],
            "spectral_excess": frac_text(
                polynomial_evaluate(polynomials[3], 18)
            ),
            "actual_excess": str(relation_d),
            "distance_regular": False,
            "walk_tables": {
                "K_squared": K2_TABLE,
                "N_transpose_A_N": N_T_A_N_TABLE,
                "K_cubed": k3_table,
            },
            "p2_relation_entries": {
                key: frac_text(value) for key, value in p2_entries.items()
            },
            "p3_relation_entries": {
                key: frac_text(value) for key, value in p3_entries.items()
            },
            "defect": {
                "identity": "p3(K)-A_D=(A_C-2*A_B)/4",
                "entries": {
                    key: frac_text(value)
                    for key, value in defect_entries.items()
                },
                "normalized_norm_squared": frac_text(defect_norm),
                "p3_norm_squared": frac_text(p3_norm),
                "A_D_norm_squared": frac_text(distance_3_norm),
                "inner_product_p3_A_D": frac_text(inner_p3_distance_3),
                "signed_form": {
                    "identity": "F=A_C-2*A_B=4*(p3(K)-A_D)",
                    "row_sum": 72,
                    "trace": 0,
                    "trace_square": 66528,
                    "indefinite": True,
                },
            },
            "distance_matrix_projection": {
                "projection": (
                    f"{frac_text(projection_coefficient)}*p3(K)"
                ),
                "normalized_residual_norm_squared": frac_text(
                    projection_residual_norm
                ),
                "angle_cosine": (
                    "4/5" if angle_cosine_squared == Fraction(16, 25) else None
                ),
            },
            "pair_neighborhood_gram": {
                "entry_identity": "binom((K^2)_RS,2)",
                "matrix_identity": "153I+10K+A_B",
                "entries": {
                    key: frac_text(value)
                    for key, value in pair_gram_entries.items()
                },
                "trace": int(pair_gram_trace),
                "trace_square": int(pair_gram_trace_square),
                "weyl_lower_bound": pair_gram_lower_bound,
                "positive_definite": pair_gram_lower_bound > 0,
                "rank": 231,
            },
        },
        "nonbacktracking": ihara_bass_data(),
        "cage_comparison": {
            "biregular_girth_8_edge_root_Moore_bound": {
                "points": moore_points,
                "lines": moore_lines,
                "total": moore_points + moore_lines,
            },
            "degree_balance": "7*39=3*91=273",
            "equality_geometry_order": "(s,t)=(2,6)",
            "target_total": 330,
            "excess_over_bound": 330 - moore_points - moore_lines,
            "contradiction": False,
        },
        "source_metadata_check": {
            "title": (
                "The Spectral Excess Theorem for Distance-Biregular Graphs."
            ),
            "author": "Miquel Àngel Fiol",
            "journal": "The Electronic Journal of Combinatorics",
            "volume_issue_article": "20(3), P21",
            "published": "2013-08-16",
            "doi": "10.37236/3305",
            "primary_pdf_sha256": PRIMARY_PDF_SHA256,
            "relevant_result": "Theorem 6, statement on printed page 6",
            "theorem_case_check": (
                "Case (c): d even and m(0)=n1-n2, with n1=231 "
                "and n2=99."
            ),
        },
        "corrections": [
            {
                "severity": "metadata-only",
                "field": "source-metadata.json authors[0]",
                "discovery": "Miquel Angel Fiol",
                "verified": "Miquel Àngel Fiol",
                "effect": "Diacritics only; no mathematical effect.",
            },
            {
                "severity": "precision",
                "field": "source-metadata.json relevant_result.location",
                "discovery": "Theorem 6, printed pages 6-7",
                "verified": (
                    "The theorem statement is on printed page 6; its proof "
                    "continues on later pages."
                ),
                "effect": "Citation-location precision only.",
            },
        ],
        "verdict": {
            "finite_conditional_claims": "VERIFIED",
            "discovery_code_opened_imported_or_executed": False,
            "endpoint_excluded": False,
            "strict_n3_upper_bound": "NOT_OBTAINED",
            "conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }

    assert p3_norm == 50
    assert distance_3_norm == 32
    assert defect_norm == 18
    assert projection_coefficient == Fraction(16, 25)
    assert projection_residual_norm == Fraction(288, 25)
    assert pair_gram_lower_bound == 87
    assert moore_points + moore_lines == 130
    return result


def compare_discovery(independent: Mapping[str, object], discovery: Mapping[str, object]) -> list[str]:
    """Compare only the sealed claim envelope, never discovery internals."""

    checks = (
        (
            "incidence girth",
            independent["incidence_graph_L"]["girth"],  # type: ignore[index]
            discovery["incidence_graph"]["girth"],  # type: ignore[index]
        ),
        (
            "incidence diameter",
            independent["incidence_graph_L"]["diameter"],  # type: ignore[index]
            discovery["incidence_graph"]["diameter"],  # type: ignore[index]
        ),
        (
            "point layers",
            independent["incidence_graph_L"]["point_root"]["distance_layers"],  # type: ignore[index]
            discovery["incidence_graph"]["point_root"]["distance_layers"],  # type: ignore[index]
        ),
        (
            "triangle layers",
            independent["incidence_graph_L"]["triangle_root"]["distance_layers"],  # type: ignore[index]
            discovery["incidence_graph"]["triangle_root"]["distance_layers"],  # type: ignore[index]
        ),
        (
            "relation valencies",
            independent["triangle_relations"]["valencies"],  # type: ignore[index]
            discovery["triangle_relations"]["valencies"],  # type: ignore[index]
        ),
        (
            "K^2 table",
            independent["triangle_graph_K"]["walk_tables"]["K_squared"],  # type: ignore[index]
            discovery["triangle_line_graph"]["walk_tables"]["K_squared"],  # type: ignore[index]
        ),
        (
            "K^3 table",
            independent["triangle_graph_K"]["walk_tables"]["K_cubed"],  # type: ignore[index]
            discovery["triangle_line_graph"]["walk_tables"]["K_cubed"],  # type: ignore[index]
        ),
        (
            "spectral excess",
            independent["triangle_graph_K"]["spectral_excess"],  # type: ignore[index]
            discovery["triangle_line_graph"]["spectral_excess"],  # type: ignore[index]
        ),
        (
            "projection residual",
            independent["triangle_graph_K"]["distance_matrix_projection"][  # type: ignore[index]
                "normalized_residual_norm_squared"
            ],
            discovery["triangle_line_graph"]["distance_matrix_projection"][  # type: ignore[index]
                "normalized_residual_norm_squared"
            ],
        ),
        (
            "Bass determinant",
            independent["nonbacktracking"]["determinant_factorization"],  # type: ignore[index]
            discovery["nonbacktracking"]["bass_determinant"],  # type: ignore[index]
        ),
        (
            "nonbacktracking traces",
            independent["nonbacktracking"]["trace_H_powers"],  # type: ignore[index]
            discovery["nonbacktracking"]["trace_H_powers"],  # type: ignore[index]
        ),
        (
            "simple cycles",
            independent["nonbacktracking"]["simple_cycle_counts"],  # type: ignore[index]
            discovery["nonbacktracking"]["simple_cycle_counts"],  # type: ignore[index]
        ),
    )
    mismatches = [
        f"{label}: independent={left!r}, discovery={right!r}"
        for label, left, right in checks
        if left != right
    ]
    return mismatches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare-discovery", type=Path)
    arguments = parser.parse_args()

    result = compute_result()
    if arguments.compare_discovery is not None:
        actual_hash = sha256_file(arguments.compare_discovery)
        if actual_hash != DISCOVERY_RESULT_SHA256:
            raise SystemExit(
                "sealed discovery result hash mismatch: "
                f"{actual_hash} != {DISCOVERY_RESULT_SHA256}"
            )
        discovery = json.loads(
            arguments.compare_discovery.read_text(encoding="utf-8")
        )
        mismatches = compare_discovery(result, discovery)
        result["sealed_discovery_comparison"] = {
            "path": arguments.compare_discovery.as_posix(),
            "sha256": actual_hash,
            "mismatches": mismatches,
            "matched": not mismatches,
        }
        if mismatches:
            raise SystemExit("\n".join(mismatches))

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
