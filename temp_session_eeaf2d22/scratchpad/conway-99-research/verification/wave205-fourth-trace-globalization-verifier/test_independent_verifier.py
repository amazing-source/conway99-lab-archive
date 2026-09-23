import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import independent_verifier as v


class TestSourceBlindWave205Verifier(unittest.TestCase):
    def test_dimension_ledger_uses_operator_coordinates(self):
        self.assertEqual(
            v.dimension_ledger(),
            {
                "dim_V": 11,
                "dim_self_adjoint_End_V": 66,
                "dim_trace_zero_self_adjoint_End_V": 65,
                "dim_Sym2_trace_zero_self_adjoint_End_V": 2145,
                "dim_wedge2_V": 55,
                "dim_self_adjoint_End_wedge2_V": 1540,
                "dim_trace_zero_self_adjoint_End_wedge2_V": 1539,
            },
        )

    def test_crossing_and_wedge_fourth_trace_factorization(self):
        p = [
            [1, 1, 0, 2],
            [1, 2, 1, 0],
            [0, 1, 0, 1],
            [2, 0, 1, 1],
        ]
        q = [
            [2, 0, 1, 1],
            [0, 1, 2, 0],
            [1, 2, 2, 1],
            [1, 0, 1, 0],
        ]
        result = v.fourth_trace_identity(p, q)
        self.assertTrue(result["functorial"])
        self.assertEqual(result["crossing"], result["h"])
        self.assertEqual(result["wedge_formula_h"], result["h"])

    def test_rank6_projector_wedge_is_trace_zero_operator(self):
        p = [[int(i == j and i < 6) for j in range(11)] for i in range(11)]
        wp = v.wedge_square(p)
        self.assertEqual(v.matmul(p, p), p)
        self.assertEqual(v.trace(p), 0)
        self.assertEqual(v.rank(wp), 15)
        self.assertEqual(v.trace(wp), 0)
        self.assertEqual(v.matmul(wp, wp), wp)
        self.assertEqual(len(wp), 55)

    def test_local_cross_mask_exhaustion(self):
        result = v.enumerate_local_cross_masks()
        self.assertEqual(result["feasible_count"], 52)
        self.assertEqual(
            result["edge_count_distribution"], {0: 1, 1: 9, 2: 36, 3: 6}
        )
        self.assertEqual(result["three_edge_count"], 6)
        self.assertEqual(result["three_edge_perfect_matchings"], 6)
        self.assertEqual(result["prism_free_max_edges"], 2)

    def test_graph_forced_margins_and_localizer(self):
        for c in v.FOURTH_TRACE_CONTROLS.values():
            self.assertTrue(v.has_graph_forced_margins(c))
            self.assertTrue(all(sum(row) % 3 == 0 for row in c))
            self.assertTrue(
                all(sum(c[i][j] for i in range(7)) % 3 == 0 for j in range(7))
            )
            loc = v.localized_invariants(c)
            self.assertEqual(loc["reconstructed"], c)
            self.assertEqual(loc["localized_rank"], loc["cross_rank"])
            direct = v.cross_invariants(c)
            self.assertEqual(loc["g"], direct["g"])
            self.assertEqual(loc["h"], direct["h"])

    def test_relaxed_controls_separate_fourth_trace_at_same_pair_trace(self):
        records = [
            v.cross_invariants(c) for c in v.FOURTH_TRACE_CONTROLS.values()
        ]
        self.assertEqual({x["g"] for x in records}, {2})
        self.assertEqual({x["h"] for x in records}, {0, 1, 2})
        self.assertEqual({x["union_gram_rank"] for x in records}, {11})
        self.assertTrue(
            all(v.locally_projectively_distinct(v.union_gram(c))
                for c in v.FOURTH_TRACE_CONTROLS.values())
        )

    def test_star_pair_rank_is_cross_rank_in_explicit_quotient(self):
        # Union Gram rank 11 gives its own nondegenerate quotient.  Each
        # star restriction has rank six and the cross pairing has the stored
        # cross rank; these are invariant under the quotient realization.
        for c in v.FOURTH_TRACE_CONTROLS.values():
            gamma = v.union_gram(c)
            self.assertEqual(v.rank(gamma), 11)
            self.assertEqual(v.rank(v.STAR_GRAM), 6)
            self.assertEqual(
                v.rank(c), v.localized_invariants(c)["localized_rank"]
            )

    def test_gram_kernel_is_not_automatically_true_relation(self):
        hostile = v.radical_realization()
        self.assertEqual(hostile["ambient_rank"], 11)
        self.assertEqual(hostile["union_gram_rank"], 9)
        self.assertEqual(hostile["column_span_rank"], 10)
        self.assertEqual(hostile["gram_kernel_dim"], 5)
        self.assertEqual(hostile["true_kernel_dim"], 4)
        self.assertTrue(hostile["reconstructs_gram"])
        self.assertTrue(hostile["star_relations_true"])
        self.assertTrue(hostile["witness_is_gram_kernel"])
        self.assertFalse(hostile["witness_is_true_relation"])
        self.assertTrue(hostile["witness_image_is_nonzero_radical"])

    def test_status_wall(self):
        status = v.build_result()["statuses"]
        self.assertEqual(status["complete_nonedge_classification"], "UNKNOWN")
        self.assertEqual(status["rank_11_endpoint"], "UNKNOWN")
        self.assertEqual(status["n3_4158_endpoint"], "UNKNOWN")
        self.assertEqual(status["Conway_99"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
