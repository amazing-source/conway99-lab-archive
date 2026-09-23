from __future__ import annotations

import importlib.util
import json
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave27_a2free_exact_check",
    HERE / "exact_check.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load exact_check.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave27A2FreeConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = CHECK.build_results()
        cls.matrices = cls.results["construction"]["matrices"]
        cls.blocks = cls.results["construction"]["blocks"]

    def test_01_frozen_public_base_and_inputs(self) -> None:
        frozen = self.results["frozen_inputs"]
        self.assertEqual(
            frozen["public_base_commit"],
            "2ac11809fafee7ab752965ae49a96e922859b5ee",
        )
        self.assertEqual(frozen["sha256"], CHECK.INPUT_HASHES)
        for relative, expected in CHECK.INPUT_HASHES.items():
            self.assertEqual(CHECK.sha256_file(CHECK.ROOT / relative), expected)
        freeze_lines = (
            HERE / "input-freeze.sha256"
        ).read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            freeze_lines[0],
            "# public_base_commit "
            "2ac11809fafee7ab752965ae49a96e922859b5ee",
        )
        parsed = {
            line.split("  ", 1)[1]: line.split("  ", 1)[0]
            for line in freeze_lines[1:]
        }
        self.assertEqual(parsed, CHECK.INPUT_HASHES)

    def test_02_complete_matrix_dimensions_and_integrality(self) -> None:
        for name in ("S", "Q", "G", "B", "C"):
            matrix = self.matrices[name]
            self.assertEqual(len(matrix), 44, name)
            self.assertTrue(all(len(row) == 44 for row in matrix), name)
            self.assertTrue(
                all(isinstance(value, int) for row in matrix for value in row),
                name,
            )
            self.assertEqual(
                CHECK.matrix_sha256(matrix),
                self.results["matrix_invariants"][name][
                    "sha256_canonical_json"
                ],
            )

    def test_03_e6_coordinate_convention_and_projection(self) -> None:
        e6 = self.blocks["E6"]
        edges = {
            tuple(sorted((i, j)))
            for i in range(6)
            for j in range(i + 1, 6)
            if e6[i][j] == -1
        }
        self.assertEqual(
            edges,
            {(0, 1), (1, 2), (2, 3), (3, 4), (2, 5)},
        )
        self.assertEqual(self.blocks["E6_seed"], [1, 0, -1, 0, 0, 1])
        self.assertEqual(self.blocks["E6_seed_norm"], "4/3")
        p6 = [[Fraction(value) for value in row] for row in self.blocks["P6"]]
        self.assertTrue(CHECK.matrix_equal(CHECK.matmul(p6, p6), p6))
        self.assertEqual(CHECK.rank_exact(p6), 1)

    def test_04_e6_local_q_and_b_are_exact(self) -> None:
        q6 = self.blocks["Q6"]
        b6 = self.blocks["B6"]
        self.assertEqual(CHECK.determinant(q6), 3)
        self.assertTrue(CHECK.even_integral_form(q6))
        self.assertTrue(CHECK.positive_definite(q6))
        self.assertEqual(CHECK.trace(b6), 14)
        self.assertEqual(CHECK.determinant(b6), 9)
        self.assertTrue(
            all(
                (b6[i][j] - int(i == j)) % 2 == 0
                for i in range(6)
                for j in range(6)
            )
        )

    def test_05_coupled_matrix_identities(self) -> None:
        s, q, g, b = (
            self.matrices[name] for name in ("S", "Q", "G", "B")
        )
        self.assertTrue(CHECK.matrix_equal(CHECK.matmul(s, q), b))
        self.assertTrue(
            CHECK.matrix_equal(CHECK.matmul(s, g), CHECK.matscale(21, CHECK.identity(44)))
        )
        self.assertTrue(
            CHECK.matrix_equal(CHECK.matmul(g, b), CHECK.matscale(21, q))
        )
        self.assertTrue(
            CHECK.matrix_equal(CHECK.matmul(CHECK.transpose(b), g), CHECK.matmul(g, b))
        )

    def test_06_form_invariants(self) -> None:
        invariants = self.results["matrix_invariants"]
        self.assertEqual(invariants["S"]["determinant"], 9)
        self.assertEqual(invariants["Q"]["determinant"], 9)
        self.assertEqual(invariants["Q"]["determinant_mod_4"], 1)
        self.assertEqual(invariants["G"]["determinant"], 21 ** 44 // 9)
        for name in ("S", "Q", "G"):
            self.assertEqual(invariants[name]["rank"], 44)
            self.assertTrue(invariants[name]["symmetric"])
            self.assertTrue(invariants[name]["integral"])
            self.assertTrue(invariants[name]["even"])
            self.assertTrue(invariants[name]["positive_definite"])
            self.assertTrue(
                all(Fraction(value) > 0 for value in invariants[name]["ldl_pivots"])
            )

    def test_07_b_and_c_endpoint_moments(self) -> None:
        b_row = self.results["matrix_invariants"]["B"]
        c_row = self.results["matrix_invariants"]["C"]
        self.assertEqual(
            (b_row["determinant"], b_row["trace"], b_row["trace_square"]),
            (81, 60, 204),
        )
        self.assertTrue(b_row["G_self_adjoint"])
        self.assertTrue(b_row["congruent_to_identity_mod_2"])
        # General self-adjoint endomorphisms need not be symmetric in this
        # integral coordinate basis.  This is an active hostile check.
        self.assertFalse(b_row["euclidean_symmetric"])
        self.assertEqual(
            (c_row["rank"], c_row["trace"], c_row["trace_square"]),
            (2, 8, 32),
        )
        c = self.matrices["C"]
        self.assertTrue(
            CHECK.matrix_equal(CHECK.matmul(c, c), CHECK.matscale(4, c))
        )

    def test_08_complete_minimum_and_root_enumerations(self) -> None:
        certificates = self.results["root_and_minimum_certificates"]
        self.assertEqual(
            (
                certificates["S"]["minimum"],
                certificates["S"]["root_count"],
                certificates["S"]["nonorthogonality_component_sizes"],
            ),
            (2, 1104, [240, 240, 240, 240, 72, 72]),
        )
        self.assertEqual(
            (
                certificates["Q"]["minimum"],
                certificates["Q"]["root_count"],
                certificates["Q"]["nonorthogonality_component_sizes"],
            ),
            (2, 1104, [240, 240, 240, 240, 72, 72]),
        )
        self.assertEqual(
            (
                certificates["G"]["minimum"],
                certificates["G"]["minimal_vector_count"],
                certificates["G"]["root_count"],
            ),
            (28, 108, 0),
        )
        blocks = certificates["block_vector_certificates"]
        self.assertEqual(len(blocks["S_E8"]["root_vectors"]), 240)
        self.assertEqual(len(blocks["S_E6"]["root_vectors"]), 72)
        self.assertEqual(len(blocks["Q_E8_inverse"]["root_vectors"]), 240)
        self.assertEqual(len(blocks["Q_Q6"]["root_vectors"]), 72)
        self.assertEqual(len(blocks["G_G6"]["minimal_vectors"]), 54)

    def test_09_a2_subsystem_is_not_a2_direct_summand(self) -> None:
        certificates = self.results["root_and_minimum_certificates"]
        self.assertTrue(certificates["S"]["contains_embedded_A2_root_subsystems"])
        self.assertEqual(
            certificates["S"]["embedded_A2_control_gram"],
            [[2, -1], [-1, 2]],
        )
        for name in ("S", "Q", "G"):
            self.assertFalse(
                certificates[name]["has_orthogonal_A2_direct_summand"]
            )
        self.assertNotIn(
            6, certificates["S"]["nonorthogonality_component_sizes"]
        )
        self.assertNotIn(
            6, certificates["Q"]["nonorthogonality_component_sizes"]
        )

    def test_10_discriminant_groups(self) -> None:
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
            for invariant in groups[name]["smith_invariants"]:
                product *= invariant
            self.assertEqual(product, groups[name]["determinant"])

    def test_11_bounded_seed_search_and_restrictions(self) -> None:
        search = self.results["search"]
        self.assertTrue(search["complete_within_stated_box_and_ansatz"])
        self.assertFalse(search["classification_of_all_forms_or_Q"])
        self.assertIsNone(search["assumed_automorphism"])
        self.assertEqual(search["valid_sign_canonical_seed_count"], 27)
        self.assertIn(
            [1, 0, -1, 0, 0, 1],
            [row["seed"] for row in search["valid_sign_canonical_seeds"]],
        )
        self.assertIn("No cross-block Q entries are searched.", search["global_restrictions"])

    def test_12_hostile_coordinate_and_naive_q_controls(self) -> None:
        hostile = self.results["search"]["hostile_controls"]
        self.assertEqual(hostile["wrong_E6_coordinate_seed_norm"], "10/3")
        self.assertEqual(hostile["naive_Q_equals_S_traceB"], 252)
        self.assertNotEqual(
            hostile["naive_Q_equals_S_traceB"],
            hostile["required_traceB"],
        )

    def test_13_scope_and_status_walls(self) -> None:
        status = self.results["status"]
        conclusion = self.results["conclusion"]
        self.assertEqual(status["claim_label"], "CANDIDATE")
        self.assertEqual(status["independent_verification"], "PENDING")
        self.assertFalse(status["n3_708_excluded"])
        self.assertEqual(status["n3_708_status"], "UNKNOWN")
        self.assertEqual(status["conway_99_status"], "UNKNOWN")
        self.assertEqual(
            conclusion["naive_all_h9_forms_have_A2_summand"],
            "REFUTED_BY_EXPLICIT_FORM",
        )
        self.assertEqual(conclusion["abstract_h9_relaxation"], "STILL_SURVIVES")
        self.assertEqual(
            conclusion["projector_or_schur_origin_of_new_control"],
            "NOT_ESTABLISHED",
        )

    def test_14_mutating_b_breaks_the_coupled_identity(self) -> None:
        mutated = [row[:] for row in self.matrices["B"]]
        mutated[32][32] += 2
        self.assertFalse(
            CHECK.matrix_equal(
                CHECK.matmul(self.matrices["S"], self.matrices["Q"]),
                mutated,
            )
        )

    def test_15_exact_result_is_deterministic_lf_json(self) -> None:
        expected = (
            json.dumps(
                self.results,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            + "\n"
        ).encode("ascii")
        actual = (HERE / "exact-results.json").read_bytes()
        self.assertEqual(actual, expected)
        self.assertNotIn(b"\r", actual)


if __name__ == "__main__":
    unittest.main()
