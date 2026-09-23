import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import exact_check as ec


class ExactCountAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = ec.build_results()

    def test_source_freeze_is_version_specific(self):
        self.assertEqual(
            ec.SOURCE_FREEZE["hexagon_tex"]["sha256"],
            "f6b4fc65043f825e1888b3aff4552c883bb38ba9a15745d1822037ceba1800df",
        )
        self.assertEqual(
            ec.SOURCE_FREEZE["six_tex"]["sha256"],
            "823bcaf636a99f6655af453b2a910b9953338db980480572bca81730cfa1b44f",
        )
        self.assertEqual(
            ec.SOURCE_FREEZE["seven_tex"]["sha256"],
            "0b06fdc1c2951a344592c6af23abd133c4a8a68d717f199e7a0e2d7ceb909d0a",
        )
        self.assertIn("2508.03377v2", ec.SOURCE_FREEZE["six_archive"]["url"])
        self.assertIn("2511.06572v1", ec.SOURCE_FREEZE["seven_archive"]["url"])

    def test_formula_table_cardinalities_and_totals(self):
        l = ec.four_counts()
        m = ec.five_counts()
        n6 = ec.six_counts()
        self.assertEqual(len(l), 9)
        self.assertEqual(len(m), 21)
        self.assertEqual(len(n6), 62)
        self.assertEqual(ec.affine_sum(l.values()), ec.A(ec.math.comb(99, 4)))
        self.assertEqual(ec.affine_sum(m.values()), ec.A(ec.math.comb(99, 5)))
        self.assertEqual(ec.affine_sum(n6.values()), ec.A(ec.math.comb(99, 6)))

    def test_all_raw_four_to_five_identities_pass(self):
        l = ec.four_counts()
        m = ec.five_counts()
        for row, entries in ec.FOUR_TO_FIVE.items():
            self.assertEqual(l[row] * 95, ec.sparse_rhs(m, entries), row)

    def test_raw_five_to_six_omission_is_retained(self):
        m = ec.five_counts()
        n6 = ec.six_counts()
        residuals = {
            row: m[row] * 94 - ec.sparse_rhs(n6, entries)
            for row, entries in ec.FIVE_TO_SIX_RAW.items()
        }
        self.assertEqual(
            {row: value for row, value in residuals.items() if value != ec.A()},
            {7: n6[23]},
        )
        raw_columns = ec.source_columns(ec.FIVE_TO_SIX_RAW, 21, 62)
        self.assertEqual(
            [(index + 1, sum(column)) for index, column in enumerate(raw_columns) if sum(column) != 6],
            [(23, 5)],
        )

    def test_explicit_n23_repair_closes_every_deck_identity(self):
        m = ec.five_counts()
        n6 = ec.six_counts()
        corrected = ec.corrected_five_to_six()
        self.assertNotIn(23, ec.FIVE_TO_SIX_RAW[7])
        self.assertEqual(corrected[7][23], 1)
        for row, entries in corrected.items():
            self.assertEqual(m[row] * 94, ec.sparse_rhs(n6, entries), row)
        _, m_mapping = ec.align_four_five()
        mapping = ec.align_five_six(m_mapping, corrected)
        self.assertEqual(len(mapping), 62)
        self.assertEqual(len(set(mapping)), 62)

    def test_wrong_n23_repair_is_rejected(self):
        _, m_mapping = ec.align_four_five()
        hostile = ec.corrected_five_to_six()
        del hostile[7][23]
        hostile[8][23] = 1
        with self.assertRaises(AssertionError):
            ec.align_five_six(m_mapping, hostile)

    def test_independent_graph_class_census(self):
        self.assertEqual(len(ec.locally_admissible_classes(4)), 9)
        self.assertEqual(len(ec.locally_admissible_classes(5)), 21)
        self.assertEqual(len(ec.locally_admissible_classes(6)), 62)
        hamiltonian = ec.hamiltonian_seven_classes()
        self.assertEqual(len(hamiltonian), 19)
        edge_distribution = {}
        for mask in hamiltonian:
            edge_distribution[mask.bit_count()] = edge_distribution.get(mask.bit_count(), 0) + 1
        self.assertEqual(edge_distribution, {7: 1, 8: 2, 9: 7, 10: 7, 11: 2})

    def test_n3_index_means_two_triangles_with_matching_cross_edges(self):
        classes6 = ec.locally_admissible_classes(6)
        _, m_mapping = ec.align_four_five()
        n_mapping = ec.align_five_six(m_mapping, ec.corrected_five_to_six())
        shape = ec.n3_shape(classes6[n_mapping[2]])
        self.assertEqual(shape["edge_count"], 8)
        self.assertEqual(len(shape["triangles"]), 2)
        self.assertEqual(len(shape["cross_edges"]), 2)
        self.assertTrue(shape["cross_edges_form_matching"])

    def test_nearby_n4_index_does_not_pass_n3_shape_check(self):
        classes6 = ec.locally_admissible_classes(6)
        _, m_mapping = ec.align_four_five()
        n_mapping = ec.align_five_six(m_mapping, ec.corrected_five_to_six())
        with self.assertRaises(AssertionError):
            ec.n3_shape(classes6[n_mapping[3]])

    def test_six_vertex_exact_bounds_and_congruence(self):
        forms = ec.six_counts()
        lower, upper, lower_sources, upper_sources = ec.one_variable_bounds(forms)
        self.assertEqual((lower, upper), (Fraction(0), Fraction(4158)))
        self.assertEqual(lower_sources, [3, 4])
        self.assertEqual(upper_sources, [1])
        self.assertEqual(ec.integral_residues_one_variable(forms), (3, (0,)))
        self.assertTrue(ec.all_nonnegative_integral(forms, 0))
        self.assertTrue(ec.all_nonnegative_integral(forms, 705))
        self.assertTrue(ec.all_nonnegative_integral(forms, 4158))
        self.assertFalse(ec.all_nonnegative_integral(forms, -3))
        self.assertFalse(ec.all_nonnegative_integral(forms, 4161))
        self.assertFalse(ec.all_nonnegative_integral(forms, 704))

    def test_hostile_n1_sign_mutation_destroys_tight_upper_facet(self):
        forms = ec.six_counts()
        hostile = dict(forms)
        hostile[1] = ec.A(forms[1].c, -forms[1].x)
        _, upper, _, upper_sources = ec.one_variable_bounds(hostile)
        self.assertNotEqual(upper, Fraction(4158))
        self.assertNotEqual(upper_sources, [1])
        self.assertNotEqual(ec.affine_sum(hostile.values()), ec.A(ec.math.comb(99, 6)))

    def test_all_displayed_seven_identities_pass_symbolically(self):
        residuals = ec.seven_identities(ec.five_counts(), ec.six_counts(), ec.seven_counts())
        self.assertEqual(len(residuals), 18)
        self.assertTrue(all(value == ec.A() for value in residuals.values()))

    def test_seven_integrality_requires_h11_mod_four(self):
        forms = ec.seven_counts()
        self.assertEqual(
            ec.integral_residues_two_variables(forms),
            (1, 4, ((0, 0),)),
        )
        self.assertTrue(ec.all_nonnegative_integral(forms, 3, 8))
        self.assertFalse(ec.all_nonnegative_integral(forms, 3, 6))

    def test_seven_interval_adds_no_n3_restriction(self):
        forms = ec.seven_counts()
        for n3 in range(0, 4159, 3):
            low, high = ec.y_interval(forms, n3, 4)
            self.assertEqual(low, ec.ceil_multiple(Fraction(2 * n3), 4))
            self.assertEqual(high, 4 * n3)
            self.assertLessEqual(low, high)
            self.assertTrue(ec.all_nonnegative_integral(forms, n3, high))
        self.assertEqual(ec.y_interval(forms, 705, 4), (1412, 2820))

    def test_incumbent_intersection_remains_large(self):
        incumbent = self.results["incumbent_705_intersection"]
        self.assertEqual(incumbent["feasible_n3_value_count"], 1152)
        self.assertFalse(incumbent["improves_n3_at_least_705"])
        self.assertFalse(incumbent["conflicts_with_n3_at_least_705"])

    def test_frozen_json_is_byte_exact(self):
        expected = ec.canonical_json_bytes(self.results)
        actual = (HERE / "exact-results.json").read_bytes()
        self.assertEqual(actual, expected)
        parsed = json.loads(actual)
        self.assertEqual(
            parsed["conclusion"]["status"],
            "RIGOROUS_INCONCLUSIVE_EXHAUSTION_OF_ENCODED_PUBLISHED_COUNTS",
        )


if __name__ == "__main__":
    unittest.main()
