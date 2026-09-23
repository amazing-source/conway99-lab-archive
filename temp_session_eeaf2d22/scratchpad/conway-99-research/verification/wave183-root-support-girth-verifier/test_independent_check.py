from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave183_independent_check", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave183Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = CHECK.build_results()

    def test_pair_rule_records_both_cases(self) -> None:
        rule = self.results["pair_common_neighbor_rule"]
        self.assertEqual(rule["adjacent_case"], "lambda=1")
        self.assertIn("orthogonality", rule["nonadjacent_case"])
        self.assertEqual(rule["maximum_inside_support"], 1)

    def test_unordered_two_path_boundary(self) -> None:
        rows = {row["multiplicity"]: row for row in self.results["support_rows"]}
        self.assertEqual(rows[8]["internal_two_paths"], 24)
        self.assertEqual(rows[8]["internal_pairs"], 28)
        self.assertTrue(rows[8]["pair_bound_survives"])
        self.assertEqual(rows[9]["internal_two_paths"], 54)
        self.assertEqual(rows[9]["internal_pairs"], 36)
        self.assertFalse(rows[9]["pair_bound_survives"])
        self.assertEqual(rows[10]["internal_two_paths"], 100)
        self.assertEqual(rows[10]["internal_pairs"], 45)
        self.assertFalse(rows[10]["pair_bound_survives"])

    def test_cubic_nonedge_exclusion(self) -> None:
        cubic = self.results["cubic_case"]
        self.assertEqual(cubic["two_paths"], 24)
        self.assertEqual(cubic["nonedge_endpoint_capacity"], 16)
        self.assertEqual(cubic["adjacent_endpoint_lower"], 8)

    def test_cubic_triangle_rounding_and_disjointness(self) -> None:
        cubic = self.results["cubic_case"]
        self.assertEqual(cubic["triangle_edge_divisor"], 3)
        self.assertEqual(cubic["triangle_lower"], 3)
        self.assertTrue(cubic["triangles_vertex_disjoint"])
        self.assertEqual(cubic["vertex_disjoint_triangle_upper"], 2)
        self.assertTrue(cubic["contradiction"])

    def test_support_classification(self) -> None:
        self.assertEqual(self.results["allowed_multiplicities"], [5, 6, 7])
        self.assertEqual(
            self.results["support_shapes"],
            {"5": "5K1", "6": "3K2", "7": "C7"},
        )

    def test_root_count_and_defect(self) -> None:
        global_result = self.results["global"]
        self.assertEqual(global_result["root_incidences"], 2079)
        self.assertEqual(global_result["distinct_root_lower"], 297)
        self.assertEqual(global_result["distinct_root_upper"], 415)
        self.assertEqual(
            global_result["defect_equation"], "7*R-2079=2*n5+n6"
        )

    def test_frame_is_split_not_contradiction(self) -> None:
        frame = self.results["frame"]
        self.assertEqual(frame["coefficient_mod3"], {"5": 2, "6": 0, "7": 1})
        self.assertEqual(
            frame["split_identity"],
            "sum_(m=7) r tensor r=sum_(m=5) r tensor r",
        )
        self.assertFalse(frame["contradiction_obtained"])
        self.assertEqual(self.results["endpoint_status"], "UNKNOWN")

    def test_verdict_scope(self) -> None:
        self.assertEqual(self.results["verdict"], "VERIFIED_WITH_SCOPE")


if __name__ == "__main__":
    unittest.main()
