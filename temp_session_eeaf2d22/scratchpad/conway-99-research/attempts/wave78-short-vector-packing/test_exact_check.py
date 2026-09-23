import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave78_exact_check", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Wave78ExactTests(unittest.TestCase):
    def setUp(self):
        self.result = MODULE.compute()

    def test_no_admissible_triple_on_eight_points(self):
        row = self.result["set_family_checks"]["four_subsets_of_8_family_3"]
        self.assertEqual(row["admissible_family_count"], 0)

    def test_admissible_triples_on_nine_points_are_rigid(self):
        row = self.result["set_family_checks"]["four_subsets_of_9_family_3"]
        self.assertGreater(row["admissible_family_count"], 0)
        self.assertEqual(row["union_sizes"], [9])
        self.assertEqual(row["pair_intersection_profiles"], [[1, 1, 1]])
        self.assertEqual(row["triple_intersection_sizes"], [0])

    def test_no_admissible_four_family_on_nine_points(self):
        row = self.result["set_family_checks"]["four_subsets_of_9_family_4"]
        self.assertEqual(row["admissible_family_count"], 0)

    def test_norm16_histogram_is_unique(self):
        self.assertEqual(self.result["histograms"]["norm16"], [[11, 64, 8]])

    def test_norm18_h0_histograms(self):
        rows = self.result["histograms"]["norm18_h0"]
        self.assertEqual(len(rows), 7)
        for row in rows:
            self.assertEqual(sum(row), 81)
            self.assertEqual(sum(i * count for i, count in enumerate(row)), 90)
            self.assertEqual(
                sum(i * (i - 1) // 2 * count for i, count in enumerate(row)),
                18,
            )

    def test_norm18_h1_histograms(self):
        rows = self.result["histograms"]["norm18_h1"]
        self.assertEqual(len(rows), 4)
        self.assertFalse(
            self.result["packing_consequences"][
                "norm18_h1_d3_block_meets_same_sign_edge_endpoints"
            ]
        )
        for row in rows:
            self.assertEqual(sum(row), 81)
            self.assertEqual(sum(i * count for i, count in enumerate(row)), 86)
            self.assertEqual(
                sum(i * (i - 1) // 2 * count for i, count in enumerate(row)),
                9,
            )

    def test_status_wall(self):
        self.assertEqual(self.result["status"]["conway_99"], "UNKNOWN")
        self.assertEqual(self.result["status"]["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
