#!/usr/bin/env python3
"""Calibration tests for the rooted SAT encodings."""

from __future__ import annotations

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory

from matching_orbits import (
    n3_joint_branch_decisions,
    n3_refined_branch_specification,
    n3_refined_orbits,
)
from sat_model import EncodedRootModel, main, solve_model


EXPECTED_N3_POSITIVE_LITERALS = (
    (24, 943, 1834, 1947, 2056, 2161),
    (24, 943, 1834, 1947, 2057, 2110),
    (24, 943, 1834, 1948, 2004, 2110),
    (24, 943, 1835, 1892, 2057, 2110),
    (24, 943, 1835, 1893, 2004, 2110),
    (24, 944, 1777, 1947, 2056, 2161),
    (24, 944, 1777, 1947, 2057, 2110),
    (24, 944, 1777, 1948, 2004, 2110),
    (24, 944, 1778, 1892, 2056, 2161),
    (24, 944, 1778, 1892, 2057, 2110),
    (24, 944, 1778, 1893, 2003, 2161),
    (24, 944, 1778, 1893, 2004, 2110),
)

EXPECTED_REFINED_LITERAL_BY_ENDPOINT = {
    0: 2,
    1: 14,
    3: 34,
    6: 44,
    7: 45,
    8: 46,
    9: 47,
    10: 48,
    11: 49,
    12: 50,
    13: 51,
}


