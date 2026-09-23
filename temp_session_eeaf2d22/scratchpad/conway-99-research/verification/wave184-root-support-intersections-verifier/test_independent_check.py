from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave184_independent_check", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave184Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = CHECK.build_results()

    def test_support_intersection_logic(self) -> None:
        result = self.results["support_intersections"]
        self.assertEqual(result["maximum_for_distinct_roots"], 2)
        self.assertEqual(result["size_two_type"], "graph edge")
        self.assertIn("nonedge uniqueness", result["reason"])
        self.assertIn("binom(c_xy,2)", result["root_pair_identity"])

    def test_four_column_circuit_contract(self) -> None:
        circuit = self.results["edge_root_circuit"]
        self.assertTrue(circuit["shared_triangle_excluded"])
        self.assertEqual(circuit["distinct_columns"], 4)
        self.assertEqual(circuit["nonzero_coefficients"], 4)
        self.assertEqual(circuit["dual_distance_lower"], 4)
        self.assertEqual(circuit["weight"], 4)
        self.assertTrue(circuit["projective_root_recoverable"])

    def test_all_collision_classes_are_excluded(self) -> None:
        self.assertEqual(
            self.results["injectivity"],
            {
                "different_roots_same_edge": True,
                "different_graph_edges": True,
                "disjoint_from_canonical_nonedge_conics": True,
            },
        )

    def test_exact_support_edge_count(self) -> None:
        self.assertEqual(
            self.results["support_edge_counts"],
            {"5K1": 0, "3K2": 3, "C7": 7},
        )
        self.assertEqual(
            self.results["edge_root_circuit_count"], "E=3*n6+7*n7"
        )

    def test_every_sub_twelve_case_fails_the_residue(self) -> None:
        rows = self.results["sub_twelve_candidates"]
        self.assertEqual(
            [(row["n6"], row["n7"], row["E"]) for row in rows],
            [(0, 0, 0), (1, 0, 3), (2, 0, 6), (3, 0, 9),
             (0, 1, 7), (1, 1, 10)],
        )
        self.assertEqual(self.results["sub_twelve_valid_residue_count"], 0)
        self.assertEqual(self.results["edge_projective_weight4_lower"], 12)

    def test_scalar_sharpness_is_not_geometry(self) -> None:
        sharpness = self.results["scalar_sharpness"]
        self.assertEqual(
            sharpness["distribution"], {"n5": 411, "n6": 4, "n7": 0}
        )
        self.assertEqual(sharpness["root_incidences"], 2079)
        self.assertEqual(sharpness["E"], 12)
        self.assertFalse(sharpness["geometric_construction"])

    def test_projective_to_word_factor(self) -> None:
        count = self.results["weight4_count"]
        self.assertEqual(count["canonical_projective"], 2079)
        self.assertEqual(count["new_edge_projective_lower"], 12)
        self.assertEqual(count["total_projective_lower"], 2091)
        self.assertEqual(count["nonzero_scalars_per_projective_class"], 2)
        self.assertEqual(count["B4_lower"], 4182)

    def test_scope_wall(self) -> None:
        self.assertEqual(self.results["verdict"], "VERIFIED_WITH_SCOPE")
        self.assertEqual(self.results["endpoint_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
