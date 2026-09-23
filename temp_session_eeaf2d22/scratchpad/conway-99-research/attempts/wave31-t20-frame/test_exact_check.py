#!/usr/bin/env python3
"""Regression tests for the exact Wave 31 T20 construction lane."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
CHECKER_PATH = HERE / "exact_check.py"
RESULT_PATH = HERE / "exact-results.json"


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "wave31_t20_exact_check", CHECKER_PATH
    )
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load Wave 31 checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CHECK = load_checker()


class Wave31T20Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_result()
        cls.stored = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_frozen_inputs(self) -> None:
        self.assertEqual(
            self.result["frozen_inputs"],
            CHECK.FROZEN_INPUTS,
        )

    def test_complete_shell_and_residue_injectivity(self) -> None:
        t20 = self.result["T20"]
        self.assertEqual(t20["norm_four_vector_count"], 5076)
        self.assertEqual(t20["antipodal_line_count"], 2538)
        self.assertEqual(t20["distinct_residue_classes_mod_2"], 2538)
        self.assertEqual(t20["distinct_residue_classes_mod_3"], 2538)
        self.assertEqual(
            t20["canonical_lines_sha256"],
            "25af9df21492a5b9022c1888424f4892e0e1cb56d82adee73b49197a536f569e",
        )

    def test_all_pair_inner_products(self) -> None:
        geometry = self.result["line_pair_geometry"]
        self.assertEqual(
            geometry["signed_inner_product_counts"],
            {
                "-2": 80883,
                "-1": 671126,
                "0": 1382670,
                "1": 923008,
                "2": 161766,
            },
        )
        self.assertEqual(
            geometry["absolute_inner_product_counts"],
            {"0": 1382670, "1": 1594134, "2": 242649},
        )
        self.assertEqual(
            sum(geometry["absolute_inner_product_counts"].values()),
            geometry["unordered_pair_count"],
        )

    def test_absolute_two_graph_degrees(self) -> None:
        geometry = self.result["line_pair_geometry"]
        self.assertEqual(
            geometry["absolute_two_degree_distribution"],
            {
                "160": 108,
                "178": 840,
                "196": 1242,
                "214": 330,
                "232": 15,
                "322": 3,
            },
        )
        degree_sum = sum(
            int(degree) * multiplicity
            for degree, multiplicity
            in geometry["absolute_two_degree_distribution"].items()
        )
        self.assertEqual(degree_sum, 2 * geometry["absolute_two_graph_edges"])

    def test_gf2_system_is_consistent_but_not_decisive(self) -> None:
        parity = self.result["exact_105_row_problem"]["GF2_relaxation"]
        self.assertEqual(
            parity,
            {
                "equations_including_row_count": 211,
                "rank": 210,
                "dependencies": 1,
                "inconsistent": False,
            },
        )

    def test_exact_rational_relaxation_witness(self) -> None:
        relaxation = self.result["exact_105_row_problem"][
            "rational_relaxation"
        ]
        self.assertEqual(
            relaxation["status"],
            "EXACT_RATIONAL_SECOND_MOMENT_RELAXATION_WITNESS",
        )
        self.assertEqual(relaxation["support_size"], 243)
        self.assertEqual(relaxation["unit_weight_count"], 33)
        self.assertEqual(relaxation["fractional_weight_count"], 210)
        self.assertEqual(
            relaxation["weight_certificate_sha256"],
            "2e7f5d482685db1c98f99fe239021f87e3f7c27f0506d92611e935a0617af161",
        )

    def test_near_frame_and_radius_two_restriction(self) -> None:
        scout = self.result["exact_105_row_problem"][
            "bounded_integer_neighbourhood"
        ]
        self.assertEqual(scout["near_frame_status"], "NOT_A_FRAME")
        self.assertEqual(scout["frobenius_residual_score"], 121)
        self.assertEqual(
            scout["nonzero_residual_entries_upper_triangle"], 63
        )
        self.assertEqual(scout["maximum_absolute_residual_entry"], 2)
        self.assertEqual(scout["radius_one"]["exact_matches"], [])
        self.assertEqual(scout["radius_two"]["exact_matches"], [])
        self.assertEqual(scout["radius_two"]["removal_pair_count"], 5460)
        self.assertEqual(
            scout["radius_two"]["addition_pair_count"], 2958528
        )
        self.assertEqual(scout["global_second_moment_frame"], "UNKNOWN")

    def test_restricted_cap_one_obstruction_is_not_global(self) -> None:
        restriction = self.result["exact_105_row_problem"][
            "cap_one_coordinate_restriction"
        ]
        self.assertEqual(restriction["available_lines"], 1196)
        self.assertEqual(
            restriction["status"],
            "EXCLUDED_ONLY_IN_THIS_RESTRICTED_DOMAIN",
        )
        self.assertEqual(
            self.result["status"]["global_105_row_second_moment_frame"],
            "UNKNOWN",
        )

    def test_block_counts_and_A4_coupling(self) -> None:
        block = self.result["full_T20_block_constraints_after_a_frame"]
        self.assertEqual(
            block["aggregate_directed_internal_counts"],
            {
                "plus_one": 2316,
                "minus_one": 648,
                "minus_two": 1044,
                "zero": 6912,
                "sum_c_minus_two": 1044,
                "sum_q_actual_graph_notation": 216,
            },
        )
        self.assertEqual(
            block["A4_diagonal"],
            {
                "form": (
                    "(A4_A)[i,i]=4*(1+e_i), "
                    "e_i nonnegative integer"
                ),
                "excess_units_on_A_block": 84,
                "trace_A4_A": 756,
            },
        )
        sharpening = self.result["coupling_to_U_block"][
            "actual_graph_only_sharpening"
        ]
        self.assertTrue(sharpening["not_imposed_on_matrix_search"])
        self.assertEqual(
            sharpening["U_profile"],
            {"c9": 4, "c10": 122, "c11": 0},
        )

    def test_stored_result_is_byte_identical(self) -> None:
        self.assertEqual(self.result, self.stored)
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "regenerated.json"
            CHECK.write_json(output, self.result)
            self.assertEqual(output.read_bytes(), RESULT_PATH.read_bytes())


if __name__ == "__main__":
    unittest.main()
