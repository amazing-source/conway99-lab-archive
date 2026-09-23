from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("independent_check.py")
SPEC = importlib.util.spec_from_file_location("wave177_independent", MODULE)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class IndependentWave177Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.analyze()

    def test_adjacent_average(self) -> None:
        values = self.result["adjacent"]["outside_average_by_dimension"]
        self.assertEqual(set(values.values()), {"8"})

    def test_adjacent_support_and_lift(self) -> None:
        adjacent = self.result["adjacent"]
        self.assertEqual(adjacent["support_bounds"], [4, 8])
        self.assertEqual(adjacent["coefficient_sum"], 0)
        self.assertTrue(adjacent["uncentered_lift"])

    def test_nonadjacent_average(self) -> None:
        values = self.result["nonadjacent"]["outside_average_by_dimension"]
        self.assertEqual(set(values.values()), {"28/3"})

    def test_nonadjacent_support(self) -> None:
        self.assertEqual(self.result["nonadjacent"]["support_bounds"], [4, 9])

    def test_actual_switched_gram(self) -> None:
        switched = self.result["type_4_plus_2"]
        self.assertEqual(switched["weight"], 4)
        self.assertEqual(
            switched["switched_gram"],
            [
                [0, 1, 1, 1],
                [1, 0, 1, 1],
                [1, 1, 0, 1],
                [1, 1, 1, 0],
            ],
        )

    def test_complete_conic(self) -> None:
        frame = self.result["plane_frame"]
        self.assertEqual(
            (frame["plane_points"], frame["conic_points"], frame["complement_points"]),
            (13, 4, 9),
        )

    def test_frame_cancellation(self) -> None:
        frame = self.result["plane_frame"]
        self.assertEqual(
            frame["conic_frame"], [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
        )
        self.assertEqual(
            frame["complement_frame"], [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        )
        self.assertEqual(frame["full_frame"], [[0] * 3 for _ in range(3)])

    def test_no_distinctness_inflation(self) -> None:
        self.assertFalse(self.result["indexing"]["distinct_relations_claimed"])


if __name__ == "__main__":
    unittest.main()

