#!/usr/bin/env python3
"""Exact structural tests for the Wave 37 endpoint OPB exporter."""

from __future__ import annotations

import unittest

from export_endpoint_opb import build_endpoint_formula


class EndpointFormulaTests(unittest.TestCase):
    def test_first_endpoint_refinement_has_frozen_shape(self) -> None:
        encoded, parent, metadata = build_endpoint_formula(15)
        self.assertEqual(parent, 4)
        self.assertEqual(metadata["refinement_literal"], 2)
        self.assertEqual(encoded.statistics(), {
            "pair_count": 7,
            "residual_vertex_count": 84,
            "full_vertex_count": 99,
            "named_edge_variables": 3486,
            "named_wedge_variables": 285852,
            "total_variables": 289338,
            "clauses": 568777,
            "variant": "compact",
            "cardinality_backend": "native",
            "native_atmost_constraints": 5838,
        })
        strengthening = metadata["fixed_triangle_prism_strengthening"]
        self.assertEqual(strengthening["fixed_triangle_count"], 6)
        self.assertEqual(
            strengthening["deduplicated_active_clause_count"],
            282774,
        )
        self.assertEqual(
            strengthening["clause_length_histogram"],
            {"3": 606, "5": 282168},
        )

    def test_nonendpoint_refinement_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "endpoint-incompatible"):
            build_endpoint_formula(1)


if __name__ == "__main__":
    unittest.main()
