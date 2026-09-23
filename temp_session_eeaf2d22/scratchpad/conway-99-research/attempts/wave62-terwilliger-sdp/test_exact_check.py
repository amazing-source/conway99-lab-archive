import json
import unittest
from fractions import Fraction
from pathlib import Path

import exact_check


HERE = Path(__file__).resolve().parent


class SignedEdgeSchemeTests(unittest.TestCase):
    def test_84_labels_and_orbit_valencies(self):
        vertices = exact_check.labels()
        self.assertEqual(len(vertices), 84)
        self.assertEqual(len(set(vertices)), 84)
        observed = [
            sum(exact_check.relation(vertices[0], v) == r for v in vertices)
            for r in range(6)
        ]
        self.assertEqual(observed, [1, 2, 1, 20, 20, 40])

    def test_exact_association_scheme(self):
        result = exact_check.verify_association_scheme()
        self.assertEqual(result["multiplicities"], [1, 6, 7, 14, 21, 35])
        self.assertEqual(sum(result["multiplicities"]), 84)

    def test_endpoint_orbit_identity(self):
        for y in range(43):
            counts = exact_check.endpoint_edge_counts(y)
            self.assertEqual(sum(counts), 504)
            self.assertEqual(2 * counts[2] + counts[4], 84)

    def test_spectral_projectors_survive_all_integer_y(self):
        for y in range(43):
            data = exact_check.spectral_projector_data(Fraction(y))
            self.assertEqual(data["b_bar_eigenvalues"][0:3], ["12", "-2", "0"])
            self.assertEqual(data["p3_trace"], "40")

    def test_bounded_schur_scan(self):
        scan = exact_check.hadamard_schur_scan(8)
        self.assertEqual(scan["negative_eigenvalues"], 0)
        self.assertEqual(
            scan["endpoint_block_inequalities"], 12 * scan["averaged_matrices"]
        )

    def test_frozen_result(self):
        frozen = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
        self.assertEqual(frozen, exact_check.build_result(24))


if __name__ == "__main__":
    unittest.main()
