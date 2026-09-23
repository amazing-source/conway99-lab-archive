"""Focused hostile tests for the independent Wave147 verification output."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import independent_verify as verify  # noqa: E402


class Wave147IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(
            (HERE / "verification-results.json").read_text(encoding="utf-8")
        )

    def test_manifest_freeze(self) -> None:
        package = self.result["sealed_discovery_package"]
        self.assertEqual(
            package["manifest_sha256"], verify.EXPECTED_DISCOVERY_MANIFEST
        )
        self.assertEqual(package["entry_count"], 11)
        self.assertTrue(package["manifest_pass"])
        self.assertTrue(package["entries_pass"])

    def test_flag_bases(self) -> None:
        self.assertEqual(self.result["flag_bases"]["ordered_edge"]["count"], 66)
        self.assertEqual(
            self.result["flag_bases"]["ordered_nonedge"]["count"], 87
        )
        self.assertEqual(
            tuple(self.result["flag_bases"]["ordered_edge"]["masks"]),
            verify.flag_basis(True),
        )
        self.assertEqual(
            tuple(self.result["flag_bases"]["ordered_nonedge"]["masks"]),
            verify.flag_basis(False),
        )

    def test_class_streams(self) -> None:
        expected = {5: 21, 6: 62, 7: 208, 8: 916}
        for order, count in expected.items():
            self.assertEqual(
                self.result["class_streams"][str(order)]["count"], count
            )
            self.assertEqual(
                self.result["class_streams"][str(order)]["sha256"],
                verify.EXPECTED_STREAMS[order][1],
            )
        self.assertTrue(
            self.result["class_streams"]["order8_extension"][
                "stored_mask_list_exact_match"
            ]
        )

    def test_full_artifact_counts(self) -> None:
        artifact = self.result["artifact"]
        self.assertEqual(artifact["total_class_matrix_records"], 2414)
        self.assertEqual(artifact["total_nonzero_upper_entries"], 272054)
        self.assertEqual(artifact["deletion_rows"], 208)
        self.assertEqual(artifact["deletion_nonzero_terms"], 5333)
        self.assertEqual(
            artifact["payload_sha256"],
            "a7402e77048090ea492c435190aadc1d32bd1df99276e612f6d199aec9e14b08",
        )

    def test_representative_semantics_and_carriers(self) -> None:
        semantics = self.result["coefficient_semantics"]
        self.assertEqual(semantics["representative_matrix_check_count"], 24)
        self.assertTrue(
            all(
                row["pass"]
                for row in semantics["representative_matrix_checks"]
            )
        )
        edge = semantics["carriers"]["ordered_edge"]
        nonedge = semantics["carriers"]["ordered_nonedge"]
        self.assertEqual(
            (edge["row"], edge["column"], edge["n3_coefficient"], edge["prism_coefficient"]),
            (29, 32, 4, 0),
        )
        self.assertEqual(
            (
                nonedge["row"],
                nonedge["column"],
                nonedge["n3_coefficient"],
                nonedge["prism_coefficient"],
            ),
            (36, 42, 4, 0),
        )

    def test_rook_positive_control(self) -> None:
        rook = self.result["rook_positive_control"]
        self.assertEqual((rook["degree"], rook["lambda"], rook["mu"]), (4, 1, 2))
        self.assertEqual(rook["induced_n3_count"], 0)
        self.assertEqual(rook["induced_triangular_prism_count"], 6)
        for family in ("ordered_edge", "ordered_nonedge"):
            moment = rook["direct_moments"][family]
            self.assertEqual(moment["root_embeddings"], 36)
            self.assertEqual(moment["free_triples_per_root"], 35)
            self.assertEqual(moment["rank_over_Q"], 1)
            self.assertEqual(moment["sum_all_entries"], 44100)
            self.assertEqual(moment["trace"], 2412)

    def test_scope_wall(self) -> None:
        self.assertEqual(self.result["verdict"]["overall"], "PASS_WITH_SCOPE")
        self.assertEqual(
            self.result["status_wall"]["strong_marked_vertex_pair_order8_rows"],
            "NOT_BUILT",
        )
        self.assertEqual(
            self.result["status_wall"]["strict_n3_upper_bound"], "UNKNOWN"
        )
        self.assertEqual(self.result["status_wall"]["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
