#!/usr/bin/env python3
"""Independent standard-library checker for Wave 63 certificates."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
INPUT = ROOT / "attempts/wave60-c3-incidence-design/component-census.json"
WAVE60_RESULTS = ROOT / "attempts/wave60-c3-incidence-design/exact-results.json"
WAVE61_RESULTS = ROOT / "attempts/wave61-c3-finite-field/exact-results.json"
FROZEN = {
    "attempts/wave60-c3-incidence-design/component-census.json":
        "16e124587df5b37b3f4735e14894982750c60a303043125985383101331eb4de",
    "attempts/wave60-c3-incidence-design/exact_check.py":
        "635db0b96e23584ec66afcdc1fc3dba166068e23a5598dd31a93cb5391a5900b",
    "attempts/wave60-c3-incidence-design/invariant_scan.py":
        "4888255db7de515548437c7ecdc9d9483242ed85b064c42965136afc519c9f8c",
    "attempts/wave60-c3-incidence-design/exact-results.json":
        "35b6436c7ba5619fcf7e3840cbdacd594461c01df8758686450f5d8eea8e36f3",
    "attempts/wave61-c3-finite-field/exact-results.json":
        "936c76b7487d713421ef663aae4cc591f9bcf93f5d6a11f4aae3c0b5d4aa52f6",
    "attempts/wave61-c3-finite-field/exact_check.py":
        "30caa745f3e6c2ac42b0a1ca4f218666405baf145353d6b644b2a3eab66ccc48",
    "verification/wave36-block-compatibility/independent-results.json":
        "b92ee5cde6a63ba3cce09bc2eae1518979aea09c4f5db39789b65f117b0768c4",
}
PAIR_LIST_12 = tuple(itertools.combinations(range(12), 2))
PAIR_LIST_36 = tuple(itertools.combinations(range(36), 2))
PAIR_INDEX_36 = {pair: index for index, pair in enumerate(PAIR_LIST_36)}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_frozen_inputs() -> None:
    freeze_lines = (PACKAGE / "input-freeze.sha256").read_text(
        encoding="utf-8"
    ).splitlines()
    parsed = {}
    for line in freeze_lines:
        if not line or line.startswith("#"):
            continue
        digest, relative = line.split("  ", 1)
        parsed[relative] = digest
    if parsed != FROZEN:
        raise AssertionError("input-freeze.sha256 contents do not match checker")
    for relative, expected in FROZEN.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise AssertionError(
                f"frozen input changed: {relative}: {actual} != {expected}"
            )


def global_vertex(component: int, local_vertex: int) -> int:
    fibre, local_index = divmod(local_vertex, 4)
    return fibre * 12 + component * 4 + local_index


def component_rows(record: dict) -> tuple[int, ...]:
    rows = [0] * 12
    for left, right in record["edges"]:
        if not 0 <= left < right < 12:
            raise AssertionError("malformed edge")
        if rows[left] >> right & 1:
            raise AssertionError("duplicate edge")
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    if {row.bit_count() for row in rows} != {3}:
        raise AssertionError("component not cubic")
    reached = 1
    frontier = 1
    while frontier:
        new = 0
        for vertex in range(12):
            if frontier >> vertex & 1:
                new |= rows[vertex]
        new &= ~reached
        reached |= new
        frontier = new
    if reached != (1 << 12) - 1:
        raise AssertionError("component disconnected")
    for fibre in range(3):
        vertices = tuple(range(4 * fibre, 4 * fibre + 4))
        if any(
            sum(rows[left] >> right & 1 for right in vertices) != 1
            for left in vertices
        ):
            raise AssertionError("within-fibre matching failed")
    for first, second in itertools.combinations(range(3), 2):
        if any(
            sum(
                rows[left] >> right & 1
                for right in range(4 * second, 4 * second + 4)
            ) != 1
            for left in range(4 * first, 4 * first + 4)
        ):
            raise AssertionError("cross-fibre matching failed")
    if any(
        (rows[left] & rows[right]).bit_count()
        for left, right in itertools.combinations(range(12), 2)
        if rows[left] >> right & 1
    ):
        raise AssertionError("triangle found")
    return tuple(rows)


def load_types() -> list[dict]:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    records = data["component_census"]["types"]
    if len(records) != 18:
        raise AssertionError("expected 18 types")
    if [record["type_index"] for record in records] != list(range(18)):
        raise AssertionError("unexpected type ordering")
    for record in records:
        component_rows(record)
    return records


def local_gram(record: dict) -> tuple[tuple[int, ...], ...]:
    rows = component_rows(record)
    return tuple(
        tuple(
            (12 if left == right else 0)
            - (1 if rows[left] >> right & 1 else 0)
            + 2
            - (1 if left // 4 == right // 4 else 0)
            - (rows[left] & rows[right]).bit_count()
            for right in range(12)
        )
        for left in range(12)
    )


def target_gram(records: Sequence[dict]) -> tuple[tuple[int, ...], ...]:
    rows = [0] * 36
    for component, record in enumerate(records):
        local = component_rows(record)
        for left in range(12):
            for right in range(left + 1, 12):
                if local[left] >> right & 1:
                    global_left = global_vertex(component, left)
                    global_right = global_vertex(component, right)
                    rows[global_left] |= 1 << global_right
                    rows[global_right] |= 1 << global_left
    matrix = tuple(
        tuple(
            (12 if left == right else 0)
            - (1 if rows[left] >> right & 1 else 0)
            + 2
            - (1 if left // 12 == right // 12 else 0)
            - (rows[left] & rows[right]).bit_count()
            for right in range(36)
        )
        for left in range(36)
    )
    if min(map(min, matrix)) < 0:
        raise AssertionError("negative target")
    if [matrix[index][index] for index in range(36)] != [10] * 36:
        raise AssertionError("wrong target diagonal")
    return matrix


def pair_profile(pair: tuple[int, int]) -> tuple[int, int, int]:
    values = [0, 0, 0]
    values[pair[0] // 4] += 1
    values[pair[1] // 4] += 1
    return tuple(values)


PROFILE_VALUES = tuple(sorted({pair_profile(pair) for pair in PAIR_LIST_12}))
PROFILE_TRIPLES = tuple(
    triple
    for triple in itertools.product(range(len(PROFILE_VALUES)), repeat=3)
    if tuple(
        sum(PROFILE_VALUES[triple[component]][fibre]
            for component in range(3))
        for fibre in range(3)
    ) == (2, 2, 2)
)


def allowed_pairs(record: dict) -> tuple[tuple[int, ...], ...]:
    gram = local_gram(record)
    output = [[] for _ in PROFILE_VALUES]
    for index, pair in enumerate(PAIR_LIST_12):
        if gram[pair[0]][pair[1]] > 0:
            profile_index = PROFILE_VALUES.index(pair_profile(pair))
            output[profile_index].append(index)
    return tuple(tuple(values) for values in output)


def candidate_count(records: Sequence[dict]) -> int:
    allowed = [allowed_pairs(record) for record in records]
    return sum(
        len(allowed[0][triple[0]])
        * len(allowed[1][triple[1]])
        * len(allowed[2][triple[2]])
        for triple in PROFILE_TRIPLES
    )


def candidates(records: Sequence[dict]) -> list[tuple[int, ...]]:
    allowed = [allowed_pairs(record) for record in records]
    output = []
    seen = set()
    for profiles in PROFILE_TRIPLES:
        for indices in itertools.product(*(
            allowed[component][profiles[component]]
            for component in range(3)
        )):
            candidate = tuple(sorted(
                global_vertex(component, vertex)
                for component, pair_index in enumerate(indices)
                for vertex in PAIR_LIST_12[pair_index]
            ))
            if candidate in seen:
                raise AssertionError("duplicate candidate")
            seen.add(candidate)
            output.append(candidate)
    return output


def verify_witness(
    witness_records: Sequence[dict],
    candidate_list: Sequence[tuple[int, ...]],
    gram: Sequence[Sequence[int]],
    upper_bound_one: bool,
) -> dict:
    coefficients = {}
    for record in witness_records:
        index = record["candidate_index"]
        if index in coefficients:
            raise AssertionError("duplicate witness index")
        if not 0 <= index < len(candidate_list):
            raise AssertionError("witness index out of range")
        value = Fraction(record["numerator"], record["denominator"])
        if value < 0:
            raise AssertionError("negative coefficient")
        if upper_bound_one and value > 1:
            raise AssertionError("x<=1 violation")
        coefficients[index] = value
    totals = [Fraction(0) for _ in PAIR_LIST_36]
    total_weight = Fraction(0)
    for index, value in coefficients.items():
        total_weight += value
        for pair in itertools.combinations(candidate_list[index], 2):
            totals[PAIR_INDEX_36[pair]] += value
    expected = [
        Fraction(gram[left][right]) for left, right in PAIR_LIST_36
    ]
    if totals != expected:
        raise AssertionError("witness does not replay all pair equations")
    if total_weight != 60:
        raise AssertionError("witness total is not 60")
    return {
        "coefficient_count": len(coefficients),
        "all_630_pair_equations_exact": True,
        "total_weight": "60",
        "all_coefficients_at_most_one": all(
            value <= 1 for value in coefficients.values()
        ),
        "maximum_coefficient": str(
            max(coefficients.values(), default=Fraction(0))
        ),
    }


def expected_lane_indices(wave61: dict, minimum: int, maximum: int) -> set[int]:
    records = wave61["triple_census"]["records"]
    selected = set()
    seen_ranks = set()
    for record in records:
        index = record["triple_index"]
        triple = record["type_triple"]
        count = record["pair_inventory_F2"][
            "candidate_count_before_exact_multiplicities"
        ]
        if count in (minimum, maximum):
            selected.add(index)
        if triple[0] == triple[1] == triple[2]:
            selected.add(index)
        rank = record["pair_inventory_F2"]["full_630_rank"]
        if rank not in seen_ranks:
            selected.add(index)
            seen_ranks.add(rank)
    return selected


def verify(path: Path) -> dict:
    check_frozen_inputs()
    result = json.loads(path.read_text(encoding="utf-8"))
    types = load_types()
    wave60 = json.loads(WAVE60_RESULTS.read_text(encoding="utf-8"))
    wave61 = json.loads(WAVE61_RESULTS.read_text(encoding="utf-8"))
    imported = wave61["triple_census"]["records"]
    triples = list(itertools.combinations_with_replacement(range(18), 3))
    if len(imported) != len(triples) or len(triples) != 1140:
        raise AssertionError("triple census length mismatch")
    counts = []
    for triple in triples:
        counts.append(candidate_count([types[index] for index in triple]))
    imported_counts = [
        record["pair_inventory_F2"][
            "candidate_count_before_exact_multiplicities"
        ]
        for record in imported
    ]
    if counts != imported_counts:
        raise AssertionError("candidate census mismatch")
    minimum = min(counts)
    maximum = max(counts)
    if minimum != wave60["individual_column_support"]["minimum_over_triples"]:
        raise AssertionError("minimum support mismatch")
    if maximum != wave60["individual_column_support"]["maximum_over_triples"]:
        raise AssertionError("maximum support mismatch")
    expected_indices = expected_lane_indices(wave61, minimum, maximum)
    lane_indices = [record["triple_index"] for record in result["results"]]
    if result["lane_selection"]["lane_limit"] is None:
        if set(lane_indices) != expected_indices:
            raise AssertionError("full lane selection differs from frozen rule")
    elif lane_indices != sorted(expected_indices)[:len(lane_indices)]:
        raise AssertionError("limited lane selection differs from frozen rule")
    exact_cone = 0
    exact_cone_with_upper_bounds = 0
    candidate_designs = 0
    for lane in result["results"]:
        index = lane["triple_index"]
        if lane["type_triple"] != imported[index]["type_triple"]:
            raise AssertionError("lane triple mismatch")
        records = [types[value] for value in lane["type_triple"]]
        gram = target_gram(records)
        candidate_list = candidates(records)
        if len(candidate_list) != lane["candidate_count"]:
            raise AssertionError("lane candidate count mismatch")
        cone = lane["rational_cone"]
        if cone["claim_label"] == "DERIVED":
            exact_cone += 1
            replay = verify_witness(
                cone["exact_witness"], candidate_list, gram, False
            )
            if replay["coefficient_count"] != cone["exact_replay"][
                "coefficient_count"
            ]:
                raise AssertionError("cone replay metadata mismatch")
            if replay["all_coefficients_at_most_one"]:
                exact_cone_with_upper_bounds += 1
        elif "exact_witness" in cone:
            raise AssertionError("unlabelled cone witness")
        integer = lane["distinct_column_milp"]
        if integer["claim_label"] == "CANDIDATE":
            candidate_designs += 1
            verify_witness(
                integer["exact_witness"], candidate_list, gram, True
            )
        elif "exact_witness" in integer:
            raise AssertionError("unlabelled integer witness")
    summary = result["summary"]
    if summary["exact_rational_cone_witnesses"] != exact_cone:
        raise AssertionError("cone summary mismatch")
    if summary["exact_distinct_column_candidates"] != candidate_designs:
        raise AssertionError("integer summary mismatch")
    if summary["endpoint_status"] != "UNKNOWN":
        raise AssertionError("endpoint status inflation")
    if summary["conway_99_status"] != "UNKNOWN":
        raise AssertionError("Conway status inflation")
    return {
        "claim_label": "DERIVED",
        "checked_path": str(path.resolve().relative_to(ROOT)).replace("\\", "/"),
        "input_hashes_checked": len(FROZEN),
        "component_types_checked": len(types),
        "triple_candidate_counts_checked": len(triples),
        "selected_lanes_checked": len(result["results"]),
        "exact_rational_witnesses_checked": exact_cone,
        "exact_rational_witnesses_with_all_coefficients_at_most_one":
            exact_cone_with_upper_bounds,
        "integer_candidates_checked": candidate_designs,
        "all_witness_pair_equations_checked": 630,
        "endpoint_status": "UNKNOWN",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify",
        type=Path,
        default=PACKAGE / "exact-results.json",
    )
    arguments = parser.parse_args()
    print(json.dumps(
        verify(arguments.verify), indent=2, sort_keys=True
    ))


if __name__ == "__main__":
    main()
