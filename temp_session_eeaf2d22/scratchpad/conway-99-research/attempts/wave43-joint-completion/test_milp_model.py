from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import numpy as np


PACKAGE = Path(__file__).resolve().parent
if str(PACKAGE) not in sys.path:
    sys.path.insert(0, str(PACKAGE))
MODULE_PATH = PACKAGE / "solve_joint_milp.py"
SPEC = importlib.util.spec_from_file_location("wave43_joint_milp", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load Wave 43 MILP construction module")
MILP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MILP)


class SparseMilpModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = MILP.read_source(MILP.SOURCE)
        witness = source["rank_identity"]["minimum_witness"]
        cls.adjacency = MILP.adjacency_from_edges(witness["core_edges"])
        cls.gram = MILP.forced_gram(cls.adjacency)
        core_components = MILP.components(cls.adjacency)
        cls.pairs = tuple(
            MILP.fibre_pairs(fibre, cls.gram) for fibre in range(3)
        )
        cls.candidates = MILP.enumerate_candidates(
            cls.pairs,
            cls.gram,
            cls.adjacency,
            frozenset(core_components[0]),
        )
        cls.matrix, cls.targets = MILP.build_sparse_system(
            cls.candidates, cls.pairs, cls.gram
        )

    def test_sparse_model_census(self) -> None:
        self.assertEqual(self.matrix.shape, (612, 45032))
        self.assertEqual(self.matrix.nnz, 675480)
        self.assertEqual(float(self.targets.sum()), 900.0)
        self.assertEqual(float(self.targets[:180].sum()), 180.0)
        self.assertTrue(np.all(self.targets >= 0))

    def test_every_column_has_three_partition_and_twelve_cell_entries(self) -> None:
        pair_sums = np.asarray(self.matrix[:180, :].sum(axis=0)).reshape(-1)
        cell_sums = np.asarray(self.matrix[180:, :].sum(axis=0)).reshape(-1)
        self.assertTrue(np.all(pair_sums == 3))
        self.assertTrue(np.all(cell_sums == 12))

    def test_certificate_checker_rejects_wrong_cardinality(self) -> None:
        with self.assertRaisesRegex(ValueError, "60 distinct"):
            MILP.exact_certificate(
                [],
                self.candidates,
                self.pairs,
                self.gram,
                self.adjacency,
            )

    def test_retained_milp_scout_is_non_evidentiary_unknown(self) -> None:
        record = json.loads(
            (PACKAGE / "solve-result-milp-t600.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(record["claim_label"], "UNKNOWN")
        self.assertIsNone(record["certificate"])
        self.assertFalse(
            record["bounded_run"]["terminal_negative_certificate"]
        )
        self.assertEqual(record["model"]["total_exact_rows"], 612)
        self.assertFalse(record["status_wall"]["endpoint_excluded"])


if __name__ == "__main__":
    unittest.main()
