#!/usr/bin/env python3
"""Regression and hostile-control tests for the Wave 31 T20 verifier."""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
CHECKER_PATH = HERE / "independent_check.py"
RESULT_PATH = HERE / "independent-results.json"
SUBMISSION_PATH = (
    HERE.parents[1] / "attempts" / "wave31-t20-frame"
    / "exact-results.json"
)


def load_checker():
    specification = importlib.util.spec_from_file_location(
        "wave31_t20_independent_check", CHECKER_PATH
    )
    if specification is None or specification.loader is None:
        raise AssertionError("cannot load independent verifier")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


CHECK = load_checker()


class Wave31T20IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_result()
        cls.stored = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_scoped_verdict_and_frozen_commit(self) -> None:
        self.assertEqual(
            self.result["verdict"], "PASS_SCOPED_FINITE_EVIDENCE"
        )
        frozen = self.result["frozen_submission"]
        self.assertEqual(frozen["commit"], CHECK.FROZEN_COMMIT)
        self.assertEqual(frozen["tree"], CHECK.FROZEN_TREE)
        self.assertTrue(frozen["all_exact"])

    def test_complete_shell_in_two_bases(self) -> None:
        shell = self.result["complete_shell"]
        self.assertEqual(shell["norm_counts_including_zero"], {
            "0": 1, "4": 5076,
        })
        self.assertEqual(shell["antipodal_lines"], 2538)
        self.assertTrue(
            shell["changed_basis_enumeration"]["mapped_shell_equals_original"]
        )
        self.assertEqual(
            shell["canonical_lines_sha256"],
            "25af9df21492a5b9022c1888424f4892e0e1cb56d82adee73b49197a536f569e",
        )

    def test_pair_geometry_and_residue_injectivity(self) -> None:
        shell = self.result["complete_shell"]
        self.assertEqual(shell["distinct_residue_classes_mod_2"], 2538)
        self.assertEqual(shell["distinct_residue_classes_mod_3"], 2538)
        geometry = self.result["line_pair_geometry"]
        self.assertEqual(geometry["signed_inner_product_counts"], {
            "-2": 80883,
            "-1": 671126,
            "0": 1382670,
            "1": 923008,
            "2": 161766,
        })
        self.assertEqual(geometry["absolute_two_edges"], 242649)
        self.assertTrue(geometry["degree_sum_equals_twice_edges"])

    def test_moment_formulation_and_gf2_consistency(self) -> None:
        moment = self.result["second_moment_formulation"]
        self.assertEqual(moment["Boolean_line_variables"], 2538)
        self.assertEqual(moment["selected_lines"], 105)
        self.assertEqual(moment["upper_triangle_moment_equations"], 210)
        self.assertEqual(moment["cardinality_from_T20_trace"], 105)
        self.assertEqual(moment["GF2"], {
            "variables": 2538,
            "equations_including_cardinality": 211,
            "coefficient_rank": 210,
            "augmented_rank": 210,
            "dependencies": 1,
            "consistent": True,
        })

    def test_exact_rational_witness(self) -> None:
        witness = self.result["rational_relaxation"]
        self.assertTrue(
            witness["all_2538_weights_in_closed_unit_interval"]
        )
        self.assertEqual(witness["weight_sum"], "105")
        self.assertEqual(witness["verified_moment_entries"], 210)
        self.assertTrue(witness["not_boolean"])
        self.assertEqual(
            witness["weight_certificate_sha256"],
            "2e7f5d482685db1c98f99fe239021f87e3f7c27f0506d92611e935a0617af161",
        )

    def test_named_neighbourhood_is_only_restricted_nonhit(self) -> None:
        neighbourhood = self.result["named_radius_two_neighbourhood"]
        self.assertEqual(neighbourhood["frobenius_residual_score"], 121)
        self.assertEqual(
            neighbourhood["radius_one"]["exact_repairs"], []
        )
        self.assertEqual(
            neighbourhood["radius_two"]["exact_repairs"], []
        )
        self.assertEqual(
            neighbourhood["radius_two"]["addition_pair_count"], 2958528
        )
        self.assertEqual(
            neighbourhood["global_second_moment_frame"], "UNKNOWN"
        )

    def test_fingerprint_linearity_with_negative_entries(self) -> None:
        coefficients = CHECK.splitmix64_coefficients(4)
        left = (25, -7, 0, -25)
        right = (-3, 8, -4, 11)
        summed = CHECK.add_vectors(left, right)
        self.assertEqual(
            CHECK.modular_fingerprint(summed, coefficients),
            (
                CHECK.modular_fingerprint(left, coefficients)
                + CHECK.modular_fingerprint(right, coefficients)
            ) & CHECK.MASK64,
        )
        difference = CHECK.subtract_vectors(left, right)
        self.assertEqual(
            CHECK.modular_fingerprint(difference, coefficients),
            (
                CHECK.modular_fingerprint(left, coefficients)
                - CHECK.modular_fingerprint(right, coefficients)
            ) & CHECK.MASK64,
        )

    def test_positional_encoding_is_injective_on_bounded_control(self) -> None:
        coefficients = [1, 7, 49]
        seen: dict[int, tuple[int, int, int]] = {}
        for a in range(-3, 4):
            for b in range(-3, 4):
                for c in range(-3, 4):
                    vector = (a, b, c)
                    code = CHECK.linear_code(vector, coefficients)
                    self.assertNotIn(code, seen)
                    seen[code] = vector

    def test_cap_one_and_A4_transfer_are_conditional(self) -> None:
        cap = self.result["cap_one_coordinate_restriction"]
        self.assertEqual(cap["available_lines"], 1196)
        self.assertEqual(cap["remaining_lines_not_excluded"], 1342)
        self.assertEqual(
            cap["verdict"], "EXCLUDED_ONLY_IN_THIS_RESTRICTED_DOMAIN"
        )
        transfer = self.result["A4_U_transfer"]
        self.assertEqual(transfer["U_excess_units"], 0)
        self.assertEqual(transfer["A_excess_units"], 84)
        self.assertEqual(transfer["A_trace_A4"], 756)
        self.assertTrue(transfer["transfer_verified"])

    def test_status_wall_rejects_promotion_mutation(self) -> None:
        submission = json.loads(SUBMISSION_PATH.read_text(encoding="utf-8"))
        mutated = copy.deepcopy(submission)
        mutated["status"]["global_105_row_second_moment_frame"] = "EXCLUDED"
        with self.assertRaises(CHECK.VerificationError):
            CHECK.verify_status_walls(mutated)

    def test_stored_result_is_byte_identical(self) -> None:
        self.assertEqual(self.result, self.stored)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "independent-results.json"
            CHECK.write_json(output, self.result)
            self.assertEqual(output.read_bytes(), RESULT_PATH.read_bytes())


if __name__ == "__main__":
    unittest.main()
