from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave195_proof_a", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave195ProofATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = MODULE.derive()

    def test_equal_A_forces_weight_two(self) -> None:
        local = self.result["ternary_cancellations"]
        self.assertEqual(local["equal_A_cancellation_weight"], 2)
        self.assertLess(
            local["equal_A_cancellation_weight"],
            local["dual_distance_input"],
        )

    def test_disjoint_A_forces_weight_three(self) -> None:
        local = self.result["ternary_cancellations"]
        self.assertEqual(local["disjoint_A_cancellation_weight"], 3)
        self.assertLess(
            local["disjoint_A_cancellation_weight"],
            local["dual_distance_input"],
        )

    def test_hilton_milner_specialization(self) -> None:
        hm = self.result["local_set_system"]["hilton_milner"]
        self.assertEqual(hm["first_term"], 15)
        self.assertEqual(hm["subtracted_term"], 3)
        self.assertEqual(hm["nontrivial_cap"], 13)

    def test_local_affine_envelope(self) -> None:
        local = self.result["local_set_system"]
        self.assertEqual(local["common_star_distinct_neighbor_cap"], 12)
        self.assertEqual(local["hm_global_center_capacity"], 1287)
        self.assertEqual(local["affine_constant_H"], 3861)
        self.assertEqual(local["unified_local_row"], "j_x<=39")

    def test_certificate_coefficients(self) -> None:
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

    def test_rational_null_control(self) -> None:
        control = self.result["rational_null_control"]
        self.assertFalse(control["is_object"])
        self.assertEqual(control["target"], "13959/2")
        for slack in ("SI", "S2", "SE2", "RA", "SL", "SG"):
            self.assertEqual(control["evaluation"][slack], "0")

    def test_old_equality_face_is_refuted(self) -> None:
        old = self.result["old_equality_face"]
        self.assertEqual(old["packets"], 1386)
        self.assertEqual(old["global_center_capacity"], 1287)
        self.assertEqual(old["capacity_deficit"], 99)
        self.assertEqual(old["SG"], -297)

    def test_strict_bound(self) -> None:
        bound = self.result["bound"]
        self.assertEqual(bound["rational_Q0"], "13959/2")
        self.assertEqual(bound["integral_Q"], 6980)
        self.assertEqual(bound["edge_added_projective"], 7673)
        self.assertEqual(bound["circuit_scalar_words"], 15346)

    def test_scope(self) -> None:
        scope = self.result["search_scope"].lower()
        self.assertIn("no graph", scope)
        self.assertNotIn("gram", scope)


if __name__ == "__main__":
    unittest.main()
