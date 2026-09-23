from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave27_a2free_independent",
    HERE / "independent_check.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load independent_check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave27A2FreeIndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = CHECK.independent_results()
        cls.built = cls.results["construction"]

    def test_01_preinspection_hash_freeze(self) -> None:
        self.assertEqual(
            self.results["frozen_discovery"]["sha256"],
            CHECK.DISCOVERY_HASHES,
        )
        for relative, expected in CHECK.DISCOVERY_HASHES.items():
            self.assertEqual(CHECK.sha256_file(CHECK.ROOT / relative), expected)
        lines = (
            HERE / "preinspection-freeze.sha256"
        ).read_text(encoding="utf-8").splitlines()
        parsed = {
            line.split("  ", 1)[1]: line.split("  ", 1)[0]
            for line in lines
            if line and not line.startswith("#")
        }
        self.assertEqual(parsed, CHECK.DISCOVERY_HASHES)

    def test_02_cartan_forms_rebuilt_from_edges(self) -> None:
        self.assertEqual(CHECK.determinant(self.built["E8"]), 1)
        self.assertEqual(CHECK.determinant(self.built["E6"]), 3)
        self.assertTrue(CHECK.is_even_integral_form(self.built["E8"]))
        self.assertTrue(CHECK.is_even_integral_form(self.built["E6"]))
        self.assertTrue(CHECK.is_positive_definite(self.built["E8"]))
        self.assertTrue(CHECK.is_positive_definite(self.built["E6"]))

    def test_03_e6_rank_one_projector(self) -> None:
        self.assertEqual(self.built["seed"], [1, 0, -1, 0, 0, 1])
        self.assertEqual(self.built["seed_dual_norm"], "4/3")
        projector = [
            [Fraction(value) for value in row]
            for row in self.built["projector"]
        ]
        self.assertEqual(CHECK.rank_exact(projector), 1)
        self.assertTrue(
            CHECK.matrix_equal(CHECK.matmul(projector, projector), projector)
        )
        self.assertTrue(
            CHECK.matrix_equal(
                CHECK.matmul(self.built["E6"], self.built["Q6"]),
                self.built["B6"],
            )
        )

    def test_04_local_q6_and_b6(self) -> None:
        q6 = self.built["Q6"]
        b6 = self.built["B6"]
        self.assertEqual(CHECK.determinant(q6), 3)
        self.assertTrue(CHECK.is_even_integral_form(q6))
        self.assertTrue(CHECK.is_positive_definite(q6))
        self.assertEqual(CHECK.trace(b6), 14)
        self.assertEqual(CHECK.determinant(b6), 9)
        self.assertEqual(CHECK.rank_exact(CHECK.matsub(b6, CHECK.identity(6))), 1)
        self.assertTrue(all(
            (b6[i][j] - int(i == j)) % 2 == 0
            for i in range(6)
            for j in range(6)
        ))

    def test_05_full_form_invariants(self) -> None:
        invariants = self.results["matrix_invariants"]
        self.assertEqual(invariants["S"]["determinant"], 9)
        self.assertEqual(invariants["Q"]["determinant"], 9)
        self.assertEqual(invariants["G"]["determinant"], 21 ** 44 // 9)
        for name in ("S", "Q", "G"):
            self.assertEqual(invariants[name]["rank"], 44)
            self.assertTrue(invariants[name]["symmetric"])
            self.assertTrue(invariants[name]["integral"])
            self.assertTrue(invariants[name]["even"])
            self.assertTrue(invariants[name]["positive_definite"])

    def test_06_coupled_identities(self) -> None:
        s, q, g, b = (
            self.built[name] for name in ("S", "Q", "G", "B")
        )
        self.assertTrue(CHECK.matrix_equal(CHECK.matmul(s, q), b))
        self.assertTrue(
            CHECK.matrix_equal(
                CHECK.matmul(s, g),
                CHECK.matscale(21, CHECK.identity(44)),
            )
        )
        self.assertTrue(
            CHECK.matrix_equal(CHECK.matmul(g, b), CHECK.matscale(21, q))
        )
        self.assertTrue(
            CHECK.matrix_equal(
                CHECK.matmul(CHECK.transpose(b), g),
                CHECK.matmul(g, b),
            )
        )

    def test_07_b_parity_spectrum_and_moments(self) -> None:
        row = self.results["matrix_invariants"]["B"]
        self.assertEqual(row["determinant"], 81)
        self.assertEqual(row["trace"], 60)
        self.assertEqual(row["trace_square"], 204)
        self.assertEqual(row["spectrum"], {"1": 42, "9": 2})
        self.assertTrue(row["congruent_to_identity_mod_2"])
        self.assertTrue(row["G_self_adjoint"])
        self.assertFalse(row["euclidean_symmetric"])

    def test_08_c_integrality_rank_and_moments(self) -> None:
        c = self.built["C"]
        row = self.results["matrix_invariants"]["C"]
        self.assertTrue(all(isinstance(value, int) for line in c for value in line))
        self.assertEqual(row["rank"], 2)
        self.assertEqual(row["trace"], 8)
        self.assertEqual(row["trace_square"], 32)
        self.assertTrue(
            CHECK.matrix_equal(CHECK.matmul(c, c), CHECK.matscale(4, c))
        )

    def test_09_unique_block_root_enumerations(self) -> None:
        blocks = self.results["root_and_minimum_certificates"]["unique_blocks"]
        expected = {
            "S_E8": (240, [240]),
            "S_E6": (72, [72]),
            "Q_E8_inverse": (240, [240]),
            "Q_Q6": (72, [72]),
        }
        for name, (count, components) in expected.items():
            self.assertEqual(blocks[name]["root_count"], count)
            self.assertEqual(blocks[name]["component_sizes"], components)
            self.assertEqual(
                blocks[name]["root_vectors_sha256"],
                CHECK.canonical_sha256(
                    [tuple(vector) for vector in blocks[name]["root_vectors"]]
                ),
            )

    def test_10_full_root_components_exclude_a2_summand(self) -> None:
        forms = self.results["root_and_minimum_certificates"]["full_forms"]
        for name in ("S", "Q"):
            self.assertEqual(forms[name]["minimum"], 2)
            self.assertEqual(forms[name]["root_count"], 1104)
            self.assertEqual(
                forms[name]["component_sizes"],
                [240, 240, 240, 240, 72, 72],
            )
            self.assertNotIn(6, forms[name]["component_sizes"])
            self.assertFalse(forms[name]["has_orthogonal_A2_direct_summand"])
        self.assertTrue(
            self.results["root_and_minimum_certificates"][
                "embedded_A2_control"
            ]["present"]
        )

    def test_11_e6_dual_and_g_minima(self) -> None:
        blocks = self.results["root_and_minimum_certificates"]["unique_blocks"]
        self.assertEqual(blocks["E6_dual"]["minimum"], "4/3")
        self.assertEqual(blocks["E6_dual"]["minimal_vector_count"], 54)
        self.assertEqual(blocks["G_E6"]["minimum"], "28/1")
        self.assertEqual(blocks["G_E6"]["minimal_vector_count"], 54)
        self.assertEqual(blocks["G_E8"]["minimum"], "42/1")
        self.assertEqual(blocks["G_E8"]["minimal_vector_count"], 240)
        self.assertEqual(
            self.results["root_and_minimum_certificates"]["full_forms"]["G"][
                "minimum"
            ],
            28,
        )

    def test_12_discriminant_groups(self) -> None:
        groups = self.results["discriminant_groups"]
        self.assertEqual(groups["S"]["group"], "(Z/3Z)^2")
        self.assertEqual(groups["Q"]["group"], "(Z/3Z)^2")
        self.assertEqual(
            groups["G"]["group"],
            "(Z/7Z)^2 direct_sum (Z/21Z)^42",
        )
        self.assertEqual(groups["S"]["rank_mod_3"], 42)
        self.assertEqual(groups["Q"]["rank_mod_3"], 42)
        self.assertEqual(groups["G"]["rank_mod_3"], 2)
        self.assertEqual(groups["G"]["rank_mod_7"], 0)
        for name in ("S", "Q", "G"):
            product = 1
            for value in groups[name]["smith_invariants"]:
                product *= value
            self.assertEqual(product, groups[name]["determinant"])

    def test_13_independent_rebuild_matches_submitted_matrices(self) -> None:
        comparison = self.results["submitted_matrix_comparison"]
        self.assertEqual(
            set(comparison),
            {"S", "Q", "G", "B", "C", "E6", "E8", "Q6", "B6"},
        )
        self.assertTrue(all(comparison.values()))

    def test_14_scope_and_status_walls(self) -> None:
        status = self.results["status"]
        self.assertEqual(status["verdict"], "PASS_SCOPED_CANDIDATE")
        self.assertEqual(status["verified_object_label"], "CANDIDATE")
        self.assertEqual(status["projector_or_schur_origin"], "NOT_ESTABLISHED")
        self.assertEqual(status["n3_708"], "UNKNOWN")
        self.assertEqual(status["conway_99"], "UNKNOWN")
        not_claimed = " ".join(self.results["scope"]["not_verified_or_claimed"])
        self.assertIn("No 231-row projector frame.", not_claimed)
        self.assertIn("No Schur-square", not_claimed)
        self.assertIn("No graph", not_claimed)

    def test_15_hostile_mutation_breaks_endpoint(self) -> None:
        mutated = [row[:] for row in self.built["B"]]
        mutated[32][32] += 2
        self.assertFalse(
            CHECK.matrix_equal(
                CHECK.matmul(self.built["S"], self.built["Q"]),
                mutated,
            )
        )
        self.assertNotEqual(CHECK.trace(mutated), 60)

    def test_16_output_is_deterministic_ascii_lf_json(self) -> None:
        expected = (
            json.dumps(
                self.results,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            + "\n"
        ).encode("ascii")
        actual = (HERE / "independent-results.json").read_bytes()
        self.assertEqual(actual, expected)
        self.assertNotIn(b"\r", actual)


if __name__ == "__main__":
    unittest.main()
