from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave128_exact_check", PACKAGE / "exact_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECK
SPEC.loader.exec_module(CHECK)


class AlternativeSpaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = CHECK.build_results()

    def test_incidence_lattice(self) -> None:
        lattice = self.data["incidence_kernel"]
        self.assertEqual(lattice["rank_Lambda"], 74)
        self.assertEqual(lattice["rank_W"], 13)
        self.assertEqual(
            lattice["outside_pattern_histogram"], {"0": 3, "1": 48, "2": 36}
        )
        self.assertEqual(
            lattice["det_Lambda_equals_det_QtQ"], 6_191_736_422_400
        )

    def test_induced_projector_certificate(self) -> None:
        action = self.data["discriminant_action"]
        self.assertTrue(action["projector_quotient_integral"])
        self.assertGreater(action["projector_quotient_max_abs"], 0)

    def test_ambient_primary_profiles(self) -> None:
        profiles = self.data["primary_split"]
        self.assertEqual(
            profiles["2"]["ambient_valuations"], [2, 3, 3, 3, 3, 8]
        )
        self.assertEqual(
            profiles["3"]["ambient_valuations"], [1, 1, 1, 1, 2, 2, 2]
        )
        self.assertEqual(profiles["5"]["ambient_valuations"], [1, 1])
        self.assertEqual(profiles["7"]["ambient_valuations"], [])

    def test_u_primary_profiles(self) -> None:
        profiles = self.data["primary_split"]
        self.assertEqual(profiles["2"]["U_valuations"], [2, 8])
        self.assertEqual(profiles["3"]["U_valuations"], [1, 1, 2, 2])
        self.assertEqual(profiles["5"]["U_valuations"], [1, 1])

    def test_k_primary_profiles(self) -> None:
        profiles = self.data["primary_split"]
        self.assertEqual(profiles["2"]["K_valuations"], [3, 3, 3, 3])
        self.assertEqual(profiles["3"]["K_valuations"], [1, 1, 2])
        self.assertEqual(profiles["5"]["K_valuations"], [])

    def test_exact_gauss_phases(self) -> None:
        gauss = self.data["finite_quadratic_gauss"]
        self.assertEqual(
            {
                prime: row["normalized_phase"]
                for prime, row in gauss["U"].items()
            },
            {"2": "-i", "3": "-1", "5": "-1"},
        )
        self.assertEqual(
            {
                prime: row["normalized_phase"]
                for prime, row in gauss["K"].items()
            },
            {"2": "+1", "3": "-1", "5": "+1"},
        )
        self.assertEqual(gauss["non_seven_phase"], {"U": "-i", "K": "-1"})
        self.assertEqual(
            gauss["milgram_forced_seven_phase"], {"U": "-1", "K": "-1"}
        )
        self.assertEqual(
            gauss["seven_determinant_legendre_symbol"], "(-1)^(k/2+1)"
        )
        self.assertEqual(
            gauss["seven_primary_type"], {"U": "O^-(k,7)", "K": "O^-(k,7)"}
        )

    def test_primary_lengths_partition(self) -> None:
        for profile in self.data["primary_split"].values():
            self.assertTrue(profile["valuation_check"])

    def test_determinant_rows(self) -> None:
        determinant_lambda = self.data["incidence_kernel"][
            "det_Lambda_equals_det_QtQ"
        ]
        rows = self.data["eigenlattices"]["rows"]
        self.assertEqual([row["local_mod7_rank_k"] for row in rows],
                         list(range(16, 31, 2)))
        for row in rows:
            k = row["local_mod7_rank_k"]
            self.assertEqual(
                row["det_U"] * row["det_K"],
                7 ** (2 * k) * determinant_lambda,
            )
            self.assertEqual(row["index_U_over_BLambda"], f"7^{42-k}")
            self.assertEqual(
                row["index_K_over_7IminusB_Lambda"], f"7^{32-k}"
            )
            self.assertFalse(row["excluded"])

    def test_rootless_coordinate_obstruction(self) -> None:
        for adjacency_entry in (0, 1):
            coordinate = -adjacency_entry
            self.assertNotEqual(coordinate, 3)
            self.assertNotEqual(coordinate, -4)
        rootless = self.data["eigenlattices"]["rootless"]
        self.assertEqual(rootless["U_minimum_at_least"], 4)
        self.assertEqual(rootless["K_minimum_at_least"], 4)

    def test_local_smith_toy_diagonal(self) -> None:
        toy = [
            [0, 0, 16],
            [9, 0, 0],
            [0, 2, 0],
        ]
        self.assertEqual(CHECK.local_smith_valuations(toy, 2), [0, 1, 4])
        self.assertEqual(CHECK.local_smith_valuations(toy, 3), [0, 0, 2])

    def test_hostile_action_mutation_breaks_projector(self) -> None:
        gram = CHECK.gram(CHECK.q_matrix())
        action = CHECK.transpose(CHECK.b_on_w_coordinates())
        action[0][0] += 1
        polynomial = CHECK.matrix_subtract(
            CHECK.matmul(action, action),
            [[7 * value for value in row] for row in action],
        )
        quotient = CHECK.solve_square(gram, polynomial)
        self.assertTrue(
            any(value.denominator != 1 for row in quotient for value in row)
        )

    def test_status_wall(self) -> None:
        status = self.data["status_wall"]
        self.assertFalse(status["any_rank_row_excluded"])
        self.assertFalse(status["motif_excluded"])
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
