from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("residual_profile.py")
SPEC = importlib.util.spec_from_file_location("wave41_residual_profile", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.path.insert(0, str(MODULE_PATH.parent))
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ResidualProfileTests(unittest.TestCase):
    def test_live_profile_has_tight_constraints(self) -> None:
        root = MODULE.Path(__file__).resolve().parents[2]
        closure = (
            root
            / "attempts"
            / "wave41-proof-producing-search"
            / "branch-15-propagation-certificate.json"
        )
        profile = MODULE.build_profile(MODULE.DEFAULT_SOURCE, closure, 8)
        self.assertGreater(profile["open_constraints"], 0)
        self.assertGreater(profile["tight_slack_one_constraints"], 0)
        self.assertEqual(len(profile["top_primary_probe_variables"]), 8)
        self.assertEqual(profile["claim_label"], "CANDIDATE_DIAGNOSTIC")


if __name__ == "__main__":
    unittest.main()
