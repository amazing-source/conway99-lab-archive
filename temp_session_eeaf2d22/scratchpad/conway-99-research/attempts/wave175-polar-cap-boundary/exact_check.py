"""Exact Wave 175 finite-polar boundary checks."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


def fraction_text(value: Fraction) -> str:
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def analyze() -> dict[str, Any]:
    field = 3
    ambient_dimension = 11
    selected = 231
    selected_degree = 32

    # Singular points and the collinearity graph of Q(10,3).
    vertices = (field**10 - 1) // (field - 1)
    degree = field * (field**8 - 1) // (field - 1)
    positive_eigenvalue = field**4 - 1
    negative_eigenvalue = -(field**4 + 1)
    mu = degree + positive_eigenvalue * negative_eigenvalue
    lam = mu + positive_eigenvalue + negative_eigenvalue

    trivial_energy = Fraction(selected * selected, vertices)
    centered_energy = Fraction(selected) - trivial_energy
    centered_adjacency = (
        Fraction(selected * selected_degree)
        - Fraction(degree * selected * selected, vertices)
    )
    energy_positive = (
        centered_adjacency - negative_eigenvalue * centered_energy
    ) / (positive_eigenvalue - negative_eigenvalue)
    energy_negative = centered_energy - energy_positive

    # Orthogonality counts on singular points.
    selected_closed_degree = selected_degree + 1
    total_b = selected * (degree + 1)
    ordered_orthogonal_pairs = selected * selected_degree
    ordered_nonorthogonal_pairs = selected * (selected - 1 - selected_degree)
    total_b2 = (
        selected * (degree + 1)
        + ordered_orthogonal_pairs * (lam + 2)
        + ordered_nonorthogonal_pairs * mu
    )

    outside_vertices = vertices - selected
    outside_b = total_b - selected * selected_closed_degree
    outside_b2 = total_b2 - selected * selected_closed_degree**2
    outside_mean = Fraction(outside_b, outside_vertices)
    lower_multiple = 75
    upper_multiple = 78
    evans_slack = (
        outside_b2
        - (lower_multiple + upper_multiple) * outside_b
        + lower_multiple * upper_multiple * outside_vertices
    )

    symmetric_square_dimension = ambient_dimension * (ambient_dimension + 1) // 2
    singular_veronese_dimension = symmetric_square_dimension - 1

    return {
        "ambient": {
            "field": field,
            "vector_dimension": ambient_dimension,
            "quadric": "Q(10,3)",
        },
        "polar_graph": {
            "parameters": {
                "v": vertices,
                "k": degree,
                "lambda": lam,
                "mu": mu,
            },
            "eigenvalues": [degree, positive_eigenvalue, negative_eigenvalue],
        },
        "selected_configuration": {
            "points": selected,
            "internal_orthogonality_degree": selected_degree,
            "orthogonal_pairs": selected * selected_degree // 2,
        },
        "spectral_energies": {
            "eigenvalue_80": fraction_text(energy_positive),
            "eigenvalue_minus_82": fraction_text(energy_negative),
            "both_positive": energy_positive > 0 and energy_negative > 0,
        },
        "outside_singular_moments": {
            "count": outside_vertices,
            "sum_b": outside_b,
            "sum_b2": outside_b2,
            "mean": fraction_text(outside_mean),
            "b_congruence": "0 mod 3",
            "consecutive_multiples": [lower_multiple, upper_multiple],
            "evans_slack": evans_slack,
        },
        "singular_veronese": {
            "symmetric_square_dimension": symmetric_square_dimension,
            "quadric_hyperplane_dimension": singular_veronese_dimension,
            "identity": "D^(o2)=J-I-R",
            "rank_F3_J_minus_I_minus_R_upper": singular_veronese_dimension,
            "rank_F3_I_plus_R_upper": singular_veronese_dimension + 1,
        },
        "terminology_boundary": (
            "Moorhouse polar caps forbid every orthogonal pair; the Wave174 "
            "projective cap has 3696 orthogonal pairs."
        ),
        "conclusion": "rank k=11 survives these exact polar tests",
    }


def verify(data: dict[str, Any]) -> None:
    assert data["polar_graph"]["parameters"] == {
        "v": 29_524,
        "k": 9_840,
        "lambda": 3_278,
        "mu": 3_280,
    }
    assert data["polar_graph"]["eigenvalues"] == [9_840, 80, -82]
    assert data["selected_configuration"]["orthogonal_pairs"] == 3_696
    assert data["spectral_energies"] == {
        "eigenvalue_80": "37961/732",
        "eigenvalue_minus_82": "532/3",
        "both_positive": True,
    }
    assert data["outside_singular_moments"] == {
        "count": 29_293,
        "sum_b": 2_265_648,
        "sum_b2": 176_288_112,
        "mean": "205968/2663",
        "b_congruence": "0 mod 3",
        "consecutive_multiples": [75, 78],
        "evans_slack": 1_008_018,
    }
    assert data["singular_veronese"]["rank_F3_J_minus_I_minus_R_upper"] == 65
    assert data["singular_veronese"]["rank_F3_I_plus_R_upper"] == 66


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    data = analyze()
    verify(data)
    if args.verify:
        assert json.loads(args.verify.read_text(encoding="utf-8")) == data
    if args.write:
        args.write.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    if not args.write and not args.verify:
        print(json.dumps(data, indent=2, sort_keys=True))
    print("PASS: Wave175 finite-polar boundary checks")


if __name__ == "__main__":
    main()
