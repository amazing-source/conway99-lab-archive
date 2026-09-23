"""Tests for Wave137 exact branch replay."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave137_exact_check", HERE / "exact_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class BranchReplayTests(unittest.TestCase):
    def test_all_binary_branches(self):
        cases = [
            ("binary-global-plus.json", 1, 0),
            ("binary-global-minus.json", -1, 0),
            ("binary-k1-plus.json", 1, 1),
            ("binary-k1-minus.json", -1, 1),
            ("binary-k2-plus.json", 1, 2),
            ("binary-k2-minus.json", -1, 2),
            ("binary-k3-plus.json", 1, 3),
            ("binary-k3-minus.json", -1, 3),
            ("binary-k4-plus.json", 1, 4),
            ("binary-k4-minus.json", -1, 4),
            ("binary-k5-plus.json", 1, 5),
            ("binary-k5-minus.json", -1, 5),
            ("binary-shadow1-plus.json", 1, 5),
            ("binary-shadow1-minus.json", -1, 5),
        ]
        for filename, sign, max_moment in cases:
            with self.subTest(filename=filename):
                result = CHECK.verify(HERE / filename)
                self.assertTrue(result["terminal_witness_replayed"])
                self.assertEqual(result["sign"], sign)
                self.assertEqual(result["max_moment"], max_moment)
                self.assertTrue(
                    result["G_E_equals_minus_G_R_over_32"]
                )
                if max_moment:
                    self.assertEqual(result["K1_signed_moment"], "0")
                self.assertEqual(
                    len(result["signed_krawtchouk_moments"]),
                    max(0, max_moment - 1),
                )
                if "shadow1" in filename:
                    self.assertEqual(
                        set(result["shadow_cut_values"]),
                        {"K6", "K93"},
                    )


if __name__ == "__main__":
    unittest.main()
