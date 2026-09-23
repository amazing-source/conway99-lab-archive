"""Tests for Wave202 three-unit equality face."""

import unittest

try:
    from .exact_check import derive
except ImportError:
    from exact_check import derive


class Wave202EqualityFaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_three_unit_rhs(self) -> None:
        certificate = self.result["certificate"]
        self.assertEqual(certificate["base"], 70587)
        self.assertEqual(certificate["rhs"], 3)

    def test_forced_zero(self) -> None:
        self.assertEqual(
            self.result["certificate"]["forced_zero"],
            ["RA", "S2", "SI", "W", "b3"],
        )
        replay = self.result["certificate"][
            "coefficient_replay_after_weighted_row"
        ]
        self.assertEqual(replay["eta"], 2)
        self.assertEqual(replay["SF"], 1)

    def test_partition_classes(self) -> None:
        classes = self.result["partitions"]["classes"]
        self.assertEqual(set(classes), {"A", "B", "C"})
        for values in classes.values():
            self.assertEqual(
                3 * values["SL"] + 2 * values["E"] + values["U"], 3
            )

    def test_local_conditions(self) -> None:
        local = self.result["local_slack"]
        self.assertEqual(local["center_sizes"], [12, 13])
        self.assertEqual(local["m1_bound"], "r<=L<=3")
        self.assertIn("e_P+k_P=1", local["tight_zero"])

    def test_two_center_null(self) -> None:
        two_center = self.result["two_center"]
        self.assertTrue(two_center["m1_forces_opposite_occupied"])
        self.assertFalse(two_center["baseline_obstruction_found"])
        self.assertEqual(two_center["global_realization"], "UNKNOWN")

    def test_no_bound_inflation(self) -> None:
        claim = self.result["claim"]
        self.assertEqual(claim["conditional_Q_lower_bound"], 7059)
        self.assertFalse(claim["Q0_7059_excluded"])

    def test_scope(self) -> None:
        scope = self.result["search_scope"]
        self.assertIn("tiny symbolic slack partition", scope)
        self.assertIn("no graph", scope)


if __name__ == "__main__":
    unittest.main()
