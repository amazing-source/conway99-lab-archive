from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave199_b", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Wave199NearFaceAuditTests(unittest.TestCase):
    def test_frozen_result(self) -> None:
        expected = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.derive(), expected)

    def test_scaled_budget(self) -> None:
        face = MODULE.derive()["wave198_face"]
        self.assertEqual(face["scaled_budget"], 23)
        self.assertEqual(face["immediate_caps"], {"SF": 1, "g": 2, "SH": 7, "S5": 23})

    def test_symbolic_identities(self) -> None:
        identities = MODULE.identity_checks()
        self.assertEqual(
            identities["S5_identity"],
            "S5=5*delta+5*eta+epsilon",
        )
        self.assertEqual(
            identities["q_identity"],
            "4*q=297-3*SF-3*g-SH+epsilon+delta+eta",
        )

    def test_global_lower_bound(self) -> None:
        global_data = MODULE.derive()["global_multiplicity"]
        self.assertEqual(global_data["q_min"], 71)
        self.assertEqual(global_data["multiplicity_five_orientations_min"], 48)

    def test_local_c13_bound(self) -> None:
        local = MODULE.derive()["local_gluing"]
        self.assertEqual(local["c13_degree_five_pair_cap"], 3)
        self.assertEqual(local["c13_deficit_per_saturated_center"], 3)
        self.assertEqual(local["c13_global_saturated_cap"], 3)

    def test_deficient_center_bound(self) -> None:
        local = MODULE.derive()["local_gluing"]
        self.assertEqual(local["c12_saturated_orientation_cap"], 7)
        self.assertEqual(local["global_saturated_orientation_cap"], 7)
        self.assertEqual(local["proof_a_looser_cap"], 12)

    def test_contradiction_and_consequence(self) -> None:
        result = MODULE.derive()
        self.assertEqual(result["contradiction"]["status"], "CONTRADICTION")
        self.assertGreater(
            result["contradiction"]["required_saturated_orientations"],
            result["contradiction"]["maximum_saturated_orientations"],
        )
        self.assertEqual(result["consequence"]["conditional_Q_lower_bound"], 7038)
        self.assertEqual(result["consequence"]["edge_added_projective"], 7731)
        self.assertEqual(result["consequence"]["circuit_scalar_words"], 15462)


if __name__ == "__main__":
    unittest.main()
