#!/usr/bin/env python3
"""Build the exact Wave 15 dense-active-subset obstruction certificate.

The proof uses only integer arithmetic and the SRG common-neighbor equations.
The optional Wave 14 JSON is read only to replay the concrete all-size-two
relaxation at the newly found global obstruction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


V = 99
K = 14
LAMBDA = 1
MU = 2
BASELINE_INTERNAL_DEGREE = 6


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edge(a: int, b: int) -> tuple[int, int]:
    assert a != b
    return (a, b) if a < b else (b, a)


def degrees(order: int, records: list[list[int]]) -> tuple[int, ...]:
    result = [0] * order
    seen: set[tuple[int, int]] = set()
    for raw_a, raw_b in records:
        a, b = edge(int(raw_a), int(raw_b))
        assert 0 <= a < b < order
        assert (a, b) not in seen
        seen.add((a, b))
        result[a] += 1
        result[b] += 1
    return tuple(result)


def base_defect(m: int) -> int:
    """Cauchy left minus right when every internal degree is six."""

    outside_square_sum = 2 * m * m - 30 * m
    outside_incidence_sum = 8 * m
    return (V - m) * outside_square_sum - outside_incidence_sum**2


def defect_t_coefficient(m: int) -> int:
    """Coefficient of T=sum(d_x-6) in the expanded Cauchy defect."""

    return 29 * m - 1287


def size_profile_rows() -> list[dict[str, int | str]]:
    rows = []
    # 2*x2 + 3*x3 = 48 and x2,x3 are nonnegative integers.
    for x3 in range(0, 17, 2):
        x2 = (48 - 3 * x3) // 2
        assert 2 * x2 + 3 * x3 == 48
        m = x2 + x3
        phi0 = base_defect(m)
        coefficient = defect_t_coefficient(m)
        assert phi0 == -2 * m * (m - 27) * (m - 55)
        assert phi0 < 0
        assert coefficient < 0
        rows.append(
            {
                "x2": x2,
                "x3": x3,
                "active_vertex_count_m": m,
                "spectral_min_degree_gap_numerator_over_99": (
                    11 * m * (27 - m)
                ),
                "defect_at_T0_U0": phi0,
                "T_coefficient": coefficient,
                "U_coefficient": -(V - m),
                "T_squared_coefficient": -1,
                "conclusion": "STRICTLY_NEGATIVE_FOR_ALL_T_U_NONNEGATIVE",
            }
        )
    return rows


def replay_countermodel(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema"] == "wave14-all2-active-countermodel-v1"
    points = data["point_sets"]
    assert len(points) == 24
    assert all(len(point) == 2 for point in points)
    active_degrees = degrees(len(points), data["active_original_adjacency"])
    assert active_degrees == (6,) * 24

    m = len(points)
    internal_edge_count = sum(active_degrees) // 2
    outside_incidence_sum = K * m - 2 * internal_edge_count
    pair_common_neighbor_total = (
        LAMBDA * internal_edge_count
        + MU * (m * (m - 1) // 2 - internal_edge_count)
    )
    inside_pair_contribution = sum(d * (d - 1) // 2 for d in active_degrees)
    outside_factorial_second_moment = (
        pair_common_neighbor_total - inside_pair_contribution
    )
    outside_square_sum_forced = (
        2 * outside_factorial_second_moment + outside_incidence_sum
    )

    outside_count = V - m
    quotient, remainder = divmod(outside_incidence_sum, outside_count)
    integer_minimum_square_sum = (
        (outside_count - remainder) * quotient**2
        + remainder * (quotient + 1) ** 2
    )
    assert outside_square_sum_forced < integer_minimum_square_sum

    return {
        "input_path": path.as_posix(),
        "input_sha256": sha256(path),
        "active_vertex_count": m,
        "active_internal_degree_histogram": {
            str(key): value for key, value in sorted(Counter(active_degrees).items())
        },
        "active_internal_edge_count": internal_edge_count,
        "outside_incidence_sum": outside_incidence_sum,
        "pair_common_neighbor_total": pair_common_neighbor_total,
        "inside_pair_contribution": inside_pair_contribution,
        "outside_factorial_second_moment_forced": (
            outside_factorial_second_moment
        ),
        "outside_square_sum_forced": outside_square_sum_forced,
        "outside_square_sum_cauchy_numerator": outside_incidence_sum**2,
        "outside_square_sum_cauchy_denominator": outside_count,
        "outside_square_sum_integer_minimum": integer_minimum_square_sum,
        "integer_square_sum_deficit": (
            integer_minimum_square_sum - outside_square_sum_forced
        ),
        "lift_status": "REFUTED_BY_SRG_COMMON_NEIGHBOR_MOMENT",
    }


def build(countermodel: Path | None) -> dict[str, object]:
    result: dict[str, object] = {
        "schema": "wave15-srg-subset-moment-obstruction-v1",
        "claim_label": "DERIVED",
        "scope": (
            "conditional n3=48 residual after the audited Wave14 reduction; "
            "not an unconditional Conway-99 result"
        ),
        "srg_parameters": {
            "v": V,
            "k": K,
            "lambda": LAMBDA,
            "mu": MU,
        },
        "active_incidence_equation": "2*x2 + 3*x3 = 48",
        "mandatory_internal_degree": {
            "lower_bound": BASELINE_INTERNAL_DEGREE,
            "size2_reason": (
                "four active-triangle neighbors plus two distinct support "
                "neighbors; H-degree-four support cannot be a meeting edge"
            ),
            "size3_reason": (
                "six active-triangle neighbors plus three support neighbors "
                "with at most three overlaps"
            ),
        },
        "spectral_identities": {
            "adjacency_equation": "A^2 = 12*I - A + 2*J",
            "nontrivial_eigenvalues": [3, -4],
            "induced_twice_edge_upper_bound": (
                "2*e(X) <= 3*m + 11*m^2/99"
            ),
            "minimum_degree_six_lower_bound": "2*e(X) >= 6*m",
            "consequence": "m >= 27",
        },
        "moment_identities": {
            "outside_incidence_sum": "14*m - sum(d_x)",
            "outside_square_sum": (
                "2*m^2 + 12*m - sum(d_x^2+d_x)"
            ),
            "cauchy_requirement": (
                "(99-m)*outside_square_sum >= outside_incidence_sum^2"
            ),
            "degree_substitution": "d_x=6+s_x, T=sum(s_x), U=sum(s_x^2)",
            "defect_formula": (
                "-2*m*(m-27)*(m-55) + (29*m-1287)*T "
                "- (99-m)*U - T^2"
            ),
        },
        "size_profile_rows": size_profile_rows(),
        "conditional_n3_48_exclusion": "DERIVED_PENDING_INDEPENDENT_VERIFICATION",
        "target_result": "UNKNOWN",
        "novelty": "UNKNOWN",
    }
    if countermodel is not None:
        result["wave14_countermodel_replay"] = replay_countermodel(countermodel)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--countermodel", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = build(args.countermodel)
    # Public certificates must have canonical LF bytes even on Windows.
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
