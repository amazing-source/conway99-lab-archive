from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave58_exact", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class Wave58ExactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wave57, cls.wave36, cls.wave40 = CHECK.load_inputs()

    def test_gram_entry_ledgers(self) -> None:
        ledger = CHECK.gram_entry_ledger()
        self.assertEqual(
            ledger["B_transpose_B"], "12I-A_Y+2J-A_Y^2"
        )
        self.assertIn("blockdiag", ledger["B_B_transpose"])

    def test_wave36_replay(self) -> None:
        replay = CHECK.replay_wave36(self.wave36)
        self.assertEqual(replay["component_count_values"], [1, 2, 3])
        self.assertEqual(replay["mult_Y_3"], 18)

    def test_kernel_rank_rows(self) -> None:
        rows = CHECK.kernel_rank_derivation()["rows"]
        self.assertEqual(
            [
                (
                    row["a_mult_Y_3"],
                    row["b_mult_Y_minus4"],
                    row["kappa_components"],
                    row["rank_B"],
                )
                for row in rows
            ],
            [(18, 8, 1, 34), (18, 9, 2, 33), (18, 10, 3, 32)],
        )

    def test_wave57_rows_collapse_18_to_3(self) -> None:
        collapse = CHECK.collapse_wave57(self.wave57)
        self.assertEqual(collapse["input_row_count"], 18)
        self.assertEqual(collapse["survivor_count"], 3)

    def test_missing_wave57_row_rejected(self) -> None:
        mutated = copy.deepcopy(self.wave57)
        mutated["multiplicity_fourth_moment_ledger"].pop()
        with self.assertRaises(AssertionError):
            CHECK.collapse_wave57(mutated)

    def test_component_censuses(self) -> None:
        m4 = CHECK.component_census(4)
        m6 = CHECK.component_census(6)
        self.assertEqual(
            m4["C4_distribution"], {"2": 6, "4": 30, "6": 14}
        )
        self.assertEqual(m4["raw_labelled_configurations"], 216)
        self.assertEqual(m6["raw_labelled_configurations"], 162000)
        self.assertEqual(
            m6["C4_values"], [0, 1, 2, 3, 4, 5, 6, 7, 9]
        )

    def test_kappa3_reduction_and_control(self) -> None:
        result = CHECK.structural_reduction()
        self.assertEqual(
            result["universal_wedge_bound"]["C4_X_upper_bound"], 27
        )
        self.assertEqual(result["kappa2_union_C4_X_bounds"], [0, 24])
        self.assertEqual(
            result["universal_kappa3_C4_X_values"],
            [6, 8, 10, 12, 14, 16, 18],
        )
        self.assertEqual(
            result["kappa3_local_A_X_control"]["component_sizes"],
            [12, 12, 12],
        )
        self.assertEqual(
            result["kappa3_aligned_scalar_control"]["C4_X"], 12
        )

    def test_wedge_bound_hostile_size(self) -> None:
        with self.assertRaises(AssertionError):
            CHECK.wedge_four_cycle_bound(vertices=40)

    def test_bad_scalar_control_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            CHECK.verify_linear_spectral_control(
                18, 10, 12, (5, 6, 8, 1, 9, 1)
            )

    def test_restricted_wave40_census(self) -> None:
        replay = CHECK.replay_wave40(self.wave40)
        census = replay["canonical_replay"]
        self.assertEqual(census["triangle_free_masks"], 37378)
        self.assertEqual(
            census["component_profile_distribution"], {"12+24": 37378}
        )

    def test_status_wall(self) -> None:
        result = CHECK.build_results()
        self.assertEqual(result["claim_label"], "DERIVED")
        self.assertFalse(result["result"]["contradiction"])
        self.assertEqual(result["result"]["endpoint"], "UNKNOWN")
        self.assertFalse(
            result["upstream_novelty_guard"][
                "rank_and_multiplicity_identities_are_new"
            ]
        )


if __name__ == "__main__":
    unittest.main()
