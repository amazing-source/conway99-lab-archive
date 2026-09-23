from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_wave64 as verifier


class IndependentWave64Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = verifier.verify()

    def test_full_independent_verification(self) -> None:
        self.assertTrue(self.result["passed"])
        self.assertEqual(self.result["claim_label"], "VERIFIED")

    def test_exact_finite_counts(self) -> None:
        census = self.result["components"]["finite_census"]
        self.assertEqual(census["candidate_blocks"], 35_560)
        self.assertEqual(census["allowed_transitions"], 840)
        self.assertEqual(census["local_perfect_matching_counts"], [6_040] * 14)
        self.assertEqual(census["transition_triangle_cuts"], 280)

    def test_integral_witness(self) -> None:
        witness = self.result["components"]["integral_block_witness"]
        self.assertTrue(witness["passed"])
        self.assertEqual(witness["selected_blocks"], 140)
        self.assertEqual(
            witness["support_occupancy_profiles_n0_n1_n2"],
            [[32, 96, 12]] * 7,
        )
        self.assertEqual(
            witness["relation_counts_support_union_2_3_4"], [5, 74, 341]
        )

    def test_fractional_control(self) -> None:
        fractional = self.result["components"][
            "fractional_linear_master_control"
        ]
        self.assertTrue(fractional["passed"])
        self.assertEqual(fractional["endpoint_profile_residual_values"], ["0"])
        self.assertEqual(fractional["transition_triangle_lhs"], "3/10")

    def test_codegree_scope(self) -> None:
        closure = self.result["components"]["codegree_closure"]
        self.assertEqual(
            closure["residual_pair_partition"],
            {
                "disjoint": 2_562,
                "intersect_allowed": 840,
                "intersect_forbidden": 84,
            },
        )
        self.assertIn("do not independently forbid prisms", closure["scope"])

    def test_duplicate_block_is_rejected(self) -> None:
        payload = json.loads(
            (verifier.DISCOVERY / "block-witness.json").read_text(encoding="utf-8")
        )
        corrupted = copy.deepcopy(payload)
        corrupted["selected_blocks"][1] = copy.deepcopy(
            corrupted["selected_blocks"][0]
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text(json.dumps(corrupted), encoding="utf-8")
            with self.assertRaises(AssertionError):
                verifier.load_block_witness(path)

    def test_changed_label_is_rejected(self) -> None:
        payload = json.loads(
            (verifier.DISCOVERY / "block-witness.json").read_text(encoding="utf-8")
        )
        corrupted = copy.deepcopy(payload)
        corrupted["selected_blocks"][0]["labels"][0][0] ^= 1
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "changed-label.json"
            path.write_text(json.dumps(corrupted), encoding="utf-8")
            with self.assertRaises(AssertionError):
                verifier.load_block_witness(path)

    def test_result_is_deterministic(self) -> None:
        first = json.dumps(self.result, indent=2, sort_keys=True) + "\n"
        second = json.dumps(verifier.verify(), indent=2, sort_keys=True) + "\n"
        self.assertEqual(first.encode("utf-8"), second.encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
