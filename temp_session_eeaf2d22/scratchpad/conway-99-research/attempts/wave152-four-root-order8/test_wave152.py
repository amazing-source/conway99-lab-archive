from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SCOUT = load_module("wave152_test_scout", HERE / "four_root_scout.py")
CUT_BUILDER = load_module("wave152_test_cuts", HERE / "build_exact_cuts.py")
WAVE147 = load_module("wave152_test_wave147", SCOUT.WAVE147)
RESULT = json.loads((HERE / "four-root-scout.json").read_text(encoding="utf-8"))
CUTS = json.loads((HERE / "exact-cuts.json").read_text(encoding="utf-8"))
EXACT_AFTER = json.loads(
    (HERE / "exact-witness-after-two-cuts.json").read_text(encoding="utf-8")
)
EXACT_AFTER_FOUR = json.loads(
    (HERE / "exact-witness-after-four-cuts.json").read_text(encoding="utf-8")
)
EXACT_AFTER_FIVE = json.loads(
    (HERE / "exact-witness-after-five-cuts.json").read_text(encoding="utf-8")
)
EXACT_AFTER_EIGHT = json.loads(
    (HERE / "exact-witness-after-eight-cuts.json").read_text(encoding="utf-8")
)
EXACT_AFTER_THIRTEEN = json.loads(
    (HERE / "exact-witness-after-thirteen-cuts.json").read_text(encoding="utf-8")
)
SIMPLIFIED_MASK12 = json.loads(
    (HERE / "simplified-mask12-cut.json").read_text(encoding="utf-8")
)["cut"]
SIMPLIFIED_MASK12_2 = json.loads(
    (HERE / "simplified-mask12-cut-2.json").read_text(encoding="utf-8")
)["cut"]


