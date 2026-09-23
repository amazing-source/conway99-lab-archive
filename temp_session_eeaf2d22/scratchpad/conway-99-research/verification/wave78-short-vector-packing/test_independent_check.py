import importlib.util
import json
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave78_independent_check", MODULE_PATH)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class PackingTests(unittest.TestCase):
    def test_discovery_freeze(self):
        CHECK.verify_frozen_discovery()

    def test_norm16_three_blocks_need_nine_points(self):
        minimum, count = CHECK.minimum_union_linear_uniform(8, 4, 3)
        self.assertEqual(minimum, 9)
        self.assertEqual(count, 0)

    def test_norm18_triples_have_rigid_equality(self):
        minimum, count = CHECK.minimum_union_linear_uniform(9, 4, 3)
        self.assertEqual(minimum, 9)
        self.assertGreater(count, 0)
        audit = CHECK.equality_rigid_triples_on_nine()
        self.assertTrue(audit["all_union_nine_triples_rigid"])
        self.assertEqual(
            audit["union_nine_triples"],
            audit["rigid_union_nine_triples"],
        )

    def test_four_blocks_do_not_fit_on_nine_points(self):
        lower_bound, count = CHECK.minimum_union_linear_uniform(9, 4, 4)
        self.assertEqual(lower_bound, 10)
        self.assertEqual(count, 0)

    def test_histogram_counts(self):
        result = CHECK.build_results()
        self.assertEqual(result["lanes"]["norm16_h0"]["histogram_count"], 1)
        self.assertEqual(result["lanes"]["norm18_h0"]["histogram_count"], 7)
        self.assertEqual(result["lanes"]["norm18_h1"]["histogram_count"], 4)

    def test_norm16_exact_row(self):
        rows = CHECK.enumerate_histograms(83, 80, 8, 2)
        self.assertEqual(rows, [[11, 64, 8, 0, 0, 0, 0, 0]])

    def test_histogram_moments(self):
        for lane in CHECK.build_results()["lanes"].values():
            for row in lane["histograms"]:
                self.assertEqual(sum(row), lane["outside_vertices"])
                self.assertEqual(
                    sum(d * n for d, n in enumerate(row)),
                    lane["outside_incidences_per_side"],
                )
                self.assertEqual(
                    sum(CHECK.comb(d, 2) * n for d, n in enumerate(row)),
                    lane["outside_pair_incidences"],
                )
                self.assertTrue(
                    all(n == 0 for n in row[lane["maximum_d"] + 1 :])
                )

    def test_endpoint_degree_five_obstruction_arithmetic(self):
        # A degree-5 cross row plus two degree-4 rows has 13 incidences.
        # Pairwise intersections at most one can save at most three points.
        self.assertGreater(5 + 4 + 4 - 3, 9)

    def test_exact_discovery_comparison(self):
        result = CHECK.verify()
        for lane in result["discovery_comparison"].values():
            self.assertTrue(lane["histogram_count_exactly_equal"])
            self.assertTrue(lane["histograms_exactly_equal"])

    def test_stored_result_matches_verifier(self):
        stored = json.loads(
            pathlib.Path(__file__)
            .with_name("independent-results.json")
            .read_text("utf-8")
        )
        self.assertEqual(CHECK.verify(), stored)


if __name__ == "__main__":
    unittest.main()
