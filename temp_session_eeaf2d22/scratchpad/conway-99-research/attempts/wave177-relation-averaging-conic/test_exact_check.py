from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave177_exact_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave177ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = CHECK.analyze()
        CHECK.verify(cls.data)

    def test_adjacent_average_is_dimension_free(self) -> None:
        self.assertEqual(
            set(
                self.data["adjacent_pair"][
                    "nonstar_average_by_possible_dimension"
                ].values()
            ),
            {"8"},
        )

    def test_adjacent_support_bound(self) -> None:
        adjacent = self.data["adjacent_pair"]
        self.assertEqual(adjacent["true_relation_support_bounds"], [4, 8])
        self.assertTrue(adjacent["avoids_common_block"])
        self.assertTrue(adjacent["lifts_to_uncentered_columns"])

    def test_nonadjacent_average_is_dimension_free(self) -> None:
        self.assertEqual(
            set(
                self.data["nonadjacent_pair"][
                    "nonstar_average_by_possible_dimension"
                ].values()
            ),
            {"28/3"},
        )

    def test_nonadjacent_support_bound(self) -> None:
        self.assertEqual(
            self.data["nonadjacent_pair"]["true_relation_support_bounds"],
            [4, 9],
        )

    def test_complete_conic(self) -> None:
        conic = self.data["type_4_plus_2"]
        self.assertEqual(conic["projective_points"], 13)
        self.assertEqual(conic["conic_points"], 4)
        self.assertEqual(conic["nonconic_points"], 9)

    def test_local_frame_cancellation(self) -> None:
        conic = self.data["type_4_plus_2"]
        self.assertEqual(
            conic["full_plane_frame_operator"],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        )

    def test_scope(self) -> None:
        self.assertIn("endpoint remains unexcluded", self.data["conclusion"])


if __name__ == "__main__":
    unittest.main()
