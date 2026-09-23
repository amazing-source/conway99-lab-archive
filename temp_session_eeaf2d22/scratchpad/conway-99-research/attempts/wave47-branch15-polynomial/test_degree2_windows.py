"""Exact tests for the Wave 47 degree-2 F2 window scout."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave47_degree2_windows",
    HERE / "degree2_windows.py",
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("could not load degree2_windows.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class DegreeTwoWindowTests(unittest.TestCase):
    def test_positive_negative_clause_polynomial(self) -> None:
        monomials = [(), (2,), (3,), (2, 3)]
        columns = {monomial: index for index, monomial in enumerate(monomials)}
        # (x2 OR not x3) is falsified by (1+x2)*x3.
        row = MODULE.clause_polynomial(((2, True), (3, False)), columns)
        expected = (1 << columns[(3,)]) | (1 << columns[(2, 3)])
        self.assertEqual(row, expected)

    def test_exact_one_slice_degree_two_nullity(self) -> None:
        variables = (2, 3, 5)
        monomials = [()]
        monomials.extend((variable,) for variable in variables)
        monomials.extend(
            (first, second)
            for index, first in enumerate(variables)
            for second in variables[index + 1 :]
        )
        columns = {
            monomial: index for index, monomial in enumerate(monomials)
        }
        relations, evaluation_rank, _ = MODULE.slice_relations(
            variables,
            1,
            columns,
        )
        self.assertEqual(evaluation_rank, 3)
        self.assertEqual(len(relations), 4)

    def test_stored_result_contract(self) -> None:
        data = json.loads((HERE / "degree2-window-result.json").read_text())
        self.assertEqual(
            data["format"],
            "wave47-branch15-degree2-coordinate-windows-v1",
        )
        aggregate = data["aggregate"]
        self.assertEqual(aggregate["windows"], 7)
        self.assertEqual(aggregate["wave43_active_rows_in_windows"], 34_340)
        self.assertTrue(aggregate["wave43_degree_at_least_four_barrier"])
        self.assertEqual(aggregate["windows_deriving_contradiction"], 0)
        self.assertEqual(aggregate["new_linear_rank_total"], 13)
        self.assertEqual(aggregate["new_assignments_total"], 0)
        self.assertTrue(
            aggregate[
                "all_new_linear_relations_persist_in_exact_blocks_only_control"
            ]
        )
        self.assertEqual(
            [window["new_linear_rank"] for window in data["windows"]],
            [2, 1, 2, 2, 2, 2, 2],
        )
        self.assertTrue(
            all(
                window["exact_blocks_only_control"][
                    "full_and_control_linear_spaces_equal"
                ]
                for window in data["windows"]
            )
        )
        self.assertTrue(
            all(not window["new_assignments"] for window in data["windows"])
        )

    def test_source_hashes_and_window_partition(self) -> None:
        assignments, _ = MODULE.load_closure()
        loaded = []
        base = None
        for path in (
            MODULE.BASE_OPB,
            MODULE.WAVE42_DELTA,
            MODULE.WAVE43_DELTA,
        ):
            constraints, _ = MODULE.load_constraints(path)
            loaded.extend(constraints)
            if path == MODULE.BASE_OPB:
                base = constraints
        self.assertIsNotNone(base)
        blocks = MODULE.exact_blocks(base, assignments)
        self.assertEqual(len(blocks), 1_176)
        windows = MODULE.coordinate_windows()
        self.assertEqual(len(windows), 7)
        self.assertTrue(
            all(len(window["variables"]) == 276 for window in windows)
        )


if __name__ == "__main__":
    unittest.main()
