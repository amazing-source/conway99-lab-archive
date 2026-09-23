from __future__ import annotations

import copy
import importlib.util
import json
import math
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave44_rooted_flags_tested", HERE / "exact_check.py"
)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
FROZEN_SPEC = importlib.util.spec_from_file_location(
    "wave44_frozen_replay_tested", HERE / "verify_frozen.py"
)
assert FROZEN_SPEC is not None and FROZEN_SPEC.loader is not None
FROZEN = importlib.util.module_from_spec(FROZEN_SPEC)
FROZEN_SPEC.loader.exec_module(FROZEN)
RESULT = json.loads((HERE / "exact-results.json").read_text(encoding="utf-8"))
WITNESS = json.loads((HERE / "rooted-witness.json").read_text(encoding="utf-8"))


class RootedFlagTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.system = CHECK.endpoint_system()

    def test_signature_censuses_and_category_sizes(self) -> None:
        self.assertEqual(len(self.system["vertex_rows"]), 7)
        self.assertEqual(len(self.system["edge_rows"]), 36)
        self.assertEqual(len(self.system["nonedge_rows"]), 46)
        self.assertEqual(
            CHECK.signature_universe(1)[-1][0] <= 1, True
        )
        self.assertEqual(
            CHECK.signature_universe(2)[-1][0] <= 2, True
        )

    def test_rooted_family_totals(self) -> None:
        total = math.comb(99, 7)
        self.assertEqual(sum(self.system["vertex_rhs"]), 7 * total)
        self.assertEqual(
            sum(self.system["edge_rhs"]),
            99 * 14 * math.comb(97, 5),
        )
        self.assertEqual(
            sum(self.system["nonedge_rhs"]),
            99 * 84 * math.comb(97, 5),
        )
        self.assertEqual(
            sum(self.system["edge_rhs"])
            + sum(self.system["nonedge_rhs"]),
            42 * total,
        )

    def test_column_pair_partition(self) -> None:
        for column in range(len(self.system["classes"])):
            vertex_total = sum(row[column] for row in self.system["vertex_rows"])
            edge_total = sum(row[column] for row in self.system["edge_rows"])
            nonedge_total = sum(
                row[column] for row in self.system["nonedge_rows"]
            )
            self.assertEqual(vertex_total, 7)
            self.assertEqual(edge_total + nonedge_total, 42)

    def test_exact_witness(self) -> None:
        certificate = CHECK.validate_rooted_witness(self.system)
        self.assertEqual(certificate["h11"], 16_632)
        self.assertEqual(certificate["support_size"], 91)
        self.assertEqual(certificate["zero_classes"], 117)
        self.assertEqual(certificate["all_170_exact_integer_rows"], "PASS")
        self.assertEqual(certificate["seven_subset_total"], math.comb(99, 7))

    def test_frozen_row_rhs_hashes_and_standard_library_replay(self) -> None:
        expected = {
            "base": (
                "4788642cf268145dbcfdca456ef5078f1c2c2edb3626698ecf5c327b1efca359"
            ),
            "vertex": (
                "042ec8cf9026fadc1408ab5401f240dd8ae528a9d7dffd9068bd31230194c9d7"
            ),
            "edge": (
                "255237841b93babdd825fff9c9e2bdd30e8132d9470b9015005a8d660cbac482"
            ),
            "nonedge": (
                "9a20e3a28a00f4850d747630348ff4db8f512ba5cb462fd366362165f52d0bec"
            ),
            "combined": (
                "863a75a616c138e750178c93234a92289363318f4bd0775c7b0792e44b7c61cb"
            ),
        }
        self.assertEqual(CHECK.row_rhs_hashes(self.system), expected)
        self.assertEqual(RESULT["rooted_system"]["row_rhs_sha256"], expected)
        replay = FROZEN.verify(
            HERE / "row-system.json",
            HERE / "rooted-witness.json",
            HERE / "exact-results.json",
        )
        self.assertEqual(replay["status"], "PASS")
        self.assertEqual(replay["total_rows"], 170)
        self.assertFalse(any(replay["family_nonzero_residuals"].values()))

    def test_mutated_positive_count_rejected(self) -> None:
        hostile = copy.deepcopy(WITNESS)
        hostile["support"][0]["count"] += 1
        with self.assertRaises(AssertionError):
            CHECK.validate_rooted_witness(self.system, hostile)

    def test_mutated_sign_detected(self) -> None:
        certificate = CHECK.validate_rooted_witness(self.system)
        vector = certificate["vector"]
        row = list(self.system["edge_rows"][0])
        nonzero = next(index for index, value in enumerate(row) if value)
        row[nonzero] *= -1
        residual = CHECK.residuals(
            (tuple(row),),
            (self.system["edge_rhs"][0],),
            vector,
        )
        self.assertNotEqual(residual, (0,))

    def test_mutated_rooted_rhs_detected(self) -> None:
        certificate = CHECK.validate_rooted_witness(self.system)
        vector = certificate["vector"]
        hostile_rhs = list(self.system["nonedge_rhs"])
        hostile_rhs[0] += 1
        residual = CHECK.residuals(
            self.system["nonedge_rows"], hostile_rhs, vector
        )
        self.assertEqual(sum(value != 0 for value in residual), 1)

    def test_rank_increment_and_old_witness_attack(self) -> None:
        table = RESULT["rooted_system"]["finite_field_rank_table"]
        for record in table.values():
            self.assertEqual(
                (
                    record["base"],
                    record["base_plus_vertex"],
                    record["base_plus_vertex_edge"],
                    record["all_rooted"],
                ),
                (81, 82, 87, 93),
            )
        attack = RESULT["stored_unrooted_witness_attack"]
        self.assertEqual(attack["vertex_nonzero_residual_rows"], 7)
        self.assertEqual(attack["edge_nonzero_residual_rows"], 36)
        self.assertEqual(attack["nonedge_nonzero_residual_rows"], 46)

    def test_result_status_wall(self) -> None:
        CHECK.validate_record(RESULT)
        self.assertEqual(
            RESULT["claim_label"],
            "EXACTLY_VALIDATED_ROOTED_COUNT_WITNESS",
        )
        self.assertEqual(
            RESULT["conclusion"]["rooted_count_system"], "EXACT_FEASIBLE"
        )
        self.assertEqual(RESULT["conclusion"]["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(RESULT["conclusion"]["Conway_99"], "UNKNOWN")
        self.assertFalse(RESULT["conclusion"]["graph_constructed"])

    def test_false_scipy_status_not_evidence(self) -> None:
        diagnostic = RESULT["solver_diagnostics"]["superseded_scipy_milp"]
        self.assertEqual(
            diagnostic["classification"],
            "FALSE_NEGATIVE_REFUTED_BY_EXACT_WITNESS",
        )
        self.assertFalse(diagnostic["used_as_evidence"])


if __name__ == "__main__":
    unittest.main()
