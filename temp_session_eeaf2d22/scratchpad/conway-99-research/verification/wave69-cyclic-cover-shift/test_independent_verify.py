"""Hostile tests for the independent Wave 69 verifier."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave69_independent", HERE / "independent_verify.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load independent verifier")
subject = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(subject)


EXPECTED_SHAPES = {
    0: (
        (0, 0, 2, 2, 2, 2, 3, 3),
        (0, 1, 1, 1, 2, 3, 3, 3),
        (0, 1, 1, 2, 2, 2, 2, 4),
        (1, 1, 1, 1, 1, 2, 3, 4),
    ),
    2: (
        (0, 0, 1, 1, 2, 2, 3, 3),
        (0, 1, 1, 1, 1, 2, 2, 4),
    ),
    4: ((1, 1, 1, 1, 1, 1, 2, 2),),
}


class AlgebraTests(unittest.TestCase):
    def test_rational_representation_forces_144(self) -> None:
        self.assertEqual(subject.quotient_spectrum(), {14: 1, 3: 4, -4: 4})

    def test_exactly_seven_row_shapes(self) -> None:
        self.assertEqual(subject.derive_row_shapes(), EXPECTED_SHAPES)
        for diagonal, shapes in EXPECTED_SHAPES.items():
            for shape in shapes:
                self.assertEqual(sum(shape), 14 - diagonal)
                self.assertEqual(
                    sum(value * value for value in shape),
                    34 - diagonal * diagonal - diagonal,
                )

    def test_labeled_template_counts(self) -> None:
        self.assertEqual(
            {key: len(value) for key, value in subject.row_templates().items()},
            {0: 2716, 2: 3360, 4: 28},
        )

    def test_exactly_three_sorted_diagonal_cases(self) -> None:
        self.assertEqual(
            subject.derive_diagonal_cases(),
            (
                (0, 0, 0, 0, 0, 0, 2, 4, 4),
                (0, 0, 0, 0, 0, 2, 2, 2, 4),
                (0, 0, 0, 0, 2, 2, 2, 2, 2),
            ),
        )

    def test_sorted_diagonal_is_only_simultaneous_relabeling(self) -> None:
        matrix = [
            [4, 7, 8],
            [7, 0, 9],
            [8, 9, 2],
        ]
        permutation = sorted(range(3), key=lambda index: matrix[index][index])
        relabeled = [
            [matrix[old_i][old_j] for old_j in permutation]
            for old_i in permutation
        ]
        self.assertEqual([relabeled[i][i] for i in range(3)], [0, 2, 4])
        self.assertEqual(relabeled[0][1], relabeled[1][0])

    def test_direct_validator_rejects_near_miss(self) -> None:
        matrix = [[0] * 9 for _ in range(9)]
        self.assertFalse(subject.validate_quotient(matrix))


class ScopeAndFourierTests(unittest.TestCase):
    def test_group_order_99_audit(self) -> None:
        audit = subject.abelian_group_and_fourier_audit()
        self.assertTrue(audit["all_groups_of_order_99_abelian"])
        self.assertEqual(audit["conjugation_image_order"], 1)
        self.assertEqual(
            audit["group_isomorphism_types"], ["C99", "C3xC3xC11"]
        )

    def test_fourier_values_are_rational_nonintegers(self) -> None:
        audit = subject.abelian_group_and_fourier_audit()
        for record in audit["forced_S_X_values"].values():
            self.assertNotEqual(record["numerator"] % record["denominator"], 0)

    def test_wave72_must_be_verified(self) -> None:
        source = json.loads(
            (
                HERE.parent
                / "wave72-order11-automorphism"
                / "independent-results.json"
            ).read_text(encoding="utf-8")
        )
        source["claim_label"] = "DERIVED"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mutated.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaises(AssertionError):
                subject.load_verified_wave72(path)


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        discovery = json.loads(
            (
                HERE.parent.parent
                / "attempts"
                / "wave69-cyclic-cover-shift"
                / "exact-results.json"
            ).read_text(encoding="ascii")
        )
        cls.discovery = discovery

    def test_label_complete_tree_has_no_canonical_rejection(self) -> None:
        for record in self.discovery["searches"]["unpruned"]:
            self.assertFalse(
                any(record["canonical_rejections_by_depth"].values())
            )

    def test_all_searches_have_zero_solutions(self) -> None:
        for mode in ("canonical", "unpruned"):
            self.assertEqual(
                [record["solutions"] for record in self.discovery["searches"][mode]],
                [0, 0, 0],
            )

    def test_canonical_is_not_the_proof_basis(self) -> None:
        canonical_nodes = sum(
            record["nodes"] for record in self.discovery["searches"]["canonical"]
        )
        unpruned_nodes = sum(
            record["nodes"] for record in self.discovery["searches"]["unpruned"]
        )
        self.assertLess(canonical_nodes, unpruned_nodes)
        self.assertEqual(unpruned_nodes, 1_108_533)

    def test_transcript_mutation_is_detected(self) -> None:
        independent_path = HERE / "independent-results.json"
        if not independent_path.exists():
            self.skipTest("independent result not generated yet")
        independent = json.loads(independent_path.read_text(encoding="ascii"))
        discovery_path = (
            HERE.parent.parent
            / "attempts"
            / "wave69-cyclic-cover-shift"
            / "exact-results.json"
        )
        independent["searches"]["unpruned"][0]["transcript_sha256"] = "0" * 64
        comparison = subject.compare_with_discovery(independent, discovery_path)
        self.assertGreater(comparison["mismatches"], 0)
        telemetry = [
            record
            for record in comparison["comparisons"]
            if record["kind"] == "search_telemetry"
            and record["mode"] == "unpruned"
            and record["diagonal"] == [0, 0, 0, 0, 0, 0, 2, 4, 4]
        ]
        self.assertEqual(
            telemetry[0]["different_fields"], ["transcript_sha256"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
