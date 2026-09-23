from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave123_independent", HERE / "independent_verify.py"
)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)


class IndependentWave123Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = VERIFY.build_results()

    def test_manifest_preinspection(self) -> None:
        self.assertEqual(self.data["preinspection"]["discovery_entries_checked"], 10)

    def test_all40_and_first26_fail(self) -> None:
        self.assertEqual(len(self.data["all40"]["violating_coordinates"]), 46)
        self.assertEqual(len(self.data["first26"]["violating_coordinates"]), 6)
        self.assertFalse(self.data["all40"]["diagonal_gate_passes"])
        self.assertFalse(self.data["first26"]["diagonal_gate_passes"])

    def test_explicit26_diagonal_pass_and_pair_failure(self) -> None:
        row = self.data["explicit26"]
        self.assertTrue(row["diagonal"]["diagonal_gate_passes"])
        self.assertEqual(
            row["diagonal"]["maximum_leverage"],
            "1217462828759965373070564/2744155911807689338327015",
        )
        self.assertEqual(
            row["two_by_two_completion"]["invalid_pair_count"], 352
        )
        self.assertFalse(row["two_by_two_completion"]["passes_every_pair"])

    def test_three_point_and_feature_blocks(self) -> None:
        row = self.data["explicit26"]
        self.assertEqual(row["three_point"]["triple_count"], 2600)
        self.assertEqual(
            row["three_point"][
                "pair_overlap_tuples_with_multiple_triple_intersections"
            ],
            28,
        )
        self.assertEqual(row["three_point"]["minimum_signed_triple_norm"], 22)
        blocks = row["rooted_feature_blocks"]
        self.assertEqual(
            (
                blocks["centered_endpoint_one"],
                blocks["within_block_degree_two"],
                blocks["cross_block_degree_two"],
                blocks["total"],
            ),
            (312, 468, 1560, 2340),
        )
        self.assertTrue(blocks["all_psd_by_explicit_F_F_transpose_factorization"])

    def test_nonexhaustive_scope(self) -> None:
        row = self.data["nonexhaustive_search_scope"]
        self.assertFalse(row["telemetry_algorithm_independently_replayed"])
        self.assertFalse(row["exhaustive_certificate_present"])
        self.assertFalse(row["negative_inference_allowed"])

    def test_unknown_wall(self) -> None:
        status = self.data["status_wall"]
        self.assertEqual(status["some_26_word_graph_compatible_family"], "UNKNOWN")
        self.assertEqual(status["local_cap_25"], "UNKNOWN")
        self.assertFalse(status["rank28_excluded"])
        self.assertFalse(status["rank30_excluded"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
