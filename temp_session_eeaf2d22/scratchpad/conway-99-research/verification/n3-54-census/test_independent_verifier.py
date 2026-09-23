"""Hostile unit tests for the independent Wave 17 census verifier."""

from __future__ import annotations

import gzip
import importlib.util
import itertools
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave17_census_independent_verifier", HERE / "independent_verifier.py"
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class StrictGraph6Tests(unittest.TestCase):
    def test_triangle_record(self) -> None:
        rows = VERIFY.decode_short_graph6(b"Bw")
        self.assertEqual(VERIFY.graph_edges(rows), ((0, 1), (0, 2), (1, 2)))

    def test_rejects_truncation_and_trailing_data(self) -> None:
        with self.assertRaisesRegex(ValueError, "truncated|trailing"):
            VERIFY.decode_short_graph6(b"B")
        with self.assertRaisesRegex(ValueError, "truncated|trailing"):
            VERIFY.decode_short_graph6(b"Bw?")

    def test_rejects_noncanonical_padding(self) -> None:
        # n=3 needs three bits; "w" is 111000, while "x" is 111001.
        with self.assertRaisesRegex(ValueError, "padding"):
            VERIFY.decode_short_graph6(b"Bx")

    def test_rejects_bad_byte_and_header(self) -> None:
        with self.assertRaisesRegex(ValueError, "63..126"):
            VERIFY.decode_short_graph6(b"B\x00")
        with self.assertRaisesRegex(ValueError, "header"):
            VERIFY.decode_short_graph6(b">>graph6<<Bw")


class CatalogTamperingTests(unittest.TestCase):
    def test_compressed_tampering_is_detected_before_use(self) -> None:
        original = VERIFY.CATALOGS[12]
        clean = gzip.compress(b"A?\n", mtime=0)
        VERIFY.CATALOGS[12] = {
            **original,
            "compressed_bytes": len(clean),
            "compressed_sha256": VERIFY.sha256_bytes(clean),
            "decompressed_bytes": 3,
            "decompressed_sha256": VERIFY.sha256_bytes(b"A?\n"),
            "records": 1,
        }
        try:
            altered = bytearray(clean)
            altered[-1] ^= 1
            with self.assertRaisesRegex(AssertionError, "SHA-256|gzip"):
                VERIFY.validate_catalog_blob(12, bytes(altered))
        finally:
            VERIFY.CATALOGS[12] = original

    def test_record_count_tampering_is_detected(self) -> None:
        original = VERIFY.CATALOGS[12]
        clean = gzip.compress(b"A?\n", mtime=0)
        VERIFY.CATALOGS[12] = {
            **original,
            "compressed_bytes": len(clean),
            "compressed_sha256": VERIFY.sha256_bytes(clean),
            "decompressed_bytes": 3,
            "decompressed_sha256": VERIFY.sha256_bytes(b"A?\n"),
            "records": 2,
        }
        try:
            with self.assertRaisesRegex(AssertionError, "record count"):
                VERIFY.validate_catalog_blob(12, clean)
        finally:
            VERIFY.CATALOGS[12] = original


class CandidateCompatibilityTests(unittest.TestCase):
    def test_disjoint_components_make_a_candidate(self) -> None:
        graph = VERIFY.graph_from_edges(4, ((0, 1), (2, 3)))
        candidates = VERIFY.compatible_supports(graph)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0][:2], (0, 1))
        self.assertEqual(candidates[0][2].bit_count(), 4)

    def test_mandatory_k_rectangle_is_rejected(self) -> None:
        graph = VERIFY.graph_from_edges(4, ((0, 1), (1, 2), (2, 3)))
        points = VERIFY.graph_edges(graph)
        outer_indices = (points.index((0, 1)), points.index((2, 3)))
        candidate_pairs = {candidate[:2] for candidate in VERIFY.compatible_supports(graph)}
        self.assertNotIn(outer_indices, candidate_pairs)

    def test_k33_has_no_internal_compatible_support(self) -> None:
        graph = VERIFY.graph_from_edges(6, VERIFY.k33_edges())
        self.assertEqual(VERIFY.compatible_supports(graph), ())


class ColumnKernelTests(unittest.TestCase):
    def test_column_kernel_matches_tiny_bruteforce(self) -> None:
        # Equations x0+x1=0 and x1+x2=0, stored by columns.
        columns = (0b01, 0b11, 0b10)
        rank, basis = VERIFY.column_kernel_basis(columns)
        self.assertEqual(rank, 2)
        self.assertEqual(len(basis), 1)
        VERIFY.assert_kernel_basis(columns, basis)
        actual = {
            vector
            for vector in range(1 << len(columns))
            if VERIFY.syndrome_of_vector(columns, vector) == 0
        }
        generated = {
            sum(
                basis[index]
                for index in range(len(basis))
                if coefficient >> index & 1
            )
            for coefficient in range(1 << len(basis))
        }
        self.assertEqual(actual, {0, 0b111})
        self.assertEqual(generated, actual)

    def test_many_tiny_matrices_against_bruteforce(self) -> None:
        for variable_count in range(1, 6):
            possible_columns = range(8)
            for columns in itertools.islice(
                itertools.product(possible_columns, repeat=variable_count), 80
            ):
                rank, basis = VERIFY.column_kernel_basis(columns)
                VERIFY.assert_kernel_basis(columns, basis)
                brute = sum(
                    VERIFY.syndrome_of_vector(columns, vector) == 0
                    for vector in range(1 << variable_count)
                )
                self.assertEqual(brute, 1 << len(basis))
                self.assertEqual(rank + len(basis), variable_count)

    def test_rejects_tampered_kernel_vector(self) -> None:
        with self.assertRaisesRegex(AssertionError, "nonzero syndrome"):
            VERIFY.assert_kernel_basis((0b1,), (0b1,))

    def test_degree_two_enumeration_positive_control(self) -> None:
        examined, passing = VERIFY.enumerate_kernel_degree_two(
            (0b11,), (0b11, 0b11)
        )
        self.assertEqual((examined, passing), (2, 1))

    def test_row_commitment_rank_agrees(self) -> None:
        columns = (0b01, 0b11, 0b10)
        rows = VERIFY.rows_from_columns(columns, 2)
        reduced, pivots, basis = VERIFY.low_pivot_row_commitments(rows, 3)
        self.assertEqual(len(reduced), 2)
        self.assertEqual(len(pivots), 2)
        self.assertEqual(basis, (0b111,))


class MixedCountingTests(unittest.TestCase):
    def test_exact_boundary_and_strict_obstruction(self) -> None:
        obstructed, cross, internal = VERIFY.mixed_degree_count_obstruction(
            9, 18, 0, 8
        )
        self.assertTrue(obstructed)
        self.assertEqual((cross, internal), (18, 9))
        obstructed, _, _ = VERIFY.mixed_degree_count_obstruction(9, 18, 0, 9)
        self.assertFalse(obstructed)

    def test_internal_first_candidate_defeats_this_count_only(self) -> None:
        obstructed, cross, internal = VERIFY.mixed_degree_count_obstruction(
            9, 18, 1, 0
        )
        self.assertFalse(obstructed)
        self.assertEqual((cross, internal), (-1, -1))


class CommitmentTests(unittest.TestCase):
    def test_exact_compare_rejects_mutation(self) -> None:
        with self.assertRaisesRegex(AssertionError, "differs"):
            VERIFY.exact_equal({"rank": 1}, {"rank": 2}, "hostile mutation")


if __name__ == "__main__":
    unittest.main(verbosity=2)
