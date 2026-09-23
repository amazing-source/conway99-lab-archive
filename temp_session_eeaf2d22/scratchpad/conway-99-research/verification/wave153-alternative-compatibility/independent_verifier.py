"""Clean-room verifier for the sealed Wave153 rational witnesses.

This module does not import or execute any Wave153 discovery code.  It builds
the component action, target Gram entries, allowed six-set columns, and exact
rational replays directly from the frozen JSON inputs.
"""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import itertools
import json
import math
import re
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
DISCOVERY = ROOT / "attempts" / "wave153-alternative-compatibility"
COMPONENTS_PATH = (
    ROOT / "attempts" / "wave60-c3-incidence-design/component-census.json"
)
INVARIANTS_PATH = (
    ROOT / "attempts" / "wave60-c3-incidence-design/invariant-results.json"
)
RESULTS_PATH = DISCOVERY / "exact-results.json.gz"
INPUT_FREEZE_PATH = DISCOVERY / "input-freeze.sha256"
PACKAGE_MANIFEST_PATH = DISCOVERY / "package-manifest.sha256"

EXPECTED_PACKAGE_MANIFEST_SHA256 = (
    "31234fe670e26a534d6087515ec969e7ac1b670190da318dd97cbcdae26ee8d0"
)
EXPECTED_RESULTS_SHA256 = (
    "af3df69fa2542066cd1089f75f09f16582c0583f0304b60df3b9516d0ff035dd"
)
EXPECTED_INPUT_FREEZE_SHA256 = (
    "5b55cb9f338b5b8d21a1ddf0c8ec490f9a33a31f1e10f875d249fa0d43a9e06d"
)

PAIRS12 = tuple(itertools.combinations(range(12), 2))
PAIRS36 = tuple(itertools.combinations(range(36), 2))
PAIR12_INDEX = {pair: index for index, pair in enumerate(PAIRS12)}
PAIR36_INDEX = {pair: index for index, pair in enumerate(PAIRS36)}
PERM4 = tuple(itertools.permutations(range(4)))
PERM3 = tuple(itertools.permutations(range(3)))
RATIONAL_RE = re.compile(r"(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?")