class DirectSatEncodingTests(unittest.TestCase):
    def test_pair_count_two_is_sat_and_decodes_srg_9_4_1_2(self) -> None:
        for variant in ("compact", "direct"):
            with self.subTest(variant=variant):
                encoded = EncodedRootModel.build(2, variant)
                satisfiable, model, _ = solve_model(encoded, "cadical300")
                self.assertTrue(satisfiable)
                self.assertIsNotNone(model)
                certificate = encoded.full_certificate(model or [])
                self.assertEqual(certificate["vertices"], 9)
                self.assertEqual(len(certificate["edges"]), 18)

                adjacency = [set() for _ in range(9)]
                for first, second in certificate["edges"]:
                    adjacency[first].add(second)
                    adjacency[second].add(first)
                self.assertEqual([len(neighbors) for neighbors in adjacency], [4] * 9)
                for first in range(9):
                    for second in range(first + 1, 9):
                        common = len(adjacency[first].intersection(adjacency[second]))
                        self.assertEqual(common, 1 if second in adjacency[first] else 2)

    def test_native_pair_count_two_is_sat_and_decodes_srg_9_4_1_2(self) -> None:
        encoded = EncodedRootModel.build(2, "compact", "native")
        satisfiable, model, _ = solve_model(encoded, "minicard")
        self.assertTrue(satisfiable)
        self.assertIsNotNone(model)
        certificate = encoded.full_certificate(model or [])
        self.assertEqual(certificate["vertices"], 9)
        self.assertEqual(len(certificate["edges"]), 18)

    def test_pair_count_three_is_unsat_negative_control(self) -> None:
        for variant in ("compact", "direct"):
            with self.subTest(variant=variant):
                encoded = EncodedRootModel.build(3, variant)
                satisfiable, model, _ = solve_model(encoded, "cadical300")
                self.assertIs(satisfiable, False)
                self.assertIsNone(model)

    def test_small_encoding_statistics_are_deterministic(self) -> None:
        statistics = EncodedRootModel.build(2, "compact").statistics()
        self.assertEqual(statistics["named_edge_variables"], 6)
        self.assertEqual(statistics["named_wedge_variables"], 12)
        self.assertGreater(statistics["total_variables"], 18)
        self.assertGreater(statistics["clauses"], 24)

    def test_compact_encoding_is_smaller_than_direct_encoding(self) -> None:
        compact = EncodedRootModel.build(3, "compact").statistics()
        direct = EncodedRootModel.build(3, "direct").statistics()
        self.assertLess(compact["total_variables"], direct["total_variables"])
        self.assertLess(compact["clauses"], direct["clauses"])

    def test_native_target_statistics_are_deterministic(self) -> None:
        statistics = EncodedRootModel.build(7, "compact", "native").statistics()
        self.assertEqual(statistics["cardinality_backend"], "native")
        self.assertEqual(statistics["total_variables"], 289_338)
        self.assertEqual(statistics["clauses"], 285_852)
        self.assertEqual(statistics["native_atmost_constraints"], 5_838)

    def test_native_constraints_reject_non_cardinality_solver(self) -> None:
        encoded = EncodedRootModel.build(2, "compact", "native")
        with self.assertRaisesRegex(ValueError, "minicard"):
            solve_model(encoded, "cadical300")

    def test_native_opb_export_preserves_every_small_constraint(self) -> None:
        encoded = EncodedRootModel.build(2, "compact", "native")
        lines = encoded.opb_text().splitlines()
        self.assertEqual(lines[0], "* #variable= 18 #constraint= 50")
        rendered = lines[1:]
        self.assertEqual(
            len(rendered),
            len(encoded.cnf.clauses) + len(encoded.cnf.atmosts),
        )

        def parse_lower_bound(line: str) -> tuple[list[int], int]:
            left, right = line.removesuffix(" ;").split(" >= ")
            tokens = left.split()
            self.assertEqual(tokens[::2], ["+1"] * (len(tokens) // 2))
            literals = [
                -int(token[2:]) if token.startswith("~x") else int(token[1:])
                for token in tokens[1::2]
            ]
            return literals, int(right)

        sources: list[tuple[str, list[int], int]] = [
            ("clause", list(clause), 1) for clause in encoded.cnf.clauses
        ]
        sources.extend(
            ("atmost", list(literals), int(bound))
            for literals, bound in encoded.cnf.atmosts
        )

        for line, (kind, source_literals, source_bound) in zip(rendered, sources):
            output_literals, output_bound = parse_lower_bound(line)
            variables = sorted(
                {abs(literal) for literal in source_literals + output_literals}
            )
            for values in product((False, True), repeat=len(variables)):
                assignment = dict(zip(variables, values))

                def truth(literal: int) -> bool:
                    value = assignment[abs(literal)]
                    return value if literal > 0 else not value

                source_sum = sum(truth(literal) for literal in source_literals)
                source_holds = (
                    source_sum >= source_bound
                    if kind == "clause"
                    else source_sum <= source_bound
                )
                output_holds = (
                    sum(truth(literal) for literal in output_literals) >= output_bound
                )
                self.assertEqual(source_holds, output_holds)

    def test_cnf_formula_rejects_opb_export(self) -> None:
        encoded = EncodedRootModel.build(2, "compact", "cnf")
        with self.assertRaisesRegex(ValueError, "native-cardinality"):
            encoded.opb_text()

    def test_cli_reports_mutually_exclusive_outputs_first(self) -> None:
        with self.assertRaisesRegex(SystemExit, "mutually exclusive"):
            main(["--cardinality", "native", "--cnf", "x.cnf", "--opb", "x.opb"])

    def test_cli_opb_output_uses_reproducible_lf_endings(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "pair2.opb"
            with redirect_stdout(StringIO()):
                self.assertEqual(
                    main(
                        [
                            "--pair-count",
                            "2",
                            "--cardinality",
                            "native",
                            "--opb",
                            str(output),
                        ]
                    ),
                    0,
                )
            payload = output.read_bytes()
            self.assertNotIn(b"\r\n", payload)
            self.assertTrue(payload.endswith(b"\n"))

    def test_n3_normalization_is_the_single_expected_unit(self) -> None:
        encoded = EncodedRootModel.build(7, "compact", "native")
        before = encoded.statistics()
        literal = encoded.add_n3_normalization()
        after = encoded.statistics()
        indices = encoded.root.label_index()

        self.assertEqual(indices[(0, 2)], 0)
        self.assertEqual(indices[(2, 4)], 24)
        self.assertEqual(literal, encoded.edge_literal(0, 24))
        self.assertEqual(literal, 24)
        self.assertEqual(encoded.cnf.clauses[-1], [24])
        self.assertEqual(after["total_variables"], before["total_variables"])
        self.assertEqual(after["clauses"], before["clauses"] + 1)
        self.assertEqual(
            after["native_atmost_constraints"],
            before["native_atmost_constraints"],
        )
        self.assertEqual(
            encoded.opb_text().splitlines()[0],
            "* #variable= 289338 #constraint= 291691",
        )

    def test_n3_normalization_rejects_non_target_scaffolds(self) -> None:
        for pair_count in (2, 3):
            with self.subTest(pair_count=pair_count):
                encoded = EncodedRootModel.build(pair_count, "compact", "native")
                with self.assertRaisesRegex(ValueError, "only to pair_count 7"):
                    encoded.add_n3_normalization()

    def test_n3_joint_cover_has_expected_literals_and_exact_unit_counts(self) -> None:
        encoded = EncodedRootModel.build(7, "compact", "native")
        for branch_number, expected in enumerate(
            EXPECTED_N3_POSITIVE_LITERALS, start=1
        ):
            decisions = n3_joint_branch_decisions(encoded.root, branch_number)
            actual = tuple(
                sorted(
                    encoded.edge_variables[edge]
                    for edge, present in decisions.items()
                    if present
                )
            )
            self.assertEqual(actual, expected)

        before = encoded.statistics()
        encoded.add_n3_normalization()
        positive_literals = encoded.add_n3_joint_branch(12)
        after = encoded.statistics()
        added_branch_clauses = encoded.cnf.clauses[-65:]

        self.assertEqual(positive_literals, EXPECTED_N3_POSITIVE_LITERALS[-1])
        self.assertEqual(encoded.n3_joint_branch_number, 12)
        self.assertEqual(after["total_variables"], before["total_variables"])
        self.assertEqual(after["clauses"], before["clauses"] + 66)
        self.assertEqual(
            after["native_atmost_constraints"],
            before["native_atmost_constraints"],
        )
        self.assertEqual(len(added_branch_clauses), 65)
        self.assertTrue(all(len(clause) == 1 for clause in added_branch_clauses))
        self.assertEqual(sum(clause[0] > 0 for clause in added_branch_clauses), 5)
        self.assertNotIn([24], added_branch_clauses)
        self.assertEqual(
            encoded.opb_text().splitlines()[0],
            "* #variable= 289338 #constraint= 291756",
        )

    def test_cli_rejects_unsafe_n3_legacy_branch_combination(self) -> None:
        with self.assertRaisesRegex(SystemExit, "n3-branch"):
            main(["--pair-count", "7", "--n3", "--branch", "6"])

    def test_cli_validates_and_reports_n3_joint_branch(self) -> None:
        with self.assertRaisesRegex(SystemExit, "requires --n3"):
            main(["--pair-count", "7", "--n3-branch", "1"])
        for branch_number in (0, 13):
            with self.subTest(branch_number=branch_number):
                with self.assertRaisesRegex(SystemExit, "must be in 1..12"):
                    main(
                        [
                            "--pair-count",
                            "7",
                            "--n3",
                            "--n3-branch",
                            str(branch_number),
                        ]
                    )
        with self.assertRaisesRegex(SystemExit, "shared coordinate 2"):
            main(
                [
                    "--pair-count",
                    "7",
                    "--n3",
                    "--n3-branch",
                    "1",
                    "--branch-coordinate",
                    "2",
                ]
            )

        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                main(
                    [
                        "--pair-count",
                        "7",
                        "--cardinality",
                        "native",
                        "--n3",
                        "--n3-branch",
                        "1",
                    ]
                ),
                0,
            )
        report = json.loads(output.getvalue())
        branch = report["n3_joint_branch"]
        self.assertEqual(branch["branch"], 1)
        self.assertEqual(branch["cover_branch_count"], 12)
        self.assertEqual(branch["fiber_coordinate"], 2)
        self.assertEqual(branch["orbit_size"], 1)
        self.assertEqual(
            branch["positive_edge_literals"],
            [24, 943, 1834, 1947, 2056, 2161],
        )
        self.assertEqual(report["encoding"]["clauses"], 285_918)

    def test_cli_rejects_n3_on_every_non_target_scaffold(self) -> None:
        for pair_count in (2, 3):
            with self.subTest(pair_count=pair_count):
                with self.assertRaisesRegex(SystemExit, "target --pair-count 7"):
                    main(["--pair-count", str(pair_count), "--n3"])

    def test_direct_api_rejects_n3_legacy_branch_in_either_order(self) -> None:
        n3_first = EncodedRootModel.build(7, "compact", "native")
        n3_first.add_n3_normalization()
        with self.assertRaisesRegex(ValueError, "verified N3 joint cover"):
            n3_first.add_matching_branch(0, (6,))

        branch_first = EncodedRootModel.build(7, "compact", "native")
        branch_first.add_matching_branch(0, (6,))
        with self.assertRaisesRegex(ValueError, "verified N3 joint cover"):
            branch_first.add_n3_normalization()

    def test_direct_api_guards_n3_joint_branch_state(self) -> None:
        wrong_size = EncodedRootModel.build(3, "compact", "native")
        with self.assertRaisesRegex(ValueError, "only to pair_count 7"):
            wrong_size.add_n3_joint_branch(1)

        encoded = EncodedRootModel.build(7, "compact", "native")
        with self.assertRaisesRegex(ValueError, "requires the N3 normalization"):
            encoded.add_n3_joint_branch(1)
        encoded.add_n3_normalization()
        encoded.add_n3_joint_branch(1)
        with self.assertRaisesRegex(ValueError, "already been added"):
            encoded.add_n3_joint_branch(2)

    def test_refined_cover_literals_counts_and_state_guards(self) -> None:
        encoded = EncodedRootModel.build(7, "compact", "native")
        for branch_number, (_, endpoint, _) in enumerate(
            n3_refined_orbits(), start=1
        ):
            _, refinement_edge, _ = n3_refined_branch_specification(
                encoded.root, branch_number
            )
            self.assertEqual(
                encoded.edge_variables[refinement_edge],
                EXPECTED_REFINED_LITERAL_BY_ENDPOINT[endpoint],
            )

        before = encoded.statistics()
        encoded.add_n3_normalization()
        positive_literals = encoded.add_n3_refined_branch(78)
        after = encoded.statistics()
        added_clauses = encoded.cnf.clauses[-66:]
        self.assertEqual(
            positive_literals,
            (24, 51, 944, 1778, 1893, 2004, 2110),
        )
        self.assertEqual(encoded.n3_joint_branch_number, 12)
        self.assertEqual(encoded.n3_refined_branch_number, 78)
        self.assertEqual(after["total_variables"], before["total_variables"])
        self.assertEqual(after["clauses"], before["clauses"] + 67)
        self.assertEqual(
            after["native_atmost_constraints"], before["native_atmost_constraints"]
        )
        self.assertEqual(len(added_clauses), 66)
        self.assertEqual(sum(clause[0] > 0 for clause in added_clauses), 6)
        self.assertEqual(sum(clause[0] < 0 for clause in added_clauses), 60)
        self.assertEqual(
            encoded.opb_text().splitlines()[0],
            "* #variable= 289338 #constraint= 291757",
        )
        with self.assertRaisesRegex(ValueError, "already been added"):
            encoded.add_n3_refined_branch(1)
        with self.assertRaisesRegex(ValueError, "already been added"):
            encoded.add_n3_joint_branch(1)

    def test_refined_cli_validation_and_report(self) -> None:
        with self.assertRaisesRegex(SystemExit, "requires --n3"):
            main(["--pair-count", "7", "--n3-refined-branch", "1"])
        with self.assertRaisesRegex(SystemExit, "mutually exclusive"):
            main(
                [
                    "--pair-count",
                    "7",
                    "--n3",
                    "--n3-branch",
                    "1",
                    "--n3-refined-branch",
                    "1",
                ]
            )
        for branch_number in (0, 79):
            with self.subTest(branch_number=branch_number):
                with self.assertRaisesRegex(SystemExit, "must be in 1..78"):
                    main(
                        [
                            "--pair-count",
                            "7",
                            "--n3",
                            "--n3-refined-branch",
                            str(branch_number),
                        ]
                    )

        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                main(
                    [
                        "--pair-count",
                        "7",
                        "--cardinality",
                        "native",
                        "--n3",
                        "--n3-refined-branch",
                        "1",
                    ]
                ),
                0,
            )
        report = json.loads(output.getvalue())
        branch = report["n3_refined_branch"]
        self.assertEqual(branch["branch"], 1)
        self.assertEqual(branch["cover_branch_count"], 78)
        self.assertEqual(branch["first_matching_branch"], 1)
        self.assertEqual(branch["additional_common_neighbor_label"], [0, 4])
        self.assertEqual(branch["additional_common_neighbor_literal"], 2)
        self.assertEqual(branch["positive_edge_literals"][0], 2)
        self.assertEqual(report["encoding"]["clauses"], 285_919)

    def test_only_small_matching_branch_is_still_sat(self) -> None:
        encoded = EncodedRootModel.build(2, "compact")
        encoded.add_matching_branch(0, (1,))
        satisfiable, _, _ = solve_model(encoded, "cadical300")
        self.assertTrue(satisfiable)


if __name__ == "__main__":
    unittest.main()
