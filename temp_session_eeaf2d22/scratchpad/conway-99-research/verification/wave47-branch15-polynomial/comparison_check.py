#!/usr/bin/env python3
"""Compare the sealed Wave47 package with the frozen clean-room calculation.

The discovery module is never imported or executed.  This checker loads its
JSON claim as untrusted data and independently reconstructs the byte-level
hash encodings that the sealed package commits to.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DISCOVERY_RESULT = (
    ROOT / "attempts/wave47-branch15-polynomial/degree2-window-result.json"
)
INDEPENDENT_RESULT = HERE / "independent-result.json"


def load_independent_module():
    path = HERE / "independent_check.py"
    spec = importlib.util.spec_from_file_location("wave47_cleanroom_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load clean-room verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


V = load_independent_module()


def row_bytes(row: int) -> bytes:
    return row.to_bytes((row.bit_length() + 7) // 8, "little")


def row_catalog_hash(rows: Iterable[int]) -> str:
    digest = hashlib.sha256()
    for index, row in enumerate(rows, 1):
        payload = row_bytes(row)
        digest.update(f"{index}:{len(payload)}:".encode("ascii"))
        digest.update(payload)
        digest.update(b"\n")
    return digest.hexdigest()


def echelon_hash(pivots: dict[int, int]) -> str:
    digest = hashlib.sha256()
    for pivot in sorted(pivots):
        payload = row_bytes(pivots[pivot])
        digest.update(f"{pivot}:{len(payload)}:".encode("ascii"))
        digest.update(payload)
        digest.update(b"\n")
    return digest.hexdigest()


def rref_lowest(rows: Iterable[int]) -> dict[int, int]:
    pivots: dict[int, int] = {}
    for row in rows:
        reduced = row
        while reduced:
            low = reduced & -reduced
            pivot = low.bit_length() - 1
            prior = pivots.get(pivot)
            if prior is None:
                pivots[pivot] = reduced
                break
            reduced ^= prior
    for pivot in sorted(pivots, reverse=True):
        reducer = pivots[pivot]
        for lower in sorted(key for key in pivots if key < pivot):
            if (pivots[lower] >> pivot) & 1:
                pivots[lower] ^= reducer
    return pivots


def rref_highest(rows: Iterable[int]) -> dict[int, int]:
    basis = V.XorBasis(rows)
    return {row.bit_length() - 1: row for row in basis.canonical_rows()}


class OrderedReducer:
    def __init__(self, max_linear_column: int) -> None:
        self.pivots: dict[int, int] = {}
        self.low_queue: list[int] = []
        self.max_linear_column = max_linear_column
        self.input_rows = 0
        self.zero_rows = 0

    def add(self, row: int) -> None:
        self.input_rows += 1
        while row:
            pivot = row.bit_length() - 1
            prior = self.pivots.get(pivot)
            if prior is None:
                self.pivots[pivot] = row
                if pivot <= self.max_linear_column:
                    self.low_queue.append(row)
                return
            row ^= prior
        self.zero_rows += 1


def exact_blocks(
    assignments: dict[int, bool],
) -> list[dict[str, object]]:
    labels, _edges, variable = V.scaffold()
    blocks = []
    for label_index, label in enumerate(labels):
        for coordinate in range(14):
            fibre = [
                other
                for other, other_label in enumerate(labels)
                if coordinate in other_label and other != label_index
            ]
            complete = tuple(
                variable[tuple(sorted((label_index, other)))] for other in fibre
            )
            target = 2 - int(coordinate in label) - int((coordinate ^ 1) in label)
            remaining = tuple(item for item in complete if item not in assignments)
            target -= sum(assignments.get(item) is True for item in complete)
            blocks.append(
                {
                    "variables": complete,
                    "remaining": remaining,
                    "target": target,
                }
            )
    blocks.sort(key=lambda item: item["variables"])
    V.require(len(blocks) == 1_176, "exact-block catalogue changed")
    return blocks


def slice_rows(
    variables: tuple[int, ...],
    target: int,
    mapping,
) -> tuple[list[int], int, str]:
    terms = V.local_terms(len(variables))
    evaluations = [
        V.evaluation_row(frozenset(chosen), terms)
        for chosen in itertools.combinations(range(len(variables)), target)
    ]
    evaluation_rref, kernel = V.nullspace(evaluations, len(terms))
    rows = [
        V.embed_local_polynomial(row, variables, terms, mapping) for row in kernel
    ]
    digest = hashlib.sha256()
    for row in rows:
        payload = row_bytes(row)
        digest.update(f"{len(payload)}:".encode("ascii"))
        digest.update(payload)
        digest.update(b"\n")
    return rows, len(evaluation_rref), digest.hexdigest()


def multiply_linear(row: int, variable: int, mapping) -> int:
    return V.multiply_affine_by_variable(
        row, mapping.variable_position[variable], mapping
    )


def quotient_relations(
    initial_rows: Iterable[int], consequence_rows: Iterable[int]
) -> list[int]:
    pivots = rref_highest(initial_rows)
    result: list[int] = []
    for row in sorted(consequence_rows, reverse=True):
        while row:
            pivot = row.bit_length() - 1
            prior = pivots.get(pivot)
            if prior is None:
                pivots[pivot] = row
                result.append(row)
                break
            row ^= prior
    return result


def active_histograms(
    assignments: dict[int, bool], all_windows: Sequence
) -> tuple[list[Counter[int]], list[Counter[int]]]:
    active = [Counter() for _ in all_windows]
    wave43 = [Counter() for _ in all_windows]
    for path in (V.BASE, V.W42, V.W43):
        for _row, _raw, constraint in V.iter_formula(path):
            if not (
                constraint.operator == ">="
                and constraint.bound == 1
                and all(term.coefficient == 1 for term in constraint.terms)
            ):
                continue
            state, residual = V.simplify_clause(constraint, assignments)
            if state != "ACTIVE":
                continue
            variables = [variable for variable, _positive in residual]
            for window_index in V.window_memberships(variables, all_windows):
                active[window_index][len(residual)] += 1
                if path == V.W43:
                    wave43[window_index][len(residual)] += 1
    return active, wave43


def analyze(
    window,
    assignments: dict[int, bool],
    blocks: Sequence[dict[str, object]],
    clause_catalogue: Sequence[dict[str, object]],
    active_widths: Counter[int],
    wave43_widths: Counter[int],
    include_clauses: bool,
) -> tuple[dict[str, object], list[int]]:
    mapping = V.monomial_map(window.free_variables)
    window_variables = set(window.variables)
    local_blocks = [
        block for block in blocks if set(block["variables"]).issubset(window_variables)
    ]
    V.require(len(local_blocks) == 48, "local exact-block count changed")

    axiom_rows: list[int] = []
    slice_histogram = Counter()
    outer_slice_digest = hashlib.sha256()
    initial_linear_rows: list[int] = []
    for block_index, block in enumerate(local_blocks, 1):
        remaining = tuple(block["remaining"])
        target = int(block["target"])
        rows, evaluation_rank, relation_hash = slice_rows(
            remaining, target, mapping
        )
        axiom_rows.extend(rows)
        slice_histogram[
            f"n={len(remaining)},t={target},rank={evaluation_rank}"
        ] += 1
        outer_slice_digest.update(
            f"{block_index}:{relation_hash}\n".encode("ascii")
        )
        parity = target & 1
        for variable in remaining:
            parity ^= 1 << (1 + mapping.variable_position[variable])
        initial_linear_rows.append(parity)

    degree2_rows: list[int] = []
    if include_clauses:
        for item in clause_catalogue:
            residual = tuple(
                (literal["variable"], literal["positive"])
                for literal in item["literals"]
            )
            degree2_rows.append(V.clause_polynomial(residual, mapping))
        axiom_rows.extend(degree2_rows)

    reducer = OrderedReducer(len(mapping.free_variables))
    for row in axiom_rows:
        reducer.add(row)
    processed: set[int] = set()
    rounds = 0
    multiplied = 0
    while True:
        pending = [row for row in reducer.low_queue if row not in processed]
        if not pending:
            break
        rounds += 1
        reducer.low_queue.clear()
        for row in pending:
            processed.add(row)
            if row == 1:
                continue
            for variable in mapping.free_variables:
                reducer.add(multiply_linear(row, variable, mapping))
                multiplied += 1

    initial_basis = rref_lowest(initial_linear_rows)
    final_basis = rref_highest(
        row
        for row in reducer.pivots.values()
        if row and row.bit_length() - 1 <= len(mapping.free_variables)
    )
    new_rows = quotient_relations(initial_basis.values(), final_basis.values())
    relation_records = []
    labels, edges, _variable = V.scaffold()
    for row in new_rows:
        variables = [
            mapping.free_variables[column - 1]
            for column in range(1, len(mapping.free_variables) + 1)
            if (row >> column) & 1
        ]
        common: set[int] | None = None
        decoded_edges = []
        for variable in variables:
            left, right = edges[variable - 1]
            coordinates = set(labels[left]).intersection(labels[right])
            common = coordinates if common is None else common.intersection(coordinates)
            decoded_edges.append(
                {
                    "variable": variable,
                    "residual_vertices": [left, right],
                    "residual_labels": [list(labels[left]), list(labels[right])],
                }
            )
        relation_records.append(
            {
                "constant": int(bool(row & 1)),
                "variables": variables,
                "decoded_edges": decoded_edges,
                "support_common_coordinates": sorted(common or ()),
                "term_count": len(variables) + int(bool(row & 1)),
                "row_sha256": hashlib.sha256(row_bytes(row)).hexdigest(),
            }
        )
    assignments_found = []
    for pivot, row in sorted(final_basis.items()):
        if pivot and (row & ~1).bit_count() == 1:
            assignments_found.append(
                {
                    "variable": mapping.free_variables[pivot - 1],
                    "value": bool(row & 1),
                }
            )
    degree_pivots = Counter(
        0 if pivot == 0
        else 1 if pivot <= len(mapping.free_variables)
        else 2
        for pivot in reducer.pivots
    )
    record = {
        "pair_index": window.index,
        "coordinates": list(window.coordinates),
        "residual_vertices": len(window.vertices),
        "window_variables": len(window.variables),
        "free_variables_after_wave42_closure": len(window.free_variables),
        "fixed_variables_from_wave42_closure": len(window.variables) - len(window.free_variables),
        "monomial_columns": mapping.column_count,
        "monomial_columns_by_degree": {
            "0": 1,
            "1": len(window.free_variables),
            "2": mapping.column_count - len(window.free_variables) - 1,
        },
        "exact_blocks": len(local_blocks),
        "exact_block_residual_histogram": dict(sorted(slice_histogram.items())),
        "active_clause_residual_width_histogram": {
            str(key): value for key, value in sorted(active_widths.items())
        },
        "wave43_active_clause_residual_width_histogram": {
            str(key): value for key, value in sorted(wave43_widths.items())
        },
        "degree2_clause_rows": len(degree2_rows),
        "axiom_rows": len(axiom_rows),
        "axiom_catalog_sha256": row_catalog_hash(axiom_rows),
        "slice_relation_catalog_sha256": outer_slice_digest.hexdigest(),
        "saturation_rounds": rounds,
        "multiplied_linear_rows": multiplied,
        "macaulay_input_rows": reducer.input_rows,
        "macaulay_zero_rows": reducer.zero_rows,
        "macaulay_rank": len(reducer.pivots),
        "pivot_histogram_by_degree": {
            str(key): value for key, value in sorted(degree_pivots.items())
        },
        "echelon_sha256": echelon_hash(reducer.pivots),
        "initial_linear_rank": len(initial_basis),
        "final_linear_rank": len(final_basis),
        "final_linear_rref_sha256": row_catalog_hash(
            final_basis[pivot] for pivot in sorted(final_basis)
        ),
        "new_linear_rank": len(new_rows),
        "new_linear_relation_catalog_sha256": row_catalog_hash(new_rows),
        "new_linear_relations": relation_records,
        "contradiction_derived": final_basis.get(0) == 1,
        "new_assignments": assignments_found,
    }
    return record, list(final_basis.values())


def compare_record(
    independent: dict[str, object],
    discovery: dict[str, object],
) -> list[str]:
    fields = [
        "pair_index", "coordinates", "residual_vertices", "window_variables",
        "free_variables_after_wave42_closure", "fixed_variables_from_wave42_closure",
        "monomial_columns", "monomial_columns_by_degree", "exact_blocks",
        "exact_block_residual_histogram", "active_clause_residual_width_histogram",
        "wave43_active_clause_residual_width_histogram", "axiom_rows",
        "axiom_catalog_sha256", "slice_relation_catalog_sha256",
        "saturation_rounds", "multiplied_linear_rows", "macaulay_input_rows",
        "macaulay_zero_rows", "macaulay_rank", "pivot_histogram_by_degree",
        "echelon_sha256", "initial_linear_rank", "final_linear_rank",
        "final_linear_rref_sha256", "new_linear_rank",
        "new_linear_relation_catalog_sha256", "contradiction_derived",
    ]
    mismatches = [
        field for field in fields if independent[field] != discovery.get(field)
    ]
    if independent["degree2_clause_rows"] != discovery["axiom_rows_by_type"]["active_clause_degree2_relations"]:
        mismatches.append("axiom_rows_by_type.active_clause_degree2_relations")
    expected_relations = independent["new_linear_relations"]
    actual_relations = discovery.get("new_linear_relations")
    if not isinstance(actual_relations, list) or len(expected_relations) != len(actual_relations):
        mismatches.append("new_linear_relations.length")
    else:
        relation_fields = (
            "constant", "variables", "decoded_edges", "support_common_coordinates",
            "term_count", "row_sha256",
        )
        for index, (expected, actual) in enumerate(zip(expected_relations, actual_relations)):
            for field in relation_fields:
                if expected[field] != actual.get(field):
                    mismatches.append(f"new_linear_relations[{index}].{field}")
    if independent["new_assignments"] != [
        {"variable": item["variable"], "value": item["value"]}
        for item in discovery.get("new_assignments", [])
    ]:
        mismatches.append("new_assignments")
    return mismatches


def compute() -> dict[str, object]:
    discovery = V.strict_json(DISCOVERY_RESULT)
    independent_precomparison = V.strict_json(INDEPENDENT_RESULT)
    certificate = V.strict_json(V.CLOSURE_CERT)
    assignments = {
        int(item["variable"]): bool(item["value"])
        for item in certificate["derivations"]
    }
    all_windows = V.windows(assignments)
    blocks = exact_blocks(assignments)
    clause_catalogues, _statistics = V.eligible_clause_catalogues(
        assignments, all_windows
    )
    active_widths, wave43_widths = active_histograms(assignments, all_windows)
    discovery_windows = discovery.get("windows")
    V.require(isinstance(discovery_windows, list) and len(discovery_windows) == 7,
              "discovery window list malformed")

    records = []
    all_mismatches: list[str] = []
    for window in all_windows:
        full, full_linear_rows = analyze(
            window, assignments, blocks, clause_catalogues[window.index],
            active_widths[window.index], wave43_widths[window.index], True,
        )
        control, control_linear_rows = analyze(
            window, assignments, blocks, (), Counter(), Counter(), False,
        )
        claimed = discovery_windows[window.index]
        mismatches = compare_record(full, claimed)
        control_claim = claimed.get("exact_blocks_only_control")
        V.require(isinstance(control_claim, dict), "missing exact-only control")
        control_fields = (
            "axiom_rows", "macaulay_input_rows", "macaulay_rank",
            "initial_linear_rank", "final_linear_rank", "new_linear_rank",
            "contradiction_derived", "final_linear_rref_sha256",
        )
        for field in control_fields:
            if control[field] != control_claim.get(field):
                mismatches.append(f"exact_blocks_only_control.{field}")
        full_basis = V.XorBasis(full_linear_rows)
        control_basis = V.XorBasis(control_linear_rows)
        mutual = (
            all(control_basis.reduce(row) == 0 for row in full_linear_rows)
            and all(full_basis.reduce(row) == 0 for row in control_linear_rows)
        )
        if not mutual or control_claim.get("full_and_control_linear_spaces_equal") is not True:
            mismatches.append("exact_blocks_only_control.mutual_rowspace_equality")

        pre = independent_precomparison["windows"][window.index]
        pre_fields = {
            "free_variables_after_wave42_closure": len(pre["free_variables"]),
            "initial_linear_rank": pre["initial_linear_rank"],
            "macaulay_rank": pre["saturated_rank"],
            "final_linear_rank": pre["final_linear_rank"],
            "new_linear_rank": pre["new_linear_rank"],
            "contradiction_derived": pre["contradiction"],
        }
        for field, value in pre_fields.items():
            if full[field] != value:
                mismatches.append(f"precomparison.{field}")
        records.append(
            {
                "pair_index": window.index,
                "mismatches": sorted(set(mismatches)),
                "hashes": {
                    key: full[key]
                    for key in (
                        "axiom_catalog_sha256",
                        "slice_relation_catalog_sha256",
                        "echelon_sha256",
                        "final_linear_rref_sha256",
                        "new_linear_relation_catalog_sha256",
                    )
                },
                "ranks": {
                    "initial": full["initial_linear_rank"],
                    "macaulay": full["macaulay_rank"],
                    "final_linear": full["final_linear_rank"],
                    "new_linear": full["new_linear_rank"],
                },
                "new_assignment_count": len(full["new_assignments"]),
                "exact_only_mutual_rowspace_equality": mutual,
            }
        )
        all_mismatches.extend(
            f"window[{window.index}].{item}" for item in mismatches
        )

    independent_partition = independent_precomparison["wave43_degree_four_partition"]
    aggregate = discovery.get("aggregate")
    V.require(isinstance(aggregate, dict), "discovery aggregate missing")
    aggregate_checks = {
        "windows": aggregate.get("windows") == 7,
        "new_linear_rank_total": aggregate.get("new_linear_rank_total") == 13,
        "new_assignments_total": aggregate.get("new_assignments_total") == 0,
        "windows_deriving_contradiction": aggregate.get("windows_deriving_contradiction") == 0,
        "wave43_active_rows_in_windows": (
            aggregate.get("wave43_active_rows_in_windows")
            == independent_partition["active_rows"]
            == 34_340
        ),
        "wave43_degree_barrier": (
            aggregate.get("wave43_degree_at_least_four_barrier") is True
            and independent_partition["all_negative_width_four"] is True
        ),
    }
    if not all(aggregate_checks.values()):
        all_mismatches.extend(
            f"aggregate.{key}" for key, passed in aggregate_checks.items() if not passed
        )
    return {
        "format": "wave47-branch15-polynomial-comparison-v1",
        "role": "verifier",
        "claim_label": "VERIFIED_SCOPED" if not all_mismatches else "REFUTED",
        "discovery_result_sha256": V.sha256_file(DISCOVERY_RESULT),
        "precomparison_result_sha256": V.sha256_file(INDEPENDENT_RESULT),
        "windows": records,
        "aggregate_checks": aggregate_checks,
        "mismatches": all_mismatches,
        "zero_new_assignments_interpretation": (
            "The sealed claim is zero newly forced single-variable assignments; "
            "it is not a claim that the literal all-zero vector satisfies the "
            "affine exact-count theory."
        ),
        "scope_wall": {
            "branch_15": "UNKNOWN",
            "endpoint_exclusion": "UNKNOWN",
            "strict_upper_bound": "UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
    }


def validate(result: dict[str, object]) -> None:
    V.require(result["format"] == "wave47-branch15-polynomial-comparison-v1", "bad format")
    V.require(result["claim_label"] == "VERIFIED_SCOPED", "comparison has mismatches")
    V.require(result["mismatches"] == [], "nonempty mismatch list")
    V.require(all(result["aggregate_checks"].values()), "aggregate check failed")
    for window in result["windows"]:
        V.require(window["mismatches"] == [], "window mismatch")
        V.require(window["exact_only_mutual_rowspace_equality"] is True, "control mismatch")
        V.require(window["new_assignment_count"] == 0, "unexpected new assignment")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--compute", metavar="OUTPUT")
    group.add_argument("--validate", metavar="INPUT")
    args = parser.parse_args()
    if args.compute:
        result = compute()
        Path(args.compute).write_bytes(V.canonical(result))
    else:
        result = V.strict_json(Path(args.validate))
    validate(result)
    print("PASS: all sealed Wave47 hashes and scoped claims match clean-room replay")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
