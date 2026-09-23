from __future__ import annotations

import json
import unittest
from pathlib import Path

import exact_check


class LocalProjectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = exact_check.exact_results()

    def test_input_manifests(self) -> None:
        for relative, expected in exact_check.INPUT_MANIFESTS.items():
            self.assertEqual(exact_check.sha256(exact_check.ROOT / relative), expected)

    def test_forced_incidence(self) -> None:
        patterns = exact_check.forced_patterns()
        self.assertEqual(len(patterns), 87)
        self.assertEqual({size: [len(x) for x in patterns].count(size) for size in range(3)}, {0: 3, 1: 48, 2: 36})

    def test_primitive_q(self) -> None:
        data = self.result["incidence_lattice"]
        self.assertEqual(data["rank_Q_over_Q"], 13)
        self.assertEqual(data["primitive_minor_determinant"], 1)
        self.assertEqual(data["smith_invariant_factors_Q"], [1] * 13)

    def test_lambda_discriminant(self) -> None:
        data = self.result["incidence_lattice"]
        self.assertEqual(data["Lambda_rank"], 74)
        self.assertEqual(data["Lambda_gram_determinant"], 2**22 * 3**10 * 5**2)

    def test_witt_type_is_nonsplit(self) -> None:
        data = self.result["mod_seven_orthogonal_space"]
        self.assertEqual(data["gram_determinant_mod_7"], 4)
        self.assertTrue(data["gram_determinant_square"])
        self.assertEqual(data["type"], "O^-(74,7)")
        self.assertEqual(data["witt_index"], 36)

    def test_projector_dimensions(self) -> None:
        data = self.result["local_projector"]
        self.assertEqual(data["identity"], "B^2=7B")
        self.assertEqual((data["rational_rank"], data["rational_nullity"]), (42, 32))
        self.assertEqual(data["motif_block_determinant_mod_7"], 1)

    def test_rank_transfer(self) -> None:
        data = self.result["rank_transfer"]
        self.assertEqual(data["local_rows"], list(range(16, 31, 2)))
        self.assertEqual(data["identity"], "rank_F7(B|Lambda)=r-12")

    def test_smith_rows(self) -> None:
        rows = self.result["smith_and_index_consequences"]["rows"]
        self.assertEqual(len(rows), 8)
        for row in rows:
            k = row["local_rank_k"]
            self.assertEqual(row["snf_nonzero_factors"], {"1": k, "7": 42 - k})
            self.assertFalse(row["excluded"])

    def test_archived_results_match(self) -> None:
        path = Path(__file__).with_name("exact-results.json")
        if path.exists():
            archived = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(archived, self.result)


if __name__ == "__main__":
    unittest.main()
