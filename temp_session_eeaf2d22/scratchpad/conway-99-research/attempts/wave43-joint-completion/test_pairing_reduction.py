from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("solve_joint.py")
SPEC = importlib.util.spec_from_file_location("wave43_joint", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load Wave 43 construction module")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class PairingReductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record_path = Path(__file__).with_name("pairing-reduction.json")
        cls.record = json.loads(cls.record_path.read_text(encoding="utf-8"))

    def test_frozen_record_replays_byte_for_byte(self) -> None:
        actual = CHECK.describe_pairing_reduction(CHECK.SOURCE, 0)
        self.assertEqual(
            self.record_path.read_bytes(),
            CHECK.canonical_bytes(actual),
        )

    def test_exact_candidate_and_pairing_census(self) -> None:
        self.assertEqual(
            self.record["candidate_enumeration"]["filter_census"],
            [216000, 118718, 49736, 45032],
        )
        self.assertEqual(
            self.record["pairing_projection"]["pairing_combo_counts_01_02_12"],
            [2881, 2881, 2694],
        )
        self.assertEqual(
            self.record["candidate_enumeration"]["retained_candidate_sha256"],
            "f796334943793224fb28bc0bcfc40d427bf56892c16386887ca7866a3b9ac963",
        )

    def test_compact_cnf_census(self) -> None:
        stats = self.record["canonical_sequential_counter_cnf"]
        self.assertEqual(stats["semantic_pairing_variables"], 8456)
        self.assertEqual(stats["cnf_variables_including_auxiliary"], 82532)
        self.assertEqual(stats["cnf_clauses"], 338528)
        self.assertEqual(stats["perfect_matching_exactly_one_constraints"], 360)
        self.assertEqual(stats["cross_cell_upper_bound_constraints"], 412)
        self.assertEqual(stats["illegal_triple_binary_clauses"], 96408)
        self.assertEqual(stats["legal_triple_ternary_clauses"], 45032)

    def test_status_wall_rejects_promotion(self) -> None:
        wall = self.record["status_wall"]
        self.assertEqual(wall["full_B"], "NOT_CONSTRUCTED_OR_EXCLUDED")
        self.assertEqual(wall["compatible_H"], "NOT_CONSTRUCTED_OR_EXCLUDED")
        self.assertFalse(wall["endpoint_excluded"])
        self.assertFalse(wall["conway_99_resolved"])


if __name__ == "__main__":
    unittest.main()
