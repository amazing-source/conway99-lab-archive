from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


REPLAY = load_module("wave159_replay", HERE / "replay_fifteen.py")


class Wave159Tests(unittest.TestCase):
    def test_exact_replay(self):
        result = REPLAY.build_results()
        self.assertEqual(result["claim_label"], "DERIVED")
        self.assertEqual(result["checks"]["retained_cut_count"], 15)
        self.assertEqual(result["checks"]["support_size_x7"], 204)
        self.assertEqual(result["checks"]["support_size_x8"], 887)
        self.assertEqual(
            result["checks"]["exact_negative_four_root_blocks"], [3, 12]
        )
        self.assertEqual(
            result["conclusion"]["fifteen_cut_finite_relaxation"],
            "EXACT_RATIONAL_FEASIBLE",
        )
        self.assertEqual(result["conclusion"]["endpoint_n3_4158"], "UNKNOWN")

    def test_fresh_cut_shapes_and_signs(self):
        payload = REPLAY.read_json(
            "attempts/wave159-four-root-cut-loop/fresh-two-cuts.json"
        )
        cuts = payload["cuts"]
        self.assertEqual([cut["root_mask"] for cut in cuts], [3, 12])
        self.assertEqual(
            [cut["cut_sha256"] for cut in cuts],
            [
                "93c3dcebda9332946cf3391812a4d1f466f7cacc6da4246bc9d625a66879f113",
                "8fc952768230bd900febf656bddfa9dd6b4d4c89b5190e0b74e01e55639f525b",
            ],
        )
        self.assertEqual(
            [
                (
                    sum(int(value) != 0 for value in cut["direction"]),
                    len(cut["order7_coefficients"]),
                    len(cut["order8_coefficients"]),
                    cut["primitive_divisor"],
                )
                for cut in cuts
            ],
            [(53, 155, 842, "33264"), (49, 79, 573, "133056")],
        )
        self.assertTrue(
            all(Fraction(cut["wave150_witness_value"]) < 0 for cut in cuts)
        )

    def test_evaluator_resource_floor_and_exact_certificates(self):
        evaluation = REPLAY.read_json(
            "attempts/wave159-four-root-cut-loop/"
            "four-root-evaluation-after-fifteen-cuts.json"
        )
        self.assertGreater(
            evaluation["resource_report"][
                "minimum_free_physical_memory_percent"
            ],
            15.0,
        )
        certified = [
            block
            for block in evaluation["root_blocks"]
            if block["negative_certificate"] is not None
        ]
        self.assertEqual([block["root_mask"] for block in certified], [3, 12])
        self.assertTrue(
            all(
                int(block["negative_certificate"]["quadratic_value_scaled"]) < 0
                for block in certified
            )
        )

    def test_stored_replay_artifact(self):
        expected = REPLAY.build_results()
        stored = json.loads(
            (HERE / "replay-results.json").read_text(encoding="utf-8")
        )
        self.assertEqual(stored, expected)


if __name__ == "__main__":
    unittest.main()
