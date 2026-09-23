#!/usr/bin/env python3
"""Focused unit tests for the independent Wave 19 closure verifier."""

from __future__ import annotations

from fractions import Fraction
import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).with_name("independent_closure_verifier.py")
SPEC = importlib.util.spec_from_file_location("independent_closure_verifier", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


class StrictInputTests(unittest.TestCase):
    def test_k4_graph6(self) -> None:
        graph = verifier.strict_decode_graph6(b"C~", expected_order=4)
        self.assertEqual(len(verifier.edges(graph)), 6)
        self.assertEqual({row.bit_count() for row in graph}, {3})

    def test_graph6_rejects_wrong_length_padding_and_bytes(self) -> None:
        for record in (b"", b"C", b"C~?", b"C\x7f"):
            with self.subTest(record=record):
                with self.assertRaises(ValueError):
                    verifier.strict_decode_graph6(record)

    def test_duplicate_json_keys_rejected(self) -> None:
        with self.assertRaises(ValueError):
            verifier.strict_json_bytes(b'{"x":1,"x":2}')


class CombinatorialTests(unittest.TestCase):
    def test_opposite_path_cycle_finder_on_c6(self) -> None:
        rows = [0] * 6
        for left in range(6):
            right = (left + 1) % 6
            rows[left] |= 1 << right
            rows[right] |= 1 << left
        self.assertEqual(
            verifier.six_cycle_masks_by_opposite_paths(tuple(rows)),
            ((1 << 6) - 1,),
        )

    def test_all_nine_z_types(self) -> None:
        examples = (
            (),
            ((0, 1),),
            ((0, 1), (1, 2)),
            ((0, 1), (2, 3)),
            ((0, 1), (0, 2), (0, 3)),
            ((0, 1), (1, 2), (0, 2)),
            ((0, 1), (1, 2), (2, 3)),
            ((0, 1), (1, 2), (3, 4)),
            ((0, 1), (2, 3), (4, 5)),
        )
        self.assertEqual(
            len({verifier.z_abstract_type(selected) for selected in examples}),
            9,
        )

    def test_m27_cubic_census(self) -> None:
        result = verifier.m27_cubic_six_audit()
        self.assertEqual(result["labeled_cubic_graph_count"], 70)
        self.assertEqual(result["labeled_K3,3_count"], 10)
        self.assertEqual(result["labeled_prism_count"], 60)


class ExactLinearAlgebraTests(unittest.TestCase):
    def test_rank_and_kernel(self) -> None:
        matrix = ((1, 2, 3), (2, 4, 6), (0, 1, 1))
        self.assertEqual(verifier.fraction_echelon_rank(matrix), 2)
        kernel = verifier.kernel_basis_independent(matrix)
        self.assertEqual(len(kernel), 1)
        for vector in kernel:
            self.assertTrue(
                all(
                    sum(Fraction(entry) * coordinate for entry, coordinate in zip(row, vector))
                    == 0
                    for row in matrix
                )
            )

    def test_exact_psd_controls(self) -> None:
        self.assertTrue(verifier.psd_by_exact_ldl(((2, 1), (1, 2))))
        self.assertTrue(verifier.psd_by_exact_ldl(((0, 0), (0, 3))))
        self.assertFalse(verifier.psd_by_exact_ldl(((1, 2), (2, 1))))
        self.assertFalse(verifier.psd_by_exact_ldl(((0, 1), (1, 0))))

    def test_farkas_accept_and_reject(self) -> None:
        gram = ((1, 1), (1, 1))
        supports = (1, 2)
        target, scores = verifier.farkas_check(
            supports, gram, {(0, 1): -1}
        )
        self.assertEqual(target, -1)
        self.assertEqual(scores, {0: 2})
        with self.assertRaises(AssertionError):
            verifier.farkas_check(supports, gram, {(0, 1): 1})


class ReleaseTests(unittest.TestCase):
    def test_v3_release_authentication(self) -> None:
        manifest = verifier.authenticate_release()
        self.assertEqual(manifest["schema_version"], 3)


if __name__ == "__main__":
    unittest.main()
