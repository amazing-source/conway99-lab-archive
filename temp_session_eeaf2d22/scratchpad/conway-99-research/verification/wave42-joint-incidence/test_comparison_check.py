import copy
import unittest

import comparison_check as comparison


class DiscoveryComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.independent = comparison.load_json_at_hash(
            comparison.INDEPENDENT, comparison.INDEPENDENT_SHA256
        )
        cls.discovery = comparison.load_json_at_hash(
            comparison.DISCOVERY, comparison.DISCOVERY_SHA256
        )

    def test_frozen_results_match(self):
        result = comparison.compare_payloads(self.independent, self.discovery)
        self.assertEqual(
            result["exact_matches"]["six_set_filter_counts"],
            [216000, 118718, 49736, 45032],
        )
        self.assertTrue(
            result["two_fibre_positive_controls"][
                "independent_certificate_is_distinct"
            ]
        )

    def test_hostile_candidate_count_mutation_is_rejected(self):
        hostile = copy.deepcopy(self.discovery)
        hostile["exhaustive_B_reduction"]["candidate_census"][
            "after_mixed_BH_nonnegativity"
        ] += 1
        with self.assertRaises(ValueError):
            comparison.compare_payloads(self.independent, hostile)

    def test_hostile_status_inflation_is_rejected(self):
        hostile = copy.deepcopy(self.discovery)
        hostile["status_wall"]["endpoint_excluded"] = True
        with self.assertRaises(ValueError):
            comparison.compare_payloads(self.independent, hostile)

    def test_hostile_discovery_certificate_mutation_is_rejected(self):
        hostile = copy.deepcopy(self.discovery)
        hostile["two_fibre_positive_control"]["certificate"][0] = hostile[
            "two_fibre_positive_control"
        ]["certificate"][1]
        with self.assertRaises(ValueError):
            comparison.compare_payloads(self.independent, hostile)


if __name__ == "__main__":
    unittest.main()
