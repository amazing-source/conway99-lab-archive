from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave100_exact_tested", HERE / "exact_check.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load Wave 100 checker")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave100ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.exact_result()

    def test_archived_result(self) -> None:
        archived = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(archived, self.result)

    def test_all_rooted_floors(self) -> None:
        for f in range(85):
            self.assertEqual(
                CHECK.rooted_valid_upper(f), 350 + (5 * f) // 2
            )

    def test_full_compatible_domain(self) -> None:
        self.assertEqual(
            self.result["global_formula"]["compatible_rows_checked"], 1387
        )

    def test_endpoint_values(self) -> None:
        rows = self.result["global_formula"]["selected_rows"]
        self.assertEqual(rows["4158"]["N14_even_upper"], 4950)
        self.assertEqual(rows["4155"]["N14_even_upper"], 4952)
        self.assertEqual(rows["708"]["N14_even_upper"], 7414)
        self.assertEqual(rows["0"]["N14_even_upper"], 7920)

    def test_antipodal_rounding_never_weakens(self) -> None:
        for prisms in range(1387):
            n3 = 4158 - 3 * prisms
            numerator = 55_440 - 5 * n3
            ordinary = numerator // 7
            even = CHECK.even_floor(numerator, 7)
            self.assertLessEqual(even, ordinary)
            self.assertEqual(even % 2, 0)

    def test_scope_is_fail_closed(self) -> None:
        scope = self.result["scope"]
        self.assertFalse(scope["requires_rank_28"])
        self.assertFalse(scope["requires_prism_free"])
        self.assertTrue(
            self.result["status"]["depends_on_unverified_wave99_pair_moment"]
        )
        self.assertEqual(
            self.result["status"]["strict_n3_upper_bound"], "NOT_PROVED"
        )
        self.assertEqual(self.result["status"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
