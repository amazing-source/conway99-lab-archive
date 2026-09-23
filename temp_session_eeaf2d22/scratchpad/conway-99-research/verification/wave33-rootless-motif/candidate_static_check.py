#!/usr/bin/env python3
"""Static candidate comparison for the Wave 33 rootless-motif package.

This module reads candidate text and data only after the independent
precomparison package was hash-frozen.  It never imports or executes
candidate code.  Mathematical checks use the verifier's own independently
written implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Sequence

import independent_check as independent


ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_FREEZE = (
    ROOT / "verification/wave33-rootless-motif-candidate-freeze.sha256"
)
CANDIDATE_FREEZE_SHA256 = (
    "8cca06d858a401c6c4f054daae8e35fb4796fabb0f15877547a6c943971c32e0"
)
PRECOMPARISON_MANIFEST = (
    ROOT / "verification/wave33-rootless-motif/precomparison-manifest.sha256"
)
PRECOMPARISON_MANIFEST_SHA256 = (
    "b76da4963b9588102b657e04dfd9195bb4a5d9bbe7a365ae255023b6385863e8"
)
CANDIDATE_REPORT = ROOT / "agents/2026-07-24-wave33-rootless-motif.md"
CANDIDATE_DIR = ROOT / "attempts/wave33-rootless-motif"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_hash_list(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest = line[:64]
        remainder = line[64:].strip()
        if remainder.startswith("*"):
            remainder = remainder[1:]
        if (
            len(digest) != 64
            or not remainder
            or any(character not in "0123456789abcdef" for character in digest)
        ):
            raise AssertionError(f"malformed hash line in {path}: {line}")
        if remainder in result:
            raise AssertionError(f"duplicate hash path in {path}: {remainder}")
        result[remainder] = digest
    return result


def verify_hash_list(path: Path) -> dict[str, object]:
    entries = parse_hash_list(path)
    mismatches = []
    for relative, expected in entries.items():
        target = (ROOT / relative).resolve()
        if not target.is_relative_to(ROOT.resolve()):
            raise AssertionError(f"hash-list path escapes repository: {relative}")
        if not target.is_file():
            mismatches.append({
                "path": relative,
                "expected": expected,
                "observed": "MISSING",
            })
            continue
        observed = sha256_file(target)
        if observed != expected:
            mismatches.append({
                "path": relative,
                "expected": expected,
                "observed": observed,
            })
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "entry_count": len(entries),
        "all_match": not mismatches,
        "mismatches": mismatches,
        "entries": entries,
    }


def provenance_validation() -> dict[str, object]:
    if sha256_file(CANDIDATE_FREEZE) != CANDIDATE_FREEZE_SHA256:
        raise AssertionError("orchestrator candidate freeze changed")
    if sha256_file(PRECOMPARISON_MANIFEST) != PRECOMPARISON_MANIFEST_SHA256:
        raise AssertionError("precomparison manifest changed")

    candidate_freeze = verify_hash_list(CANDIDATE_FREEZE)
    precomparison = verify_hash_list(PRECOMPARISON_MANIFEST)
    candidate_manifest = verify_hash_list(
        CANDIDATE_DIR / "artifact-manifest.sha256"
    )
    candidate_inputs = verify_hash_list(CANDIDATE_DIR / "input-freeze.sha256")
    for result in (
        candidate_freeze,
        precomparison,
        candidate_manifest,
        candidate_inputs,
    ):
        if not result["all_match"]:
            raise AssertionError(f"hash validation failed: {result}")

    freeze_entries = candidate_freeze["entries"]
    assert isinstance(freeze_entries, dict)
    manifest_relative = "attempts/wave33-rootless-motif/artifact-manifest.sha256"
    if freeze_entries[manifest_relative] != sha256_file(
        CANDIDATE_DIR / "artifact-manifest.sha256"
    ):
        raise AssertionError("candidate freeze does not bind candidate manifest")

    return {
        "candidate_freeze_sha256": CANDIDATE_FREEZE_SHA256,
        "candidate_freeze": {
            "entry_count": candidate_freeze["entry_count"],
            "all_match": True,
        },
        "candidate_manifest": {
            "entry_count": candidate_manifest["entry_count"],
            "all_match": True,
        },
        "candidate_input_freeze": {
            "entry_count": candidate_inputs["entry_count"],
            "all_match": True,
        },
        "precomparison_manifest_sha256": PRECOMPARISON_MANIFEST_SHA256,
        "precomparison_manifest": {
            "entry_count": precomparison["entry_count"],
            "all_match": True,
        },
    }


def load_candidate_results() -> dict[str, object]:
    return json.loads(
        (CANDIDATE_DIR / "exact-results.json").read_text(encoding="utf-8")
    )


def metadata_comparison(candidate: dict[str, object]) -> dict[str, object]:
    expected_keys = {
        "actual_incidence_board",
        "constructs_global_graph_or_endpoint",
        "inputs",
        "local_moment_controls",
        "mixed_trace",
        "scope",
        "spectral_and_incidence_algebra",
        "status",
        "strongest_self_objection",
        "uses_automorphism",
    }
    if set(candidate) != expected_keys:
        raise AssertionError("candidate top-level schema differs")
    if candidate["scope"] != (
        "Exact tensor/adjacency-algebra and actual local-incidence "
        "reductions for the Wave 33 rootless mixed-motif branch."
    ):
        raise AssertionError("candidate top-level scope differs")
    if candidate["uses_automorphism"] is not False:
        raise AssertionError("candidate introduced an automorphism restriction")
    if candidate["constructs_global_graph_or_endpoint"] is not False:
        raise AssertionError("candidate inflated a local control to a graph")

    frozen_inputs = parse_hash_list(CANDIDATE_DIR / "input-freeze.sha256")
    if candidate["inputs"] != frozen_inputs:
        raise AssertionError("candidate JSON inputs differ from input freeze")
    return {
        "top_level_schema_exact": True,
        "input_hashes_match_candidate_input_freeze": True,
        "uses_automorphism": False,
        "constructs_global_graph_or_endpoint": False,
        "scope_is_local_reduction": True,
    }


def algebra_comparison(candidate: dict[str, object]) -> dict[str, object]:
    submitted = candidate["spectral_and_incidence_algebra"]
    assert isinstance(submitted, dict)
    if set(submitted) != {
        "C_definition",
        "C_spectrum",
        "Gamma_spectrum",
        "M_definition",
        "M_spectrum",
        "basis",
        "incidence_reduction",
        "multiplication_identities",
    }:
        raise AssertionError("candidate algebra schema differs")
    independent_algebra = independent.gamma_multiplication_table()
    expected_identities = {
        "Gamma^2": "18*I+5*Gamma+C",
        "Gamma*C": "-18*I+18*J-2*Gamma-C",
        "C^2": "72*I+216*J-16*Gamma-14*C",
    }
    expected_gamma_spectrum = [
        {"eigenvalue": 18, "multiplicity": 1},
        {"eigenvalue": 7, "multiplicity": 54},
        {"eigenvalue": 0, "multiplicity": 44},
        {"eigenvalue": -3, "multiplicity": 132},
    ]
    algebra_numeric_values = [
        *(item["eigenvalue"] for item in submitted["Gamma_spectrum"]),
        *(item["multiplicity"] for item in submitted["Gamma_spectrum"]),
        *submitted["C_spectrum"],
        *submitted["M_spectrum"],
    ]
    if any(type(value) is not int for value in algebra_numeric_values):
        raise AssertionError("candidate algebra numeric field is not an integer")
    if submitted["multiplication_identities"] != expected_identities:
        raise AssertionError("candidate multiplication identities differ")
    if submitted["Gamma_spectrum"] != expected_gamma_spectrum:
        raise AssertionError("candidate Gamma spectrum differs")
    if submitted["C_definition"] != "C=Gamma^2-5*Gamma-18*I":
        raise AssertionError("candidate C definition differs")
    if submitted["M_definition"] != "M=3*I+J-Gamma-C":
        raise AssertionError("candidate M definition differs")
    if submitted["C_spectrum"] != [216, -4, -18, 6]:
        raise AssertionError("candidate C spectrum differs")
    if submitted["M_spectrum"] != [0, 0, 21, 0]:
        raise AssertionError("candidate M spectrum differs")
    if submitted["basis"] != list(independent.BASIS):
        raise AssertionError("candidate basis order differs")

    report = CANDIDATE_REPORT.read_text(encoding="utf-8")
    required_scope_sentences = [
        "The individual `Rj` need not lie in (4).",
        "This is stronger than a pair-count objection, but it remains local.",
        "Equation (10) does not erase actual incidence from the problem.",
    ]
    missing = [text for text in required_scope_sentences if text not in report]
    if missing:
        raise AssertionError(f"candidate algebra scope text missing: {missing}")

    return {
        "basis": submitted["basis"],
        "basis_dimension": independent_algebra["dimension"],
        "basis_independence_determinant": (
            independent_algebra["basis_evaluation_determinant"]
        ),
        "Gamma_spectrum_match": True,
        "multiplication_identities_match": True,
        "C_spectrum_match": True,
        "M_scaled_projector_spectrum_match": True,
        "candidate_scope_sentences_present": True,
    }


def table_comparison(candidate: dict[str, object]) -> dict[str, object]:
    controls = candidate["local_moment_controls"]
    assert isinstance(controls, dict)
    if set(controls) != {
        "interpretation",
        "motif_one",
        "motif_zero",
        "null_trade_checks",
        "null_trade_one_minus_zero",
        "scope",
        "universal_blindness",
    }:
        raise AssertionError("candidate local-control schema differs")
    if controls["interpretation"] != (
        "For a fixed ordered R2 pair (T,U), entry (a,b) counts third "
        "triangles V with relation a from T and relation b to U."
    ):
        raise AssertionError("candidate table interpretation differs")
    expected_scope = (
        "Exact local moment controls only. They are not globally compatible "
        "relation tensors, 231-by-231 matrices, projectors, frames, incidence "
        "structures, or graphs."
    )
    if controls["scope"] != expected_scope:
        raise AssertionError("candidate local-table scope differs")
    if controls["universal_blindness"] != (
        "Bilinearity implies that both tables give the same (FG)[T,U] for "
        "every F,G in Q[Gamma]."
    ):
        raise AssertionError("candidate universal-blindness scope differs")
    expected_relation_order = ["D", "G", "R0", "R1", "R2", "R3"]
    expected_margins = {
        relation: margin
        for relation, margin in zip(
            expected_relation_order,
            independent.margins_for_q(2),
        )
    }
    validations = {}
    tables = {}
    for name in ("motif_zero", "motif_one"):
        payload = controls[name]
        assert isinstance(payload, dict)
        if set(payload) != {
            "base_pair_relation",
            "basis_contraction_matrix",
            "basis_order",
            "common_R3_neighbours",
            "projector_contraction_M_squared",
            "q_endpoint_values",
            "relation_order",
            "row_and_column_margins",
            "table",
        }:
            raise AssertionError(f"candidate {name} schema differs")
        table = payload["table"]
        assert isinstance(table, list)
        if any(
            type(entry) is not int or entry < 0
            for row in table
            for entry in row
        ):
            raise AssertionError(
                f"candidate {name} table is not exactly nonnegative integral"
            )
        validation = independent.validate_local_table(table)
        expected_common = 0 if name == "motif_zero" else 1
        if validation["common_R3_count"] != expected_common:
            raise AssertionError(f"candidate {name} common-R3 count differs")
        if payload["common_R3_neighbours"] != expected_common:
            raise AssertionError(f"candidate {name} labels its R3 count wrongly")
        if payload["q_endpoint_values"] != [2, 2]:
            raise AssertionError(f"candidate {name} q endpoint differs")
        if payload["relation_order"] != expected_relation_order:
            raise AssertionError(f"candidate {name} relation order differs")
        if payload["basis_order"] != list(independent.BASIS):
            raise AssertionError(f"candidate {name} basis order differs")
        if payload["row_and_column_margins"] != expected_margins:
            raise AssertionError(f"candidate {name} labelled margins differ")
        if payload["base_pair_relation"] != "R2 / C=2 / M=-1":
            raise AssertionError(f"candidate {name} base relation differs")
        if payload["basis_contraction_matrix"] != validation["contractions"]:
            raise AssertionError(f"candidate {name} contraction bytes differ")
        m_vector = (4, 0, 1, 0, -1, -2)
        m_squared = independent.bilinear_contraction(
            m_vector,
            table,
            m_vector,
        )
        if m_squared != -21:
            raise AssertionError(f"candidate {name} M^2 entry differs")
        if payload["projector_contraction_M_squared"] != m_squared:
            raise AssertionError(f"candidate {name} labels M^2 wrongly")
        validations[name] = validation
        tables[name] = table

    zero = tables["motif_zero"]
    one = tables["motif_one"]
    switch = [
        [one[i][j] - zero[i][j] for j in range(6)]
        for i in range(6)
    ]
    vectors = independent.entry_vectors()
    if [sum(row) for row in switch] != [0] * 6:
        raise AssertionError("candidate trade changes row margins")
    for left in independent.BASIS:
        for right in independent.BASIS:
            if independent.bilinear_contraction(
                vectors[left],
                switch,
                vectors[right],
            ) != 0:
                raise AssertionError("candidate trade visible to fused algebra")
    if switch[5][5] != 1:
        raise AssertionError("candidate trade does not change decisive cell")
    if controls["null_trade_one_minus_zero"] != switch:
        raise AssertionError("candidate labelled null trade differs")
    null_checks = controls["null_trade_checks"]
    assert isinstance(null_checks, dict)
    expected_null_checks = {
        "M_squared_contraction_zero": True,
        "all_Q_Gamma_bilinear_contractions_zero": True,
        "all_relation_margins_zero": True,
        "change_in_common_R3_count": 1,
    }
    if null_checks != expected_null_checks:
        raise AssertionError("candidate null-trade check labels differ")

    independent_tables = [
        [list(row) for row in table]
        for table in independent.local_tables()
    ]
    independently_different = all(
        table not in independent_tables
        for table in (zero, one)
    )
    if not independently_different:
        raise AssertionError(
            "candidate unexpectedly reused precomparison table bytes"
        )

    return {
        "candidate_tables_nonnegative_integral_symmetric": True,
        "candidate_margins": validations["motif_zero"]["margins"],
        "candidate_fixed_R2_cells": validations["motif_zero"]["fixed_cells"],
        "candidate_QGamma_contractions": (
            validations["motif_zero"]["contractions"]
        ),
        "candidate_common_R3_counts": [0, 1],
        "candidate_M_squared_entries": [-21, -21],
        "null_trade_invisible_to_all_basis_pairs": True,
        "candidate_tables_differ_from_independent_controls": (
            independently_different
        ),
        "global_realizability": "NOT_ESTABLISHED",
        "formal_q2_R2_pair_global_occurrence": "NOT_ESTABLISHED",
    }


def transport_comparison(candidate: dict[str, object]) -> dict[str, object]:
    submitted = candidate["spectral_and_incidence_algebra"]
    assert isinstance(submitted, dict)
    reduction = submitted["incidence_reduction"]
    assert isinstance(reduction, dict)
    if set(reduction) != {
        "checked_exponents",
        "conclusion",
        "does_not_cover",
        "identity",
        "spectral_values",
    }:
        raise AssertionError("candidate transport schema differs")
    if reduction["identity"] != (
        "N^T*A^k*N=(3I+Gamma)*(Gamma-4I)^k"
    ):
        raise AssertionError("candidate incidence identity differs")
    values = reduction["spectral_values"]
    assert isinstance(values, dict)
    if any(
        type(value) is not int
        for row in values.values()
        for value in row
    ):
        raise AssertionError(
            "candidate transport spectral value is not an integer"
        )
    if reduction["checked_exponents"] != list(range(6)):
        raise AssertionError("candidate checked-exponent label differs")
    if any(
        type(exponent) is not int
        for exponent in reduction["checked_exponents"]
    ):
        raise AssertionError("candidate checked exponent is not an integer")
    if reduction["does_not_cover"] != (
        "uncontracted vertex labels or genuine three-leg and higher "
        "incidence compatibility"
    ):
        raise AssertionError("candidate transport scope label differs")
    expected_conclusion = (
        "Every fully contracted two-leg expression obtained from N, N^T, "
        "and a polynomial in A lies in Q[Gamma]."
    )
    if reduction["conclusion"] != expected_conclusion:
        raise AssertionError("candidate transport conclusion differs")
    eigenvalues = (18, 7, 0, -3)
    for exponent in range(6):
        expected = [
            (3 + eigenvalue) * (eigenvalue - 4) ** exponent
            for eigenvalue in eigenvalues
        ]
        if values[str(exponent)] != expected:
            raise AssertionError(
                f"candidate transport k={exponent} differs"
            )

    scope = independent.fused_algebra_scope()
    report = CANDIDATE_REPORT.read_text(encoding="utf-8")
    broad_phrase = (
        "all two-leg spectral/incidence contractions are locally blind "
        "to the motif;"
    )
    if broad_phrase not in report:
        raise AssertionError("expected broad summary phrase not found")
    qualifying_text = (
        "uncontracted three-leg incidence and full projector/Schur "
        "compatibility"
    )
    if qualifying_text.lower() not in report.lower():
        raise AssertionError("candidate report lost its scope qualifier")

    return {
        "identity_for_all_nonnegative_k": True,
        "first_six_spectral_rows_match": True,
        "R2_matrix_in_QGamma": scope["R2_matrix_in_QGamma"],
        "R3_matrix_in_QGamma": scope["R3_matrix_in_QGamma"],
        "common_R3_determined_by_QGamma": (
            scope["common_R3_determined_by_QGamma"]
        ),
        "literal_broad_summary_phrase": broad_phrase,
        "literal_unqualified_phrase_status": "TOO_BROAD",
        "candidate_result_conclusion": expected_conclusion,
        "candidate_result_conclusion_status": (
            "PASS_ONLY_FOR_MATRIX_MULTIPLICATION_WORDS_REDUCIBLE_TO_"
            "N_TRANSPOSE_P_OF_A_N"
        ),
        "verified_replacement": (
            "At a formally allowed q(T)=q(U)=2 R2 pair, every bilinear "
            "Q[Gamma] contraction and every N^T p(A) N contraction is "
            "blind to the displayed null trade."
        ),
        "candidate_contains_explicit_limiting_text": True,
        "wording_objection": "NONBLOCKING_IF_SCOPED_REPLACEMENT_IS_USED",
    }


def add_edge(
    adjacency: dict[str, set[str]],
    left: str,
    right: str,
) -> None:
    adjacency[left].add(right)
    adjacency[right].add(left)


def derive_r2_board() -> dict[str, object]:
    """Derive the q=2 R2 board from lambda/mu and two cross edges."""

    cross = [[1, 0, 0], [0, 1, 0], [0, 0, 0]]
    row_degrees = [sum(row) for row in cross]
    column_degrees = [
        sum(cross[row][column] for row in range(3))
        for column in range(3)
    ]
    counts = []
    for row in range(3):
        count_row = []
        for column in range(3):
            adjacent = cross[row][column] == 1
            parameter = 1 if adjacent else 2
            common_inside_base = (
                row_degrees[row]
                + column_degrees[column]
                - 2 * cross[row][column]
            )
            count_row.append(parameter - common_inside_base)
        counts.append(count_row)

    row_only = [
        14 - 2 - row_degrees[row] - sum(counts[row])
        for row in range(3)
    ]
    column_only = [
        14
        - 2
        - column_degrees[column]
        - sum(counts[row][column] for row in range(3))
        for column in range(3)
    ]
    board_vertices = [
        {
            "copy": copy,
            "name": f"b{row}{column}_{copy}",
            "t_index": row,
            "u_index": column,
        }
        for row in range(3)
        for column in range(3)
        for copy in range(counts[row][column])
    ]
    candidates = [
        [item["name"] for item in triple]
        for triple in itertools.combinations(board_vertices, 3)
        if {item["t_index"] for item in triple} == {0, 1, 2}
        and {item["u_index"] for item in triple} == {0, 1, 2}
    ]
    outside_total = 99 - 6
    neither = (
        outside_total
        - len(board_vertices)
        - sum(row_only)
        - sum(column_only)
    )
    return {
        "cross_edges": [["t0", "u0"], ["t1", "u1"]],
        "counts": counts,
        "row_only": row_only,
        "column_only": column_only,
        "neither": neither,
        "outside_total": outside_total,
        "board_vertices": board_vertices,
        "candidates": candidates,
    }


def rebuild_partial_control(
    board: dict[str, object],
    close_one: bool,
) -> dict[str, object]:
    names = [f"t{i}" for i in range(3)] + [f"u{i}" for i in range(3)]
    board_vertices = board["board_vertices"]
    assert isinstance(board_vertices, list)
    board_names = [item["name"] for item in board_vertices]
    row_only = board["row_only_counts"]
    column_only = board["column_only_counts"]
    neither = board["neither_side_count"]
    assert isinstance(row_only, list)
    assert isinstance(column_only, list)
    names += board_names
    names += [
        f"rt{row}_{copy}"
        for row, count in enumerate(row_only)
        for copy in range(count)
    ]
    names += [
        f"cu{column}_{copy}"
        for column, count in enumerate(column_only)
        for copy in range(count)
    ]
    names += [f"n_{copy}" for copy in range(neither)]
    if len(names) != 99 or len(set(names)) != 99:
        raise AssertionError("independent partial control vertex census differs")

    adjacency = {name: set() for name in names}
    for triple in (
        [f"t{i}" for i in range(3)],
        [f"u{i}" for i in range(3)],
    ):
        for left, right in itertools.combinations(triple, 2):
            add_edge(adjacency, left, right)
    add_edge(adjacency, "t0", "u0")
    add_edge(adjacency, "t1", "u1")
    for item in board_vertices:
        add_edge(adjacency, f"t{item['t_index']}", item["name"])
        add_edge(adjacency, f"u{item['u_index']}", item["name"])
    for row, count in enumerate(row_only):
        for copy in range(count):
            add_edge(adjacency, f"t{row}", f"rt{row}_{copy}")
    for column, count in enumerate(column_only):
        for copy in range(count):
            add_edge(adjacency, f"u{column}", f"cu{column}_{copy}")

    selected = ["b00_0", "b11_0", "b22_0"]
    if close_one:
        for left, right in itertools.combinations(selected, 2):
            add_edge(adjacency, left, right)

    base = [f"t{i}" for i in range(3)] + [f"u{i}" for i in range(3)]
    degrees = {name: len(adjacency[name]) for name in names}
    if {name: degrees[name] for name in base} != {name: 14 for name in base}:
        raise AssertionError("independent partial base degree differs")

    cap_violations = []
    for left, right in itertools.combinations(names, 2):
        common = len(adjacency[left] & adjacency[right])
        cap = 1 if right in adjacency[left] else 2
        if common > cap:
            cap_violations.append((left, right, common, cap))
    if cap_violations:
        raise AssertionError(f"independent partial cap failure: {cap_violations}")

    for left, right in itertools.combinations(base, 2):
        common = len(adjacency[left] & adjacency[right])
        expected = 1 if right in adjacency[left] else 2
        if common != expected:
            raise AssertionError("independent base lambda/mu failure")

    candidates = board["transversal_candidates"]
    assert isinstance(candidates, list)
    closed = [
        candidate
        for candidate in candidates
        if all(
            right in adjacency[left]
            for left, right in itertools.combinations(candidate, 2)
        )
    ]
    expected_closed = [selected] if close_one else []
    if closed != expected_closed:
        raise AssertionError("independent partial closure differs")

    absent = [
        sorted((left, right))
        for left, right in itertools.combinations(board_names, 2)
        if right not in adjacency[left]
    ]
    absent.sort()
    return {
        "vertex_count": len(names),
        "edge_count": sum(degrees.values()) // 2,
        "base_degrees": {name: degrees[name] for name in base},
        "maximum_outside_degree": max(
            degree for name, degree in degrees.items() if name not in base
        ),
        "closed_candidates": closed,
        "fixed_absent_board_edges": absent,
        "all_caps_pass": True,
        "base_lambda_mu_exact": True,
    }


def board_and_partial_comparison(
    candidate: dict[str, object],
) -> dict[str, object]:
    actual = candidate["actual_incidence_board"]
    assert isinstance(actual, dict)
    if set(actual) != {
        "board",
        "partial_controls",
        "remaining_obligation",
        "rootless_clause",
    }:
        raise AssertionError("candidate actual-incidence schema differs")
    if actual["rootless_clause"] != (
        "For each of the 708 unordered R2 pairs, all four pair-indexed "
        "transversal candidates must fail to be graph triangles."
    ):
        raise AssertionError("candidate rootless clause differs")
    if actual["remaining_obligation"] != (
        "Prove that the full SRG and projector/Schur compatibility cannot "
        "keep all 2832 pair-indexed candidates open, or construct a complete "
        "endpoint satisfying them."
    ):
        raise AssertionError("candidate remaining obligation differs")
    board = actual["board"]
    partial = actual["partial_controls"]
    assert isinstance(board, dict)
    assert isinstance(partial, dict)
    if set(board) != {
        "base_pair",
        "board_size",
        "board_vertices",
        "both_side_common_neighbour_counts",
        "cell_columns",
        "cell_rows",
        "column_only_counts",
        "equivalence",
        "neither_side_count",
        "outside_vertex_total",
        "pair_indexed_candidates_at_n3_708",
        "row_only_counts",
        "transversal_candidate_count_per_R2_pair",
        "transversal_candidates",
    }:
        raise AssertionError("candidate board schema differs")
    if set(partial) != {"motif_free", "motif_one"}:
        raise AssertionError("candidate partial-control collection differs")
    derived = derive_r2_board()
    expected_board = derived["counts"]
    base_pair = board["base_pair"]
    assert isinstance(base_pair, dict)
    if set(base_pair) != {"cross_edges", "relation", "triangles"}:
        raise AssertionError("candidate base-pair schema differs")
    if base_pair["triangles"] != [
        ["t0", "t1", "t2"],
        ["u0", "u1", "u2"],
    ]:
        raise AssertionError("candidate base triangles differ")
    if base_pair["relation"] != "R2 / exactly two independent cross edges":
        raise AssertionError("candidate base relation label differs")
    if board["cell_rows"] != ["t0", "t1", "t2"]:
        raise AssertionError("candidate board row labels differ")
    if board["cell_columns"] != ["u0", "u1", "u2"]:
        raise AssertionError("candidate board column labels differ")
    if board["equivalence"] != (
        "A triangle on one board vertex from every row and every column is "
        "exactly a triangle V that is R3 from both base triangles."
    ):
        raise AssertionError("candidate transversal equivalence differs")
    board_numeric_values = [
        board["board_size"],
        board["neither_side_count"],
        board["outside_vertex_total"],
        board["pair_indexed_candidates_at_n3_708"],
        board["transversal_candidate_count_per_R2_pair"],
        *board["row_only_counts"],
        *board["column_only_counts"],
        *(
            entry
            for row in board["both_side_common_neighbour_counts"]
            for entry in row
        ),
        *(
            entry
            for item in board["board_vertices"]
            for entry in (item["copy"], item["t_index"], item["u_index"])
        ),
    ]
    if any(type(value) is not int for value in board_numeric_values):
        raise AssertionError("candidate board numeric field is not an integer")
    if base_pair["cross_edges"] != derived["cross_edges"]:
        raise AssertionError("candidate normalized R2 cross edges differ")
    if board["both_side_common_neighbour_counts"] != expected_board:
        raise AssertionError("candidate board differs")
    if board["board_vertices"] != derived["board_vertices"]:
        raise AssertionError("candidate weighted board vertices differ")
    if board["board_size"] != len(derived["board_vertices"]):
        raise AssertionError("candidate board size differs")
    if board["row_only_counts"] != derived["row_only"]:
        raise AssertionError("candidate row-only census differs")
    if board["column_only_counts"] != derived["column_only"]:
        raise AssertionError("candidate column-only census differs")
    if board["neither_side_count"] != derived["neither"]:
        raise AssertionError("candidate neither-side census differs")
    if board["outside_vertex_total"] != derived["outside_total"]:
        raise AssertionError("candidate outside census differs")
    if board["transversal_candidates"] != derived["candidates"]:
        raise AssertionError("candidate transversal enumeration differs")
    if board["transversal_candidate_count_per_R2_pair"] != len(
        derived["candidates"]
    ):
        raise AssertionError("candidate transversal count differs")
    if board["pair_indexed_candidates_at_n3_708"] != (
        708 * len(derived["candidates"])
    ):
        raise AssertionError("candidate endpoint candidate count differs")

    zero = rebuild_partial_control(board, False)
    one = rebuild_partial_control(board, True)
    submitted_zero = partial["motif_free"]
    submitted_one = partial["motif_one"]
    assert isinstance(submitted_zero, dict)
    assert isinstance(submitted_one, dict)
    comparisons = (
        (zero, submitted_zero, "motif_free"),
        (one, submitted_one, "one_closed_transversal"),
    )
    for rebuilt, submitted, expected_mode in comparisons:
        if set(submitted) != {
            "all_base_pair_lambda_mu_counts_exact",
            "all_present_pair_common_neighbour_caps_pass",
            "base_vertex_degrees",
            "closed_transversal_candidates",
            "closed_transversal_count",
            "fixed_absent_board_edges",
            "fixed_present_edge_count",
            "maximum_current_outside_degree",
            "mode",
            "scope",
            "vertex_count",
        }:
            raise AssertionError("candidate partial-control schema differs")
        if submitted["vertex_count"] != rebuilt["vertex_count"]:
            raise AssertionError("candidate partial vertex count differs")
        partial_numeric_values = [
            submitted["vertex_count"],
            submitted["closed_transversal_count"],
            submitted["fixed_present_edge_count"],
            submitted["maximum_current_outside_degree"],
            *submitted["base_vertex_degrees"].values(),
        ]
        if any(type(value) is not int for value in partial_numeric_values):
            raise AssertionError(
                "candidate partial numeric field is not an integer"
            )
        if submitted["mode"] != expected_mode:
            raise AssertionError("candidate partial mode differs")
        if submitted["closed_transversal_count"] != len(
            rebuilt["closed_candidates"]
        ):
            raise AssertionError("candidate partial closed count differs")
        if submitted["all_base_pair_lambda_mu_counts_exact"] is not True:
            raise AssertionError("candidate partial lambda/mu label differs")
        if submitted["all_present_pair_common_neighbour_caps_pass"] is not True:
            raise AssertionError("candidate partial cap label differs")
        if submitted["scope"] != (
            "A partial 99-vertex edge assignment only. Most outside-outside "
            "adjacencies and all missing outside degrees and lambda/mu "
            "completions remain unspecified. This is not an SRG extension "
            "or a graph construction."
        ):
            raise AssertionError("candidate partial scope label differs")
        if rebuilt["edge_count"] != submitted["fixed_present_edge_count"]:
            raise AssertionError("candidate partial edge count differs")
        if rebuilt["base_degrees"] != submitted["base_vertex_degrees"]:
            raise AssertionError("candidate partial base degrees differ")
        if rebuilt["maximum_outside_degree"] != (
            submitted["maximum_current_outside_degree"]
        ):
            raise AssertionError("candidate partial max degree differs")
        if rebuilt["closed_candidates"] != (
            submitted["closed_transversal_candidates"]
        ):
            raise AssertionError("candidate partial closures differ")
        submitted_absent = sorted(submitted["fixed_absent_board_edges"])
        if rebuilt["fixed_absent_board_edges"] != submitted_absent:
            raise AssertionError("candidate fixed-absent board edges differ")

    report = CANDIDATE_REPORT.read_text(encoding="utf-8")
    normalized_report = " ".join(report.split())
    partial_scope_markers = [
        "These are deliberately partial edge assignments.",
        "They are not graph constructions or extension certificates.",
        "Most outside-outside edges, outside degrees, and `lambda/mu` equations remain unspecified.",
    ]
    missing = [
        marker
        for marker in partial_scope_markers
        if " ".join(marker.split()) not in normalized_report
    ]
    if missing:
        raise AssertionError(f"partial-control scope markers missing: {missing}")

    return {
        "multiplicity_board": expected_board,
        "board_vertex_count": board["board_size"],
        "board_derived_from_lambda_mu": True,
        "transversals_independently_enumerated": True,
        "row_only_counts": board["row_only_counts"],
        "column_only_counts": board["column_only_counts"],
        "neither_side_count": board["neither_side_count"],
        "transversal_candidates": board["transversal_candidates"],
        "transversal_candidate_count_per_R2_pair": 4,
        "pair_indexed_candidate_count_at_n3_708": 2832,
        "partial_zero_rebuilt": zero,
        "partial_one_rebuilt": one,
        "partial_scope_markers_present": True,
        "global_extension_evidence": False,
    }


def independent_trace_factor() -> dict[str, int]:
    """Witness one unordered motif and evaluate the ordered trace count."""

    relation_r2 = [
        [0, 1, 0],
        [1, 0, 0],
        [0, 0, 0],
    ]
    relation_r3 = [
        [0, 0, 1],
        [0, 0, 1],
        [1, 1, 0],
    ]

    def multiply(
        left: list[list[int]],
        right: list[list[int]],
    ) -> list[list[int]]:
        return [
            [
                sum(
                    left[row][middle] * right[middle][column]
                    for middle in range(3)
                )
                for column in range(3)
            ]
            for row in range(3)
        ]

    square_r3 = multiply(relation_r3, relation_r3)
    product = multiply(relation_r2, square_r3)
    trace = sum(product[index][index] for index in range(3))
    return {
        "unordered_motifs": 1,
        "ordered_R2_orientations": 2,
        "trace": trace,
    }


def mixed_trace_and_status(candidate: dict[str, object]) -> dict[str, object]:
    trace = candidate["mixed_trace"]
    status = candidate["status"]
    objection = candidate["strongest_self_objection"]
    assert isinstance(trace, dict)
    assert isinstance(status, dict)
    assert isinstance(objection, dict)
    if set(trace) != {
        "actual_incidence_forces_positive_value",
        "identity",
        "rootless_required_value",
        "unordered_motif_multiplier",
    }:
        raise AssertionError("candidate mixed-trace schema differs")
    if set(objection) != {"disposition", "effect", "objection"}:
        raise AssertionError("candidate objection schema differs")
    if (
        type(trace["unordered_motif_multiplier"]) is not int
        or type(trace["rootless_required_value"]) is not int
    ):
        raise AssertionError("candidate trace numeric field is not an integer")
    expected_identity = (
        "tr(A_R2*A_R3^2)=sum_(ordered R2 pairs T,U) "
        "#{V: T R3 V and V R3 U}"
    )
    if trace["identity"] != expected_identity:
        raise AssertionError("candidate mixed-trace identity differs")
    if trace["unordered_motif_multiplier"] != 2:
        raise AssertionError("candidate mixed-trace factor differs")
    if trace["rootless_required_value"] != 0:
        raise AssertionError("candidate rootless trace value differs")
    if trace["actual_incidence_forces_positive_value"] != "UNKNOWN":
        raise AssertionError("candidate actual trace status inflated")
    witness = independent_trace_factor()
    if witness != {
        "unordered_motifs": 1,
        "ordered_R2_orientations": 2,
        "trace": 2,
    }:
        raise AssertionError("independent trace normalization failed")
    expected_status = {
        "Conway_99": "UNKNOWN",
        "Q_Gamma_two_leg_local_blindness": "DERIVED",
        "actual_incidence_forces_positive_mixed_trace": "UNKNOWN",
        "eight_vertex_board_and_four_candidates_per_R2_pair": "DERIVED",
        "fully_contracted_two_leg_incidence_local_blindness": "DERIVED",
        "n3_708": "UNKNOWN",
        "novelty": "UNKNOWN",
        "rootless_indecomposable_endpoint": "UNKNOWN",
    }
    if status != expected_status:
        raise AssertionError("candidate status wall differs or is inflated")
    unknown_keys = tuple(
        key for key, value in expected_status.items() if value == "UNKNOWN"
    )
    if objection["disposition"] != "VALID_AND_BLOCKING":
        raise AssertionError("candidate strongest objection not blocking")
    expected_objection = (
        "The null trade is local and the 99-vertex controls are partial. "
        "They do not prove that either table extends simultaneously across "
        "all triangle pairs, satisfies uncontracted three-leg incidence, "
        "realizes M^2=21M as a global matrix, or comes from an "
        "srg(99,14,1,2). A global compatibility theorem could still force "
        "the mixed trace positive."
    )
    if objection["objection"] != expected_objection:
        raise AssertionError("candidate strongest objection lost substance")
    if objection["effect"] != (
        "The controls delimit failed moment routes but do not exclude the "
        "rootless endpoint or change any global status."
    ):
        raise AssertionError("candidate strongest objection effect differs")

    return {
        "mixed_trace_identity": trace["identity"],
        "unordered_motif_multiplier": 2,
        "independent_one_motif_trace_witness": witness,
        "rootless_required_trace": 0,
        "candidate_global_statuses": {
            key: status[key] for key in unknown_keys
        },
        "strongest_self_objection_preserved": True,
    }


def static_source_audit() -> dict[str, object]:
    source = (CANDIDATE_DIR / "exact_check.py").read_text(encoding="utf-8")
    tests = (CANDIDATE_DIR / "test_exact_check.py").read_text(encoding="utf-8")
    forbidden_runtime_markers = (
        "subprocess.",
        "os.system",
        "eval(",
        "exec(",
    )
    found = [
        marker for marker in forbidden_runtime_markers if marker in source
    ]
    if found:
        raise AssertionError(f"candidate source runtime markers found: {found}")
    test_count = tests.count("    def test_")
    if test_count != 14:
        raise AssertionError(f"candidate static test count differs: {test_count}")
    return {
        "candidate_source_read_statically": True,
        "candidate_source_imported": False,
        "candidate_source_executed": False,
        "candidate_test_file_imports_discovery_code": "import exact_check" in tests,
        "candidate_static_test_method_count": test_count,
        "candidate_runtime_markers_found": found,
        "independent_verifier_substitutes_for_candidate_test_independence": True,
    }


def build_comparison() -> dict[str, object]:
    provenance = provenance_validation()
    candidate = load_candidate_results()
    return {
        "schema_version": 1,
        "role": "clean_room_adversarial_verifier_candidate_comparison",
        "verdict": "PASS_SCOPED_WITH_NONBLOCKING_WORDING_QUALIFIER",
        "provenance": provenance,
        "candidate_metadata": metadata_comparison(candidate),
        "algebra": algebra_comparison(candidate),
        "formal_local_tables": table_comparison(candidate),
        "incidence_transport_and_scope": transport_comparison(candidate),
        "actual_board_and_partial_controls": board_and_partial_comparison(candidate),
        "mixed_trace_and_status": mixed_trace_and_status(candidate),
        "static_source_audit": static_source_audit(),
        "obligations": {
            "QGamma_basis_and_multiplication": "PASS",
            "formal_q2_R2_table_feasibility": "PASS",
            "all_bilinear_QGamma_contractions": "PASS_SCOPED",
            "global_realizability_of_local_tables": "UNKNOWN",
            "N_transpose_Ak_N_closure": "PASS",
            "arbitrary_two_leg_incidence_statistic_closure": "NOT_ESTABLISHED",
            "R2_multiplicity_board": "PASS",
            "four_weighted_transversal_candidates": "PASS",
            "transversal_triangle_equivalence": "PASS",
            "partial_control_arithmetic": "PASS",
            "partial_control_extendibility": "UNKNOWN",
            "mixed_trace_factor_two": "PASS",
            "actual_global_motif_forcing": "UNKNOWN",
            "actual_global_motif_avoidance": "UNKNOWN",
            "rootless_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "candidate_code_imported_or_executed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = independent.canonical_bytes(build_comparison())
    if args.output:
        args.output.write_bytes(encoded)
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
