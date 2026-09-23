import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave44_rooted_verifier", HERE / "independent_check.py")
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)
RESULT = json.loads((HERE / "independent-results.json").read_text(encoding="utf-8"))


class RootedVerifierTests(unittest.TestCase):
    def test_result_validates(self):
        MOD.validate(RESULT)

    def test_pre_discovery_protocol_hash(self):
        self.assertEqual(
            MOD.sha256((HERE / "protocol-freeze.md").read_bytes()),
            "18316e2d36e981a64f369d852c132c905d695a521388763c24f2362b741668a3",
        )

    def test_exact_shape_and_rank_increment(self):
        system = RESULT["system"]
        self.assertEqual(
            (system["unrooted_rows"], system["vertex_rows"], system["edge_rows"], system["nonedge_rows"]),
            (81, 7, 36, 46),
        )
        for record in system["rank_table"].values():
            self.assertEqual(
                (record["base"], record["base_plus_vertex"], record["base_plus_vertex_edge"], record["all_rooted"]),
                (81, 82, 87, 93),
            )

    def test_exact_witness(self):
        certificate = RESULT["certificate"]
        self.assertEqual(certificate["y"], 4158)
        self.assertEqual(certificate["h11"], 16632)
        self.assertEqual(certificate["support_size"], 91)
        self.assertEqual(certificate["seven_subset_total"], 14887031544)
        self.assertEqual(certificate["all_170_exact_integer_rows"], "PASS")

    def test_complete_independent_row_hashes(self):
        system = RESULT["system"]
        self.assertEqual(system["base_rows_rhs_sha256"], "4788642cf268145dbcfdca456ef5078f1c2c2edb3626698ecf5c327b1efca359")
        self.assertEqual(system["vertex_rows_rhs_sha256"], "042ec8cf9026fadc1408ab5401f240dd8ae528a9d7dffd9068bd31230194c9d7")
        self.assertEqual(system["edge_rows_rhs_sha256"], "255237841b93babdd825fff9c9e2bdd30e8132d9470b9015005a8d660cbac482")
        self.assertEqual(system["nonedge_rows_rhs_sha256"], "9a20e3a28a00f4850d747630348ff4db8f512ba5cb462fd366362165f52d0bec")
        self.assertEqual(system["all_170_rows_rhs_sha256"], "863a75a616c138e750178c93234a92289363318f4bd0775c7b0792e44b7c61cb")
        self.assertEqual(system["internal_numeric_pair_encoding_sha256"], "319d4586c21faa218c577cfed9eb9565fb3b7bae8697ff773e3e1b482305a2c4")
        self.assertEqual(system["zero_residual_stream_sha256"], "dd3388b7233ff3708100650c3dc83592b5b1082159931601b12f294016b144d5")

    def test_post_freeze_full_row_comparison(self):
        comparison = RESULT["comparison"]
        self.assertTrue(comparison["class_stream_exact_ordered_match"])
        self.assertTrue(comparison["all_170_rows_exact_ordered_match"])
        self.assertTrue(comparison["all_170_rhs_exact_ordered_match"])
        self.assertEqual(comparison["coefficients_compared"], 170 * 209)
        self.assertEqual(comparison["rhs_values_compared"], 170)

    def test_all_hostile_mutations_rejected(self):
        self.assertEqual(len(RESULT["controls"]), 6)
        self.assertTrue(all(record["outcome"] == "REJECTED" for record in RESULT["controls"]))

    def test_false_highs_infeasibility(self):
        diagnostic = RESULT["solver_diagnostic"]
        self.assertEqual(diagnostic["unscaled"]["status"], 2)
        self.assertTrue(diagnostic["unscaled_infeasible_status_is_false"])
        self.assertEqual(diagnostic["exact_witness_max_abs_integer_residual"], 0)
        self.assertEqual(diagnostic["exact_witness_max_abs_float_residual"], 0.0)
        self.assertEqual(diagnostic["exact_witness_fixed_bounds_presolve"]["status"], 0)
        self.assertEqual(diagnostic["exact_witness_fixed_bounds_no_presolve"]["status"], 0)
        self.assertFalse(diagnostic["solver_exit_code_used_as_certificate"])

    def test_status_wall(self):
        conclusion = RESULT["conclusion"]
        self.assertEqual(conclusion["aggregate_rooted_system"], "EXACT_FEASIBLE")
        self.assertFalse(conclusion["graph_constructed"])
        self.assertFalse(conclusion["endpoint_evidence"])
        self.assertEqual(conclusion["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(conclusion["upper_bound_below_4158"], "NOT_PROVED")
        self.assertEqual(conclusion["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
