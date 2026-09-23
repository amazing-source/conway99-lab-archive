"""Tests for the exact Wave144 discovery checker."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave144_exact_check_tested",
    HERE / "exact_check.py",
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Wave144Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_result()

    def test_all_62_source_classes_are_present(self) -> None:
        records = self.result["class_profiles"]
        self.assertEqual([row["source_class"] for row in records], list(range(1, 63)))

    def test_forced_singleton_leads(self) -> None:
        self.assertEqual(
            self.result["forced_singleton_cells"],
            {"1": 66, "3": 56, "5": 46, "14": 36},
        )

    def test_supports_are_exact_nontrivial_sets(self) -> None:
        records = {
            row["source_class"]: row["attainable_weights"]
            for row in self.result["class_profiles"]
        }
        self.assertEqual(records[2], [56, 60, 64])
        self.assertEqual(
            records[36],
            [24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 72],
        )
        self.assertNotIn(68, records[36])

    def test_selected_local_profiles_replay(self) -> None:
        wave21 = CHECK.load_wave21()
        _, m_mapping = wave21.align_four_five()
        six_mapping = wave21.align_five_six(
            m_mapping,
            wave21.corrected_five_to_six(),
        )
        classes = wave21.locally_admissible_classes(6)
        for record in self.result["selected_local_integer_witnesses"]:
            profile = [0] * 64
            for cell, value in record["z_by_subset_mask_sparse"].items():
                profile[int(cell)] = value
            mask = classes[six_mapping[record["source_class"] - 1]]
            CHECK.verify_profile(mask, profile, record["output_weight"])

    def test_integral_endpoint_and_marginals(self) -> None:
        certificate = self.result["aggregate_endpoint_certificate"]
        self.assertEqual(certificate["n3"], 4158)
        self.assertEqual(certificate["variable_domain"], "nonnegative integers")
        self.assertEqual(
            sum(certificate["class_marginals"].values()),
            math.comb(99, 6),
        )
        self.assertEqual(certificate["moment_lhs"], certificate["moment_rhs"])

    def test_sealed_file_matches_recomputation(self) -> None:
        sealed = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(sealed, self.result)


if __name__ == "__main__":
    unittest.main()
