from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave196_proof_a", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave196ProofATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.derive()

    def test_four_fibers_partition_nonneighbors(self) -> None:
        geometry = self.result["local_geometry"]
        self.assertEqual(geometry["two_block_types"], 21)
        self.assertEqual(geometry["fiber_size"], 4)
        self.assertEqual(geometry["partitioned_nonneighbors"], 84)

    def test_hilton_milner_templates(self) -> None:
        templates = self.result["local_geometry"][
            "hilton_milner_equality_templates"
        ]
        for template in templates.values():
            self.assertEqual(template["members"], 13)
            self.assertEqual(template["number_pair_degree_five"], 3)
            self.assertGreaterEqual(template["forced_fiber_repeats"], 3)
            self.assertLessEqual(template["leaf_union_cap"], 36)

    def test_common_star_cap(self) -> None:
        geometry = self.result["local_geometry"]
        self.assertEqual(geometry["common_star_flag_cap"], 12)
        self.assertEqual(geometry["universal_local_oriented_label_cap"], 36)

    def test_global_cap(self) -> None:
        geometry = self.result["local_geometry"]
        self.assertEqual(geometry["global_flag_cap"], 1287)
        self.assertEqual(geometry["global_oriented_label_cap_H"], 3564)

    def test_certificate(self) -> None:
        certificate = self.result["certificate"]
        self.assertTrue(certificate["all_remainder_coefficients_nonnegative"])
        self.assertEqual(
            certificate["remainder_coefficients"],
            {
                "a1": "1/6",
                "b3": "1/2",
                "c2": "1/6",
                "W": "1/3",
            },
        )

    def test_integer_null_control(self) -> None:
        control = self.result["integer_null_control"]
        self.assertFalse(control["is_object"])
        self.assertEqual(control["target"], "7029")
        for slack in ("SI", "S2", "SE2", "RA", "SL", "S36"):
            self.assertEqual(control["evaluation"][slack], "0")

    def test_bound(self) -> None:
        bound = self.result["bound"]
        self.assertEqual(bound["projective_nonedge_Q"], 7029)
        self.assertEqual(bound["edge_added_projective"], 7722)
        self.assertEqual(bound["circuit_scalar_words"], 15444)

    def test_scope(self) -> None:
        scope = self.result["search_scope"].lower()
        self.assertIn("no graph", scope)
        self.assertNotIn("numerical", scope)


if __name__ == "__main__":
    unittest.main()
