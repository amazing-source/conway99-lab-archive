from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave39_edge_local_verifier", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class IndependentEdgeLocalRankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = MODULE.exact_record()

    def test_exhausts_all_pulled_back_matchings(self) -> None:
        census = self.record["completeness"]
        self.assertEqual(census["pulled_back_matching_count"], 10_395)
        self.assertEqual(census["normal_form_count"], 11)
        self.assertEqual(
            sum(row["labelled_matching_count"] for row in census["normal_forms"]),
            10_395,
        )

    def test_independent_rank_formula_for_every_normal_form(self) -> None:
        for row in self.record["completeness"]["normal_forms"]:
            wanted = 25 - 2 * row["even_part_count"]
            self.assertEqual(row["local_rank_F7"], wanted)
        self.assertEqual(
            min(
                row["local_rank_F7"]
                for row in self.record["completeness"]["normal_forms"]
            ),
            19,
        )

    def test_endpoint_table_and_pair_arithmetic(self) -> None:
        endpoint = self.record["conditional_prism_free_endpoint"]
        self.assertEqual(
            endpoint["surviving_local_table"],
            [
                {"partition": [2, 2, 2], "local_rank_F7": 19},
                {"partition": [2, 4], "local_rank_F7": 21},
                {"partition": [3, 3], "local_rank_F7": 25},
                {"partition": [6], "local_rank_F7": 23},
            ],
        )
        arithmetic = endpoint["rank_pair_arithmetic"]
        self.assertEqual(arithmetic["admissible_pair_count"], 429)
        self.assertEqual(
            arithmetic["if_r3_equals_12"]["admissible_r7_values"],
            list(range(20, 45, 2)),
        )

    def test_rank_transfer_rejects_zero_scalar(self) -> None:
        with self.assertRaisesRegex(AssertionError, "not invertible"):
            MODULE.rank_transfer_proof(scalar=7)

    def test_geometry_rejects_tampered_parameters(self) -> None:
        for kwargs in ({"k": 13}, {"lam": 2}, {"mu": 3}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaisesRegex(AssertionError, "parameters"):
                    MODULE.local_geometry(**kwargs)

    def test_matching_rejects_duplicate_vertex(self) -> None:
        bad = ((0, 1), (0, 2), (3, 4), (5, 6), (7, 8), (9, 10))
        with self.assertRaisesRegex(AssertionError, "cover"):
            MODULE.build_local_graph(bad)

    def test_rank_kernel_is_exact_on_known_matrices(self) -> None:
        self.assertEqual(MODULE.rank_mod_prime([[1, 0], [0, 1]]), 2)
        self.assertEqual(MODULE.rank_mod_prime([[1, 2], [2, 4]]), 1)
        self.assertEqual(MODULE.rank_mod_prime([[7, 0], [0, 14]]), 0)

    def test_hostile_rank_floor_tamper_is_rejected(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["verified_universal_result"]["rank_F7_M_lower_bound"] = 20
        with self.assertRaisesRegex(AssertionError, "differs"):
            MODULE.validate_record(bad)

    def test_hostile_partition_rank_tamper_is_rejected(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["completeness"]["normal_forms"][0]["local_rank_F7"] += 1
        with self.assertRaisesRegex(AssertionError, "differs"):
            MODULE.validate_record(bad)

    def test_hostile_endpoint_status_inflation_is_rejected(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["conditional_prism_free_endpoint"]["endpoint_excluded"] = True
        with self.assertRaisesRegex(AssertionError, "differs"):
            MODULE.validate_record(bad)

    def test_hostile_novelty_status_inflation_is_rejected(self) -> None:
        bad = copy.deepcopy(self.record)
        bad["status"]["novelty"] = "VERIFIED"
        with self.assertRaisesRegex(AssertionError, "differs"):
            MODULE.validate_record(bad)

    def test_strict_json_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"claim_label":"VERIFIED","claim_label":"UNKNOWN"}')
            with self.assertRaisesRegex(ValueError, "duplicate"):
                MODULE.load_json(path)

    def test_stored_result_is_canonical_and_valid(self) -> None:
        result_path = Path(__file__).with_name("independent-results.json")
        record = MODULE.load_json(result_path)
        MODULE.validate_record(record)
        self.assertEqual(result_path.read_bytes(), MODULE.canonical_json(record))

    def test_status_wall_preserves_open_problem(self) -> None:
        self.assertEqual(self.record["claim_label"], "VERIFIED")
        self.assertEqual(self.record["status"]["conway_99"], "UNKNOWN")
        self.assertEqual(self.record["status"]["endpoint"], "UNKNOWN")
        self.assertEqual(self.record["status"]["novelty"], "UNKNOWN")
        self.assertEqual(
            self.record["status"]["strongest_general_upper_bound_on_n3"], 4158
        )
        self.assertFalse(
            self.record["conditional_prism_free_endpoint"][
                "upper_bound_improved_below_4158"
            ]
        )


if __name__ == "__main__":
    unittest.main()
