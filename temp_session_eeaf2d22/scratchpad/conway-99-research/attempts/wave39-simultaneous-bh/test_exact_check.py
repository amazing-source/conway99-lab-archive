#!/usr/bin/env python3
"""Focused hostile tests for the Wave 39 simultaneous B/H package."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave39_simultaneous_bh_exact_check",
    HERE / "exact_check.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class SimultaneousBHTests(unittest.TestCase):
    def test_frozen_inputs(self) -> None:
        CHECK.verify_frozen_inputs()

    def test_centered_equal_and_antipodal_rejections(self) -> None:
        result = CHECK.centered_projective_boundary()
        self.assertTrue(result["centered_projective_points_distinct"])
        self.assertEqual(
            result["equal_centered_rows_rejection"][
                "forced_integer_difference_norm_squared"
            ],
            450,
        )
        self.assertEqual(
            result["antipodal_centered_rows_rejection"][
                "forced_integer_sum_norm_squared"
            ],
            2_034,
        )
        self.assertEqual(
            result["antipodal_centered_rows_rejection"][
                "reflection_sum_norm_squared"
            ],
            882,
        )

    def test_centered_inner_distribution(self) -> None:
        distribution = CHECK.centered_projective_boundary()[
            "oriented_inner_distribution"
        ]
        self.assertEqual(
            distribution,
            {
                "equal": 1,
                "antipodal": 0,
                "inner_0": 32,
                "inner_1": 162,
                "inner_2": 36,
            },
        )
        self.assertEqual(sum(distribution.values()), 231)

    def test_oriented_scheme_characters(self) -> None:
        scheme = CHECK.centered_oriented_scheme()
        self.assertEqual(
            scheme["valencies"],
            [1, 1, 19_680, 19_683, 19_683],
        )
        self.assertEqual(len(scheme["intersection_matrices"]), 5)
        self.assertEqual(len(scheme["first_eigenmatrix"]), 5)

    def test_oriented_scheme_does_not_exclude(self) -> None:
        scheme = CHECK.centered_oriented_scheme()
        self.assertFalse(scheme["excluded"])
        self.assertEqual(
            [
                item["display"]
                for item in scheme["delsarte_transforms"]
            ],
            ["231", "209/135", "13/27", "493/1107", "23/9"],
        )

    def test_centered_code_low_weight_bounds(self) -> None:
        code = CHECK.centered_code_constraints()
        self.assertEqual(
            code["dual_low_weight_lower_bounds"],
            {"7": 198, "12": 1_386, "13": 1_386, "14": 16_632},
        )
        self.assertEqual(
            code["distinguished_primal_words"]["weight"],
            198,
        )

    def test_frozen_core_and_gram_histogram(self) -> None:
        adjacency = CHECK.core_adjacency()
        self.assertEqual(CHECK.four_cycle_count(adjacency), 4)
        result = CHECK.simultaneous_bh_constraints()[
            "frozen_rank_ten_core_control"
        ]
        self.assertEqual(
            result["required_BBt_unordered_off_diagonal_histogram"],
            {"0": 26, "1": 308, "2": 296},
        )

    def test_block_overlap_census(self) -> None:
        result = CHECK.simultaneous_bh_constraints()[
            "frozen_rank_ten_core_control"
        ]
        self.assertEqual(
            result["forced_block_pair_overlap_counts_if_B_exists"],
            {"0": 446, "1": 1_028, "2": 296},
        )
        self.assertEqual(
            result["forced_H_nonedge_overlap_counts_if_completion_exists"],
            {"0": 350, "1": 884, "2": 296},
        )

    def test_h_edge_triangle_decomposition(self) -> None:
        result = CHECK.simultaneous_bh_constraints()
        self.assertEqual(
            result["simultaneous_H_edge_overlap_counts"],
            {"0": 96, "1": 144, "2": 0},
        )
        frozen = result["frozen_rank_ten_core_control"]
        self.assertEqual(frozen["forced_H_triangles_if_completion_exists"], 32)
        self.assertEqual(
            frozen["forced_H_four_cycles_if_completion_exists"],
            175,
        )

    def test_status_wall(self) -> None:
        conclusion = CHECK.build_results()["conclusion"]
        self.assertFalse(conclusion["rank_twelve_boundary_excluded"])
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["upper_bound_improved_below_4158"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