class VerificationError(AssertionError):
    """Raised whenever a certificate fails closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def free_memory_percent() -> float:
    """Return available physical-memory percentage on Windows."""

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong),
            ("available_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.available_physical / status.total_physical


def parse_manifest(path: Path) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"malformed manifest line {line_number} in {path}")
        digest, relative_text = match.groups()
        relative = Path(relative_text)
        require(not relative.is_absolute(), f"absolute manifest path: {relative}")
        resolved = (ROOT / relative).resolve()
        require(
            resolved == ROOT or ROOT in resolved.parents,
            f"manifest path escapes repository: {relative}",
        )
        require(resolved not in seen, f"duplicate manifest path: {relative}")
        seen.add(resolved)
        entries.append((digest, resolved))
    require(entries, f"empty manifest: {path}")
    return entries


def verify_manifest(path: Path) -> int:
    entries = parse_manifest(path)
    for expected, target in entries:
        require(target.is_file(), f"manifest target is missing: {target}")
        require(sha256(target) == expected, f"hash mismatch: {target}")
    return len(entries)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_gzip_json(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as source:
        return json.load(source)


def adjacency(record: dict) -> tuple[frozenset[int], ...]:
    require(record.get("type_index") in range(18), "invalid component type index")
    rows = [set() for _ in range(12)]
    edges = record.get("edges")
    require(isinstance(edges, list) and len(edges) == 18, "component edge count changed")
    seen: set[tuple[int, int]] = set()
    for item in edges:
        require(
            isinstance(item, list)
            and len(item) == 2
            and all(isinstance(v, int) and not isinstance(v, bool) for v in item),
            "malformed component edge",
        )
        left, right = item
        require(0 <= left < right < 12, "component edge is not canonical")
        require((left, right) not in seen, "duplicate component edge")
        seen.add((left, right))
        rows[left].add(right)
        rows[right].add(left)
    require(all(len(row) == 3 for row in rows), "component is not cubic")
    require(
        all(not (rows[u] & rows[v]) for u, v in seen),
        "component contains a triangle",
    )
    return tuple(frozenset(row) for row in rows)


def component_records(component_data: dict) -> list[dict]:
    census = component_data.get("component_census", {})
    records = census.get("types")
    require(isinstance(records, list) and len(records) == 18, "expected 18 types")
    require(
        [record.get("type_index") for record in records] == list(range(18)),
        "component type order changed",
    )
    require(census.get("fibre_preserving_type_count") == 18, "type count mismatch")
    for record in records:
        adjacency(record)
    return records


def edge_mask(edges: Iterable[tuple[int, int]], relabel: Sequence[int]) -> int:
    mask = 0
    for left, right in edges:
        image = tuple(sorted((relabel[left], relabel[right])))
        mask |= 1 << PAIR12_INDEX[image]
    return mask


def fibre_canonical_key(edges: Sequence[tuple[int, int]]) -> int:
    best: int | None = None
    for p0 in PERM4:
        for p1 in PERM4:
            for p2 in PERM4:
                permutations = (p0, p1, p2)
                relabel = [
                    4 * fibre + permutations[fibre][position]
                    for fibre in range(3)
                    for position in range(4)
                ]
                mask = edge_mask(edges, relabel)
                if best is None or mask < best:
                    best = mask
    require(best is not None, "failed to canonicalize component")
    return best


def reconstruct_action(records: Sequence[dict]) -> list[dict]:
    """Rebuild the S3 fibre-coordinate action using only graph isomorphism."""

    base_keys = [
        fibre_canonical_key([tuple(edge) for edge in record["edges"]])
        for record in records
    ]
    require(len(set(base_keys)) == 18, "component types are not distinct")
    key_to_type = {key: index for index, key in enumerate(base_keys)}
    action = []
    for fibre_permutation in PERM3:
        mapping = []
        for record in records:
            moved_edges = []
            for left, right in record["edges"]:
                moved_edges.append(
                    (
                        4 * fibre_permutation[left // 4] + left % 4,
                        4 * fibre_permutation[right // 4] + right % 4,
                    )
                )
            key = fibre_canonical_key(moved_edges)
            require(key in key_to_type, "fibre action leaves the frozen type set")
            mapping.append(key_to_type[key])
        require(sorted(mapping) == list(range(18)), "type action is not bijective")
        action.append(
            {
                "fibre_permutation": list(fibre_permutation),
                "type_mapping": mapping,
            }
        )
    return action


def reconstruct_orbits(
    triples: Sequence[Sequence[int]], action: Sequence[dict]
) -> list[dict]:
    canonical_triples = [tuple(triple) for triple in triples]
    require(
        canonical_triples
        == list(itertools.combinations_with_replacement(range(18), 3)),
        "the 1,140 triples are not in canonical order",
    )
    triple_index = {triple: index for index, triple in enumerate(canonical_triples)}
    unseen = set(range(len(canonical_triples)))
    orbits = []
    while unseen:
        representative_index = min(unseen)
        representative = canonical_triples[representative_index]
        orbit_triples = {
            tuple(sorted(action_item["type_mapping"][entry] for entry in representative))
            for action_item in action
        }
        indices = sorted(triple_index[triple] for triple in orbit_triples)
        require(representative_index == min(indices), "orbit representative is not minimal")
        require(set(indices) <= unseen, "coordinate orbits overlap")
        unseen.difference_update(indices)
        orbits.append(
            {
                "orbit_size": len(indices),
                "triple_indices": indices,
                "type_triple": list(representative),
            }
        )
    require(len(orbits) == 275, "safe coordinate orbit count is not 275")
    require(sum(item["orbit_size"] for item in orbits) == 1140, "orbit coverage failed")
    require(
        set(itertools.chain.from_iterable(item["triple_indices"] for item in orbits))
        == set(range(1140)),
        "coordinate action does not cover all triples",
    )
    return orbits


def local_to_global(component: int, local_vertex: int) -> int:
    fibre, position = divmod(local_vertex, 4)
    return 12 * fibre + 4 * component + position


def target_pair_values(type_triple: Sequence[int], rows_by_type: Sequence) -> tuple[int, ...]:
    neighbours = [set() for _ in range(36)]
    for component, type_index in enumerate(type_triple):
        local_rows = rows_by_type[type_index]
        for left in range(12):
            global_left = local_to_global(component, left)
            neighbours[global_left] = {
                local_to_global(component, right) for right in local_rows[left]
            }

    target = []
    for left, right in PAIRS36:
        value = (
            2
            - int(right in neighbours[left])
            - int(left // 12 == right // 12)
            - len(neighbours[left] & neighbours[right])
        )
        require(value in (0, 1, 2), "invalid off-diagonal Gram entry")
        target.append(value)
    for vertex in range(36):
        diagonal = 12 + 2 - 1 - len(neighbours[vertex])
        require(diagonal == 10, "Gram diagonal is not ten")
        require(
            sum(
                target[PAIR36_INDEX[tuple(sorted((vertex, other)))]]
                for other in range(36)
                if other != vertex
            )
            == 50,
            "off-diagonal Gram row sum is not fifty",
        )
    return tuple(target)


def pair_profile(pair: tuple[int, int]) -> tuple[int, int, int]:
    return tuple(sum(vertex // 4 == fibre for vertex in pair) for fibre in range(3))


PROFILES = tuple(sorted({pair_profile(pair) for pair in PAIRS12}))
PROFILE_TRIPLES = tuple(
    profiles
    for profiles in itertools.product(range(len(PROFILES)), repeat=3)
    if tuple(
        sum(PROFILES[profiles[component]][fibre] for component in range(3))
        for fibre in range(3)
    )
    == (2, 2, 2)
)
require(len(PROFILES) == 6, "local pair-profile count changed")
require(len(PROFILE_TRIPLES) == 21, "compatible profile-pattern count changed")


def local_pair_value(rows: Sequence[frozenset[int]], pair: tuple[int, int]) -> int:
    left, right = pair
    return (
        2
        - int(right in rows[left])
        - int(left // 4 == right // 4)
        - len(rows[left] & rows[right])
    )


def allowed_pairs_by_type(rows_by_type: Sequence) -> tuple:
    output = []
    for rows in rows_by_type:
        groups = [[] for _ in PROFILES]
        for pair_index, pair in enumerate(PAIRS12):
            if local_pair_value(rows, pair) > 0:
                groups[PROFILES.index(pair_profile(pair))].append(pair_index)
        require(all(groups), "a component has an empty local pair profile")
        output.append(tuple(tuple(group) for group in groups))
    return tuple(output)


def candidate_columns(
    type_triple: Sequence[int],
    allowed: Sequence,
    target: Sequence[int],
) -> tuple[tuple[int, ...], ...]:
    """Enumerate every allowed six-set in a canonical profile/product order."""

    component_groups = [allowed[type_index] for type_index in type_triple]
    output: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    for profiles in PROFILE_TRIPLES:
        groups = [
            component_groups[component][profiles[component]]
            for component in range(3)
        ]
        for local_pair_indices in itertools.product(*groups):
            column = tuple(
                sorted(
                    local_to_global(component, vertex)
                    for component, pair_index in enumerate(local_pair_indices)
                    for vertex in PAIRS12[pair_index]
                )
            )
            require(column not in seen, "duplicate candidate six-set")
            seen.add(column)
            require(len(column) == 6 and len(set(column)) == 6, "bad six-set")
            require(
                Counter(vertex // 12 for vertex in column)
                == Counter({0: 2, 1: 2, 2: 2}),
                "candidate violates two-per-fibre",
            )
            require(
                Counter((vertex % 12) // 4 for vertex in column)
                == Counter({0: 2, 1: 2, 2: 2}),
                "candidate violates two-per-component",
            )
            require(
                all(
                    target[PAIR36_INDEX[pair]] > 0
                    for pair in itertools.combinations(column, 2)
                ),
                "candidate contains a zero-target pair",
            )
            output.append(column)
    return tuple(output)


def decode_rational(text: object) -> Fraction:
    require(isinstance(text, str), "coefficient is not a string")
    require(RATIONAL_RE.fullmatch(text) is not None, "malformed rational coefficient")
    value = Fraction(text)
    require(str(value) == text, "rational coefficient is not canonical")
    return value


def verify_lane_identity(lane: dict, position: int, orbit: dict) -> None:
    require(lane.get("orbit_position") == position, "wrong orbit position")
    require(lane.get("type_triple") == orbit["type_triple"], "wrong type triple")
    require(
        lane.get("representative_triple_index") == orbit["triple_indices"][0],
        "wrong representative triple index",
    )
    require(lane.get("orbit_size") == orbit["orbit_size"], "wrong orbit size")
    require(lane.get("claim_label") == "CANDIDATE", "lane status inflation")


def verify_lane(
    lane: dict,
    position: int,
    orbit: dict,
    candidates: Sequence[tuple[int, ...]],
    target: Sequence[int],
) -> dict:
    verify_lane_identity(lane, position, orbit)
    require(lane.get("candidate_count") == len(candidates), "candidate count mismatch")
    require(
        lane.get("active_pair_equations") == sum(value > 0 for value in target),
        "active pair-equation count mismatch",
    )

    witness = lane.get("exact_witness")
    require(isinstance(witness, list) and witness, "missing exact witness")
    coefficients: dict[int, Fraction] = {}
    for item in witness:
        require(isinstance(item, list) and len(item) == 2, "malformed witness item")
        candidate_index, rational_text = item
        require(
            isinstance(candidate_index, int) and not isinstance(candidate_index, bool),
            "candidate index is not an integer",
        )
        require(candidate_index not in coefficients, "duplicate candidate index")
        require(0 <= candidate_index < len(candidates), "candidate index out of range")
        coefficient = decode_rational(rational_text)
        require(0 < coefficient <= 1, "coefficient violates 0 < x <= 1")
        coefficients[candidate_index] = coefficient

    pair_totals = [Fraction(0) for _ in PAIRS36]
    row_margins = [Fraction(0) for _ in range(36)]
    total_weight = Fraction(0)
    for candidate_index, coefficient in coefficients.items():
        column = candidates[candidate_index]
        total_weight += coefficient
        for vertex in column:
            row_margins[vertex] += coefficient
        for pair in itertools.combinations(column, 2):
            pair_totals[PAIR36_INDEX[pair]] += coefficient

    require(
        pair_totals == [Fraction(value) for value in target],
        "one or more of 630 pair equations failed",
    )
    require(row_margins == [Fraction(10)] * 36, "one or more row margins failed")
    require(total_weight == 60, "total weight is not sixty")

    replay = lane.get("exact_replay", {})
    support = len(coefficients)
    fixed_one = sum(value == 1 for value in coefficients.values())
    maximum = max(coefficients.values())
    maximum_denominator = max(value.denominator for value in coefficients.values())
    require(replay.get("support") == support, "support metadata mismatch")
    require(replay.get("fixed_one_coordinates") == fixed_one, "fixed-one mismatch")
    require(
        replay.get("square_minor_order") == support - fixed_one,
        "square-minor order mismatch",
    )
    require(
        replay.get("maximum_coefficient") == str(maximum),
        "maximum-coefficient metadata mismatch",
    )
    require(
        replay.get("maximum_denominator") == maximum_denominator,
        "maximum-denominator metadata mismatch",
    )
    require(decode_rational(replay.get("total_weight")) == 60, "replay total mismatch")
    require(replay.get("all_630_pair_equations_exact") is True, "pair replay flag false")
    require(replay.get("all_36_row_margins_exact") is True, "row replay flag false")
    require(replay.get("all_coefficients_in_0_1") is True, "bound replay flag false")
    return {
        "candidate_count": len(candidates),
        "support": support,
        "maximum_coefficient": maximum,
        "maximum_denominator": maximum_denominator,
    }


def verify_scope_wall(results: dict) -> None:
    result = results.get("result", {})
    require(result.get("binary_incidence_design") == "UNKNOWN", "binary status inflated")
    require(result.get("compatible_residual_graph") == "UNKNOWN", "residual status inflated")
    require(result.get("endpoint_n3_4158") == "UNKNOWN", "endpoint status inflated")
    require(result.get("Conway_99") == "UNKNOWN", "Conway-99 status inflated")
    require(result.get("external_novelty") == "UNKNOWN", "novelty status inflated")
    require(result.get("strict_n3_upper_bound") == "NOT_OBTAINED", "bound status inflated")


def run_verification() -> dict:
    started = time.perf_counter()
    memory_start = free_memory_percent()
    require(memory_start >= 15.0, "available physical memory is below 15%")

    require(
        sha256(PACKAGE_MANIFEST_PATH) == EXPECTED_PACKAGE_MANIFEST_SHA256,
        "sealed package manifest changed",
    )
    manifest_entries = verify_manifest(PACKAGE_MANIFEST_PATH)
    require(sha256(RESULTS_PATH) == EXPECTED_RESULTS_SHA256, "results payload changed")
    require(
        sha256(INPUT_FREEZE_PATH) == EXPECTED_INPUT_FREEZE_SHA256,
        "input-freeze file changed",
    )
    frozen_input_entries = verify_manifest(INPUT_FREEZE_PATH)

    component_data = load_json(COMPONENTS_PATH)
    invariant_data = load_json(INVARIANTS_PATH)
    results = load_gzip_json(RESULTS_PATH)
    records = component_records(component_data)
    rows_by_type = [adjacency(record) for record in records]

    action = reconstruct_action(records)
    require(
        action == invariant_data.get("simultaneous_fibre_permutation_action"),
        "independent coordinate action differs from frozen action",
    )
    triples = component_data.get("component_type_triples")
    require(isinstance(triples, list) and len(triples) == 1140, "triple census changed")
    orbits = reconstruct_orbits(triples, action)
    frozen_orbits = invariant_data.get("safe_triple_orbit_reduction", {})
    require(frozen_orbits.get("orbit_count") == 275, "frozen orbit count mismatch")
    require(orbits == frozen_orbits.get("representatives"), "orbit representatives differ")

    require(results.get("claim_label") == "CANDIDATE", "discovery status inflated")
    lanes = results.get("results")
    require(isinstance(lanes, list) and len(lanes) == 275, "expected 275 witnesses")
    allowed = allowed_pairs_by_type(rows_by_type)

    lane_summaries = []
    candidate_histogram: Counter[int] = Counter()
    for position, (lane, orbit) in enumerate(zip(lanes, orbits)):
        target = target_pair_values(orbit["type_triple"], rows_by_type)
        candidates = candidate_columns(orbit["type_triple"], allowed, target)
        summary = verify_lane(lane, position, orbit, candidates, target)
        lane_summaries.append(summary)
        candidate_histogram[summary["candidate_count"]] += orbit["orbit_size"]
        if position % 25 == 0:
            require(free_memory_percent() >= 15.0, "memory floor breached")

    candidate_counts = [item["candidate_count"] for item in lane_summaries]
    supports = [item["support"] for item in lane_summaries]
    global_maximum = max(item["maximum_coefficient"] for item in lane_summaries)
    global_denominator = max(item["maximum_denominator"] for item in lane_summaries)
    polytope = results.get("polytope", {})
    require(polytope.get("equations_per_lane") == 630, "equation metadata mismatch")
    require(polytope.get("row_margins_checked_per_lane") == 36, "row metadata mismatch")
    require(polytope.get("candidate_count_range") == [min(candidate_counts), max(candidate_counts)], "candidate range mismatch")
    require(polytope.get("witness_support_range") == [min(supports), max(supports)], "support range mismatch")
    require(polytope.get("maximum_coefficient") == str(global_maximum), "global maximum mismatch")
    require(polytope.get("maximum_denominator") == global_denominator, "global denominator mismatch")
    require(polytope.get("coefficient_bounds") == ["0", "1"], "bound metadata mismatch")
    require(polytope.get("all_coefficients_in_0_1") is True, "global bound flag false")
    require(polytope.get("all_pair_equations_exact") is True, "global pair flag false")
    require(polytope.get("all_row_margins_exact") is True, "global row flag false")

    expected_distribution = invariant_data["available_distinct_column_count"]["distribution"]
    require(
        {str(key): value for key, value in sorted(candidate_histogram.items())}
        == expected_distribution,
        "representative candidate histogram differs from frozen 1,140-triple histogram",
    )

    coverage = results.get("coverage", {})
    require(coverage.get("component_types") == 18, "coverage type count mismatch")
    require(coverage.get("unordered_type_triples") == 1140, "coverage triple count mismatch")
    require(coverage.get("safe_coordinate_orbits") == 275, "coverage orbit count mismatch")
    require(coverage.get("representatives_with_exact_witnesses") == 275, "witness count mismatch")
    require(
        coverage.get("representatives_not_previously_tested_as_the_exact_triple")
        == sum(not lane.get("previously_tested_exact_triple") for lane in lanes),
        "prior-lane coverage mismatch",
    )
    require(
        coverage.get("all_1140_transferred_by_frozen_coordinate_action") is True,
        "transfer coverage flag false",
    )
    verify_scope_wall(results)

    memory_end = free_memory_percent()
    require(memory_end >= 15.0, "available physical memory fell below 15%")
    elapsed = time.perf_counter() - started
    return {
        "claim_label": "VERIFIED",
        "disposition": (
            "VERIFIED_WITH_SCOPE: exact rational null witness for the complete "
            "safe-orbit bounded pair-correlation projection only"
        ),
        "scope": (
            "complete 275-representative bounded rational pair-correlation "
            "projection covering 1,140 unordered component triples"
        ),
        "package_manifest_sha256": EXPECTED_PACKAGE_MANIFEST_SHA256,
        "exact_results_sha256": EXPECTED_RESULTS_SHA256,
        "package_manifest_entries_verified": manifest_entries,
        "frozen_input_entries_verified": frozen_input_entries,
        "component_adjacency_matrices_rebuilt": 18,
        "coordinate_action_elements_rebuilt": 6,
        "coordinate_orbits_rebuilt": len(orbits),
        "unordered_triples_covered": sum(item["orbit_size"] for item in orbits),
        "representatives_replayed": len(lanes),
        "pair_equations_replayed": 630 * len(lanes),
        "row_margins_replayed": 36 * len(lanes),
        "candidate_count_range": [min(candidate_counts), max(candidate_counts)],
        "witness_support_range": [min(supports), max(supports)],
        "maximum_denominator": global_denominator,
        "hostile_mutations": "tested separately by test_independent_verifier.py",
        "scope_exclusions": [
            "binary incidence design",
            "compatible residual graph",
            "endpoint existence or exclusion",
            "strict n3 upper bound",
            "Conway-99 resolution",
            "external novelty",
        ],
        "free_memory_percent_start": memory_start,
        "free_memory_percent_end": memory_end,
        "elapsed_seconds": elapsed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    arguments = parser.parse_args()
    result = run_verification()
    print(
        json.dumps(
            result,
            sort_keys=True,
            separators=(",", ":") if arguments.compact else None,
            indent=None if arguments.compact else 2,
        )
    )


if __name__ == "__main__":
    main()
