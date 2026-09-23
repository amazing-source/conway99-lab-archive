from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave134_independent",
    HERE / "independent_verify.py",
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Wave134IndependentTests(unittest.TestCase):
    def test_no_discovery_import(self) -> None:
        source = (HERE / "independent_verify.py").read_text(encoding="utf-8")
        self.assertNotIn("discover_rational", source)
        self.assertNotIn("import pickle", source)

    def test_z4_types(self) -> None:
        record = VERIFY.smith_type_audit()
        self.assertEqual(record["primal_type"], "Z4^54 x Z2")
        self.assertEqual(record["dual_type"], "Z4^44 x Z2")
        self.assertEqual(record["primal_size"] * record["dual_size"], 4**99)

    def test_hostile_torsion_gaps(self) -> None:
        record = VERIFY.torsion_audit()
        self.assertEqual(
            record["primal_torsion_gap"]["weight_7_status"],
            "ALLOWED_NOT_FORCED_ZERO",
        )
        self.assertEqual(
            record["dual_torsion_gap"]["forced_zero_weights"],
            [1, 2, 3, 4, 5, 6, 7],
        )
        zeros = VERIFY.structural_zero_audit()
        self.assertNotIn(
            7, zeros["primal_even_symbol_slice"]["forbidden_two_counts"]
        )
        self.assertIn(
            7, zeros["dual_even_symbol_slice"]["forbidden_two_counts"]
        )

    def test_hostile_dual_residue_weight_92_wall(self) -> None:
        states = VERIFY.structural_orbit_audit()
        self.assertEqual(states["primal_allowed_orbits"], 1_119)
        self.assertEqual(states["dual_allowed_orbits"], 1_114)
        self.assertEqual(states["dual_forbidden_orbits"], 161)
        self.assertEqual(states["dual_weight_92_orbits_forced_zero"], 4)
        self.assertEqual(
            states["dual_forbidden_orbits_by_odd_count"]["92"],
            4,
        )

    def test_q_plus_and_minus_are_distinct(self) -> None:
        dual = VERIFY.dual_forced_table()
        self.assertEqual(dual[(72, 24, 3)], 1_386)
        self.assertEqual(dual[(75, 24, 0)], 1_386)
        self.assertEqual(dual[(71, 26, 2)], 8_316)
        self.assertEqual(dual[(73, 26, 0)], 8_316)

    def test_complete_small_support_families(self) -> None:
        primal = VERIFY.primal_forced_table()
        dual = VERIFY.dual_forced_table()
        self.assertEqual(len(primal), 84)
        self.assertEqual(len(dual), 44)
        self.assertEqual(sum(primal.values()), 8_557_760)
        self.assertEqual(sum(dual.values()), 4_126_784)
        self.assertTrue(all(composition[1] % 2 == 0 for composition in primal))
        self.assertTrue(all(composition[1] % 2 == 0 for composition in dual))
        self.assertEqual(primal, VERIFY.brute_small_support_table("primal"))
        self.assertEqual(dual, VERIFY.brute_small_support_table("dual"))

    def test_zero_two_symmetry_orbits(self) -> None:
        primal = VERIFY.primal_forced_table()
        dual = VERIFY.dual_forced_table()
        self.assertEqual(
            {VERIFY.swapped(composition) for composition in primal},
            set(primal),
        )
        self.assertEqual(
            {VERIFY.swapped(composition) for composition in dual},
            set(dual),
        )
        self.assertFalse(any(a == c for a, _b, c in primal))
        self.assertFalse(any(a == c for a, _b, c in dual))
        self.assertEqual(len(primal) // 2, 42)
        self.assertEqual(len(dual) // 2, 22)

    def test_transform_formula(self) -> None:
        record = VERIFY.macwilliams_audit()
        self.assertEqual(
            record["substitution_matrix_square"],
            [[4, 0, 0], [0, 4, 0], [0, 0, 4]],
        )
        self.assertEqual(
            record["normalization_product"],
            record["expected_normalization_product"],
        )

    def test_preseal_derivation(self) -> None:
        record = VERIFY.preseal_derivation()
        self.assertEqual(record["claim_label"], "DERIVED_PRESEAL")
        self.assertFalse(record["status_wall"]["discovery_seal_bound"])
        self.assertEqual(record["status_wall"]["Conway_99"], "UNKNOWN")

    def test_sealed_discovery_bind(self) -> None:
        record = VERIFY.build_result()
        self.assertEqual(record["claim_label"], "VERIFIED")
        self.assertEqual(record["sealed_discovery"]["entries_checked"], 13)
        self.assertTrue(
            record["sealed_result_audit"]["forced_composition_tables_match"]
        )
        self.assertTrue(
            record["sealed_result_audit"]["structural_state_counts_match"]
        )
        self.assertEqual(
            record["status_wall"]["finite_rational_feasibility"],
            "UNKNOWN_NOT_RUN_CORRECTED_MODEL",
        )


if __name__ == "__main__":
    unittest.main()
