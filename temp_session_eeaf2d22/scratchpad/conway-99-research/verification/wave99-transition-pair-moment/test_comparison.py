from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("compare_discovery.py")
SPEC = importlib.util.spec_from_file_location(
    "wave99_compare_discovery", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
COMPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPARE)


class Wave99ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = COMPARE.comparison()

    def test_attempt_manifest_is_complete_and_frozen(self) -> None:
        entries = COMPARE.verify_attempt_manifest()
        self.assertEqual(len(entries), 9)

    def test_claim_is_verified_scoped(self) -> None:
        self.assertEqual(self.result["claim_label"], "VERIFIED")
        self.assertIn("VERIFIED SCOPED", self.result["verdict"])

    def test_all_numerical_claims_agree(self) -> None:
        self.assertEqual(
            self.result["agreement"],
            {
                "per_transition_coincidence_cap": 18,
                "first_moment": 672,
                "unordered_pair_moment_upper": 756,
                "zero_transition_seed_upper": 350,
                "N14_upper": 4950,
                "rank28_weighted_lower": 2165002,
            },
        )

    def test_scope_does_not_mix_rows(self) -> None:
        scope = self.result["scope_audit"]
        self.assertTrue(scope["N14_requires_P0_n3_4158"])
        self.assertFalse(scope["N14_requires_rank28"])
        self.assertTrue(
            scope["weighted_conclusion_requires_P0_and_rank28_q16"]
        )
        self.assertFalse(scope["scope_mixing_found"])

    def test_global_status_stays_unknown(self) -> None:
        status = self.result["status_boundary"]
        self.assertEqual(status["strict_n3_upper_bound"], "NOT_PROVED")
        self.assertFalse(status["prism_free_rank28_excluded"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
