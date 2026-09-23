#!/usr/bin/env python3
"""Independent, manifest-bound verification of the Wave144 certificate.

The discovery package is treated as hostile input.  Its manifest was copied
into this directory before its internals were read.  This verifier uses a new
graph census/deck alignment implementation, regenerates every local support,
replays every sparse local certificate, and checks the endpoint aggregate.

The only code imported from Wave21 is used as a frozen container for the two
published deck tables.  None of its census, canonicalization, alignment,
formula, or verification functions is called.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import sys
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


N = 99
K = 14
ORDER = 6
OUTSIDE = N - ORDER
ENDPOINT = 4158
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts/wave144-sixset-odd-profile"
DISCOVERY_RESULTS = DISCOVERY / "exact-results.json"
DISCOVERY_MANIFEST = DISCOVERY / "package-manifest.sha256"
FROZEN_MANIFEST = HERE / "discovery-manifest.frozen.sha256"
WAVE21_CODE = ROOT / "attempts/wave21-six-vertex-lp/exact_check.py"
WAVE21_RESULTS = ROOT / "attempts/wave21-six-vertex-lp/exact-results.json"
WAVE141_RESULTS = ROOT / "attempts/wave141-bivariate-graph-code/exact-results.json"
AUXILIARY_VERIFIER = ROOT / "verification/wave144-sixset-odd-profile"
OUTPUT = HERE / "verification-results.json"

EXPECTED_DISCOVERY_MANIFEST_SHA256 = (
    "b5369353ac6959b0662e3f424cf80e48094ac6bcdb79572bf604632c45509436"
)
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


def sha256(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            state.update(chunk)
    return state.hexdigest()


def parse_hash_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        demand(len(expected) == 64, f"bad digest in {path}")
        demand(relative not in entries, f"duplicate manifest entry: {relative}")
        entries[relative] = expected.lower()
    demand(bool(entries), f"empty manifest: {path}")
    return entries


def verify_frozen_discovery() -> dict[str, str]:
    demand(
        sha256(FROZEN_MANIFEST) == EXPECTED_DISCOVERY_MANIFEST_SHA256,
        "frozen manifest bytes changed",
    )
    demand(
        sha256(DISCOVERY_MANIFEST) == EXPECTED_DISCOVERY_MANIFEST_SHA256,
        "live discovery manifest changed after freeze",
    )
    frozen = parse_hash_manifest(FROZEN_MANIFEST)
    demand(frozen == parse_hash_manifest(DISCOVERY_MANIFEST),
           "live and frozen manifest entries differ")
    for relative, expected in frozen.items():
        demand(sha256(ROOT / relative) == expected,
               f"frozen discovery artifact mismatch: {relative}")
    return frozen


def load_deck_table_data() -> tuple[dict[int, dict[int, int]], dict[int, dict[int, int]]]:
    """Load only frozen transcription constants, never Wave21 algorithms."""

    spec = importlib.util.spec_from_file_location("wave144_frozen_tables", WAVE21_CODE)
    demand(spec is not None and spec.loader is not None, "cannot load deck data")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    four_five = {
        int(row): {int(column): int(value) for column, value in entries.items()}
        for row, entries in module.FOUR_TO_FIVE.items()
    }
    five_six = {
        int(row): {int(column): int(value) for column, value in entries.items()}
        for row, entries in module.FIVE_TO_SIX_RAW.items()
    }
    # Frozen source notes identify this omitted published term; apply it as
    # data rather than invoking Wave21's correction/alignment function.
    five_six[7][23] = 1
    return four_five, five_six


@lru_cache(maxsize=None)
def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


@lru_cache(maxsize=None)
def relabel_maps(order: int) -> tuple[tuple[int, ...], ...]:
    edge_positions = {edge: i for i, edge in enumerate(edges(order))}
    maps = []
    for permutation in itertools.permutations(range(order)):
        maps.append(tuple(
            edge_positions[tuple(sorted((permutation[u], permutation[v])))]
            for u, v in edges(order)
        ))
    return tuple(maps)


def relabel_mask(mask: int, mapping: tuple[int, ...]) -> int:
    output = 0
    for old_position, new_position in enumerate(mapping):
        if mask >> old_position & 1:
            output |= 1 << new_position
    return output


def canonical(mask: int, order: int) -> int:
    return min(relabel_mask(mask, mapping) for mapping in relabel_maps(order))


def adjacency(mask: int, order: int) -> list[int]:
    rows = [0] * order
    for position, (u, v) in enumerate(edges(order)):
        if mask >> position & 1:
            rows[u] |= 1 << v
            rows[v] |= 1 << u
    return rows


def locally_admissible(mask: int, order: int) -> bool:
    rows = adjacency(mask, order)
    for position, (u, v) in enumerate(edges(order)):
        common = (rows[u] & rows[v]).bit_count()
        limit = 1 if mask >> position & 1 else 2
        if common > limit:
            return False
    return True


@lru_cache(maxsize=None)
def graph_classes(order: int) -> tuple[int, ...]:
    unassigned = {
        mask
        for mask in range(1 << len(edges(order)))
        if locally_admissible(mask, order)
    }
    result = []
    while unassigned:
        seed = min(unassigned)
        orbit = {relabel_mask(seed, mapping) for mapping in relabel_maps(order)}
        result.append(min(orbit))
        unassigned.difference_update(orbit)
    return tuple(sorted(result))


def delete_vertex(mask: int, order: int, removed: int) -> int:
    survivors = [v for v in range(order) if v != removed]
    new_label = {old: new for new, old in enumerate(survivors)}
    new_positions = {edge: i for i, edge in enumerate(edges(order - 1))}
    answer = 0
    for old_position, (u, v) in enumerate(edges(order)):
        if removed in (u, v) or not (mask >> old_position & 1):
            continue
        new_edge = tuple(sorted((new_label[u], new_label[v])))
        answer |= 1 << new_positions[new_edge]
    return answer


def deletion_deck(mask: int, order: int, lower: tuple[int, ...]) -> tuple[int, ...]:
    lookup = {representative: index for index, representative in enumerate(lower)}
    counts = [0] * len(lower)
    for removed in range(order):
        card = canonical(delete_vertex(mask, order, removed), order - 1)
        counts[lookup[card]] += 1
    return tuple(counts)


def source_columns(
    rows: dict[int, dict[int, int]],
    row_count: int,
    column_count: int,
) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(
        rows.get(row, {}).get(column, 0)
        for row in range(1, row_count + 1)
    ) for column in range(1, column_count + 1))


def independent_six_alignment() -> tuple[tuple[int, ...], dict[str, Any]]:
    four_five, five_six = load_deck_table_data()
    classes4, classes5, classes6 = (graph_classes(i) for i in (4, 5, 6))
    demand((len(classes4), len(classes5), len(classes6)) == (9, 21, 62),
           "independent class census size failure")

    actual5 = tuple(deletion_deck(mask, 5, classes4) for mask in classes5)
    published5 = source_columns(four_five, 9, 21)
    row_map = []
    for source_row in range(9):
        signature = sorted(column[source_row] for column in published5)
        candidates = [
            canonical_row
            for canonical_row in range(9)
            if sorted(deck[canonical_row] for deck in actual5) == signature
        ]
        demand(len(candidates) == 1, f"nonunique four-class row {source_row + 1}")
        row_map.append(candidates[0])
    five_map = []
    for source_column in published5:
        translated = [0] * 9
        for source_row, canonical_row in enumerate(row_map):
            translated[canonical_row] = source_column[source_row]
        hits = [i for i, deck in enumerate(actual5) if deck == tuple(translated)]
        demand(len(hits) == 1, "nonunique five-class column")
        five_map.append(hits[0])
    demand(len(set(five_map)) == 21, "five-class alignment is not bijective")

    actual6 = tuple(deletion_deck(mask, 6, classes5) for mask in classes6)
    published6 = source_columns(five_six, 21, 62)
    six_map = []
    for source_column in published6:
        translated = [0] * 21
        for source_row, canonical_row in enumerate(five_map):
            translated[canonical_row] = source_column[source_row]
        hits = [i for i, deck in enumerate(actual6) if deck == tuple(translated)]
        demand(len(hits) == 1, "nonunique six-class column")
        six_map.append(hits[0])
    demand(len(set(six_map)) == 62, "six-class alignment is not bijective")
    return tuple(six_map), {
        "class_counts_order_4_5_6": [9, 21, 62],
        "four_row_alignment_unique": True,
        "five_alignment_bijective": True,
        "six_alignment_bijective": True,
    }


PAIR_LIST = edges(ORDER)
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIR_LIST)}


def local_rhs(mask: int) -> tuple[list[int], list[int], int]:
    rows = adjacency(mask, ORDER)
    degree = [row.bit_count() for row in rows]
    pair_rhs = []
    for position, (u, v) in enumerate(PAIR_LIST):
        prescribed = 1 if mask >> position & 1 else 2
        pair_rhs.append(prescribed - (rows[u] & rows[v]).bit_count())
    demand(all(value >= 0 for value in pair_rhs), "negative pair right side")
    return degree, pair_rhs, sum(value & 1 for value in degree)


def high_candidates(mask: int, pair_rhs: list[int], reverse: bool = False) -> list[tuple[int, tuple[int, ...], tuple[int, ...]]]:
    candidates = []
    sizes: Iterable[int] = range(3, 7) if reverse else range(6, 2, -1)
    for size in sizes:
        combos = list(itertools.combinations(range(ORDER), size))
        if reverse:
            combos.reverse()
        for vertices in combos:
            used_pairs = tuple(
                PAIR_INDEX[pair] for pair in itertools.combinations(vertices, 2)
            )
            if all(pair_rhs[index] > 0 for index in used_pairs):
                cell_mask = sum(1 << vertex for vertex in vertices)
                candidates.append((cell_mask, vertices, used_pairs))
    return candidates


def enumerate_support(
    mask: int,
    *,
    reverse: bool = False,
    target_only: int | None = None,
) -> tuple[list[int], dict[int, dict[str, int]], dict[str, int | bool]]:
    """Exhaust all high-cell multiplicities, then force pairs/singletons/empty."""

    degree, initial_pairs, inside_odd = local_rhs(mask)
    candidates = high_candidates(mask, initial_pairs, reverse=reverse)
    remaining_pairs = initial_pairs[:]
    high_incidence = [0] * ORDER
    multiplicities = [0] * len(candidates)
    witnesses: dict[int, dict[str, int]] = {}
    nodes = 0
    terminals = 0
    target_found = False

    def visit(position: int, high_total: int, odd_high_total: int) -> None:
        nonlocal nodes, terminals, target_found
        nodes += 1
        if target_only is not None and target_found:
            return
        if position < len(candidates):
            _, vertices, used_pairs = candidates[position]
            upper = min(remaining_pairs[index] for index in used_pairs)
            for value in range(upper + 1):
                multiplicities[position] = value
                for index in used_pairs:
                    remaining_pairs[index] -= value
                for vertex in vertices:
                    high_incidence[vertex] += value
                visit(
                    position + 1,
                    high_total + value,
                    odd_high_total + (value if len(vertices) & 1 else 0),
                )
                for index in used_pairs:
                    remaining_pairs[index] += value
                for vertex in vertices:
                    high_incidence[vertex] -= value
            multiplicities[position] = 0
            return

        terminals += 1
        singletons = []
        for vertex in range(ORDER):
            residual_pair_degree = sum(
                remaining_pairs[PAIR_INDEX[tuple(sorted((vertex, other)))]]
                for other in range(ORDER)
                if other != vertex
            )
            singleton = K - degree[vertex] - high_incidence[vertex] - residual_pair_degree
            if singleton < 0:
                return
            singletons.append(singleton)
        empty = OUTSIDE - high_total - sum(remaining_pairs) - sum(singletons)
        if empty < 0:
            return
        weight = inside_odd + odd_high_total + sum(singletons)
        if target_only is not None and weight != target_only:
            return
        sparse: dict[str, int] = {}
        if empty:
            sparse["0"] = empty
        for vertex, value in enumerate(singletons):
            if value:
                sparse[str(1 << vertex)] = value
        for pair_position, value in enumerate(remaining_pairs):
            if value:
                u, v = PAIR_LIST[pair_position]
                sparse[str((1 << u) | (1 << v))] = value
        for index, value in enumerate(multiplicities):
            if value:
                sparse[str(candidates[index][0])] = value
        witnesses.setdefault(weight, dict(sorted(sparse.items(), key=lambda item: int(item[0]))))
        if target_only is not None:
            target_found = True

    visit(0, 0, 0)
    return sorted(witnesses), witnesses, {
        "candidate_high_cells": len(candidates),
        "search_nodes": nodes,
        "terminal_assignments": terminals,
        "target_found": target_found,
    }


def replay_z(mask: int, sparse: dict[str, int], expected_weight: int) -> None:
    z = [0] * 64
    demand(isinstance(sparse, dict), "local witness is not a mapping")
    for raw_key, value in sparse.items():
        demand(isinstance(raw_key, str) and str(int(raw_key)) == raw_key,
               "noncanonical subset key")
        cell = int(raw_key)
        demand(0 <= cell < 64, "subset key out of range")
        demand(z[cell] == 0, "duplicate sparse subset key")
        demand(type(value) is int and value > 0, "nonpositive local cell")
        z[cell] = value
    degree, pair_rhs, inside_odd = local_rhs(mask)
    demand(sum(z) == OUTSIDE, "local total is not 93")
    for vertex in range(ORDER):
        observed = sum(z[cell] for cell in range(64) if cell >> vertex & 1)
        demand(observed == K - degree[vertex], f"local degree failure at {vertex}")
    for pair_position, (u, v) in enumerate(PAIR_LIST):
        observed = sum(
            z[cell] for cell in range(64)
            if cell >> u & 1 and cell >> v & 1
        )
        demand(observed == pair_rhs[pair_position], f"local pair failure at {(u, v)}")
    weight = inside_odd + sum(
        z[cell] for cell in range(64) if cell.bit_count() & 1
    )
    demand(weight == expected_weight, "local output weight mismatch")


def parse_fraction(text: str) -> Fraction:
    return Fraction(text)


def kraw(degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * math.comb(weight, overlap)
        * math.comb(N - weight, degree - overlap)
        for overlap in range(max(0, degree - (N - weight)), min(weight, degree) + 1)
    )


def verify_auxiliary_package() -> dict[str, Any]:
    """Integrity-audit the same-author verifier without using it as evidence."""

    manifest = AUXILIARY_VERIFIER / "package-manifest.sha256"
    entries = parse_hash_manifest(manifest)
    for relative, expected in entries.items():
        demand(sha256(ROOT / relative) == expected,
               f"auxiliary verifier manifest mismatch: {relative}")
    result = json.loads(
        (AUXILIARY_VERIFIER / "verification-results.json").read_text(encoding="utf-8")
    )
    return {
        "status": "SELF_AUTHORED_AUXILIARY_INTEGRITY_ONLY",
        "manifest_sha256": sha256(manifest),
        "manifest_entries_checked": len(entries),
        "stored_verdict": result.get("verdict"),
        "used_to_establish_cleanroom_verdict": False,
    }


def verify(payload: dict[str, Any]) -> dict[str, Any]:
    frozen_entries = verify_frozen_discovery()
    observed_prerequisites = {
        relative: sha256(ROOT / relative) for relative in EXPECTED_PREREQUISITES
    }
    demand(observed_prerequisites == EXPECTED_PREREQUISITES,
           "prerequisite hash drift")
    demand(payload["frozen_inputs_sha256"] == EXPECTED_PREREQUISITES,
           "payload prerequisite freeze mismatch")

    six_map, alignment_report = independent_six_alignment()
    classes6 = graph_classes(6)
    records = payload["class_profiles"]
    demand(len(records) == 62, "profile count is not 62")
    masks: dict[int, int] = {}
    supports: dict[int, list[int]] = {}
    independently_generated_witnesses: dict[str, dict[str, int]] = {}
    total_search_nodes = 0
    total_terminal_assignments = 0
    for source, record in enumerate(records, 1):
        demand(record["source_class"] == source, "profile source order drift")
        canonical_index = six_map[source - 1]
        mask = classes6[canonical_index]
        degree, pair_rhs, inside_odd = local_rhs(mask)
        demand(record["canonical_index_zero_based"] == canonical_index,
               f"canonical index mismatch in class {source}")
        demand(record["canonical_mask"] == mask, f"mask mismatch in class {source}")
        demand(record["edge_count"] == mask.bit_count(),
               f"edge count mismatch in class {source}")
        demand(record["degrees"] == degree, f"degree metadata mismatch in class {source}")
        demand(record["degree_rhs"] == [K - value for value in degree],
               f"degree right side mismatch in class {source}")
        demand(record["pair_rhs_in_lex_edge_order"] == pair_rhs,
               f"pair right side mismatch in class {source}")
        demand(record["inside_odd_weight"] == inside_odd,
               f"inside parity mismatch in class {source}")
        observed, own_witnesses, stats = enumerate_support(mask)
        demand(record["high_cell_count"] == stats["candidate_high_cells"],
               f"high-cell metadata mismatch in class {source}")
        demand(observed == record["attainable_weights"],
               f"exact support mismatch in class {source}")
        for weight, witness in own_witnesses.items():
            replay_z(mask, witness, weight)
            independently_generated_witnesses[f"{source}:{weight}"] = witness
        total_search_nodes += int(stats["search_nodes"])
        total_terminal_assignments += int(stats["terminal_assignments"])
        masks[source] = mask
        supports[source] = observed

    forced = {
        str(source): values[0]
        for source, values in supports.items()
        if len(values) == 1
    }
    demand(forced == {"1": 66, "3": 56, "5": 46, "14": 36},
           "forced singleton support set differs")
    demand(payload["forced_singleton_cells"] == forced,
           "stored forced singleton table differs")
    demand(supports[36] == [24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 72],
           "class-36 support differs")
    reverse_support, _, reverse_stats = enumerate_support(
        masks[36], reverse=True, target_only=68
    )
    demand(reverse_support == [] and reverse_stats["target_found"] is False,
           "reverse-order class-36 search found forbidden weight 68")

    published_local: dict[tuple[int, int], dict[str, int]] = {}
    for item in payload["selected_local_integer_witnesses"]:
        key = (item["source_class"], item["output_weight"])
        demand(key not in published_local, "duplicate selected local witness")
        demand(key[0] in supports and key[1] in supports[key[0]],
               "selected local witness has unsupported key")
        replay_z(masks[key[0]], item["z_by_subset_mask_sparse"], key[1])
        published_local[key] = item["z_by_subset_mask_sparse"]
    demand(len(published_local) == 66, "selected local witness count is not 66")

    aggregate = payload["aggregate_endpoint_certificate"]
    demand(aggregate["n3"] == ENDPOINT, "aggregate endpoint is not 4158")
    demand(aggregate["known_imported_cap"] == ENDPOINT, "imported cap is not 4158")
    cells: dict[tuple[int, int], int] = {}
    for item in aggregate["nonzero_cells"]:
        key = (item["source_class"], item["output_weight"])
        demand(key not in cells, "duplicate aggregate cell")
        demand(type(item["count"]) is int and item["count"] > 0,
               "aggregate count is not a positive integer")
        demand(key[0] in supports and key[1] in supports[key[0]],
               "aggregate uses unsupported class/weight cell")
        cells[key] = item["count"]
    demand(len(cells) == aggregate["nonzero_cell_count"] == 65,
           "aggregate nonzero-cell count differs")
    expected_local_keys = set(cells) | {
        (int(source), weight) for source, weight in forced.items()
    }
    demand(set(published_local) == expected_local_keys,
           "selected local witness key set is not aggregate union forced set")

    formula_payload = json.loads(WAVE21_RESULTS.read_text(encoding="utf-8"))
    six_formulas = formula_payload["formula_tables"]["six"]
    marginals: dict[str, int] = {}
    for source in range(1, 63):
        formula = six_formulas[str(source)]
        value = (
            parse_fraction(formula["constant"])
            + parse_fraction(formula["n3_coefficient"]) * ENDPOINT
        )
        demand(value.denominator == 1 and value >= 0,
               f"invalid class marginal {source}")
        observed = sum(
            count for (cell_source, _), count in cells.items()
            if cell_source == source
        )
        demand(observed == value, f"aggregate class marginal failure {source}")
        marginals[str(source)] = value.numerator
    demand(marginals == aggregate["class_marginals"],
           "stored class marginal table differs")
    demand(sum(marginals.values()) == math.comb(N, 6),
           "six-set marginal total is not C(99,6)")

    wave141 = json.loads(WAVE141_RESULTS.read_text(encoding="utf-8"))
    low_rows = {
        int(t): {int(weight): int(count) for weight, count in row.items()}
        for t, row in wave141["exact_low_input_rows"].items()
    }
    lhs = {
        t: sum(kraw(t, weight) * count for (_, weight), count in cells.items())
        for t in range(4)
    }
    rhs = {
        t: sum(kraw(6, weight) * count for weight, count in low_rows[t].items())
        for t in range(4)
    }
    demand(lhs == rhs, "t=0..3 reciprocity moments fail")
    demand({str(t): value for t, value in lhs.items()} == aggregate["moment_lhs"],
           "stored moment left side differs")
    demand(aggregate["moment_lhs"] == aggregate["moment_rhs"],
           "stored moment sides are unequal")
    demand(lhs == {
        0: 1120529256,
        1: 12854346120,
        2: 55869122232,
        3: 84712070520,
    }, "moment constants differ")

    signed_s6 = sum(
        (-1) ** (weight // 2) * count for (_, weight), count in cells.items()
    )
    expected_signed = Fraction(2024484) + Fraction(512, 3) * ENDPOINT
    demand(expected_signed.denominator == 1 and signed_s6 == expected_signed,
           "signed S6 affine identity fails")
    demand(signed_s6 == aggregate["signed_S6"] == 2734116,
           "signed S6 stored value differs")
    demand(payload["result"]["endpoint_survives"] is True,
           "endpoint-survival label differs")
    demand(payload["result"]["improves_known_n3_cap"] is False,
           "false bound-improvement label")

    own_witness_blob = json.dumps(
        independently_generated_witnesses,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    auxiliary = verify_auxiliary_package()
    return {
        "format": "wave144-sixset-odd-profile-cleanroom-verification-v1",
        "verdict": "PASS_NULL_BOUNDARY",
        "claim_label": "VERIFIED",
        "discovery_manifest_sha256": EXPECTED_DISCOVERY_MANIFEST_SHA256,
        "discovery_manifest_entries_checked": len(frozen_entries),
        "prerequisite_hashes": observed_prerequisites,
        "independent_alignment": alignment_report,
        "exact_local_supports_regenerated": len(supports),
        "total_attainable_class_weight_cells": sum(map(len, supports.values())),
        "independent_local_witness_digest_sha256": hashlib.sha256(
            own_witness_blob
        ).hexdigest(),
        "local_search_nodes": total_search_nodes,
        "local_terminal_assignments": total_terminal_assignments,
        "forced_singleton_cells": forced,
        "class_36_support": supports[36],
        "class_36_weight_68_reverse_order_exclusion": True,
        "published_local_witnesses_replayed": len(published_local),
        "published_local_key_set_exact": True,
        "aggregate_endpoint_n3": ENDPOINT,
        "aggregate_nonzero_integer_cells_replayed": len(cells),
        "aggregate_marginals_replayed": len(marginals),
        "reciprocity_moments_t0_through_t3": {
            str(t): value for t, value in lhs.items()
        },
        "signed_S6": signed_s6,
        "known_imported_cap": ENDPOINT,
        "bound_improvement": False,
        "graph_realization": "NOT_ESTABLISHED",
        "overlap_consistency": "NOT_ESTABLISHED",
        "auxiliary_verifier_audit": auxiliary,
        "scope_boundary": (
            "Exact feasibility of the stated six-set marginal relaxation at "
            "n3=4158 only; no simultaneous realization of overlapping local "
            "z_P witnesses by one 99-vertex graph is certified."
        ),
    }


def main() -> int:
    payload = json.loads(DISCOVERY_RESULTS.read_text(encoding="utf-8"))
    result = verify(payload)
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
