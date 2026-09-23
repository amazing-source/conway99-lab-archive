from __future__ import annotations

import hashlib
import itertools
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

import cleanroom_encoding as enc


EXPECTED_INPUT_HASHES = {
    "AGENTS.md": "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "verification/wave34-continuation-protocol.md": "60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4",
    "agents/2026-07-24-wave33-rooted-extension.md": "c324dc48f5c7b9524b8b2ac02fae3acb8b9ec342d0a61081ee86ae4771434c0c",
    "verification/wave33-rooted-extension/comparison-audit.md": "fc7abcd53154d4551a5d3d97d38024840b4228195e143559c9e8b46c15644b8a",
    "verification/wave33-rooted-extension/comparison-results.json": "2e36ecade28bca12d35a963a8c6b52777ac7d766a3c4b3267774000fe2e929fd",
    "verification/wave33-rooted-extension/independent-results.json": "66cef570dbbb4a86e2a35f780edcfc1873d0ac2c5266f1c2065c902a8f91e778",
    "verification/wave33-rooted-extension/input-freeze.sha256": "50f3581217cd995fbc704e92cd42a10d7bc4bea9efd14d9c2fc36840c377fb2e",
    "verification/wave33-rooted-extension/artifact-manifest.sha256": "a0cd7d284a23aba5576f2da2a1282c9acb209953c3da5d01e706d793f61d3ea7",
}


def clause_value(clause: tuple[int, ...], assignment: dict[int, bool]) -> bool:
    return any(
        assignment[abs(literal)] == (literal > 0) for literal in clause
    )


