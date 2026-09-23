"""Focused hostile tests for the independent Wave 17 census verifier."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave17_n3_54_verify_certificate", HERE / "verify_certificate.py"
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class CertificateTests(unittest.TestCase):
    def test_rref_and_kernel_basis(self) -> None:
        # x0+x1=0 and x1+x2=0 has kernel {000,111}.
        reduced, pivots, basis = VERIFY.reduced_kernel(
            ((1 << 0) | (1 << 1), (1 << 1) | (1 << 2)),
            3,
        )
        self.assertEqual(len(reduced), 2)
        self.assertEqual(pivots, (0, 1))
        self.assertEqual(basis, (0b111,))

    def test_kernel_enumeration_rejects_wrong_degree(self) -> None:
        examined, passing = VERIFY.enumerate_kernel(
            (0b111,),
            (0b001, 0b010, 0b100),
        )
        self.assertEqual(examined, 2)
        self.assertEqual(passing, 0)

    def test_kernel_enumeration_positive_control(self) -> None:
        examined, passing = VERIFY.enumerate_kernel(
            (0b0011, 0b1100),
            (0b1111,),
        )
        self.assertEqual(examined, 4)
        self.assertEqual(passing, 2)

    def test_exact_compare_rejects_mutation(self) -> None:
        with self.assertRaisesRegex(AssertionError, "differs"):
            VERIFY.exact_compare({"rank": 1}, {"rank": 2})

    def test_graph6_rejects_truncation(self) -> None:
        with self.assertRaisesRegex(ValueError, "truncated"):
            VERIFY.parse_graph6(b"Q")

    def test_catalog_metadata_is_frozen(self) -> None:
        self.assertEqual(VERIFY.CATALOGS[18]["records"], 455)
        self.assertEqual(VERIFY.CATALOGS[12]["records"], 2)
        self.assertEqual(
            VERIFY.CATALOGS[18]["compressed_sha256"],
            "95ff5ca833f3a1361d652e8f585d8aed21af61d73d135abf366570dcbddfcf7e",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
