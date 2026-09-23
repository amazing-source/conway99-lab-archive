from __future__ import annotations

import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import independent_check as check  # noqa: E402


class Wave185IndependentTests(unittest.TestCase):
    def test_frozen_hash_tree(self) -> None:
        result = check.verify_hash_tree(check.SOURCE_MANIFEST)
        self.assertTrue(result["passed"], result["failures"])
        paths = {row["path"] for row in result["lists_checked"]}
        self.assertIn(
            "attempts/wave185-local-a6-transition-collapse/package-manifest.sha256",
            paths,
        )
        self.assertIn(
            "attempts/wave185-local-a6-transition-collapse/input-freeze.sha256",
            paths,
        )
        self.assertIn(
            "verification/wave64-rooted-transition-design/package-manifest.sha256",
            paths,
        )

    def test_induced_prism_and_cell_restriction(self) -> None:
        result = check.induced_prism_and_cell()
        self.assertEqual(result["prism"]["degree_sequence"], [3] * 6)
        self.assertEqual(result["prism"]["edges"], 9)
        self.assertEqual(result["prism"]["triangles"], 2)
        self.assertEqual(result["cell"]["shared_endpoint_pairs_excluded"], 4)
        self.assertEqual(result["cell"]["opposite_corner_pairs_remaining"], 2)
        self.assertEqual(result["cell"]["maximum_internal_degree"], 1)
        self.assertTrue(result["cell"]["multiplicity_seven_excluded"])

    def test_transition_rows(self) -> None:
        rows = check.transition_table()
        self.assertEqual(
            rows["m5"],
            {
                "internal": 0,
                "incident_transition": 2,
                "incident_disjoint": 2,
                "orthogonal_disjoint": 8,
                "residual_degree": 12,
                "cell_transition_total": 8,
                "cell_incident_disjoint_total": 8,
            },
        )
        self.assertEqual(
            rows["m6"],
            {
                "internal": 1,
                "incident_transition": 2,
                "incident_disjoint": 0,
                "orthogonal_disjoint": 9,
                "residual_degree": 12,
                "cell_transition_total": 8,
                "cell_incident_disjoint_total": 0,
            },
        )

    def test_capacity_keeps_sharp_proved_six(self) -> None:
        result = check.incident_capacity_and_companions()
        self.assertEqual(result["common_neighbors_if_complete"], 3)
        self.assertEqual(result["mu"], 2)
        self.assertEqual(result["maximum_per_orientation"], 3)
        self.assertEqual(result["b_ef_upper"], 6)
        self.assertEqual(result["local_distinct_type5_companions"], 2)

    def test_global_companion_and_profiles(self) -> None:
        capacity = check.incident_capacity_and_companions()
        self.assertEqual(capacity["global_distinct_companions"], 10)
        self.assertEqual(capacity["raw_n5_floor"], 11)
        profiles = check.multiplicity_profiles(capacity["raw_n5_floor"])
        self.assertEqual(profiles["n5_residue_mod6"], 3)
        self.assertEqual(profiles["congruence_n5_floor"], 15)
        self.assertEqual(profiles["u_interval"], [0, 66])
        self.assertEqual(profiles["profile_count"], 67)
        self.assertEqual(profiles["root_interval"], [349, 415])
        self.assertEqual(profiles["minimum_n6"], 4)

    def test_rainbow_bound(self) -> None:
        profiles = check.multiplicity_profiles(11)
        result = check.rainbow_triangle_bound(profiles)
        self.assertEqual(result["total"], 98406)
        self.assertEqual(
            result["monochromatic_per_root"],
            {"m5": 10, "m6": 8},
        )
        self.assertEqual(result["maximum_monochromatic"], 4142)
        self.assertEqual(result["minimum_rainbow"], 94264)

    def test_deterministic_and_discovery_independent(self) -> None:
        first = check.build_result()
        second = check.build_result()
        self.assertEqual(check.canonical_json(first), check.canonical_json(second))
        self.assertFalse(first["source_checker_imported_or_executed"])
        self.assertEqual(first["global_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
