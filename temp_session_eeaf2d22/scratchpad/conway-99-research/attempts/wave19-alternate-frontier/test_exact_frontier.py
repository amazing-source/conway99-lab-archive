"""Focused tests for the Wave 19 alternate exact checker."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave19_alternate_exact", HERE / "exact_frontier.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ExactFrontierTests(unittest.TestCase):
    def test_q_profile_census(self) -> None:
        profiles = CHECK.q_profiles()
        self.assertEqual(len(profiles), 13)
        self.assertEqual(
            {len(profile) for profile in profiles}, {14, 15, 16, 17, 18, 19, 20}
        )
        self.assertEqual(
            [profile for profile in profiles if len(profile) == 20],
            [(2,) * 20],
        )

    def test_labeled_cubic_order_six_census(self) -> None:
        result = CHECK.labeled_cubic_graphs_order_six()
        self.assertEqual(result["labeled_cubic_graph_count"], 70)
        self.assertEqual(result["labeled_K3,3_count"], 10)
        self.assertEqual(result["labeled_prism_count"], 60)
        self.assertEqual(result["prism_alpha_beta_coverage"], 3)
        self.assertEqual(result["K3,3_grid_pair_count"], 18)

    def test_six_cycle_enumerator(self) -> None:
        rows = tuple(
            (1 << ((vertex - 1) % 6)) | (1 << ((vertex + 1) % 6))
            for vertex in range(6)
        )
        self.assertEqual(CHECK.six_cycle_vertex_sets(rows), ((1 << 6) - 1,))

    def test_psd_checker_controls(self) -> None:
        self.assertTrue(CHECK.is_psd_exact(((2, -1), (-1, 2))))
        self.assertFalse(CHECK.is_psd_exact(((1, 2), (2, 1))))
        self.assertTrue(CHECK.is_psd_exact(((0, 0), (0, 0))))
        self.assertFalse(CHECK.is_psd_exact(((0, 1), (1, 1))))

    def test_nullspace_control(self) -> None:
        basis = CHECK.nullspace(((1, 1, 0), (0, 1, 1)))
        self.assertEqual(basis, ((Fraction(1), Fraction(-1), Fraction(1)),))

    def test_structural_projector_arithmetic(self) -> None:
        result = CHECK.structural_arithmetic()
        self.assertEqual(result["m29_e90_projector_square_sum"], 252)
        self.assertEqual(result["m29_e89_projector_square_sum"], 1386)
        self.assertEqual(result["m30_Z_spectral_cap"], 3)
        self.assertLess(
            result["m29_e89_outside_y_square_sum"],
            result["m29_e89_outside_y_sum"],
        )
        self.assertLess(
            result["m30_z4_required_sum"], result["m30_z4_lower_bound"]
        )

    def test_farkas_weights_and_mutation_controls(self) -> None:
        self.assertEqual(len(CHECK.FARKAS_WEIGHTS), 15)
        self.assertEqual(sum(CHECK.FARKAS_WEIGHTS.values()), -3)
        self.assertEqual(
            CHECK.FINAL_Z_EDGES, ((0, 23), (1, 22), (2, 17))
        )
        self.assertEqual(
            CHECK.support_weight(
                CHECK.FARKAS_SIGN_MUTATION_WITNESS, CHECK.FARKAS_WEIGHTS
            ),
            1,
        )
        sign_mutation = dict(CHECK.FARKAS_WEIGHTS)
        sign_mutation[CHECK.FARKAS_SIGN_MUTATION] *= -1
        self.assertLess(
            CHECK.support_weight(
                CHECK.FARKAS_SIGN_MUTATION_WITNESS, sign_mutation
            ),
            0,
        )
        index_mutation = dict(CHECK.FARKAS_WEIGHTS)
        source, replacement = CHECK.FARKAS_INDEX_MUTATION
        index_mutation[replacement] = index_mutation.pop(source)
        self.assertEqual(
            CHECK.support_weight(
                CHECK.FARKAS_INDEX_MUTATION_WITNESS, CHECK.FARKAS_WEIGHTS
            ),
            0,
        )
        self.assertLess(
            CHECK.support_weight(
                CHECK.FARKAS_INDEX_MUTATION_WITNESS, index_mutation
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
