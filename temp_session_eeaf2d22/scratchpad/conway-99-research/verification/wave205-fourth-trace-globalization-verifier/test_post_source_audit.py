import pathlib
import sys
import unittest
import json

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import post_source_audit as audit


class TestPostSourceAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = audit.build_result()

    def test_sealed_manifests(self):
        self.assertTrue(all(
            item["entries_match"]
            for item in self.result["sealed_manifests"].values()
        ))

    def test_frozen_post_source_result(self):
        frozen = json.loads((HERE / "post_source_result.json").read_text(encoding="utf-8"))
        normalized = json.loads(json.dumps(self.result))
        self.assertEqual(normalized, frozen)

    def test_proof_a_census(self):
        census = self.result["proof_a"]["normalized_census"]
        self.assertEqual(census["6"]["normalized_matrix_count"], 646)
        self.assertEqual(census["7"]["normalized_matrix_count"], 7886)
        self.assertEqual(census["6"]["admissible_by_h"], {"0":0,"1":18,"2":0})
        self.assertEqual(census["7"]["admissible_by_h"], {"0":297,"1":324,"2":144})

    def test_proof_a_controls(self):
        controls = self.result["proof_a"]["controls"]
        self.assertEqual(
            [(x["name"], x["t"], x["h"]) for x in controls],
            [("t6_h1",6,1),("t7_h0",7,0),("t7_h1",7,1),("t7_h2",7,2)],
        )
        self.assertTrue(all(x["union_gram_rank"] == 11 for x in controls))
        self.assertTrue(all(x["discriminant"] == 2 for x in controls))

    def test_proof_b_factorization(self):
        factor = self.result["proof_b"]["factorization_and_contractions"]
        self.assertTrue(all(
            factor[key] for key in (
                "H_equals_U_K_U_transpose", "sum_feature_equals_vec_Q",
                "row_localizer", "w_TU_norm_contraction",
            )
        ))
        self.assertEqual(self.result["proof_b"]["star_pair_feature"]["rank_U"], 99)

    def test_proof_b_dimensions_and_control(self):
        dims = self.result["proof_b"]["dimension_ledger"]
        self.assertEqual(dims["dim_trace_zero_self_adjoint_End_wedge2_V"], 1539)
        control = self.result["proof_b"]["zero_first_moment_control"]
        self.assertEqual(control["pair_trace_rank"], 8)
        self.assertEqual(control["fourth_trace_rank"], 9)
        self.assertEqual(control["fourth_row_sums"], {0:6,1:91,2:2})

    def test_hostile_control_exact_predicates(self):
        hostile = self.result["hostile_control"]
        self.assertEqual(hostile["incidence"]["blocks"], 231)
        self.assertEqual(hostile["incidence"]["point_degree"], 14)
        self.assertEqual(hostile["comparison"]["h_differences"], 3888)
        self.assertEqual(hostile["comparison"]["edge_h_differences"], 0)
        self.assertEqual(hostile["comparison"]["nonedge_h_differences"], 3888)
        self.assertTrue(hostile["target_failures_preserved"])

    def test_status_wall(self):
        wall = self.result["status_wall"]
        self.assertEqual(wall["Conway_99"], "UNKNOWN")
        self.assertEqual(wall["rank_11_endpoint"], "UNKNOWN")
        self.assertEqual(wall["n3_4158_endpoint"], "UNKNOWN")
        self.assertEqual(wall["Q>=7060"], "NOT PROVED")


if __name__ == "__main__":
    unittest.main()
