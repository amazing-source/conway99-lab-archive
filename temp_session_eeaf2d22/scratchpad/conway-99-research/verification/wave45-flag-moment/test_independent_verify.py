from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave45_clean_verifier_tested", HERE / "independent_verify.py"
)
assert SPEC is not None and SPEC.loader is not None
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)
RESULT = json.loads(
    (HERE / "independent-results.json").read_text(encoding="utf-8")
)


class IndependentFlagMomentTests(unittest.TestCase):
    def test_flag_and_class_censuses(self) -> None:
        self.assertEqual(
            {
                root_type: len(record["canonical_masks"])
                for root_type, record in RESULT["flag_sets"].items()
            },
            {"vertex": 17, "edge": 16, "nonedge": 19},
        )
        self.assertEqual(
            {
                int(order): len(masks)
                for order, masks in RESULT["unrooted_class_sets"].items()
            },
            {4: 9, 5: 21, 6: 62, 7: 208},
        )

    def test_frozen_coefficient_hashes(self) -> None:
        expected = {
            "vertex": (
                "020ffe9943ded4adb77c308734fb05031723038d81fb7081cf9efed4352d0d27"
            ),
            "edge": (
                "c4219e7f375f8f5b21e98f66d797d80dfd8183b73e3e7867d1a41ba8f72b69e0"
            ),
            "nonedge": (
                "c7ea939d530d1713605f816a06a4acd77db1a77841e76fad89562b5d056d6564"
            ),
            "combined": (
                "5eace9a5008e40c8a1a430bec43b23027fd0d564a0d440f354a8ec101fbdd4b9"
            ),
        }
        streams = RESULT["coefficient_streams"]
        actual = {
            root_type: VERIFY.sha256_compact(streams[root_type])
            for root_type in VERIFY.ROOT_TYPES
        }
        actual["combined"] = VERIFY.sha256_compact(streams)
        self.assertEqual(actual, expected)
        self.assertEqual(RESULT["sha256"]["coefficient_streams"], expected)

    def test_every_coefficient_matrix_is_symmetric(self) -> None:
        expected_orders = {
            "vertex": {4, 5, 6, 7},
            "edge": {4, 5, 6},
            "nonedge": {4, 5, 6},
        }
        for root_type, stream in RESULT["coefficient_streams"].items():
            self.assertEqual(
                {record["order"] for record in stream},
                expected_orders[root_type],
            )
            for record in stream:
                entries = {
                    (row, column): value
                    for row, column, value in record["entries"]
                }
                for (row, column), value in entries.items():
                    self.assertEqual(entries[(column, row)], value)

    def test_overlap_orders_are_retained(self) -> None:
        streams = RESULT["coefficient_streams"]
        for order in (4, 5, 6, 7):
            self.assertTrue(
                any(
                    record["order"] == order and record["entries"]
                    for record in streams["vertex"]
                )
            )
        for root_type in ("edge", "nonedge"):
            for order in (4, 5, 6):
                self.assertTrue(
                    any(
                        record["order"] == order and record["entries"]
                        for record in streams[root_type]
                    )
                )

    def test_ordered_pair_labels_are_not_quotiented(self) -> None:
        permutation = (1, 0, 2, 3)
        edge_map = []
        for left, right in VERIFY.edge_pairs(4):
            new_left, new_right = permutation[left], permutation[right]
            if new_left > new_right:
                new_left, new_right = new_right, new_left
            edge_map.append(VERIFY.edge_index(new_left, new_right, 4))
        differences = 0
        for root_type in ("edge", "nonedge"):
            flags = RESULT["flag_sets"][root_type]["canonical_masks"]
            for flag in flags:
                swapped = VERIFY.canonical_rooted(
                    VERIFY.transform_mask(flag, edge_map), 2
                )
                differences += swapped != flag
                self.assertIn(swapped, flags)
        self.assertGreater(differences, 0)

    def test_petersen_and_clebsch_outer_product_controls(self) -> None:
        expected_parameters = {
            "Petersen": [10, 3, 0, 1],
            "Clebsch": [16, 5, 0, 2],
        }
        for control in RESULT["controls"]:
            self.assertEqual(
                control["srg_parameters"],
                expected_parameters[control["name"]],
            )
            self.assertEqual(
                control["lower_order_deck_reconstruction"], "PASS"
            )
            for root_record in control["root_types"].values():
                self.assertTrue(root_record["direct_equals_linear"])
                self.assertEqual(
                    root_record["all_ones_quadratic"],
                    root_record["all_ones_expected"],
                )
                self.assertGreaterEqual(
                    root_record["hostile_integer_quadratic"], 0
                )

    def test_single_coefficient_mutation_breaks_hash(self) -> None:
        hostile = copy.deepcopy(RESULT["coefficient_streams"])
        original = RESULT["sha256"]["coefficient_streams"]["combined"]
        target = next(
            record
            for record in hostile["vertex"]
            if record["entries"]
        )
        target["entries"][0][2] += 1
        self.assertNotEqual(VERIFY.sha256_compact(hostile), original)

    def test_status_wall(self) -> None:
        VERIFY.validate_record(RESULT)
        self.assertFalse(RESULT["status"]["discovery_inspected"])
        self.assertEqual(RESULT["status"]["endpoint_n3_4158"], "UNKNOWN")
        self.assertEqual(RESULT["status"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
