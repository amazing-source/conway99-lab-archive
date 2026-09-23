from __future__ import annotations

import gzip
import hashlib
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import combined_closure_and_probes as continuation  # noqa: E402
import coordinate_triangle_cuts as cuts  # noqa: E402


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class CoordinateTriangleCutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(
            cuts.DEFAULT_RESULT.read_text(encoding="utf-8")
        )
        cls.closure = json.loads(
            continuation.DEFAULT_CLOSURE.read_text(encoding="utf-8")
        )
        cls.probes = json.loads(
            continuation.DEFAULT_PROBES.read_text(encoding="utf-8")
        )

    def test_exact_regeneration(self) -> None:
        result, delta, active = cuts.build_artifacts()
        self.assertEqual(
            cuts.DEFAULT_RESULT.read_bytes(),
            cuts.canonical_payload(result),
        )
        self.assertEqual(cuts.DEFAULT_DELTA.read_bytes(), delta)
        self.assertEqual(cuts.DEFAULT_ACTIVE_DELTA.read_bytes(), active)

    def test_complete_bounded_enumeration_counts(self) -> None:
        enumeration = self.result["enumeration"]
        self.assertEqual(enumeration["all_coordinate_triangle_count"], 924)
        self.assertEqual(
            enumeration["wave42_forced_true_coordinate_triangles"],
            7,
        )
        self.assertEqual(
            enumeration["wave42_forced_false_coordinate_triangles"],
            157,
        )
        self.assertEqual(
            enumeration["wave42_unfixed_coordinate_triangles"],
            760,
        )
        self.assertEqual(
            enumeration["perfect_matching_visits"],
            1_556_994,
        )
        self.assertEqual(
            enumeration["matchings_killed_by_fixed_scaffold_nonedges"],
            1_516_194,
        )
        self.assertEqual(
            enumeration["accepted_matching_visits_before_deduplication"],
            40_800,
        )
        self.assertEqual(
            enumeration["vertex_disjoint_mate_anchor_pairs"],
            20_400,
        )
        self.assertEqual(
            enumeration["accepted_matching_visits_with_mate_anchors"],
            40_800,
        )
        self.assertEqual(
            enumeration[
                "accepted_matching_visits_pairing_the_anchors"
            ],
            40_800,
        )

    def test_raw_delta_is_exact_distinct_width_four_family(self) -> None:
        delta = self.result["delta"]
        self.assertEqual(delta["constraints"], 40_800)
        self.assertEqual(delta["width_histogram"], {"4": 40_800})
        self.assertEqual(
            delta["gzip_sha256"],
            sha256(cuts.DEFAULT_DELTA.read_bytes()),
        )
        raw = gzip.decompress(cuts.DEFAULT_DELTA.read_bytes())
        self.assertEqual(delta["raw_sha256"], sha256(raw))
        clauses = tuple(
            cuts.iter_negative_clauses(
                cuts.DEFAULT_DELTA,
                expected_gzip_sha256=delta["gzip_sha256"],
                expected_raw_sha256=delta["raw_sha256"],
                expected_constraints=delta["constraints"],
            )
        )
        self.assertEqual(len(clauses), len(set(clauses)))
        self.assertTrue(
            all(
                len(clause) == 4
                and len(clause) == len(set(clause))
                and all(
                    1 <= variable <= cuts.wave42.PRIMARY_VARIABLES
                    for variable in clause
                )
                for clause in clauses
            )
        )

    def test_active_delta_has_no_unit_or_contradiction(self) -> None:
        simplified = self.result["wave42_closure_simplification"]
        self.assertEqual(simplified["satisfied_new_raw_clauses"], 6_460)
        self.assertEqual(simplified["empty_residual_contradictions"], 0)
        self.assertEqual(simplified["new_active_constraints"], 34_340)
        self.assertEqual(
            simplified["active_width_histogram"],
            {"4": 34_340},
        )
        self.assertEqual(simplified["immediate_negative_units"], 0)

    def test_fixed_point_extension_is_scoped_null_result(self) -> None:
        self.assertEqual(
            self.closure["result"]["status"],
            "DERIVED_PROPAGATION_FIXED_POINT",
        )
        self.assertIsNone(self.closure["result"]["contradiction"])
        self.assertEqual(self.closure["result"]["new_forced_variables"], 0)
        self.assertEqual(
            self.closure["audit"]["active_slack_histogram"],
            {"3": 34_340},
        )
        self.assertEqual(self.closure["result"]["branch15"], "UNKNOWN")
        self.assertEqual(self.closure["result"]["endpoint_cases_closed"], 0)

    def test_bounded_probes_are_explicitly_nonterminal(self) -> None:
        self.assertEqual(self.probes["probe_count"], 64)
        self.assertEqual(len(self.probes["probe_variables"]), 32)
        self.assertEqual(
            self.probes["result"]["candidate_implication_count"],
            0,
        )
        self.assertEqual(
            self.probes["result"]["doubly_failed_variable_count"],
            0,
        )
        self.assertEqual(
            self.probes["result"][
                "total_coordinate_delta_derivations"
            ],
            0,
        )
        self.assertFalse(
            self.probes["result"][
                "branch15_candidate_unsat_by_failed_literal"
            ]
        )
        self.assertEqual(self.probes["result"]["branch15"], "UNKNOWN")

    def test_scope_wall_and_no_automorphism_assumption(self) -> None:
        derivation = self.result["derivation"]
        self.assertFalse(
            derivation["completed_graph_automorphism_assumed"]
        )
        self.assertFalse(
            derivation[
                "individual_clause_soundness_depends_on_selection_rule"
            ]
        )
        limitations = " ".join(self.result["limitations"])
        self.assertIn("Prisms involving a triangle without", limitations)
        self.assertIn("No branch closure counts", limitations)
        self.assertEqual(
            self.result["result"]["branch15_unsat"],
            "UNKNOWN",
        )


if __name__ == "__main__":
    unittest.main()
