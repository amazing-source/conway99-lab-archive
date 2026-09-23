from __future__ import annotations

import hashlib
import json
import math
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Wave53StoredResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result_path = HERE / "exact-result.json"
        cls.result = json.loads(cls.result_path.read_bytes())

    def test_scope_and_census(self) -> None:
        self.assertEqual(self.result["claim_label"], "CANDIDATE")
        configuration = self.result["configuration"]
        self.assertEqual(configuration["completed_cut_iterations"], 3)
        self.assertEqual(configuration["rational_witnesses_evaluated"], 4)
        self.assertEqual(configuration["initial_cut_count"], 174)
        self.assertEqual(configuration["final_cut_count"], 177)
        self.assertFalse(configuration["integrality_imposed"])

    def test_all_128_matrices_have_exact_negative_directions(self) -> None:
        records = [
            record
            for iteration in self.result["iterations"]
            for record in iteration["matrix_evaluation"]["records"]
        ]
        self.assertEqual(len(records), 128)
        for record in records:
            self.assertEqual(record["status"], "EXACTLY_INDEFINITE")
            self.assertLess(Fraction(record["exact_quadratic"]), 0)
            direction = record["primitive_integer_direction"]
            self.assertEqual(math.gcd(*(abs(value) for value in direction)), 1)
            self.assertGreater(next(value for value in direction if value), 0)

    def test_three_cuts_are_primitive_and_reject_sources(self) -> None:
        cuts = [
            iteration["added_cut"]
            for iteration in self.result["iterations"]
            if "added_cut" in iteration
        ]
        self.assertEqual(len(cuts), 3)
        self.assertEqual(len({cut["id"] for cut in cuts}), 3)
        for cut in cuts:
            coefficients = [abs(value) for _mask, value in cut["coefficients"]]
            self.assertEqual(math.gcd(*coefficients), 1)
            self.assertLess(Fraction(cut["exact_source_value"]), 0)
            self.assertLess(Fraction(cut["exact_matrix_value"]), 0)
            self.assertGreater(Fraction(cut["linearization_multiplier"]), 0)

    def test_successor_witness_hash_chain(self) -> None:
        iterations = self.result["iterations"]
        for index in range(3):
            expected = iterations[index]["next_witness_exact_substitution"][
                "witness_vector_sha256"
            ]
            actual = iterations[index + 1]["witness"]["witness_vector_sha256"]
            self.assertEqual(expected, actual)
            self.assertTrue(
                iterations[index]["next_witness_exact_substitution"][
                    "all_cumulative_cuts_nonnegative"
                ]
            )

    def test_inputs_and_stable_resource_summary(self) -> None:
        for record in self.result["inputs"]:
            path = ROOT / record["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"])
        guard = self.result["resource_guard"]
        self.assertEqual(guard["required_strictly_more_than_free_percent"], 20.0)
        self.assertTrue(guard["all_guard_checks_passed"])
        self.assertFalse(guard["live_telemetry_embedded"])
        self.assertNotIn("samples", guard)
        self.assertNotIn("minimum_observed_free_percent", guard)

    def test_scope_wall(self) -> None:
        conclusion = self.result["conclusion"]
        self.assertEqual(
            conclusion["augmented_finite_relaxation_after_last_new_cut"],
            "EXACTLY_FEASIBLE",
        )
        self.assertEqual(conclusion["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(conclusion["strict_upper_bound_below_4158"], "NOT_PROVED")
        self.assertFalse(conclusion["graph_constructed"])


if __name__ == "__main__":
    unittest.main()
