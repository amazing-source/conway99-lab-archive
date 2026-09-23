from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave41_rank26_comparison", HERE / "comparison_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class Rank26CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = CHECK.strict_load(HERE / "discovery-comparison.json")

    def test_comparison_regenerates_exactly(self):
        self.assertEqual(CHECK.build_comparison(), self.results)

    def test_comparison_validates(self):
        CHECK.validate_comparison(self.results)

    def test_all_seven_even_invariants_agree(self):
        records = self.results["discovery_comparison"]["types"]
        self.assertEqual(set(records), set(CHECK.TYPE_MAP))
        self.assertTrue(
            all(all(record["invariants"].values()) for record in records.values())
        )

    def test_all_eleven_partition_types_are_covered(self):
        composition = self.results["composition"]
        odd = {tuple(parts) for parts in composition["all_odd_types"]}
        even = {tuple(parts) for parts in composition["even_part_types"]}
        all_types = {
            tuple(parts)
            for parts in composition["all_positive_partitions_of_six"]
        }
        self.assertFalse(odd & even)
        self.assertEqual(odd | even, all_types)
        self.assertEqual(len(all_types), 11)

    def test_universal_rank26_is_promoted(self):
        self.assertEqual(
            self.results["composition"]["universal_rank_F7_M_lower_bound"], 26
        )
        self.assertEqual(
            self.results["status_wall"][
                "universal_rank_F7_M_at_least_26"
            ],
            "VERIFIED",
        )

    def test_hostile_missing_type_is_rejected(self):
        hostile = copy.deepcopy(self.results)
        del hostile["discovery_comparison"]["types"]["6"]
        with self.assertRaisesRegex(ValueError, "comparison is incomplete"):
            CHECK.validate_comparison(hostile)

    def test_hostile_failed_invariant_is_rejected(self):
        hostile = copy.deepcopy(self.results)
        hostile["discovery_comparison"]["types"]["4+2"]["invariants"][
            "matching_evaluations"
        ] = False
        with self.assertRaisesRegex(ValueError, "invariant failed"):
            CHECK.validate_comparison(hostile)

    def test_hostile_conway_promotion_is_rejected(self):
        hostile = copy.deepcopy(self.results)
        hostile["status_wall"]["conway_99"] = "DISPROVED"
        with self.assertRaisesRegex(ValueError, "Conway status inflated"):
            CHECK.validate_comparison(hostile)

    def test_hostile_endpoint_promotion_is_rejected(self):
        hostile = copy.deepcopy(self.results)
        hostile["status_wall"]["endpoint_n3_4158"] = "EXCLUDED"
        with self.assertRaisesRegex(ValueError, "endpoint status inflated"):
            CHECK.validate_comparison(hostile)


if __name__ == "__main__":
    unittest.main()