class Wave152Tests(unittest.TestCase):
    def test_flag_dimensions_and_negative_roots(self):
        self.assertEqual(
            [record["flag_count"] for record in RESULT["root_blocks"]],
            [224, 201, 155, 99, 69, 178, 125, 60, 70],
        )
        self.assertEqual(
            [
                record["root_mask"]
                for record in RESULT["root_blocks"]
                if record["negative_certificate"] is not None
            ],
            [3, 12],
        )

    def test_exact_negative_values(self):
        records = {
            record["root_mask"]: record for record in RESULT["root_blocks"]
        }
        self.assertEqual(
            int(records[3]["negative_certificate"]["quadratic_value_scaled"]),
            -2293145527521819747490560,
        )
        self.assertEqual(
            int(records[12]["negative_certificate"]["quadratic_value_scaled"]),
            -8605517548253993047296,
        )

    def test_cut_hashes_and_signs(self):
        self.assertEqual([cut["root_mask"] for cut in CUTS["cuts"]], [3, 12])
        for cut in CUTS["cuts"]:
            core = dict(cut)
            stored_hash = core.pop("cut_sha256")
            self.assertEqual(CUT_BUILDER.canonical_sha256(core), stored_hash)
            self.assertLess(
                CUT_BUILDER.Fraction(cut["wave150_witness_value"]), 0
            )

    def test_exact_feedback_witness_scope(self):
        self.assertEqual(
            EXACT_AFTER["conclusion"]["finite_relaxation_after_two_cuts"],
            "EXACT_RATIONAL_FEASIBLE",
        )
        self.assertEqual(EXACT_AFTER["x7_record"]["h11"], 16632)
        self.assertEqual(EXACT_AFTER["exact_cut_values"]["12"], "0")
        self.assertGreater(
            CUT_BUILDER.Fraction(EXACT_AFTER["exact_cut_values"]["3"]), 0
        )
        self.assertEqual(
            EXACT_AFTER["selection"]["modular_rank"]["rank"], 885
        )

    def test_input_hashes(self):
        for relative, expected in RESULT["inputs"].items():
            path = SCOUT.ROOT / relative
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)

    def test_later_exact_feedback_controls(self):
        for witness, cut_count in (
            (EXACT_AFTER_FOUR, 4),
            (EXACT_AFTER_FIVE, 5),
            (EXACT_AFTER_EIGHT, 8),
        ):
            self.assertEqual(
                witness["conclusion"]["finite_relaxation_after_two_cuts"],
                "EXACT_RATIONAL_FEASIBLE",
            )
            self.assertEqual(len(witness["exact_cut_values"]), cut_count)
            self.assertTrue(
                all(
                    CUT_BUILDER.Fraction(record["value"]) >= 0
                    for record in witness["exact_cut_values"].values()
                )
            )
            self.assertTrue(
                all(
                    CUT_BUILDER.Fraction(record["value"]) == 0
                    for record in witness["exact_cut_values"].values()
                    if record["active"]
                )
            )
            self.assertEqual(
                witness["selection"]["modular_rank"]["rank"], 886
            )

    def test_simplified_mask12_cut_on_eight_cut_witness(self):
        self.assertEqual(SIMPLIFIED_MASK12["constant"], "320166")
        self.assertEqual(
            [
                (record["canonical_mask"], record["coefficient"])
                for record in SIMPLIFIED_MASK12["order7_coefficients"]
            ],
            [(7864, "1")],
        )
        self.assertEqual(len(SIMPLIFIED_MASK12["order8_coefficients"]), 9)
        x7 = {
            record["canonical_mask"]: CUT_BUILDER.Fraction(str(record["count"]))
            for record in EXACT_AFTER_EIGHT["x7_support"]
        }
        x8 = {
            record["canonical_mask"]: CUT_BUILDER.Fraction(str(record["count"]))
            for record in EXACT_AFTER_EIGHT["x8_support"]
        }
        value = CUT_BUILDER.Fraction(SIMPLIFIED_MASK12["constant"])
        value += sum(
            CUT_BUILDER.Fraction(record["coefficient"])
            * x7.get(record["canonical_mask"], 0)
            for record in SIMPLIFIED_MASK12["order7_coefficients"]
        )
        value += sum(
            CUT_BUILDER.Fraction(record["coefficient"])
            * x8.get(record["canonical_mask"], 0)
            for record in SIMPLIFIED_MASK12["order8_coefficients"]
        )
        self.assertEqual(
            value,
            CUT_BUILDER.Fraction(
                4877445335571096995366917775406,
                2619572513456614590392509237,
            ),
        )

    def test_sparse_cube_wagner_cut_and_thirteen_cut_survivor(self):
        self.assertEqual(SIMPLIFIED_MASK12_2["constant"], "18711")
        self.assertEqual(SIMPLIFIED_MASK12_2["order7_coefficients"], [])
        self.assertEqual(
            [
                (record["canonical_mask"], record["coefficient"])
                for record in SIMPLIFIED_MASK12_2["order8_coefficients"]
            ],
            [(2022000, "6"), (5683824, "-2")],
        )
        self.assertLess(
            CUT_BUILDER.Fraction(SIMPLIFIED_MASK12_2["wave150_witness_value"]),
            0,
        )

        self.assertEqual(
            EXACT_AFTER_THIRTEEN["conclusion"][
                "finite_relaxation_after_two_cuts"
            ],
            "EXACT_RATIONAL_FEASIBLE",
        )
        self.assertEqual(len(EXACT_AFTER_THIRTEEN["exact_cut_values"]), 13)
        self.assertEqual(
            sum(
                bool(record["active"])
                for record in EXACT_AFTER_THIRTEEN["exact_cut_values"].values()
            ),
            3,
        )
        self.assertTrue(
            all(
                CUT_BUILDER.Fraction(record["value"]) >= 0
                for record in EXACT_AFTER_THIRTEEN["exact_cut_values"].values()
            )
        )
        self.assertEqual(
            EXACT_AFTER_THIRTEEN["exact_solve"]["all_rows_passed"], 10313
        )
        self.assertEqual(
            EXACT_AFTER_THIRTEEN["selection"]["modular_rank"]["rank"], 887
        )
        self.assertEqual(len(EXACT_AFTER_THIRTEEN["x8_support"]), 887)

    def test_named_cube_and_wagner_classes(self):
        cube = WAVE147.mask_from_edges(
            8,
            [
                (left, right)
                for left in range(8)
                for right in range(left + 1, 8)
                if (left ^ right).bit_count() == 1
            ],
        )
        wagner = WAVE147.mask_from_edges(
            8,
            [
                *((index, (index + 1) % 8) for index in range(8)),
                *((index, index + 4) for index in range(4)),
            ],
        )
        canonical = WAVE147.canonical_unrooted_by_degree
        self.assertEqual(canonical(cube, 8), canonical(2022000, 8))
        self.assertEqual(canonical(wagner, 8), canonical(5683824, 8))
        self.assertNotEqual(canonical(cube, 8), canonical(wagner, 8))

    def test_certificate_helper_rejects_psd_control(self):
        self.assertIsNone(SCOUT.exact_two_coordinate_certificate([[1, 0], [0, 1]]))
        certificate = SCOUT.exact_two_coordinate_certificate([[1, 2], [2, 1]])
        self.assertIsNotNone(certificate)
        self.assertLess(int(certificate["quadratic_value_scaled"]), 0)


if __name__ == "__main__":
    unittest.main()
