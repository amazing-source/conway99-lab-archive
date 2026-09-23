import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("exact_check.py")
SPEC = importlib.util.spec_from_file_location("wave80_exact_check", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class Wave80ExactCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = CHECK.build_results()

    def test_endpoint_dimensions_and_types(self) -> None:
        endpoint = self.result["endpoint_rank_28"]
        self.assertEqual(endpoint["hull_dimension"], 28)
        self.assertEqual(endpoint["quotient"], "O^-(16,7), Witt index 7")
        self.assertEqual(
            endpoint["dual_complement"], "O^+(26,7), Witt index 13"
        )

    def test_all_surviving_rows_have_minus_quotient(self) -> None:
        rows = self.result["geometry_rows"]
        self.assertEqual(len(rows), 8)
        self.assertTrue(
            all(row["quotient_orthogonal_type"] == "minus" for row in rows)
        )
        self.assertTrue(
            all(
                row["dual_complement_orthogonal_type"] == "plus"
                for row in rows
            )
        )

    def test_short_vector_compositions_and_dots(self) -> None:
        rows = self.result["short_vectors"]["rows"]
        self.assertEqual(
            [row["code_hamming_weight"] for row in rows], [14, 16, 18]
        )
        self.assertEqual(
            [row["code_self_dot_mod_7"] for row in rows], [0, 4, 1]
        )

    def test_small_principal_blocks(self) -> None:
        checks = self.result["dual_distance"]["small_principal_checks"]
        self.assertEqual(
            [checks[str(order)]["singular_mod_7"] for order in (2, 3, 4)],
            [0, 0, 0],
        )

    def test_five_support_exhaustion(self) -> None:
        check = self.result["dual_distance"]["five_support_exhaustion"]
        self.assertEqual(check["all_labelled_graphs"], 1024)
        self.assertEqual(check["locally_srg_admissible"], 683)
        self.assertEqual(check["singular_with_full_support"], 132)
        self.assertEqual(
            check["projective_full_support_relations"],
            check["relations_with_no_outside_pattern"],
        )
        self.assertEqual(len(check["isomorphism_classes"]), 3)

    def test_six_support_positive_control(self) -> None:
        check = self.result["dual_distance"]["six_support_positive_control"]
        self.assertGreater(check["compatible_outside_pattern_count"], 0)
        self.assertEqual(len(check["projective_kernel_vector"]), 6)
        self.assertTrue(all(check["projective_kernel_vector"]))

    def test_oa_moment_slack(self) -> None:
        rows = self.result["macwilliams_control"][
            "OA_strength_five_moments"
        ]
        self.assertEqual([row["degree"] for row in rows], list(range(6)))
        self.assertTrue(all(row["strict_slack"] > 0 for row in rows))

    def test_status_boundary(self) -> None:
        endpoint = self.result["endpoint"]
        self.assertFalse(endpoint["rank_28_excluded"])
        self.assertEqual(endpoint["conway_status"], "UNKNOWN")
        self.assertEqual(endpoint["novelty"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
