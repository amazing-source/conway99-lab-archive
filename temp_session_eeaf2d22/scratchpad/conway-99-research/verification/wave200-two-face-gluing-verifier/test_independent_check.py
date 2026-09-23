"""Tests for the independent Wave200 verifier."""

import unittest

try:
    from .independent_check import derive
except ImportError:
    from independent_check import derive


class Wave200IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_verdict_and_scope(self) -> None:
        self.assertEqual(self.result["verdict"], "VERIFIED_WITH_SCOPE")
        self.assertIn("no graph", self.result["search_scope"])
        self.assertIn("brute-force", self.result["search_scope"])

    def test_faces_and_budgets(self) -> None:
        faces = self.result["faces"]
        self.assertEqual(faces["excluded_Q0_values"], [7037, 7038])
        self.assertEqual(faces["budgets"], {"7037": 23, "7038": 63})

    def test_oriented_identities(self) -> None:
        identities = self.result["oriented_identities"]
        self.assertEqual(
            identities["S5_vector"],
            {"delta": 5, "eta": 5, "epsilon": 1},
        )
        self.assertEqual(
            identities["q_right_vector"]["constant"],
            297,
        )

    def test_coefficient_domination(self) -> None:
        forced = self.result["forced_saturation"]
        self.assertEqual(
            forced["coefficientwise_domination_residual"],
            {"SH": 8, "SF": 36, "g": 24},
        )
        self.assertEqual(
            forced["face_s_lower"],
            {"7037": 57, "7038": 27},
        )
        self.assertEqual(forced["s_lower"], 27)

    def test_fibre_collision_guard(self) -> None:
        local = self.result["local_fibre_loss"]
        self.assertEqual(local["simple_family_pair_capacity"], 5)
        self.assertEqual(local["saturated_orientation_multiplicity"], 5)
        for template in local["hilton_milner_templates"].values():
            self.assertEqual(template["maximum_pair_degree"], 5)
            self.assertEqual(len(template["degree_five_pairs"]), 3)

    def test_local_global_contradiction(self) -> None:
        local = self.result["local_fibre_loss"]
        self.assertEqual(local["delta_upper"], 12)
        self.assertEqual(local["s_upper"], 4)
        self.assertEqual(
            self.result["contradiction"],
            {
                "required_s_lower": 27,
                "permitted_s_upper": 4,
                "status": "CONTRADICTION",
            },
        )

    def test_consequence(self) -> None:
        consequence = self.result["consequence"]
        self.assertEqual(consequence["conditional_Q_lower"], 7039)
        self.assertEqual(
            consequence["all_projective_short_circuits"],
            7732,
        )
        self.assertEqual(
            consequence["nonzero_scalar_short_circuit_words"],
            15464,
        )

    def test_boundary_stays_unknown(self) -> None:
        boundary = self.result["boundary"]
        self.assertFalse(boundary["endpoint_excluded"])
        self.assertFalse(boundary["rank_11_excluded"])
        self.assertEqual(boundary["conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
