#!/usr/bin/env python3
"""Tests for the Wave 47 three-labelled-root moment discovery."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "three_root_moment.py"
SPEC = importlib.util.spec_from_file_location("wave47_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
W47 = importlib.util.module_from_spec(SPEC)
sys.modules["wave47_under_test"] = W47
SPEC.loader.exec_module(W47)


class ThreeRootMomentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.coefficients = json.loads(
            (HERE / "coefficients.json").read_text(encoding="utf-8")
        )
        cls.results = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
        cls.cuts = json.loads((HERE / "cuts.json").read_text(encoding="utf-8"))

    def test_root_partition(self) -> None:
        families = W47.families()
        self.assertEqual(
            sum(family.root_embeddings_at_target for family in families),
            99 * 98 * 97,
        )
        self.assertEqual(
            [family.root_embeddings_at_target for family in families],
            [590436, 99792, 99792, 16632, 99792, 16632, 16632, 1386],
        )

    def test_flag_census(self) -> None:
        self.assertEqual(
            [len(family.flags) for family in W47.families()],
            [64, 56, 56, 42, 56, 42, 42, 20],
        )

    def test_class_and_family_census(self) -> None:
        self.assertEqual(
            self.coefficients["class_streams"],
            {
                "5": {
                    "count": 21,
                    "sha256": self.coefficients["class_streams"]["5"]["sha256"],
                },
                "6": {
                    "count": 62,
                    "sha256": self.coefficients["class_streams"]["6"]["sha256"],
                },
                "7": {
                    "count": 208,
                    "sha256": self.coefficients["class_streams"]["7"]["sha256"],
                },
            },
        )
        self.assertEqual(len(self.coefficients["families"]), 8)
        for family in self.coefficients["families"].values():
            self.assertEqual(len(family["class_coefficients"]), 291)

    def test_controls_match_exactly(self) -> None:
        for control in self.results["controls"]:
            for family in control["families"].values():
                self.assertTrue(family["direct_equals_unrooted_expansion"])
                self.assertEqual(
                    family["exact_psd_reason"], "direct sum of integer outer products"
                )
            self.assertEqual(
                control["induced_subset_totals"],
                {
                    str(order): math.comb(control["order"], order)
                    for order in (5, 6, 7)
                },
            )

    def test_every_target_has_exact_refutation(self) -> None:
        self.assertEqual(len(self.results["targets"]), 17)
        self.assertTrue(
            self.results["conclusion"][
                "all_17_immutable_witnesses_refuted_by_three_root_layer"
            ]
        )
        for target in self.results["targets"]:
            self.assertGreater(target["exactly_indefinite_family_count"], 0)
            self.assertTrue(
                any(
                    family["exact_negative_direction_count"] > 0
                    for family in target["family_results"].values()
                )
            )

    def test_every_retained_cut_separates_source(self) -> None:
        self.assertGreater(len(self.cuts["cuts"]), 0)
        self.assertEqual(
            len(self.cuts["cuts"]), self.results["cut_ledger"]["unique_cut_count"]
        )
        classes7 = W47.frozen_classes()[7]
        source_counts = {
            target["name"]: target["counts7"]
            for target in W47.source_targets(classes7)
        }
        for cut in self.cuts["cuts"]:
            exact_value = cut["constant"] + sum(
                term["coefficient"]
                * source_counts[cut["source"]][term["canonical_mask"]]
                for term in cut["coefficients"]
            )
            self.assertEqual(exact_value, cut["source_cut_value"])
            self.assertLess(exact_value, 0)
            self.assertEqual(
                cut["cut_sha256"],
                W47.sha256_json(
                    {
                        key: cut[key]
                        for key in (
                            "family",
                            "root_pattern",
                            "vector",
                            "primitive_divisor",
                            "constant",
                            "coefficients",
                        )
                    }
                ),
            )

    def test_status_wall(self) -> None:
        conclusion = self.results["conclusion"]
        self.assertEqual(conclusion["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(conclusion["strict_upper_bound_below_4158"], "NOT_PROVED")
        self.assertFalse(conclusion["full_psd_constrained_count_system_tested"])
        self.assertFalse(conclusion["graph_constructed"])


if __name__ == "__main__":
    unittest.main()
