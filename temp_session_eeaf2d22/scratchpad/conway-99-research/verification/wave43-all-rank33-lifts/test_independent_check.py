import importlib.util
import json
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("w43_rank33_verifier", HERE / "independent_check.py")
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
RESULT = json.loads((HERE / "independent-results.json").read_text(encoding="utf-8"))


class Rank33VerifierTests(unittest.TestCase):
    def test_archived_result_validates(self):
        MOD.validate(RESULT)

    def test_complete_quotient_normalization(self):
        distribution = RESULT["canonical_quotient"]["rank_distribution_all_4050"]
        self.assertEqual(sum(distribution.values()), 4050)
        self.assertEqual(distribution["11"], 8)
        self.assertEqual(RESULT["canonical_quotient"]["metadata"]["normalized_index"], 1446)

    def test_exact_mask_stream(self):
        lift = RESULT["lift_census"]
        self.assertEqual(lift["all_masks"], 262144)
        self.assertEqual(lift["triangle_free_masks"], 37378)
        self.assertEqual(lift["rank33_mask_count"], 264)
        self.assertEqual(
            lift["rank33_masks_sha256"],
            "167ba5c0a4b40fb3711fbc861a03a853a125651f4c569dfd5688dd0cca90b130",
        )

    def test_all_per_mask_records_match(self):
        self.assertTrue(RESULT["comparison"]["rank33_masks_exact_match"])
        self.assertTrue(RESULT["comparison"]["rank33_mask_hash_exact_match"])
        self.assertTrue(RESULT["comparison"]["all_264_per_mask_records_exact_match"])
        self.assertEqual(len(RESULT["per_mask"]), 264)

    def test_kernel_and_component_facts_cover_all_masks(self):
        for record in RESULT["per_mask"]:
            self.assertEqual(record["component_sizes"], [12, 24])
            self.assertEqual(record["component_fibre_balances"], [[4, 4, 4], [8, 8, 8]])
            self.assertEqual(record["forced_gram_rank_mod_1000003"], 33)
            self.assertEqual(record["structural_kernel_dimension"], 3)

    def test_hostile_dense_rank_controls(self):
        zero = np.zeros((1, 4, 4), dtype=np.int16)
        identity = np.eye(4, dtype=np.int16)[None, :, :]
        duplicate = np.array([[[1, 2], [1, 2]]], dtype=np.int16)
        self.assertEqual(MOD.batched_rank_mod7(zero).tolist(), [0])
        self.assertEqual(MOD.batched_rank_mod7(identity).tolist(), [4])
        self.assertEqual(MOD.batched_rank_mod7(duplicate).tolist(), [1])

    def test_five_classes_are_only_numeric(self):
        self.assertEqual(
            RESULT["aggregate"]["candidate_census"],
            {
                "(118718, 49736, 45032)": 48,
                "(131908, 54560, 49328)": 48,
                "(132196, 54736, 49520)": 24,
                "(132250, 54560, 49328)": 48,
                "(132402, 54648, 49424)": 96,
            },
        )

    def test_status_wall(self):
        wall = RESULT["status_wall"]
        self.assertTrue(wall["every_lift_survives_necessary_filters"])
        self.assertEqual(wall["full_B"], "UNKNOWN")
        self.assertEqual(wall["compatible_H"], "UNKNOWN")
        self.assertFalse(wall["endpoint_excluded"])
        self.assertEqual(wall["strict_upper_bound"], "NOT_PROVED")
        self.assertEqual(wall["conway_99"], "UNKNOWN")
        self.assertFalse(wall["automorphism_assumed"])


if __name__ == "__main__":
    unittest.main()
