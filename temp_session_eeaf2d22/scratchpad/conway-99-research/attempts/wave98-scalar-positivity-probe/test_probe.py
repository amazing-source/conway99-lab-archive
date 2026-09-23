from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave98_probe_tested", HERE / "probe.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load Wave 98 probe")
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


class Wave98ProbeTests(unittest.TestCase):
    def test_short_reconstruction_matches_wave86(self) -> None:
        result = PROBE.exact_probe(50)
        self.assertTrue(result["wave86_prefix_matches"])
        self.assertTrue(result["integral_even_nonnegative_through_prefix"])
        self.assertEqual(result["first_bad"], {})

    def test_archived_long_prefix(self) -> None:
        archived = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(archived["precision"], 1000)
        self.assertTrue(archived["wave86_prefix_matches"])
        self.assertTrue(archived["integral_even_nonnegative_through_prefix"])
        self.assertEqual(archived["first_bad"], {})

    def test_finite_scope_is_fail_closed(self) -> None:
        archived = json.loads(
            (HERE / "exact-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(archived["claim_label"], "UNKNOWN")
        joined = " ".join(archived["limitations"]).lower()
        self.assertIn("finite", joined)
        self.assertIn("not a lattice", joined)
        self.assertIn("not independent", joined)


if __name__ == "__main__":
    unittest.main()
