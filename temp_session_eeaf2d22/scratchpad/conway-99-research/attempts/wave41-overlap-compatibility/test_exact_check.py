import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave41_overlap_check", MODULE_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class OverlapCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_results()

    def test_two_local_blocks(self) -> None:
        local = self.result["canonical_local_block"]
        self.assertEqual(local["rank_F7_K39"], 33)
        self.assertEqual(local["core_triangle_count"], 0)
        self.assertEqual(
            {tuple(value) for value in local["three_base_edge_types"].values()},
            {(2, 2, 2)},
        )
        overlap = self.result["two_triangle_overlap"]
        self.assertEqual(overlap["overlap_size"], 19)
        self.assertEqual(overlap["both_local_K39_ranks_F7"], [33, 33])
        self.assertTrue(overlap["induced_overlap_agreement"])

    def test_border_relaxation_is_not_closing(self) -> None:
        border = self.result["balanced_border_census"]
        self.assertEqual(border["minimum_joint_signature_span"], 1)
        self.assertEqual(border["border_congruence_floor"], 35)
        self.assertEqual(
            border["terminal_signature_subspace_rank_distribution"],
            {"1": 13, "2": 56, "3": 1},
        )
        self.assertIn("no simultaneous", border["scope"].lower())

    def test_status_is_conservative(self) -> None:
        self.assertEqual(self.result["claim_label"], "CANDIDATE")
        conclusion = self.result["conclusion"]
        self.assertFalse(conclusion["endpoint_excluded"])
        self.assertFalse(conclusion["upper_bound_improved"])
        self.assertEqual(conclusion["target_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
