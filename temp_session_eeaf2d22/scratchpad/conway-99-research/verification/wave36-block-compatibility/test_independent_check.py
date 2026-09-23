"""Tests for the independent Wave 36 block-compatibility verifier."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave36_block_independent", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load independent checker")
check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check
SPEC.loader.exec_module(check)


class IndependentBlockCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = check.build_results()

    def test_01_circle_factorization_is_exact(self) -> None:
        edges = [edge for factor in check.FACTORS for edge in factor]
        self.assertEqual(len(edges), 66)
        self.assertEqual(len(set(edges)), 66)

    def test_02_restricted_core_reconstructed(self) -> None:
        core = self.result["restricted_core"]
        self.assertEqual(core["vertices"], 36)
        self.assertEqual(core["edges"], 54)
        self.assertEqual(core["degree_set"], [3])
        self.assertEqual(core["components"], 1)
        self.assertEqual(core["triangles"], 0)
        self.assertEqual(core["four_cycles"], 0)
        self.assertEqual(
            core["upper_triangle_sha256"],
            "f97aa806e08ddeb789be3f1fc604879a1630a6f1b8a21d899dbcd57772c998c5",
        )

    def test_03_gram_rank(self) -> None:
        self.assertEqual(
            self.result["restricted_core"]["forced_gram_rank_over_Q"], 34
        )

    def test_04_old_and_new_column_censuses(self) -> None:
        census = self.result["restricted_core"]["column_census"]
        self.assertEqual(census["raw_triples"], 216000)
        self.assertEqual(census["old_count"], 183980)
        self.assertEqual(census["new_count"], 151712)
        self.assertEqual(census["removed"], 32268)

    def test_05_edge_subcensuses(self) -> None:
        census = self.result["restricted_core"]["column_census"]
        self.assertEqual(
            census["old_by_internal_edges"],
            {0: 68774, 1: 90364, 2: 24138, 3: 704},
        )
        self.assertEqual(
            census["new_by_internal_edges"],
            {0: 52868, 1: 76036, 2: 22104, 3: 704},
        )
        self.assertEqual(
            census["rejected_by_negative_entry_count"],
            {1: 30940, 2: 1316, 3: 12},
        )

    def test_06_fixed_pair_residual(self) -> None:
        self.assertEqual(
            self.result["restricted_core"]["fixed_pair_residual_census"],
            {
                "pair_certificate_realizes_forced_X0_X1_gram": True,
                "raw_choices": 3600,
                "old_cut_choices": 3266,
                "mixed_cut_choices": 2939,
            },
        )

    def test_07_component_partitions(self) -> None:
        patterns = self.result["general_checks"]["component_patterns"]
        self.assertEqual(
            patterns["surviving_partitions"],
            [[4, 4, 4], [4, 8], [6, 6], [12]],
        )

    def test_08_component_value_counts(self) -> None:
        single = self.result["general_checks"]["component_patterns"][
            "single_component_patterns"
        ]
        expected = {
            "4": [24, 32, 4],
            "6": [12, 36, 12],
            "8": [4, 32, 24],
            "12": [0, 0, 60],
        }
        for m, counts in expected.items():
            self.assertEqual(single[m]["per_fibre_counts_z0_z1_z2"], counts)

    def test_09_component_couplings(self) -> None:
        coupling = self.result["general_checks"]["component_patterns"][
            "partition_coupling"
        ]
        self.assertTrue(coupling["4+8"]["all_are_coordinatewise_complements"])
        self.assertTrue(coupling["6+6"]["all_are_coordinatewise_complements"])
        self.assertEqual(
            coupling["4+4+4"]["kind_counts"],
            {"aligned_ABB": 9, "balanced_AAA": 6, "balanced_BBB": 6},
        )

    def test_10_m_two_control(self) -> None:
        control = self.result["general_checks"]["m_equals_2_exhaustive_control"]
        self.assertEqual(control["labelled_cubic_triangle_free_graphs"], 10)
        self.assertEqual(
            control[
                "minimum_over_graphs_of_max_common_neighbors_for_a_nonedge"
            ],
            3,
        )

    def test_11_spectral_arithmetic_all_component_cases(self) -> None:
        samples = self.result["general_checks"]["spectral_transfer_samples"]
        for c in ("1", "2", "3"):
            sample = samples[c]
            self.assertEqual(
                sample["kernel_multiplicities"], {"3": 18, "-4": 7 + int(c)}
            )
            self.assertEqual(
                sample["H_traces_1_to_4"],
                {1: 0, 2: 480, 3: 192, 4: 8568},
            )
            self.assertEqual(sample["H_triangles"], 32)
            self.assertEqual(sample["H_four_cycles"], 171)
            self.assertEqual(sample["characteristic_polynomial_degree"], 60)

    def test_12_solver_scope_remains_unknown(self) -> None:
        audit = self.result["solver_scope_audit"]
        self.assertEqual(audit["status"], "UNKNOWN")
        self.assertIn("one frozen X0-X1 certificate", audit["verified_scope"])
        self.assertIn("Not independently verified", audit["execution_reproducibility"])


if __name__ == "__main__":
    unittest.main()
