"""Tests for the source-blind Wave201 verifier."""

import unittest

try:
    from .independent_check import derive, fibre_profile
except ImportError:
    from independent_check import derive, fibre_profile


class Wave201IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = derive()

    def test_pre_source_status(self) -> None:
        self.assertEqual(
            self.result["verdict"],
            "INDEPENDENTLY_DERIVED_PRE_SOURCE",
        )

    def test_multiplicity_one(self) -> None:
        profile = fibre_profile({"a": 1}, {"a": 1})
        self.assertEqual(profile["weighted"], -1)
        self.assertEqual(profile["loss"], 0)
        self.assertEqual(profile["decomposition"], 1)

    def test_multiple_selected_labels_same_fibre(self) -> None:
        profile = fibre_profile(
            {"a": 1, "b": 4},
            {"a": 1, "b": 4},
        )
        self.assertEqual(profile["r"], 2)
        self.assertEqual(profile["weighted"], 1)
        self.assertEqual(profile["loss"], 3)

    def test_selected_is_subset_of_full(self) -> None:
        profile = fibre_profile(
            {"a": 4, "b": 1},
            {"a": 2},
        )
        self.assertEqual(profile["loss"], 3)
        self.assertEqual(profile["weighted"], 0)
        with self.assertRaises(ValueError):
            fibre_profile({"a": 2}, {"a": 3})

    def test_four_point_and_pair_degree_guards(self) -> None:
        with self.assertRaises(ValueError):
            fibre_profile(
                {"a": 1, "b": 1, "c": 1, "d": 1, "e": 1},
                {},
            )
        with self.assertRaises(ValueError):
            fibre_profile({"a": 5, "b": 1}, {})

    def test_hilton_milner_baseline(self) -> None:
        templates = self.result["local_theorem"]["tight_center"][
            "hilton_milner_templates"
        ]
        for template in templates.values():
            self.assertEqual(template["members"], 13)
            self.assertEqual(template["pair_occurrences"], 39)
            self.assertEqual(template["maximum_pair_degree"], 5)
            self.assertEqual(template["number_degree_five_pairs"], 3)

    def test_global_weighted_slack(self) -> None:
        global_result = self.result["local_theorem"]["global"]
        self.assertEqual(
            global_result["new_slack"],
            "SM=delta-3*q+epsilon>=0",
        )

    def test_exact_certificate(self) -> None:
        certificate = self.result["certificate"]
        self.assertEqual(certificate["reduced_difference"], {})
        self.assertEqual(certificate["target"], "70587/10")
        self.assertEqual(certificate["integer_Q_lower"], 7059)
        self.assertEqual(
            certificate["all_projective_short_circuits"],
            7752,
        )
        self.assertEqual(
            certificate["nonzero_scalar_short_circuit_words"],
            15504,
        )

    def test_integer_near_equality_with_m1(self) -> None:
        control = self.result["accounting_controls"][
            "integer_near_equality"
        ]
        self.assertEqual(
            control["multiplicity_profile"],
            {"1": 1, "2": 232, "3": 4},
        )
        self.assertEqual(control["profile_q"], 237)
        self.assertEqual(control["profile_weighted_loss"], 3)
        self.assertEqual(control["evaluation"]["Q0"], "7059")
        self.assertFalse(control["asserted_object"])

    def test_rational_equality_is_not_object(self) -> None:
        control = self.result["accounting_controls"]["rational_equality"]
        self.assertEqual(control["evaluation"]["Q0"], "70587/10")
        self.assertFalse(control["asserted_object"])

    def test_boundary(self) -> None:
        boundary = self.result["boundary"]
        self.assertFalse(boundary["endpoint_excluded"])
        self.assertFalse(boundary["rank_11_excluded"])
        self.assertEqual(boundary["conway_99"], "UNKNOWN")
        self.assertIn("no graph", self.result["search_scope"])
        self.assertIn("brute-force", self.result["search_scope"])


if __name__ == "__main__":
    unittest.main()
