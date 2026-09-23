from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave54_centered_enumerator", HERE / "exact_check.py"
)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class CenteredEnumeratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_result()

    def test_candidate_support_and_size(self) -> None:
        self.assertEqual(
            self.result["primal_enumerator_nonzero"],
            {
                "0": 1,
                "18": 2,
                "144": 53_316,
                "153": 19_798,
                "159": 98_496,
                "162": 5_072,
                "198": 462,
            },
        )
        self.assertEqual(
            self.result["primal_moments"]["word_count"], 3**11
        )
        self.assertEqual(self.result["dual_word_count"], 3**220)

    def test_every_exact_gate_passes(self) -> None:
        self.assertTrue(all(self.result["checks"].values()))
        self.assertEqual(
            self.result["exact_replay"]["divisibility_failure_count"], 0
        )

    def test_projective_and_recorded_dual_constraints(self) -> None:
        dual = self.result["dual_selected_coefficients"]
        self.assertEqual(dual["0"], 1)
        self.assertEqual(dual["1"], 0)
        self.assertEqual(dual["2"], 0)
        for weight, lower in CHECK.DUAL_LOWER_BOUNDS.items():
            self.assertGreaterEqual(dual[str(weight)], lower)

    def test_hostile_size_preserving_mutation_is_rejected(self) -> None:
        mutated = copy.deepcopy(CHECK.PRIMAL_ENUMERATOR)
        mutated[144] -= 2
        mutated[147] = 2
        with self.assertRaises(AssertionError):
            CHECK.build_result(mutated)

    def test_krawtchouk_base_rows(self) -> None:
        table = CHECK.krawtchouk_table()
        self.assertTrue(all(value == 1 for value in table[0]))
        self.assertEqual(table[1][0], 462)
        self.assertEqual(table[1][231], -231)

    def test_candidate_hash_is_stable(self) -> None:
        self.assertEqual(
            self.result["candidate_sha256"],
            CHECK.sha256_bytes(
                CHECK.canonical_bytes(
                    self.result["primal_enumerator_nonzero"]
                )
            ),
        )


if __name__ == "__main__":
    unittest.main()
