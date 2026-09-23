#!/usr/bin/env python3
"""Clean-room verification of the sealed Wave144 certificate.

This file does not import the discovery checker.  It independently rebuilds
the local equations, exhaustively enumerates all 62 exact supports, and
replays the explicit aggregate integer certificate with standard-library
integer arithmetic.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any


N = 99
ORDER = 6
OUTSIDE = 93
ENDPOINT = 4158
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = ROOT / "attempts/wave144-sixset-odd-profile"
RESULT_PATH = PACKAGE / "exact-results.json"
MANIFEST_PATH = PACKAGE / "package-manifest.sha256"
WAVE21_PATH = ROOT / "attempts/wave21-six-vertex-lp/exact_check.py"
WAVE141_PATH = ROOT / "attempts/wave141-bivariate-graph-code/exact-results.json"
OUTPUT_PATH = HERE / "verification-results.json"

EXPECTED_PREREQUISITES = {
    "attempts/wave21-six-vertex-lp/exact_check.py":
        "0dd44ca37ca21aeaa757f3b2d7f7f9639907f22b95da39472ed9d836027a94a3",
    "attempts/wave21-six-vertex-lp/exact-results.json":
        "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b",
    "attempts/wave141-bivariate-graph-code/exact_check.py":
        "15378b9a9f807071de0aae5604c4178af5b3cfa067851230781d67d05f2ca204",
    "attempts/wave141-bivariate-graph-code/exact-results.json":
        "351857e985a871e6d69c5662f90ad5cd6a608f92b1703e84ffb549a753cc8b2e",
}


def demand(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def load_wave21() -> Any:
    spec = importlib.util.spec_from_file_location(
        "wave144_independent_wave21",
        WAVE21_PATH,
    )
    demand(spec is not None and spec.loader is not None, "cannot load Wave21")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PAIR_LIST = tuple(itertools.combinations(range(ORDER), 2))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIR_LIST)}


def graph_data(mask: int) -> tuple[list[int], list[int], int]:
    neighbor_masks = [0] * ORDER
    for position, (u, v) in enumerate(PAIR_LIST):
        if (mask >> position) & 1:
            neighbor_masks[u] |= 1 << v
            neighbor_masks[v] |= 1 << u
    degrees = [row.bit_count() for row in neighbor_masks]
    pair_budget = []
    for position, (u, v) in enumerate(PAIR_LIST):
        internal = (neighbor_masks[u] & neighbor_masks[v]).bit_count()
        prescribed = 1 if (mask >> position) & 1 else 2
        pair_budget.append(prescribed - internal)
    demand(all(value >= 0 for value in pair_budget), "negative pair budget")
    return degrees, pair_budget, sum(value & 1 for value in degrees)


def check_z(mask: int, sparse: dict[str, int], output_weight: int) -> None:
    z = [0] * 64
    for key, value in sparse.items():
        cell = int(key)
        demand(0 <= cell < 64, "invalid subset mask")
        demand(isinstance(value, int) and value > 0, "nonpositive sparse cell")
        z[cell] = value
    degrees, pair_budget, inside_odd = graph_data(mask)
    demand(sum(z) == OUTSIDE, "z total failure")
    for vertex in range(ORDER):
        demand(
            sum(z[cell] for cell in range(64) if (cell >> vertex) & 1)
            == 14 - degrees[vertex],
            f"z degree failure at {vertex}",
        )
    for pair_position, (u, v) in enumerate(PAIR_LIST):
        demand(
            sum(
                z[cell]
                for cell in range(64)
                if ((cell >> u) & 1) and ((cell >> v) & 1)
            )
            == pair_budget[pair_position],
            f"z pair failure at {(u, v)}",
        )
    observed = inside_odd + sum(
        z[cell] for cell in range(64) if cell.bit_count() & 1
    )
    demand(observed == output_weight, "z output-weight failure")


def independently_enumerate_weights(mask: int) -> list[int]:
    degrees, initial_pair_budget, inside_odd = graph_data(mask)
    candidates = []
    for size in range(ORDER, 2, -1):
        for vertices in itertools.combinations(range(ORDER), size):
            used_pairs = tuple(
                PAIR_INDEX[pair]
                for pair in itertools.combinations(vertices, 2)
            )
            if all(initial_pair_budget[index] for index in used_pairs):
                candidates.append((vertices, used_pairs))

    pair_budget = initial_pair_budget[:]
    higher_incidence = [0] * ORDER
    answers: set[int] = set()

    def search(position: int, higher_count: int, odd_higher_count: int) -> None:
        if position == len(candidates):
            singleton_counts = []
            for vertex in range(ORDER):
                incident_pairs = sum(
                    pair_budget[
                        PAIR_INDEX[tuple(sorted((vertex, other)))]
                    ]
                    for other in range(ORDER)
                    if other != vertex
                )
                singleton = (
                    14
                    - degrees[vertex]
                    - higher_incidence[vertex]
                    - incident_pairs
                )
                if singleton < 0:
                    return
                singleton_counts.append(singleton)
            empty = (
                OUTSIDE
                - higher_count
                - sum(pair_budget)
                - sum(singleton_counts)
            )
            if empty >= 0:
                answers.add(inside_odd + odd_higher_count + sum(singleton_counts))
            return

        vertices, used_pairs = candidates[position]
        upper = min(pair_budget[index] for index in used_pairs)
        for multiplicity in range(upper + 1):
            for index in used_pairs:
                pair_budget[index] -= multiplicity
            for vertex in vertices:
                higher_incidence[vertex] += multiplicity
            search(
                position + 1,
                higher_count + multiplicity,
                odd_higher_count
                + (multiplicity if len(vertices) & 1 else 0),
            )
            for index in used_pairs:
                pair_budget[index] += multiplicity
            for vertex in vertices:
                higher_incidence[vertex] -= multiplicity

    search(0, 0, 0)
    demand(bool(answers), "independent local enumeration found no solution")
    return sorted(answers)


def kraw(degree: int, weight: int) -> int:
    total = 0
    lower = max(0, degree - (N - weight))
    upper = min(weight, degree)
    for overlap in range(lower, upper + 1):
        total += (
            (-1) ** overlap
            * math.comb(weight, overlap)
            * math.comb(N - weight, degree - overlap)
        )
    return total


def parse_manifest() -> dict[str, str]:
    entries = {}
    for raw_line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        expected, relative = raw_line.split("  ", 1)
        demand(relative not in entries, "duplicate manifest path")
        entries[relative] = expected
    demand(entries, "empty package manifest")
    for relative, expected in entries.items():
        demand(
            digest(ROOT / relative) == expected,
            f"package manifest mismatch: {relative}",
        )
    return entries


def verify_payload(payload: dict[str, Any]) -> dict[str, Any]:
    prerequisite_hashes = {
        relative: digest(ROOT / relative)
        for relative in EXPECTED_PREREQUISITES
    }
    demand(
        prerequisite_hashes == EXPECTED_PREREQUISITES,
        "prerequisite hash drift",
    )
    demand(
        payload["frozen_inputs_sha256"] == EXPECTED_PREREQUISITES,
        "payload prerequisite hashes differ",
    )

    wave21 = load_wave21()
    _, five_alignment = wave21.align_four_five()
    six_alignment = wave21.align_five_six(
        five_alignment,
        wave21.corrected_five_to_six(),
    )
    classes = wave21.locally_admissible_classes(6)
    records = payload["class_profiles"]
    demand(len(records) == 62, "not 62 profile records")
    masks = {}
    exact_supports = {}
    for expected_source, record in enumerate(records, 1):
        demand(record["source_class"] == expected_source, "source order drift")
        mask = classes[six_alignment[expected_source - 1]]
        masks[expected_source] = mask
        observed = independently_enumerate_weights(mask)
        demand(
            observed == record["attainable_weights"],
            f"support mismatch in source class {expected_source}",
        )
        exact_supports[expected_source] = observed

    forced = {
        str(source): values[0]
        for source, values in exact_supports.items()
        if len(values) == 1
    }
    demand(
        forced == {"1": 66, "3": 56, "5": 46, "14": 36},
        "independent forced-cell result drift",
    )
    demand(payload["forced_singleton_cells"] == forced, "stored forced cells drift")

    local_witnesses = {}
    for record in payload["selected_local_integer_witnesses"]:
        key = (record["source_class"], record["output_weight"])
        demand(key not in local_witnesses, "duplicate local witness")
        check_z(
            masks[key[0]],
            record["z_by_subset_mask_sparse"],
            key[1],
        )
        local_witnesses[key] = record

    aggregate = payload["aggregate_endpoint_certificate"]
    demand(aggregate["n3"] == ENDPOINT, "endpoint drift")
    demand(aggregate["known_imported_cap"] == ENDPOINT, "cap drift")
    cell_counts = {}
    for row in aggregate["nonzero_cells"]:
        key = (row["source_class"], row["output_weight"])
        demand(key not in cell_counts, "duplicate aggregate cell")
        demand(isinstance(row["count"], int) and row["count"] > 0,
               "aggregate count is not positive integer")
        demand(row["output_weight"] in exact_supports[row["source_class"]],
               "aggregate uses unsupported weight")
        demand(key in local_witnesses, "aggregate cell lacks local z witness")
        cell_counts[key] = row["count"]

    forms = wave21.six_counts()
    marginal_replay = {}
    for source in range(1, 63):
        expected = forms[source].evaluate(ENDPOINT)
        demand(expected.denominator == 1 and expected >= 0,
               "invalid source marginal")
        observed = sum(
            count
            for (cell_source, _), count in cell_counts.items()
            if cell_source == source
        )
        demand(observed == expected, f"marginal failure in class {source}")
        marginal_replay[str(source)] = int(expected)
    demand(marginal_replay == aggregate["class_marginals"],
           "stored marginal table drift")
    demand(sum(marginal_replay.values()) == math.comb(N, 6),
           "marginal grand total failure")

    wave141 = json.loads(WAVE141_PATH.read_text(encoding="utf-8"))
    low_rows = {
        int(t): {int(w): int(count) for w, count in row.items()}
        for t, row in wave141["exact_low_input_rows"].items()
    }
    rhs = {
        t: sum(kraw(6, weight) * count for weight, count in low_rows[t].items())
        for t in range(4)
    }
    lhs = {
        t: sum(
            kraw(t, weight) * count
            for (_, weight), count in cell_counts.items()
        )
        for t in range(4)
    }
    demand(lhs == rhs, "independent reciprocity replay failed")
    demand(
        {str(t): value for t, value in lhs.items()} == aggregate["moment_lhs"],
        "stored moment left side drift",
    )
    demand(aggregate["moment_lhs"] == aggregate["moment_rhs"],
           "stored moment equality false")

    signed = sum(
        (-1) ** (weight // 2) * count
        for (_, weight), count in cell_counts.items()
    )
    demand(signed == 2734116, "signed S6 replay failed")
    demand(aggregate["signed_S6"] == signed, "stored signed S6 drift")
    demand(payload["result"]["endpoint_survives"] is True, "endpoint label drift")
    demand(payload["result"]["improves_known_n3_cap"] is False,
           "false bound-improvement label")

    return {
        "format": "wave144-independent-verification-v1",
        "verdict": "PASS_NULL_BOUNDARY",
        "package_manifest_entries": len(parse_manifest()),
        "prerequisite_hashes": prerequisite_hashes,
        "independent_exact_supports_recomputed": 62,
        "forced_singleton_cells": forced,
        "selected_local_z_witnesses_checked": len(local_witnesses),
        "aggregate_nonzero_integer_cells_checked": len(cell_counts),
        "endpoint_n3": ENDPOINT,
        "reciprocity_moments_t0_through_t3": {
            str(t): value for t, value in lhs.items()
        },
        "signed_S6": signed,
        "bound_improvement": False,
        "graph_realization": "NOT_ESTABLISHED",
    }


def main() -> int:
    payload = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    report = verify_payload(payload)
    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
