"""Tests for the Wave 205 hostile-control certificate."""

from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wave205_hostile_exact", HERE / "exact_check.py")
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


def analyzed():
    result, certificate = CHECK.analyze()
    CHECK.verify(result, certificate)
    return result, certificate


def test_incidence_degrees_and_bbt_identity() -> None:
    result, _ = analyzed()
    incidence = result["incidence_control"]
    assert incidence["linear_triple_system"]
    assert incidence["row_degree"] == 7
    assert incidence["column_degree"] == 3
    assert incidence["point_graph_degree"] == 14
    assert incidence["integer_bbt_identity"] == "BB^T=A+7I"
    assert incidence["ternary_bbt_identity"] == "BB^T=A+I over F_3"


def test_rank11_zero_tight_star_coupling() -> None:
    result, _ = analyzed()
    for realization in result["realizations"].values():
        assert realization["ambient_column_span_rank"] == 11
        assert realization["centered_gram_rank"] == 11
        assert realization["centered_gram_square_zero"]
        assert realization["projector_sum_zero"]
        assert realization["global_column_frame_zero"]


def test_pair_trace_and_edge_data_agree() -> None:
    result, _ = analyzed()
    comparison = result["comparison"]
    assert comparison["same_full_pairwise_projector_trace_matrix"]
    assert comparison["different_ordered_edge_fourth_trace_entries"] == 0
    assert comparison["edge_fourth_trace_distributions_unordered"] == {
        "A": {"0": 693},
        "B": {"0": 693},
    }


def test_fourth_trace_separates_only_nonedges() -> None:
    result, _ = analyzed()
    comparison = result["comparison"]
    assert comparison["different_ordered_fourth_trace_entries"] == 3888
    assert comparison["different_ordered_nonedge_fourth_trace_entries"] == 3888
    assert comparison["all_differences_are_nonedges"]


def test_relaxations_are_explicit() -> None:
    result, _ = analyzed()
    assert result["incidence_control"]["extra_graph_triangle_count"] == 1098
    assert result["incidence_control"]["connected_component_sizes"] == [27, 36, 36]
    assert result["realizations"]["A"]["distinct_projective_direction_count"] == 21
    assert len(result["failed_target_premises"]) >= 7
    assert not result["conclusions"]["srg_excluded"]
    assert result["conclusions"]["conway_99_status"] == "UNKNOWN"


def test_certificate_is_complete() -> None:
    _, certificate = analyzed()
    assert len(certificate["ambient_form"]) == 11
    assert set(certificate["projectors"]) == {"P", "Q1", "Q2"}
    assert len(certificate["blocks"]) == 231
    assert len(certificate["incidence_matrix"]) == 99
    assert len(certificate["incidence_matrix"][0]) == 231
    assert len(certificate["realization_A"]["block_vectors"]) == 231
    assert len(certificate["realization_B"]["block_vectors"]) == 231
