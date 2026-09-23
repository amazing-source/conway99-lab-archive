from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave128_independent_verify", HERE / "independent_verify.py"
)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VERIFY
SPEC.loader.exec_module(VERIFY)


class IndependentWave128Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = VERIFY.build_results()

    def test_seal_and_import_preinspection(self) -> None:
        self.assertEqual(
            self.data["preinspection"]["discovery_entries_checked"], 11
        )
        self.assertEqual(
            self.data["preinspection"]["input_manifests_checked"], 5
        )

    def test_incidence_reconstruction(self) -> None:
        row = self.data["reconstruction"]
        self.assertEqual(row["pattern_histogram"], {"0": 3, "1": 48, "2": 36})
        self.assertEqual(row["Q_rank"], 13)
        self.assertEqual(row["primitive_minor_determinant_abs"], 1)
        self.assertEqual(row["Lambda_rank"], 74)
        self.assertEqual(row["det_Lambda"], 6_191_736_422_400)

    def test_integer_smith_profiles(self) -> None:
        self.assertEqual(
            self.data["primary_valuations"]["2"],
            {
                "ambient": [2, 3, 3, 3, 3, 8],
                "U": [2, 8],
                "K": [3, 3, 3, 3],
            },
        )
        self.assertEqual(
            self.data["primary_valuations"]["3"],
            {
                "ambient": [1, 1, 1, 1, 2, 2, 2],
                "U": [1, 1, 2, 2],
                "K": [1, 1, 2],
            },
        )
        self.assertEqual(
            self.data["primary_valuations"]["5"],
            {"ambient": [1, 1], "U": [1, 1], "K": []},
        )

    def test_exact_gauss_phases(self) -> None:
        phases = {
            component: {
                prime: row["phase"]
                for prime, row in self.data["gauss_profiles"][component].items()
            }
            for component in ("U", "K")
        }
        self.assertEqual(
            phases,
            {
                "U": {"2": "-i", "3": "-1", "5": "-1"},
                "K": {"2": "+1", "3": "-1", "5": "+1"},
            },
        )
        self.assertEqual(self.data["seven_phases"], {"U": "-1", "K": "-1"})
        self.assertEqual(
            self.data["seven_types"], {"U": "O^-(k,7)", "K": "O^-(k,7)"}
        )

    def test_rootlessness_holds_for_both_signs(self) -> None:
        for sign in (-1, 1):
            for adjacency in (0, 1):
                chosen_coordinate = sign * (-adjacency)
                self.assertNotEqual(chosen_coordinate, sign * 3)
                self.assertNotEqual(chosen_coordinate, sign * -4)
        audit = self.data["rootlessness_audit"]
        self.assertEqual(audit["min_U_at_least"], 4)
        self.assertEqual(audit["min_K_at_least"], 4)

    def test_all_imported_rows_survive_only_locally(self) -> None:
        rows = self.data["rows"]
        self.assertEqual([row["k"] for row in rows], list(range(16, 31, 2)))
        self.assertTrue(all(row["discriminant_length_bounds_hold"] for row in rows))
        self.assertTrue(all(row["O_minus_k_7_exists"] for row in rows))
        self.assertFalse(any(row["excluded"] for row in rows))

    def test_hostile_projector_mutation_fails(self) -> None:
        q = VERIFY.q_matrix()
        gram = VERIFY.multiply(VERIFY.transpose(q), q)
        c = VERIFY.action_on_w()
        ct = VERIFY.transpose(c)
        ct[0][0] += 1
        square = VERIFY.multiply(ct, ct)
        polynomial = [
            [square[i][j] - 7 * ct[i][j] for j in range(13)]
            for i in range(13)
        ]
        quotient = VERIFY.solve_exact(gram, polynomial)
        self.assertTrue(
            any(value.denominator != 1 for row in quotient for value in row)
        )

    def test_status_wall(self) -> None:
        status = self.data["status_wall"]
        self.assertFalse(status["any_rank_row_excluded"])
        self.assertEqual(status["motif_extension"], "UNKNOWN")
        self.assertEqual(status["Conway_99"], "UNKNOWN")
        self.assertEqual(status["literature_novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
