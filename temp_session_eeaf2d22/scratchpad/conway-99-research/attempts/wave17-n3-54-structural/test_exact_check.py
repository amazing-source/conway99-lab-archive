"""Focused tests for the Wave 17 n3=54 structural exact companion."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave17_n3_54_exact_check", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ExactCheckTests(unittest.TestCase):
    def test_profile_census(self) -> None:
        self.assertEqual(len(CHECK.raw_profiles()), 23)
        survivors = CHECK.surviving_profiles()
        self.assertEqual(
            survivors,
            [
                (14, (2,) * 6 + (3,) * 8),
                (15, (2,) * 9 + (3,) * 6),
                (16, (2,) * 12 + (3,) * 4),
                (17, (2,) * 16 + (4,)),
                (17, (2,) * 15 + (3,) * 2),
                (18, (2,) * 18),
            ],
        )

    def test_size_two_types(self) -> None:
        for left, right in ((2, 2), (2, 4), (3, 3), (4, 4)):
            record = CHECK.size_two_type(left, right)
            self.assertTrue(record["compatible_with_0_or_4_crossings"])
            self.assertGreaterEqual(record["positive_support_neighbors"], 2)
        for left, right in ((2, 3), (3, 4)):
            self.assertFalse(
                CHECK.size_two_type(left, right)[
                    "compatible_with_0_or_4_crossings"
                ]
            )

    def test_dense_subset_boundary(self) -> None:
        self.assertLess(CHECK.spectral_average_upper(25), 6)
        self.assertEqual(CHECK.spectral_average_upper(27), Fraction(6))

    def test_surface_counts(self) -> None:
        residual = CHECK.build_result()["residual_counts"]
        self.assertEqual(
            residual["auxiliary_H_order"]
            - residual["auxiliary_H_edges"]
            + residual["hexagonal_faces"],
            -9,
        )

    def test_triangle_types(self) -> None:
        for c in range(10):
            types = CHECK.triangle_types(c)
            self.assertEqual(
                sum(
                    types[key]
                    for key in (
                        "X_vertices_0",
                        "X_vertices_1",
                        "X_vertices_2",
                        "X_vertices_3",
                    )
                ),
                231,
            )
            self.assertEqual(
                CHECK.inactive_triangle_meeting_moments(c),
                {
                    "inactive_triangle_count": 213,
                    "sum_active_meeting_triangles": 270,
                    "sum_squares_active_meeting_triangles": 756,
                },
            )

    def test_cycle_adjacency_nullities(self) -> None:
        for length in range(3, 28):
            self.assertEqual(
                CHECK.cycle_adjacency_nullity_mod2(length),
                1 if length % 2 else 2,
            )

    def test_point_graph_component_reduction(self) -> None:
        reduction = CHECK.build_result()["point_graph_component_reduction"]
        self.assertEqual(
            reduction["three_K3,3_components"],
            "excluded by exact-coverage parity",
        )
        self.assertEqual(len(reduction["surviving_options"]), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
