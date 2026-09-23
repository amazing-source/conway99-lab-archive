"""Tests for the source-blind Wave202 equality-face verifier."""

import unittest

try:
    from .independent_check import derive, fibre_term
except ImportError:
    from independent_check import derive, fibre_term


class Wave202IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_pre_source_status(self) -> None:
        self.assertEqual(
            self.result["verdict"],
            "INDEPENDENTLY_DERIVED_PRE_SOURCE",
        )

    def test_complete_analytic_partition(self) -> None:
        face = self.result["face"]
        self.assertEqual(
            face["forced_zero"],
            ["SI", "S2", "RA", "b3", "W"],
        )
        self.assertTrue(face["analytic_partition"]["complete"])

    def test_raw_formulas(self) -> None:
        formulas = self.result["face"]["raw_formulas"]
        self.assertEqual(formulas["a2"], "60-SE2-c2-2*SF")
        self.assertEqual(formulas["r2"], "30-SF")
        self.assertEqual(formulas["n2"], "357-a1-SL+SF")
        self.assertEqual(
            formulas["y"],
            "a3+3*n3-3801-SE2+SF",
        )
        self.assertEqual(
            formulas["q"],
            "3*n3+a3+eta+SM-3564",
        )

    def test_symbolic_replay(self) -> None:
        replay = self.result["face"]["symbolic_replay"]
        self.assertEqual(replay["SI"], "0")
        self.assertEqual(replay["RA"], "0")
        self.assertEqual(replay["T-p3-q"], "0")
        self.assertEqual(replay["Q0"], "7059")

    def test_tight_zero_slack_profiles(self) -> None:
        m2 = fibre_term((2, 1, 1, 1), {0: 2}, baseline=True)
        m3 = fibre_term((3, 1, 1), {0: 3}, baseline=True)
        empty = fibre_term((2, 1, 1, 1), {}, baseline=True)
        self.assertEqual(m2["local_term"], 0)
        self.assertEqual(m3["local_term"], 0)
        self.assertEqual(empty["local_term"], 0)

    def test_multiplicity_one_costs_slack(self) -> None:
        m1 = fibre_term((1, 2, 1, 1), {0: 1}, baseline=True)
        self.assertEqual(m1["local_term"], 1)
        self.assertEqual(
            self.result["local_equality"]["tight_zero_slack"][
                "multiplicity_one"
            ],
            "impossible at zero local slack; it costs at least one",
        )

    def test_locally_compatible_null_control(self) -> None:
        control = self.result["null_control"]
        self.assertEqual(
            control["locally_compatible_multiplicity_profile"],
            {"2": 234, "3": 3},
        )
        self.assertEqual(control["aggregate"]["q"], 237)
        self.assertEqual(control["aggregate"]["weighted_loss"], 3)
        self.assertEqual(control["aggregate"]["Q0"], 7059)
        self.assertFalse(control["asserted_graph_or_flag_family"])

    def test_m1_arithmetic_control_not_local_equality(self) -> None:
        m1 = self.result["null_control"]["earlier_m1_accounting_profile"]
        self.assertFalse(m1["locally_zero_slack"])

    def test_no_bound_promotion(self) -> None:
        bound = self.result["bound"]
        self.assertFalse(bound["Q0_face_excluded"])
        self.assertEqual(bound["conditional_Q_lower"], 7059)
        self.assertFalse(bound["conditional_Q_lower_improved"])

    def test_boundary_and_scope(self) -> None:
        boundary = self.result["boundary"]
        self.assertFalse(boundary["endpoint_excluded"])
        self.assertEqual(boundary["conway_99"], "UNKNOWN")
        self.assertIn("no graph", self.result["search_scope"])
        self.assertIn("brute-force", self.result["search_scope"])


if __name__ == "__main__":
    unittest.main()