class TestCleanroomEncoding(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = enc.summarize_encoding(hash_body=True)

    def test_frozen_input_hashes(self) -> None:
        for relative, expected in EXPECTED_INPUT_HASHES.items():
            actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, relative)

    def test_fixed_support_and_ss_identity(self) -> None:
        fixed = enc.build_fixed_data()
        self.assertEqual(len(fixed.o_labels), 70)
        self.assertEqual(
            sum(1 for p, line, _ in fixed.o_labels if fixed.cross[p][line]),
            28,
        )
        self.assertEqual(
            sum(1 for p, line, _ in fixed.o_labels if not fixed.cross[p][line]),
            42,
        )
        self.assertEqual({sum(row) for row in fixed.support_adjacency}, {4})
        self.assertEqual({sum(row) for row in fixed.support_to_o}, {10})

    def test_and_equivalence_exhaustive(self) -> None:
        sink = enc.ListClauseSink()
        builder = enc.EncodingBuilder(sink)
        x = builder.alloc("TOY")
        y = builder.alloc("TOY")
        z = builder.alloc("TOY")
        builder.add_and_equivalence(z, x, y)
        self.assertEqual(len(sink.clauses), 3)
        for xv, yv, zv in itertools.product((False, True), repeat=3):
            assignment = {x: xv, y: yv, z: zv}
            passes = all(clause_value(c, assignment) for c in sink.clauses)
            self.assertEqual(passes, zv == (xv and yv))

    def test_exact_counter_existentially_exhaustive_small(self) -> None:
        for n in range(1, 5):
            for target in range(n + 1):
                sink = enc.ListClauseSink()
                builder = enc.EncodingBuilder(sink)
                xs = [builder.alloc("TOY", i=i) for i in range(n)]
                builder.add_exact_count(
                    xs, target, family="TOY", key=(n, target)
                )
                auxiliaries = list(range(n + 1, builder.variable_count + 1))
                for primary_bits in itertools.product((False, True), repeat=n):
                    satisfiable = False
                    for auxiliary_bits in itertools.product(
                        (False, True), repeat=len(auxiliaries)
                    ):
                        assignment = {
                            variable: value
                            for variable, value in zip(xs, primary_bits)
                        }
                        assignment.update(
                            {
                                variable: value
                                for variable, value in zip(
                                    auxiliaries, auxiliary_bits
                                )
                            }
                        )
                        if all(
                            clause_value(clause, assignment)
                            for clause in sink.clauses
                        ):
                            satisfiable = True
                            break
                    self.assertEqual(
                        satisfiable,
                        sum(primary_bits) == target,
                        (n, target, primary_bits),
                    )

    def test_primary_layout_and_raw_domain(self) -> None:
        summary = self.summary
        self.assertEqual(summary["primary_variables"]["D_unordered_edges"], 2415)
        self.assertEqual(summary["primary_variables"]["B_ordered_incidences"], 1050)
        self.assertEqual(summary["groups"]["PRIMARY_D"]["first_variable"], 1)
        self.assertEqual(summary["groups"]["PRIMARY_D"]["last_variable"], 2415)
        self.assertEqual(summary["groups"]["PRIMARY_B"]["first_variable"], 2416)
        self.assertEqual(summary["groups"]["PRIMARY_B"]["last_variable"], 3465)

    def test_constraint_inventory_and_unrestricted_scope(self) -> None:
        summary = self.summary
        inventory = summary["inventory"]
        self.assertEqual(inventory["constraint_total"], 4985)
        self.assertEqual(
            inventory["constraint_counts"],
            {
                "B_COLUMN_QQ_DIAGONAL": 15,
                "B_ROW": 70,
                "D_ROW": 70,
                "OO_DIAGONAL": 70,
                "OO_OFFDIAGONAL": 2415,
                "OQ": 1050,
                "QQ_OFFDIAGONAL": 105,
                "SO": 980,
                "SQ": 210,
            },
        )
        self.assertEqual(summary["primary_variables"]["total"], 3465)
        self.assertEqual(
            summary["inventory"]["target_distributions"]["OO_OFFDIAGONAL"],
            [
                {"scope_size": 84, "target": 0, "count": 21},
                {"scope_size": 84, "target": 1, "count": 588},
                {"scope_size": 84, "target": 2, "count": 1806},
            ],
        )
        self.assertEqual(
            summary["inventory"]["target_distributions"]["SO"],
            [
                {"scope_size": 9, "target": 0, "count": 56},
                {"scope_size": 9, "target": 1, "count": 84},
                {"scope_size": 10, "target": 1, "count": 504},
                {"scope_size": 10, "target": 2, "count": 336},
            ],
        )

    def test_frozen_full_counts_and_clause_commitment(self) -> None:
        summary = self.summary
        self.assertEqual(summary["auxiliary_variables"]["product"], 280245)
        self.assertEqual(summary["auxiliary_variables"]["cardinality"], 946806)
        self.assertEqual(summary["total_variables"], 1230516)
        self.assertEqual(summary["total_clauses"], 4319043)
        self.assertEqual(
            summary["clause_length_histogram"],
            {"1": 12084, "2": 1823388, "3": 2483571},
        )
        self.assertEqual(
            summary["dimacs_body_sha256"],
            "5a98d5d6c505cb89d365bbae4f382c9593f53bdcc64b57ed975122461202a61d",
        )
        self.assertEqual(
            summary["fixed_data"]["support_adjacency_sha256"],
            "8e9df095563e6d7a8166a99d60f51c15c4db6b722080fd233146a2aa6626431d",
        )
        self.assertEqual(
            summary["fixed_data"]["support_to_o_sha256"],
            "8a4e68fd7bfa97917c74bde2a3ae34d9786ca1f7597b0bb0b3c77c110cfe0756",
        )
        self.assertEqual(
            summary["fixed_data"]["o_labels_sha256"],
            "391ca52fb781969d988c8f75eca24da6c131e480f0e6e5a673b83b04ec39bdb1",
        )

    def test_machine_readable_spec_and_count_snapshot(self) -> None:
        count_snapshot = json.loads(
            (HERE / "count-expectations.json").read_text(encoding="utf-8")
        )
        self.assertEqual(count_snapshot, self.summary)
        spec = json.loads(
            (HERE / "criterion-spec.json").read_text(encoding="utf-8")
        )
        self.assertEqual(spec["primary_variables"]["total"], 3465)
        self.assertFalse(spec["scope"]["assumed_automorphism"])
        self.assertFalse(spec["scope"]["symmetry_breaking"])
        self.assertFalse(spec["scope"]["fixed_O_Q_design"])
        self.assertEqual(
            [entry["block"] for entry in spec["six_blocks"]],
            ["SS", "SO", "SQ", "OO", "OQ", "QQ"],
        )
        self.assertEqual(
            sum(item["count"] for item in spec["auxiliary_products"]),
            280245,
        )

    def test_all_zero_decoding_is_rejected(self) -> None:
        d = [[0 for _ in range(enc.O_SIZE)] for _ in range(enc.O_SIZE)]
        bmat = [[0 for _ in range(enc.Q_SIZE)] for _ in range(enc.O_SIZE)]
        result = enc.six_block_mismatch_counts(d, bmat)
        self.assertFalse(result["passes"])
        self.assertEqual(result["SS_mismatches"], 0)
        self.assertGreater(result["SO_mismatches"], 0)
        self.assertGreater(result["SQ_mismatches"], 0)
        self.assertGreater(result["OO_mismatches"], 0)
        self.assertGreater(result["OQ_mismatches"], 0)
        self.assertGreater(result["QQ_mismatches"], 0)


if __name__ == "__main__":
    unittest.main()
