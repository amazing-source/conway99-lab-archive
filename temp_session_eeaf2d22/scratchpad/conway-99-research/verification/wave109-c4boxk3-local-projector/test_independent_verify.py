from __future__ import annotations

import json
import unittest
from pathlib import Path

import independent_verify


class IndependentWave109Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = independent_verify.exact_verification()

    def test_frozen_manifest(self) -> None:
        frozen = self.result["frozen_discovery_inputs"]
        self.assertEqual(
            frozen[
                "attempts/wave109-c4boxk3-local-projector/"
                "package-manifest.sha256"
            ],
            "6d54d48dbb6b1ffd3f7da845792fc12ee490471c02cc8137ebd1b03c21f5347e",
        )

    def test_primitive_incidence_lattice(self) -> None:
        data = self.result["incidence_lattice"]
        self.assertEqual(data["rank_Q_over_Q"], 13)
        self.assertEqual(abs(data["unit_minor_determinant"]), 1)
        self.assertEqual(data["smith_invariant_factors_Q"], [1] * 13)
        self.assertEqual(data["Lambda_rank"], 74)

    def test_exact_lattice_determinant(self) -> None:
        data = self.result["incidence_lattice"]
        expected = 2**22 * 3**10 * 5**2
        self.assertEqual(data["det_QtQ"], expected)
        self.assertEqual(data["det_Lambda"], expected)

    def test_nonsplit_orthogonal_type(self) -> None:
        data = self.result["orthogonal_space_mod_7"]
        self.assertEqual(data["determinant_mod_7"], 4)
        self.assertEqual(data["determinant_legendre_symbol"], 1)
        self.assertEqual(data["split_class_legendre_symbol"], -1)
        self.assertEqual((data["type"], data["witt_index"]), ("O^-(74,7)", 36))

    def test_conditional_projector(self) -> None:
        data = self.result["conditional_projector"]
        self.assertTrue(data["D_preserves_Lambda"])
        self.assertTrue(data["B_squared_equals_7B"])
        self.assertTrue(data["image_mod_7_totally_isotropic"])
        self.assertEqual(
            (
                data["rank_B_on_Lambda_over_Q"],
                data["nullity_B_on_Lambda_over_Q"],
            ),
            (42, 32),
        )

    def test_full_rank_transfer_table(self) -> None:
        rows = self.result["rank_transfer"]["rows"]
        self.assertEqual(
            [row["global_rank_r"] for row in rows],
            list(range(28, 43, 2)),
        )
        self.assertEqual(
            [row["local_rank_k"] for row in rows],
            list(range(16, 31, 2)),
        )
        self.assertTrue(all(not row["excluded"] for row in rows))

    def test_smith_index_rows(self) -> None:
        for row in self.result["rank_transfer"]["rows"]:
            k = row["local_rank_k"]
            self.assertEqual(row["snf_nonzero"], {"1": k, "7": 42 - k})
            self.assertEqual(row["residual_space"], f"O^-({74 - 2*k},7)")

    def test_no_promoted_global_claim(self) -> None:
        wall = self.result["status_wall"]
        self.assertEqual(wall["Conway_99"], "UNKNOWN")
        self.assertEqual(wall["full_extension"], "UNKNOWN")
        self.assertEqual(wall["rank_rows_excluded"], [])

    def test_archived_results(self) -> None:
        archived = json.loads(
            Path(__file__).with_name("exact-results.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(archived, self.result)


if __name__ == "__main__":
    unittest.main()
