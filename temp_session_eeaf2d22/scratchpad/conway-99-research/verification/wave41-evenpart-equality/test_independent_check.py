from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "wave41_evenpart_independent", HERE / "independent_check.py"
)
CHECK = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(CHECK)


class EvenPartEqualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = CHECK.strict_load(HERE / "independent-results.json")

    def test_results_validate(self):
        CHECK.validate_results(self.results)

    def test_frozen_inputs(self):
        self.assertEqual(CHECK.freeze_inputs(), CHECK.INPUT_HASHES)

    def test_implementation_freeze_matches_current_bytes(self):
        entries = {}
        for line in (HERE / "implementation-freeze.sha256").read_text(
            encoding="utf-8"
        ).splitlines():
            expected, relative = line.split("  ", 1)
            entries[relative] = expected
        self.assertTrue(entries)
        for relative, expected in entries.items():
            self.assertEqual(CHECK.digest(CHECK.ROOT / relative), expected, relative)

    def test_full_replay_recorded_successfully(self):
        self.assertEqual(
            (HERE / "full-replay.stdout.txt").read_text(
                encoding="utf-8"
            ).strip(),
            (
                "VERIFIED "
                "verification\\wave41-evenpart-equality\\independent-results.json"
            ),
        )
        self.assertEqual(
            (HERE / "full-replay.stderr.txt").read_text(encoding="utf-8"),
            "",
        )

    def test_all_seven_even_types_are_exactly_covered(self):
        self.assertEqual(
            set(self.results["partition_results"]),
            {CHECK.partition_label(parts) for parts in CHECK.EVEN_TYPES},
        )

    def test_all_10395_labelled_matchings_are_generated_once(self):
        matchings = list(CHECK.perfect_matchings())
        self.assertEqual(len(matchings), 10395)
        self.assertEqual(len(set(matchings)), 10395)
        self.assertEqual(
            CHECK.hashlib.sha256(
                json.dumps(matchings, separators=(",", ":")).encode("ascii")
            ).hexdigest(),
            self.results["labelled_Z_matchings"]["sha256"],
        )

    def test_every_distinct_kernel_received_full_matching_census(self):
        for label, item in self.results["partition_results"].items():
            self.assertEqual(
                item["kernel_target_matching_checks"],
                10395 * item["distinct_right_kernels"],
                label,
            )
            self.assertTrue(
                all(
                    record["labelled_Z_matchings_checked"] == 10395
                    for record in item["right_kernels"]
                )
            )

    def test_no_even_type_has_rank_25_equality(self):
        for label, item in self.results["partition_results"].items():
            self.assertEqual(item["rank_25_compatible_cases"], 0, label)
            self.assertTrue(
                all(
                    record[
                        "equality_compatible_permutation_matching_pairs"
                    ]
                    == 0
                    for record in item["right_kernels"]
                )
            )

    def test_direct_rank_and_core_laplacian_controls(self):
        for label, item in self.results["partition_results"].items():
            for record in item["right_kernels"]:
                self.assertEqual(
                    record["direct_39_block_rank"],
                    1 + record["core_laplacian_rank"],
                    label,
                )
                self.assertEqual(
                    record["direct_39_block_rank"],
                    25 + record["direct_sample_equality_core_rank"],
                    label,
                )
                self.assertGreaterEqual(record["direct_39_block_rank"], 26)

    def test_positive_hostile_symmetric_completions_attain_25(self):
        controls = 0
        for item in self.results["partition_results"].values():
            for record in item["right_kernels"]:
                self.assertEqual(record["positive_mutation_39_block_rank"], 25)
                controls += 1
        self.assertEqual(controls, self.results["totals"]["distinct_right_kernels"])

    def test_hostile_rank25_compatibility_mutation_is_rejected(self):
        hostile = copy.deepcopy(self.results)
        hostile["partition_results"]["6"]["rank_25_compatible_cases"] = 1
        with self.assertRaisesRegex(ValueError, "rank-25 compatibility"):
            CHECK.validate_results(hostile)

    def test_hostile_matching_count_mutation_is_rejected(self):
        hostile = copy.deepcopy(self.results)
        hostile["partition_results"]["4+2"][
            "kernel_target_matching_checks"
        ] -= 1
        with self.assertRaisesRegex(ValueError, "incomplete kernel matching"):
            CHECK.validate_results(hostile)

    def test_hostile_direct_rank_mutation_is_rejected(self):
        hostile = copy.deepcopy(self.results)
        hostile["partition_results"]["2+2+2"]["right_kernels"][0][
            "direct_39_block_rank"
        ] = 25
        with self.assertRaisesRegex(ValueError, "direct rank identities"):
            CHECK.validate_results(hostile)

    def test_hostile_partition_omission_is_rejected(self):
        hostile = copy.deepcopy(self.results)
        del hostile["partition_results"]["6"]
        with self.assertRaisesRegex(ValueError, "exactly the seven"):
            CHECK.validate_results(hostile)

    def test_status_inflation_is_rejected(self):
        hostile = copy.deepcopy(self.results)
        hostile["status_wall"]["conway_99"] = "DISPROVED"
        with self.assertRaisesRegex(ValueError, "conway_99 status inflated"):
            CHECK.validate_results(hostile)

    def test_strict_json_rejects_duplicate_keys(self):
        path = HERE / "_temporary-duplicate-test.json"
        try:
            path.write_text('{"x":1,"x":2}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                CHECK.strict_load(path)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
