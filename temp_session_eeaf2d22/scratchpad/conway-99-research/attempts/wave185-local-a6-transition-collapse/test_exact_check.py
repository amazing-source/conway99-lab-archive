from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave185_exact_check", HERE / "exact_check.py")
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave185ExactCheckTests(unittest.TestCase):
    def test_transition_rows(self) -> None:
        self.assertEqual(
            CHECK.transition_row(0),
            {
                "internal": 0,
                "incident_transition": 2,
                "incident_disjoint": 2,
                "orthogonal_disjoint": 8,
            },
        )
        self.assertEqual(
            CHECK.transition_row(1),
            {
                "internal": 1,
                "incident_transition": 2,
                "incident_disjoint": 0,
                "orthogonal_disjoint": 9,
            },
        )

    def test_prism_rejects_p4_degree(self) -> None:
        with self.assertRaisesRegex(AssertionError, "internal degree"):
            CHECK.transition_row(2)

    def test_multiplicity_parameterization(self) -> None:
        profiles = CHECK.multiplicity_profiles()
        self.assertEqual(len(profiles), 67)
        self.assertEqual(profiles[0], {"u": 0, "n5": 15, "n6": 334, "roots": 349})
        self.assertEqual(profiles[-1], {"u": 66, "n5": 411, "n6": 4, "roots": 415})
        self.assertTrue(all(5 * p["n5"] + 6 * p["n6"] == 2079 for p in profiles))

    def test_global_summary(self) -> None:
        data = CHECK.derive()
        self.assertTrue(data["cell"]["multiplicity_seven_excluded"])
        self.assertEqual(data["type5_companions"]["distinct_companions"], 10)
        self.assertEqual(data["type5_companions"]["congruence_n5_floor"], 15)
        self.assertEqual(data["root_interval"], [349, 415])
        self.assertEqual(data["rainbow_triangles"]["minimum_rainbow"], 94264)
        self.assertEqual(data["global_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
