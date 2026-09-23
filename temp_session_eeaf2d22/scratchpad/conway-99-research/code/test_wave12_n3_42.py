#!/usr/bin/env python3
"""Focused discovery tests for the Wave 12 n3=42 construction lane."""

from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"could not load {path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


ACTIVE = load(
    "wave12_n3_42_active_tested",
    ROOT / "code" / "wave12_n3_42_active.py",
)
CAPS = load(
    "wave12_n3_42_caps_tested",
    ROOT / "code" / "wave12_n3_42_size2_caps.py",
)
CANDIDATE_PATH = (
    ROOT
    / "attempts"
    / "wave12-computation"
    / "n3-42-size2-active-local-candidate.json"
)
CATALOG_PATH = (
    ROOT
    / "attempts"
    / "wave12-computation"
    / "n3-42-cubic-trianglefree-14.g6"
)


class Wave12N342Tests(unittest.TestCase):
    def test_six_raw_profiles_and_two_no_singleton_survivors(self) -> None:
        self.assertEqual(ACTIVE.active_q_profiles(), ACTIVE.EXPECTED_RAW_PROFILES)
        table = ACTIVE.profile_table()
        self.assertEqual(
            tuple(row["forced_singleton_lower_bound"] for row in table),
            (0, 0, 3, 4, 12, 24),
        )
        self.assertEqual(
            tuple(
                profile
                for profile, row in zip(
                    ACTIVE.active_q_profiles(), table, strict=True
                )
                if row["survives_no_singleton_premise"]
            ),
            ACTIVE.EXPECTED_SURVIVING_PROFILES,
        )

    def test_size_four_and_mixed_star_exhaustions(self) -> None:
        order13 = ACTIVE.size_four_flower_census(13, 6)
        order14 = ACTIVE.size_four_flower_census(14, 7)
        self.assertEqual(
            (order13["capacity_feasible"], order14["capacity_feasible"]),
            (9, 45),
        )
        self.assertEqual((order13["survivors"], order14["survivors"]), (0, 0))
        mixed = ACTIVE.mixed_degree_three_star_census()
        self.assertEqual(mixed["assignment_count"], 2)
        self.assertEqual(mixed["survivors"], 0)
        self.assertTrue(
            all(
                len(record["common_point_conflicts"]) == 2
                for record in mixed["assignments"]
            )
        )

    def test_restricted_candidate_and_status_mutation(self) -> None:
        candidate = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
        result = ACTIVE.validate_size2_candidate(candidate)
        self.assertEqual(
            result["status"],
            "PASS restricted n3=42 active-local candidate",
        )
        self.assertEqual(result["point_sets"], 21)
        self.assertEqual(result["K_edges"], 49)
        self.assertEqual(result["support_sum_per_point"], 8)
        self.assertEqual(result["diagnostic_adjacent_cap_violations"], 34)
        self.assertEqual(result["diagnostic_universal_two_cap_violations"], 20)
        self.assertEqual(result["target_result"], "UNKNOWN")

        inflated = copy.deepcopy(candidate)
        inflated["target_result"] = "EXISTS"
        with self.assertRaises(AssertionError):
            ACTIVE.validate_size2_candidate(inflated)

        broken_complement = copy.deepcopy(candidate)
        broken_complement["L_edges"].pop()
        with self.assertRaises(AssertionError):
            ACTIVE.validate_size2_candidate(broken_complement)

    def test_catalog_filter_and_full_cap_census(self) -> None:
        result = CAPS.run_census(CATALOG_PATH)
        self.assertEqual(result["catalog_records"], 112)
        self.assertEqual(result["mandatory_degree_rejections"], 108)
        self.assertEqual(len(result["viable_representatives"]), 4)
        self.assertEqual(result["full_cap_survivors"], 0)
        self.assertEqual(result["claim_label"], "CANDIDATE")
        self.assertEqual(result["target_result"], "UNKNOWN")
        diagnostic = result["viable_representatives"][1]["lambda_cap_search"]
        self.assertIsNotNone(diagnostic["first_solution"])
        self.assertEqual(
            len(diagnostic["first_solution"]),
            21,
        )


if __name__ == "__main__":
    unittest.main()
