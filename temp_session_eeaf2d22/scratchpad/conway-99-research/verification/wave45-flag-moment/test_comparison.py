from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave45_comparison_tested", HERE / "compare_discovery.py"
)
assert SPEC is not None and SPEC.loader is not None
COMPARE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COMPARE
SPEC.loader.exec_module(COMPARE)
RESULT = json.loads(
    (HERE / "comparison-results.json").read_text(encoding="utf-8")
)


class DiscoveryComparisonTests(unittest.TestCase):
    def test_coefficient_streams_match_exactly(self) -> None:
        comparison = RESULT["coefficient_comparison"]
        self.assertTrue(comparison["combined_entrywise_match"])
        self.assertEqual(
            comparison["converted_combined_stream_sha256"],
            "5eace9a5008e40c8a1a430bec43b23027fd0d564a0d440f354a8ec101fbdd4b9",
        )
        self.assertEqual(
            {
                name: record["records"]
                for name, record in comparison["families"].items()
            },
            {"vertex": 300, "edge": 92, "nonedge": 92},
        )

    def test_controls_match_exact_matrices(self) -> None:
        self.assertEqual(
            RESULT["control_comparison"],
            {
                "Petersen": "EXACT_MATRIX_MATCH",
                "Clebsch": "EXACT_MATRIX_MATCH",
            },
        )

    def test_all_twelve_stored_directions_are_exactly_negative(self) -> None:
        quadratics = [
            value
            for target in RESULT["target_comparison"].values()
            for value in target["exact_vertex_quadratics"]
        ]
        self.assertEqual(len(quadratics), 12)
        self.assertTrue(all(value < 0 for value in quadratics))
        self.assertEqual(
            RESULT["target_comparison"]["wave43_unrooted"][
                "exact_vertex_quadratics"
            ][0],
            -2_439_686_160_282,
        )
        self.assertEqual(
            RESULT["target_comparison"]["wave44_rooted"][
                "exact_vertex_quadratics"
            ][0],
            -3_434_158_925_036,
        )

    def test_pair_root_matrices_are_exactly_psd_rank_one(self) -> None:
        for target in RESULT["target_comparison"].values():
            for family in ("edge", "nonedge"):
                self.assertEqual(
                    target["families"][family]["exact_psd"],
                    {"is_psd": True, "rank": 1},
                )
            self.assertFalse(target["families"]["vertex"]["exact_psd"]["is_psd"])

    def test_cutting_checkpoint_replays_but_is_incomplete(self) -> None:
        cutting = RESULT["cutting_loop"]
        self.assertEqual(cutting["cut_count"], 17)
        self.assertEqual(cutting["witness_count"], 15)
        self.assertTrue(cutting["all_cut_streams_reconstructed"])
        self.assertTrue(cutting["all_witnesses_pass_original_170_rows"])
        self.assertTrue(cutting["all_witnesses_pass_prior_cuts"])
        self.assertTrue(cutting["all_new_cuts_exactly_reject_source"])
        self.assertEqual(cutting["final_status"], "QF_LIA_UNKNOWN")
        self.assertEqual(cutting["last_reason_unknown"], "timeout")
        self.assertTrue(cutting["solver_unknown_is_not_certificate"])

    def test_immutable_checkpoint_hashes(self) -> None:
        inputs = RESULT["inputs"]
        self.assertEqual(
            inputs[
                "attempts/wave45-flag-moment/"
                "checkpoint-v1-seed0-17cuts-15witnesses.json"
            ],
            "96a50f9add4b12b2c86587da29ade8b9da34f88a7b7617c048ffb7139c12b64b",
        )
        self.assertEqual(
            inputs[
                "attempts/wave45-flag-moment/"
                "checkpoint-v1-moment-coefficients.json"
            ],
            "ffcf9f9942446d66c3559d97954217af3ba17c1978ea9417c6e99920d4a45420",
        )
        self.assertEqual(
            inputs[
                "attempts/wave45-flag-moment/"
                "checkpoint-v1-stored-witness-results.json"
            ],
            "2c55b6ab1af9cac7d8f5800466abadb8c0c2603b5f96013d3fd160b6816c24df",
        )

    def test_status_wall(self) -> None:
        COMPARE.validate_record(RESULT)
        verdict = RESULT["verdict"]
        self.assertEqual(
            verdict["finite_cutting_loop"], "VERIFIED_INCOMPLETE_UNKNOWN"
        )
        self.assertEqual(verdict["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(verdict["strict_upper_bound_below_4158"], "NOT_PROVED")
        self.assertEqual(verdict["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
