#!/usr/bin/env python3
"""Standard-library exact checker for the orbit-refined affine witness.

The checker performs no optimization.  It regenerates every
locally admissible class through order seven, every vertex and pair orbit, and
all one-vertex extension coefficients.  It then checks the frozen affine
family using exact integer arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Mapping, Sequence

import model


Z_MIN = 353
Z_MAX = 705
FULL_RANK_PRIMES = {1: 3, 2: 2, 3: 5, 4: 3}
WINDOWS_ABSOLUTE_PATH = re.compile(r"(?:^|[^A-Za-z])([A-Za-z]):[\\/]")


def rank_mod(matrix: Sequence[Sequence[int]], prime: int) -> int:
    rows = [[value % prime for value in row] for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0]) if rows else 0
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(pivot_row, row_count)
                if rows[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], -1, prime)
        rows[pivot_row] = [
            value * inverse % prime for value in rows[pivot_row]
        ]
        for row in range(pivot_row + 1, row_count):
            if rows[row][column] == 0:
                continue
            factor = rows[row][column]
            rows[row] = [
                (left - factor * right) % prime
                for left, right in zip(rows[row], rows[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def exact_matvec(
    matrix: Sequence[Sequence[int]],
    vector: Sequence[int],
) -> tuple[int, ...]:
    return tuple(
        sum(coefficient * value for coefficient, value in zip(row, vector))
        for row in matrix
    )


def require_plain_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise AssertionError(f"{label} is not a plain integer")
    return value


def reject_private_paths(value: object, location: str = "payload") -> None:
    """Fail closed if a public artifact contains a Windows absolute path."""
    if isinstance(value, str):
        lowered = value.casefold().replace("\\", "/")
        if "/users/" in lowered or WINDOWS_ABSOLUTE_PATH.search(value):
            raise AssertionError(f"{location} contains a private absolute path")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            reject_private_paths(child, f"{location}.{key}")
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            reject_private_paths(child, f"{location}[{index}]")


def parse_count_record(
    record: object,
    expected_mask: int,
    label: str,
) -> tuple[int, int]:
    if not isinstance(record, dict) or set(record) != {
        "canonical_mask",
        "count_at_z_min",
        "delta_per_z",
    }:
        raise AssertionError(f"{label} has a malformed record")
    mask = require_plain_int(record["canonical_mask"], f"{label} mask")
    base = require_plain_int(record["count_at_z_min"], f"{label} base")
    delta = require_plain_int(record["delta_per_z"], f"{label} delta")
    if mask != expected_mask:
        raise AssertionError(f"{label} mask/order differs from exact census")
    return base, delta


def validate_lower_counts(
    payload: Mapping[str, object],
) -> tuple[tuple[int, ...], dict[str, int]]:
    records = payload.get("independent_lower_counts")
    if not isinstance(records, list) or len(records) != 5:
        raise AssertionError("lower-count chain must contain orders 1,...,5")
    previous: tuple[int, ...] | None = None
    ranks: dict[str, int] = {}
    for order, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise AssertionError(f"order-{order} lower record is malformed")
        if record.get("order") != order:
            raise AssertionError("lower-count orders are missing or reordered")
        masks = record.get("canonical_masks")
        counts = record.get("counts")
        expected_masks = model.locally_admissible_classes(order)
        if masks != list(expected_masks):
            raise AssertionError(f"order-{order} masks differ from exact census")
        if not isinstance(counts, list) or len(counts) != len(expected_masks):
            raise AssertionError(f"order-{order} count vector has wrong length")
        parsed = tuple(
            require_plain_int(value, f"order-{order} count {index}")
            for index, value in enumerate(counts)
        )
        if any(value < 0 for value in parsed):
            raise AssertionError(f"order-{order} count vector is negative")
        if sum(parsed) != math.comb(model.N, order):
            raise AssertionError(f"order-{order} counts have wrong total")
        if order == 1:
            if parsed != (model.N,):
                raise AssertionError("order-one base count is not n")
        else:
            assert previous is not None
            transition = model.build_transition(order - 1)
            actual = exact_matvec(transition["matrix_rows"], parsed)
            expected = model.transition_rhs(transition, previous)
            if actual != expected:
                bad = [
                    index
                    for index, pair in enumerate(zip(actual, expected))
                    if pair[0] != pair[1]
                ]
                raise AssertionError(
                    f"order-{order-1}->{order} extension rows fail: {bad[:10]}"
                )
            prime = FULL_RANK_PRIMES[order - 1]
            rank = rank_mod(transition["matrix_rows"], prime)
            if rank != len(parsed):
                raise AssertionError(
                    f"order-{order-1}->{order} uniqueness rank is {rank}"
                )
            ranks[f"{order-1}->{order}_mod_{prime}"] = rank
        previous = parsed
    assert previous is not None
    return previous, ranks


def validate_witness(
    payload: Mapping[str, object],
    witness_path: Path | None = None,
) -> dict[str, object]:
    reject_private_paths(payload)
    if payload.get("schema_version") != 1:
        raise AssertionError("unsupported witness schema")
    expected_parameters = {
        "n": model.N,
        "k": model.K,
        "lambda": model.LAMBDA,
        "mu": model.MU,
        "n3": model.N3,
        "z_min": Z_MIN,
        "z_max": Z_MAX,
        "h11_min": 4 * Z_MIN,
        "h11_max": 4 * Z_MAX,
    }
    if payload.get("parameters") != expected_parameters:
        raise AssertionError("parameter block differs from frozen scope")

    five_counts, lower_ranks = validate_lower_counts(payload)

    # Independently force the six-vector from the order-five counts plus n3.
    transition5 = model.build_transition(5)
    source_by_mask = dict(zip(model.SOURCE_N_MASKS, model.SIX_COUNTS))
    six_counts = tuple(
        source_by_mask[mask] for mask in transition5["upper_classes"]
    )
    actual5 = exact_matvec(transition5["matrix_rows"], six_counts)
    expected5 = model.transition_rhs(transition5, five_counts)
    if actual5 != expected5:
        bad = [
            index
            for index, pair in enumerate(zip(actual5, expected5))
            if pair[0] != pair[1]
        ]
        raise AssertionError(f"source six-vector fails 5->6 rows {bad[:10]}")
    rank5 = rank_mod(transition5["matrix_rows"], 7)
    if rank5 != 61:
        raise AssertionError(f"unexpected 5->6 rank mod 7: {rank5}")
    n3_column = transition5["upper_classes"].index(model.SOURCE_N_MASKS[2])
    selector5 = [
        1 if column == n3_column else 0
        for column in range(len(six_counts))
    ]
    if rank_mod(tuple(transition5["matrix_rows"]) + (tuple(selector5),), 7) != 62:
        raise AssertionError("n3 coordinate does not close the 5->6 rank defect")
    if six_counts[n3_column] != model.N3:
        raise AssertionError("source N3 coordinate is not 705")

    transition6 = model.build_transition(6)
    family = payload.get("order_seven_affine_family")
    if not isinstance(family, dict):
        raise AssertionError("missing affine-family block")
    if family.get("coordinate") != "z=h11/4":
        raise AssertionError("affine coordinate differs")
    records = family.get("records")
    classes7 = transition6["upper_classes"]
    if not isinstance(records, list) or len(records) != len(classes7):
        raise AssertionError("affine family must contain all 208 classes")
    parsed = [
        parse_count_record(record, mask, f"seven-class {index}")
        for index, (record, mask) in enumerate(zip(records, classes7))
    ]
    base = tuple(pair[0] for pair in parsed)
    delta = tuple(pair[1] for pair in parsed)
    at_max = tuple(
        value + (Z_MAX - Z_MIN) * step
        for value, step in zip(base, delta)
    )
    if min(base) < 0 or min(at_max) < 0:
        raise AssertionError("affine count is negative at an interval endpoint")
    if sum(base) != math.comb(model.N, 7) or sum(delta) != 0:
        raise AssertionError("affine seven-count total is wrong")

    rhs6 = model.transition_rhs(transition6, six_counts)
    if exact_matvec(transition6["matrix_rows"], base) != rhs6:
        raise AssertionError("z-min affine base fails a 6->7 extension row")
    zero = (0,) * len(transition6["matrix_rows"])
    if exact_matvec(transition6["matrix_rows"], delta) != zero:
        raise AssertionError("affine delta is outside the 6->7 kernel")

    rank6 = rank_mod(transition6["matrix_rows"], 5)
    if rank6 != 207:
        raise AssertionError(f"unexpected 6->7 rank mod 5: {rank6}")
    h_masks = model.source_h_masks()
    h11_column = classes7.index(h_masks[11])
    selector6 = [
        1 if column == h11_column else 0
        for column in range(len(classes7))
    ]
    if rank_mod(tuple(transition6["matrix_rows"]) + (tuple(selector6),), 5) != 208:
        raise AssertionError("H11 coordinate does not close the 6->7 rank defect")
    if base[h11_column] != 4 * Z_MIN or delta[h11_column] != 4:
        raise AssertionError("affine coordinate is not H11=4z")

    # Compare source formulas after deriving the family from only H11.
    comparison = payload.get("hamiltonian_comparison")
    if not isinstance(comparison, dict):
        raise AssertionError("missing Hamiltonian comparison")
    if comparison.get("solver_inputs") != ["H_11=4z"]:
        raise AssertionError("solver-input disclosure differs")
    expected_not_inputs = [
        f"H_{index}" for index in range(19) if index != 11
    ]
    if comparison.get("not_solver_inputs") != expected_not_inputs:
        raise AssertionError("non-input Hamiltonian disclosure differs")
    h_records = comparison.get("records")
    if not isinstance(h_records, list) or len(h_records) != 19:
        raise AssertionError("Hamiltonian comparison is incomplete")
    source_min = model.published_hamiltonian_counts(model.N3, 4 * Z_MIN)
    source_next = model.published_hamiltonian_counts(
        model.N3, 4 * (Z_MIN + 1)
    )
    for index, (record, mask) in enumerate(zip(h_records, h_masks)):
        column = classes7.index(mask)
        expected_record = {
            "source_index": index,
            "canonical_mask": mask,
            "count_at_z_min": base[column],
            "delta_per_z": delta[column],
            "used_as_solver_input": index == 11,
        }
        if record != expected_record:
            raise AssertionError(f"Hamiltonian comparison H_{index} differs")
        if base[column] != source_min[index]:
            raise AssertionError(f"source formula H_{index} differs at z_min")
        if base[column] + delta[column] != source_next[index]:
            raise AssertionError(f"source formula H_{index} has different slope")

    result = {
        "schema_version": 1,
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": (
            "Exact feasibility of all orbit-refined one-vertex extension "
            "equations through order seven, at n3=705 for every "
            "h11=4z with z=353,...,705"
        ),
        "parameters": expected_parameters,
        "census": {
            "unlabeled_counts_by_order": {
                str(order): len(model.locally_admissible_classes(order))
                for order in range(1, 8)
            },
            "labeled_order_seven": len(
                model.admissible_labeled_masks(7)
            ),
        },
        "source_independence_gate": {
            "lower_transition_ranks": lower_ranks,
            "five_to_six_rows": len(transition5["matrix_rows"]),
            "five_to_six_rank_mod_7": rank5,
            "n3_coordinate_closes_rank": True,
            "all_source_six_counts_pass": True,
        },
        "order_seven_system": {
            "rows": len(transition6["matrix_rows"]),
            "columns": len(classes7),
            "row_breakdown": {
                "deletion": sum(
                    record["kind"] == "deletion"
                    for record in transition6["row_records"]
                ),
                "vertex_orbit": sum(
                    record["kind"] == "vertex"
                    for record in transition6["row_records"]
                ),
                "edge_pair_orbit": sum(
                    record["kind"] == "pair" and record["is_edge"]
                    for record in transition6["row_records"]
                ),
                "nonedge_pair_orbit": sum(
                    record["kind"] == "pair" and not record["is_edge"]
                    for record in transition6["row_records"]
                ),
            },
            "rank_mod_5": rank6,
            "rational_rank": 207,
            "rational_rank_reason": (
                "rank mod 5 is 207 and the nonzero exact integer delta "
                "is a kernel vector"
            ),
            "h11_coordinate_closes_rank_mod_5": True,
            "all_base_rows": "PASS",
            "all_delta_rows": "PASS",
            "minimum_at_z_min": min(base),
            "minimum_at_z_max": min(at_max),
            "support_at_z_min": sum(value > 0 for value in base),
            "support_at_z_max": sum(value > 0 for value in at_max),
            "integer_values_for_all_integer_z": True,
            "nonnegative_for_full_real_interval": True,
        },
        "hamiltonian_formulas": {
            "classification": "CITED_SOURCE_FORMULAS_COMPATIBLE",
            "only_H11_used_to_parameterize": True,
            "other_18_match_derived_affine_coordinates": True,
            "panel_alignment_is_pinned_source_interpretation": True,
        },
        "conclusion": {
            "full_allowed_interval": "EXACTLY_FEASIBLE",
            "new_lower_bound_beyond_n3_705": None,
            "graph_construction": False,
            "conway_99_status": "UNKNOWN",
        },
    }
    if witness_path is not None:
        try:
            display_path = witness_path.resolve().relative_to(
                Path.cwd().resolve()
            ).as_posix()
        except ValueError:
            display_path = witness_path.name
        result["witness"] = {
            "path": display_path,
            "sha256": hashlib.sha256(witness_path.read_bytes()).hexdigest(),
        }
    return result


def canonical_json_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--witness",
        type=Path,
        default=Path(__file__).with_name("affine-witness.json"),
    )
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args(argv)
    try:
        with arguments.witness.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        result = validate_witness(payload, arguments.witness)
    except (
        AssertionError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
    ) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    output = canonical_json_bytes(result)
    if arguments.output:
        arguments.output.write_bytes(output)
    else:
        sys.stdout.buffer.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
