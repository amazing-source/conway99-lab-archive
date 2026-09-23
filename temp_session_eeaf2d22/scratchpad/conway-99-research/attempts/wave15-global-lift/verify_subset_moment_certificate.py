#!/usr/bin/env python3
"""Independent semantic verifier for the Wave 15 moment certificate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def verify(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema"] == "wave15-srg-subset-moment-obstruction-v1"
    assert data["claim_label"] == "DERIVED"
    assert data["srg_parameters"] == {
        "k": 14,
        "lambda": 1,
        "mu": 2,
        "v": 99,
    }
    assert data["mandatory_internal_degree"]["lower_bound"] == 6
    assert data["spectral_identities"]["nontrivial_eigenvalues"] == [3, -4]
    assert data["spectral_identities"]["consequence"] == "m >= 27"

    expected_profiles = []
    for x3 in range(0, 17, 2):
        x2 = (48 - 3 * x3) // 2
        assert x2 >= 0 and 2 * x2 + 3 * x3 == 48
        expected_profiles.append((x2, x3, x2 + x3))

    rows = data["size_profile_rows"]
    assert len(rows) == len(expected_profiles) == 9
    for row, (x2, x3, m) in zip(rows, expected_profiles):
        assert (row["x2"], row["x3"], row["active_vertex_count_m"]) == (
            x2,
            x3,
            m,
        )
        spectral_gap = 99 * 6 * m - (3 * 99 * m + 11 * m * m)
        assert spectral_gap == 11 * m * (27 - m)
        assert (
            row["spectral_min_degree_gap_numerator_over_99"]
            == spectral_gap
            > 0
        )
        phi0_direct = (99 - m) * (2 * m * m - 30 * m) - (8 * m) ** 2
        phi0_factored = -2 * m * (m - 27) * (m - 55)
        assert phi0_direct == phi0_factored == row["defect_at_T0_U0"]
        assert row["T_coefficient"] == 29 * m - 1287
        assert row["U_coefficient"] == -(99 - m)
        assert row["T_squared_coefficient"] == -1
        assert phi0_direct < 0
        assert row["T_coefficient"] < 0
        assert row["U_coefficient"] < 0

        # Exhaust the only potentially favorable aggregate direction.
        # U>=0, so setting U=0 maximizes the defect even when it is not
        # realizable by a nonzero T.
        for total_excess in range(0, 8 * m + 1):
            upper_bound = (
                phi0_direct
                + row["T_coefficient"] * total_excess
                - total_excess**2
            )
            assert upper_bound < 0

    replay = data.get("wave14_countermodel_replay")
    if replay is not None:
        assert replay["active_vertex_count"] == 24
        assert replay["active_internal_degree_histogram"] == {"6": 24}
        assert replay["active_internal_edge_count"] == 72
        assert replay["outside_incidence_sum"] == 192
        assert replay["pair_common_neighbor_total"] == 480
        assert replay["inside_pair_contribution"] == 360
        assert replay["outside_factorial_second_moment_forced"] == 120
        assert replay["outside_square_sum_forced"] == 432
        assert replay["outside_square_sum_cauchy_numerator"] == 192**2
        assert replay["outside_square_sum_cauchy_denominator"] == 75
        assert replay["outside_square_sum_integer_minimum"] == 510
        assert replay["integer_square_sum_deficit"] == 78
        assert replay["lift_status"] == "REFUTED_BY_SRG_COMMON_NEIGHBOR_MOMENT"

    return {
        "status": "PASS",
        "verified_size_profiles": len(rows),
        "conditional_n3_48_exclusion": "DERIVED_NOT_VERIFIED_BY_DISCOVERY_AGENT",
        "target_result": "UNKNOWN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.certificate), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
