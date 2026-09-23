from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave99_exact_tested", HERE / "exact_check.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load Wave 99 checker")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave99ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.exact_result()

    def test_archived_result(self) -> None:
        archived = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(archived, self.result)

    def test_scaffold_counts(self) -> None:
        local = self.result["canonical_local_check"]
        self.assertEqual(local["seed_count"], 560)
        self.assertEqual(local["seed_extensions_per_transition"], 8)
        self.assertEqual(local["local_perfect_matchings"], 6040)

    def test_local_contribution_dichotomy(self) -> None:
        for key in ("center_a_profile", "center_b_profile"):
            profile = self.result["canonical_local_check"][key]
            self.assertEqual(profile["with_identical_values"], [8])
            self.assertLessEqual(profile["without_identical_max"], 2)

    def test_pair_moment(self) -> None:
        moments = self.result["moments"]
        self.assertEqual(moments["first_transition_seed_moment"], 672)
        self.assertEqual(moments["pair_transition_seed_moment_upper"], 756)
        self.assertEqual(moments["bad_seed_lower"], 210)

    def test_pointwise_certificate(self) -> None:
        for j in range(1, 5):
            slack = Fraction(1) - Fraction(j, 2) + Fraction(j * (j - 1) // 2, 6)
            self.assertGreaterEqual(slack, 0)

    def test_n14_bound(self) -> None:
        self.assertEqual(self.result["bounds"]["N14_upper"], 4950)
        self.assertEqual(self.result["bounds"]["improvement"], 594)

    def test_weighted_corollary_arithmetic(self) -> None:
        bounds = self.result["bounds"]
        self.assertEqual(
            bounds["rank28_weighted_shell_inequality"],
            "407*N16+43*N18>=2165002",
        )
        self.assertGreaterEqual(407 * bounds["if_N18_zero_even_N16_lower"], 2_165_002)
        self.assertGreaterEqual(43 * bounds["if_N16_zero_even_N18_lower"], 2_165_002)

    def test_scope_is_fail_closed(self) -> None:
        scope = self.result["scope"]
        self.assertTrue(scope["requires_prism_free_endpoint"])
        self.assertFalse(scope["rank_28_used_for_n14_bound"])
        self.assertTrue(scope["rank_28_used_for_weighted_corollary"])
        self.assertEqual(
            self.result["status"]["N16_or_N18_upper_bound"], "NOT_PROVED"
        )
        self.assertEqual(self.result["status"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
