#!/usr/bin/env python3
"""Independent verifier for the sealed Wave 63 rational certificates.

This module intentionally does not import or execute Wave 63 discovery code.
It reconstructs the graph-derived targets, candidate columns, lane-selection
rule, and rational arithmetic using only Python's standard library.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "attempts" / "wave63-c3-integer-cone"
RESULT_PATH = PACKAGE / "exact-results.json"
TYPE_PATH = ROOT / "attempts" / "wave60-c3-incidence-design" / "component-census.json"
WAVE60_PATH = ROOT / "attempts" / "wave60-c3-incidence-design" / "exact-results.json"
WAVE61_PATH = ROOT / "attempts" / "wave61-c3-finite-field" / "exact-results.json"
WAVE36_PATH = ROOT / "verification" / "wave36-block-compatibility" / "independent-results.json"

EXPECTED_PACKAGE_MANIFEST_SHA256 = (
    "c85f9dcf3d0bdba2a41299c4a3c4fdd8c9802903cff04ab237f40d9840df6018"
)
EXPECTED_INPUT_HASHES = {
    TYPE_PATH: "16e124587df5b37b3f4735e14894982750c60a303043125985383101331eb4de",
    WAVE60_PATH: "35b6436c7ba5619fcf7e3840cbdacd594461c01df8758686450f5d8eea8e36f3",
    WAVE61_PATH: "936c76b7487d713421ef663aae4cc591f9bcf93f5d6a11f4aae3c0b5d4aa52f6",
    WAVE36_PATH: "b92ee5cde6a63ba3cce09bc2eae1518979aea09c4f5db39789b65f117b0768c4",
}

PAIRS12 = tuple(itertools.combinations(range(12), 2))
PAIRS36 = tuple(itertools.combinations(range(36), 2))
PAIR36_INDEX = {pair: index for index, pair in enumerate(PAIRS36)}


class VerificationError(AssertionError):
    """A certificate or metadata check failed."""


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
    """Return physical-memory availability on Windows, or 100 if unavailable."""

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

    try:
        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        if ok and status.total_physical:
            return 100.0 * status.available_physical / status.total_physical
    except (AttributeError, OSError):
        pass
    return 100.0


def parse_manifest(text: str) -> dict[str, str]:
    records: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        digest, name = line.split("  ", 1)
        require(len(digest) == 64, f"malformed manifest digest for {name}")
        require(name not in records, f"duplicate manifest entry: {name}")
        records[name] = digest
    return records


def verify_sealed_inputs() -> dict[str, int | str]:
    manifest_path = PACKAGE / "package-manifest.sha256"
    require(
        sha256(manifest_path) == EXPECTED_PACKAGE_MANIFEST_SHA256,
        "Wave 63 package manifest hash changed",
    )
    manifest = parse_manifest(manifest_path.read_text(encoding="utf-8"))
    actual_files = {
        path.name
        for path in PACKAGE.iterdir()
        if path.is_file() and path.name != manifest_path.name
    }
    require(set(manifest) == actual_files, "Wave 63 manifest file set mismatch")
    for name, expected in manifest.items():
        require(sha256(PACKAGE / name) == expected, f"manifest mismatch: {name}")
    for path, expected in EXPECTED_INPUT_HASHES.items():
        require(sha256(path) == expected, f"frozen upstream changed: {path}")
    return {
        "package_manifest_sha256": EXPECTED_PACKAGE_MANIFEST_SHA256,
        "package_files_checked": len(manifest),
        "upstream_files_checked": len(EXPECTED_INPUT_HASHES),
    }


def adjacency(record: dict) -> tuple[frozenset[int], ...]:
    require(record.get("degree_set") == [3], "component metadata is not cubic")
    rows = [set() for _ in range(12)]
    observed: set[tuple[int, int]] = set()
    for raw_left, raw_right in record["edges"]:
        require(
            isinstance(raw_left, int)
            and isinstance(raw_right, int)
            and 0 <= raw_left < raw_right < 12,
            "malformed component edge",
        )
        edge = (raw_left, raw_right)
        require(edge not in observed, "duplicate component edge")
        observed.add(edge)
        rows[raw_left].add(raw_right)
        rows[raw_right].add(raw_left)
    require(len(observed) == 18, "cubic component must have 18 edges")
    require(all(len(row) == 3 for row in rows), "component degree is not three")

    reached = {0}
    frontier = {0}
    while frontier:
        frontier = set().union(*(rows[vertex] for vertex in frontier)) - reached
        reached |= frontier
    require(len(reached) == 12, "component is disconnected")

    for fibre in range(3):
        vertices = set(range(4 * fibre, 4 * fibre + 4))
        require(
            all(len(rows[vertex] & vertices) == 1 for vertex in vertices),
            "within-fibre edges do not form a perfect matching",
        )
    for first, second in itertools.combinations(range(3), 2):
        left_vertices = range(4 * first, 4 * first + 4)
        right_vertices = set(range(4 * second, 4 * second + 4))
        require(
            all(len(rows[vertex] & right_vertices) == 1 for vertex in left_vertices),
            "cross-fibre edges do not form a perfect matching",
        )
    require(
        all(not (rows[left] & rows[right]) for left, right in observed),
        "component has a triangle",
    )
    return tuple(frozenset(row) for row in rows)


def load_types(data: dict) -> list[dict]:
    records = data["component_census"]["types"]
    require(len(records) == 18, "expected exactly 18 component types")
    require(
        [record["type_index"] for record in records] == list(range(18)),
        "component type ordering changed",
    )
    for record in records:
        adjacency(record)
    require(
        data["component_census"]["fibre_preserving_type_count"] == 18,
        "component census count mismatch",
    )
    return records


def local_to_global(component: int, local_vertex: int) -> int:
    fibre, position = divmod(local_vertex, 4)
    return 12 * fibre + 4 * component + position


def target_pair_values(records: Sequence[dict]) -> tuple[int, ...]:
    """Build the 630 off-diagonal entries of

    G = 12I - A_X + 2J - blockdiag(J_12,J_12,J_12) - A_X^2.
    """

    neighbours = [set() for _ in range(36)]
    for component, record in enumerate(records):
        local = adjacency(record)
        for left in range(12):
            global_left = local_to_global(component, left)
            for right in local[left]:
                neighbours[global_left].add(local_to_global(component, right))

    values = []
    for left, right in PAIRS36:
        value = (
            2
            - int(right in neighbours[left])
            - int(left // 12 == right // 12)
            - len(neighbours[left] & neighbours[right])
        )
        require(value >= 0, "target Gram entry is negative")
        values.append(value)
    for vertex in range(36):
        diagonal = 12 + 2 - 1 - len(neighbours[vertex])
        require(diagonal == 10, "target Gram diagonal is not ten")
    return tuple(values)


def pair_profile(pair: tuple[int, int]) -> tuple[int, int, int]:
    counts = [0, 0, 0]
    counts[pair[0] // 4] += 1
    counts[pair[1] // 4] += 1
    return tuple(counts)


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


def local_pair_value(record: dict, pair: tuple[int, int]) -> int:
    rows = adjacency(record)
    left, right = pair
    return (
        2
        - int(right in rows[left])
        - int(left // 4 == right // 4)
        - len(rows[left] & rows[right])
    )


def allowed_pairs_by_profile(record: dict) -> tuple[tuple[int, ...], ...]:
    groups = [[] for _ in PROFILES]
    for pair_index, pair in enumerate(PAIRS12):
        if local_pair_value(record, pair) > 0:
            groups[PROFILES.index(pair_profile(pair))].append(pair_index)
    return tuple(tuple(group) for group in groups)


def candidate_count(
    type_triple: Sequence[int],
    allowed_by_type: Sequence[Sequence[Sequence[int]]],
) -> int:
    allowed = [allowed_by_type[index] for index in type_triple]
    return sum(
        len(allowed[0][profiles[0]])
        * len(allowed[1][profiles[1]])
        * len(allowed[2][profiles[2]])
        for profiles in PROFILE_TRIPLES
    )


def candidate_columns(
    type_triple: Sequence[int],
    allowed_by_type: Sequence[Sequence[Sequence[int]]],
    target: Sequence[int],
) -> tuple[tuple[int, ...], ...]:
    allowed = [allowed_by_type[index] for index in type_triple]
    output: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    for profiles in PROFILE_TRIPLES:
        pair_groups = (
            allowed[component][profiles[component]] for component in range(3)
        )
        for pair_indices in itertools.product(*pair_groups):
            column = tuple(
                sorted(
                    local_to_global(component, vertex)
                    for component, pair_index in enumerate(pair_indices)
                    for vertex in PAIRS12[pair_index]
                )
            )
            require(column not in seen, "candidate enumeration has a duplicate")
            seen.add(column)
            require(len(column) == 6 and len(set(column)) == 6, "bad candidate size")
            require(
                Counter(vertex // 12 for vertex in column) == Counter({0: 2, 1: 2, 2: 2}),
                "candidate violates fixed-fibre margins",
            )
            require(
                Counter((vertex % 12) // 4 for vertex in column)
                == Counter({0: 2, 1: 2, 2: 2}),
                "candidate violates component margins",
            )
            require(
                all(target[PAIR36_INDEX[pair]] > 0 for pair in itertools.combinations(column, 2)),
                "candidate uses a zero-target pair",
            )
            output.append(column)
    return tuple(output)


def expected_lane_map(
    wave61_records: Sequence[dict], minimum: int, maximum: int
) -> tuple[dict[int, set[str]], list[int]]:
    reasons: dict[int, set[str]] = {}
    first_rank_indices: list[int] = []
    seen_ranks: set[int] = set()
    for record in wave61_records:
        index = record["triple_index"]
        triple = record["type_triple"]
        support = record["pair_inventory_F2"][
            "candidate_count_before_exact_multiplicities"
        ]
        current: set[str] = set()
        if triple[0] == triple[1] == triple[2]:
            current.add("diagonal component triple")
        rank = record["pair_inventory_F2"]["full_630_rank"]
        if rank not in seen_ranks:
            seen_ranks.add(rank)
            first_rank_indices.append(index)
            current.add(f"first full-pair F2 rank {rank}")
        if support == minimum:
            current.add("global minimum candidate support")
        if support == maximum:
            current.add("global maximum candidate support")
        if current:
            reasons[index] = current
    return reasons, first_rank_indices


def verify_selection(
    result: dict,
    wave61_records: Sequence[dict],
    minimum: int,
    maximum: int,
) -> dict[str, object]:
    expected, first_ranks = expected_lane_map(wave61_records, minimum, maximum)
    actual_indices = [lane["triple_index"] for lane in result["results"]]
    require(result["lane_selection"]["lane_limit"] is None, "lane limit is not full")
    require(actual_indices == sorted(expected), "fixed 74-lane selection mismatch")
    require(len(actual_indices) == 74, "fixed selection does not contain 74 lanes")
    require(len(set(actual_indices)) == 74, "duplicate selected lane")
    require(
        result["lane_selection"]["available_lane_count"] == 74
        and result["lane_selection"]["executed_lane_count"] == 74,
        "lane selection metadata mismatch",
    )
    for lane in result["results"]:
        require(
            set(lane["selection_reasons"]) == expected[lane["triple_index"]],
            f"selection reasons mismatch at lane {lane['triple_index']}",
        )
    rank_values = [
        wave61_records[index]["pair_inventory_F2"]["full_630_rank"]
        for index in first_ranks
    ]
    require(
        rank_values == [438, 446, 442, 454, 450, 462, 458],
        "first rank-stratum representatives changed",
    )
    return {
        "selected_lane_count": 74,
        "minimum_support_lane_count": sum(
            "global minimum candidate support" in item for item in expected.values()
        ),
        "maximum_support_lane_count": sum(
            "global maximum candidate support" in item for item in expected.values()
        ),
        "diagonal_lane_count": sum(
            "diagonal component triple" in item for item in expected.values()
        ),
        "rank_strata": sorted(set(rank_values)),
        "first_rank_stratum_indices": first_ranks,
        "category_memberships_before_overlap_removal": 56 + 1 + 18 + 7,
        "overlap_memberships_removed": 8,
    }


def verify_witness(
    witness: Sequence[dict],
    candidates: Sequence[tuple[int, ...]],
    expected_pairs: Sequence[int],
    *,
    require_upper_bound: bool = True,
) -> dict[str, object]:
    require(len(expected_pairs) == 630, "target equation count changed")
    coefficients: dict[int, Fraction] = {}
    for item in witness:
        index = item["candidate_index"]
        require(isinstance(index, int), "candidate index is not an integer")
        require(index not in coefficients, "duplicate candidate index")
        require(0 <= index < len(candidates), "candidate index out of range")
        numerator = item["numerator"]
        denominator = item["denominator"]
        require(
            isinstance(numerator, int) and isinstance(denominator, int),
            "coefficient is not integral numerator/denominator data",
        )
        require(denominator > 0, "coefficient denominator is not positive")
        value = Fraction(numerator, denominator)
        require(value > 0, "declared positive support has a nonpositive coefficient")
        if require_upper_bound:
            require(value <= 1, "coefficient exceeds distinct-column bound one")
        coefficients[index] = value

    totals = [Fraction(0) for _ in PAIRS36]
    for index, value in coefficients.items():
        for pair in itertools.combinations(candidates[index], 2):
            totals[PAIR36_INDEX[pair]] += value
    expected = [Fraction(value) for value in expected_pairs]
    require(totals == expected, "exact witness fails at least one pair equation")
    total_weight = sum(coefficients.values(), Fraction(0))
    require(total_weight == 60, "exact witness total weight is not 60")
    maximum = max(coefficients.values(), default=Fraction(0))
    maximum_denominator = max(
        (value.denominator for value in coefficients.values()), default=1
    )
    return {
        "support_size": len(coefficients),
        "pair_equations_checked": len(expected_pairs),
        "total_weight": str(total_weight),
        "minimum_coefficient": str(min(coefficients.values())),
        "maximum_coefficient": str(maximum),
        "maximum_denominator": maximum_denominator,
        "all_coefficients_strictly_positive": True,
        "all_coefficients_at_most_one": True,
    }


def verify_milp_metadata(results: Sequence[dict]) -> dict[str, object]:
    probed = []
    for lane in results:
        record = lane["distinct_column_milp"]
        require(record["claim_label"] == "UNKNOWN", "MILP status inflation")
        require("exact_witness" not in record, "unverified MILP witness present")
        if record.get("status") == "NOT_RUN":
            continue
        probed.append((lane["triple_index"], record))
    require(len(probed) == 1 and probed[0][0] == 0, "unexpected MILP probe set")
    record = probed[0][1]
    require(record["solver_status"] == 1, "MILP solver status changed")
    require(record["proof_certificate_supplied"] is False, "MILP proof flag inflated")
    require(
        "Time limit reached" in record["solver_message"],
        "MILP result is not the reported time-limit outcome",
    )
    require(
        "no nonexistence evidence" in record["interpretation"],
        "MILP nonhit interpretation changed",
    )
    return {
        "bounded_binary_milp_probes": 1,
        "integer_candidates": 0,
        "proof_certificates": 0,
        "status": "UNKNOWN",
        "interpretation": "30-second nonhit is not negative evidence",
    }


def verify_all(result_path: Path = RESULT_PATH) -> dict[str, object]:
    start_memory = free_memory_percent()
    require(start_memory >= 15.0, "less than 15 percent free physical memory")
    sealed = verify_sealed_inputs()

    result = json.loads(result_path.read_text(encoding="utf-8"))
    type_data = json.loads(TYPE_PATH.read_text(encoding="utf-8"))
    wave60 = json.loads(WAVE60_PATH.read_text(encoding="utf-8"))
    wave61 = json.loads(WAVE61_PATH.read_text(encoding="utf-8"))
    types = load_types(type_data)
    allowed_by_type = tuple(allowed_pairs_by_profile(record) for record in types)

    triples = list(itertools.combinations_with_replacement(range(18), 3))
    require(
        type_data["component_type_triples"] == [list(item) for item in triples],
        "Wave 60 triple ordering mismatch",
    )
    wave61_records = wave61["triple_census"]["records"]
    require(len(wave61_records) == 1140, "Wave 61 record count mismatch")
    counts = []
    ranks = []
    for index, triple in enumerate(triples):
        record = wave61_records[index]
        require(record["triple_index"] == index, "Wave 61 triple index mismatch")
        require(record["type_triple"] == list(triple), "Wave 61 triple mismatch")
        count = candidate_count(triple, allowed_by_type)
        imported_count = record["pair_inventory_F2"][
            "candidate_count_before_exact_multiplicities"
        ]
        require(count == imported_count, f"candidate census mismatch at triple {index}")
        counts.append(count)
        ranks.append(record["pair_inventory_F2"]["full_630_rank"])

    minimum = min(counts)
    maximum = max(counts)
    require((minimum, maximum) == (15936, 27200), "candidate extrema changed")
    require(
        minimum == wave60["individual_column_support"]["minimum_over_triples"]
        and maximum == wave60["individual_column_support"]["maximum_over_triples"],
        "Wave 60 candidate extrema mismatch",
    )
    histogram = {str(key): value for key, value in sorted(Counter(counts).items())}
    validation = result["input_validation"]
    require(validation["triple_count"] == 1140, "reported triple count mismatch")
    require(validation["count_histogram"] == histogram, "candidate histogram mismatch")
    require(validation["minimum"] == minimum, "reported minimum mismatch")
    require(validation["maximum"] == maximum, "reported maximum mismatch")
    expected_minimum_records = [
        {"triple_index": index, "type_triple": list(triples[index])}
        for index, count in enumerate(counts)
        if count == minimum
    ]
    expected_maximum_records = [
        {"triple_index": index, "type_triple": list(triples[index])}
        for index, count in enumerate(counts)
        if count == maximum
    ]
    require(
        validation["minimum_records"] == expected_minimum_records,
        "minimum-support records mismatch",
    )
    require(
        validation["maximum_records"] == expected_maximum_records,
        "maximum-support records mismatch",
    )
    require(len(expected_minimum_records) == 56, "minimum-support count changed")
    require(len(expected_maximum_records) == 1, "maximum-support count changed")

    selection = verify_selection(result, wave61_records, minimum, maximum)
    result_by_index = {lane["triple_index"]: lane for lane in result["results"]}
    witness_stats = []
    for position, index in enumerate(sorted(result_by_index)):
        if position % 8 == 0:
            require(
                free_memory_percent() >= 15.0,
                "physical memory fell below 15 percent during verification",
            )
        lane = result_by_index[index]
        triple = triples[index]
        require(lane["type_triple"] == list(triple), f"lane {index} triple mismatch")
        require(lane["candidate_count"] == counts[index], f"lane {index} count mismatch")
        require(
            lane["full_pair_F2_rank"] == ranks[index],
            f"lane {index} rank mismatch",
        )
        records = [types[type_index] for type_index in triple]
        target = target_pair_values(records)
        require(
            lane["all_pair_equations"] == 630,
            f"lane {index} equation-count mismatch",
        )
        require(
            lane["active_positive_pair_equations"]
            == sum(value > 0 for value in target),
            f"lane {index} active-equation mismatch",
        )
        candidates = candidate_columns(triple, allowed_by_type, target)
        require(
            len(candidates) == counts[index],
            f"lane {index} candidate enumeration mismatch",
        )
        cone = lane["rational_cone"]
        require(cone["claim_label"] == "DERIVED", f"lane {index} cone not DERIVED")
        require(cone["floating_only"] is False, f"lane {index} is floating-only")
        replay = verify_witness(cone["exact_witness"], candidates, target)
        metadata = cone["exact_replay"]
        support = replay["support_size"]
        require(
            support == metadata["coefficient_count"]
            == metadata["square_minor_order"]
            == cone["floating_positive_support"],
            f"lane {index} support metadata mismatch",
        )
        require(
            support == lane["full_pair_F2_rank"],
            f"lane {index} support size differs from reported F2 rank",
        )
        require(
            replay["maximum_coefficient"] == metadata["maximum_coefficient"],
            f"lane {index} maximum coefficient mismatch",
        )
        require(
            replay["maximum_denominator"] == metadata["maximum_denominator"],
            f"lane {index} maximum denominator mismatch",
        )
        require(
            metadata["all_630_pair_equations_exact"] is True
            and metadata["total_weight"] == "60",
            f"lane {index} exact replay metadata mismatch",
        )
        witness_stats.append(replay)

    require(result["claim_label"] == "DERIVED", "result label changed")
    require(result["summary"]["exact_rational_cone_witnesses"] == 74, "cone summary mismatch")
    require(result["summary"]["exact_distinct_column_candidates"] == 0, "integer summary mismatch")
    require(result["summary"]["endpoint_status"] == "UNKNOWN", "endpoint status inflated")
    require(result["summary"]["conway_99_status"] == "UNKNOWN", "Conway status inflated")
    require(result["summary"]["novelty"] == "UNKNOWN", "novelty status inflated")
    milp = verify_milp_metadata(result["results"])

    support_histogram = {
        str(key): value
        for key, value in sorted(Counter(item["support_size"] for item in witness_stats).items())
    }
    rank_histogram_selected = {
        str(key): value
        for key, value in sorted(Counter(ranks[index] for index in sorted(result_by_index)).items())
    }
    require(
        support_histogram == rank_histogram_selected,
        "selected support/rank histograms differ",
    )
    finish_memory = free_memory_percent()
    require(finish_memory >= 15.0, "less than 15 percent free memory after verification")
    return {
        "claim_label": "VERIFIED",
        "scope": (
            "conditional prism-free n3=4158, kappa=3 fixed-triangle lane; "
            "74 selected rational pair-cone certificates only"
        ),
        "sealed_inputs": sealed,
        "component_types_checked": 18,
        "component_type_triples_recounted": 1140,
        "candidate_count_minimum": minimum,
        "candidate_count_maximum": maximum,
        "candidate_count_histogram": histogram,
        "selection": selection,
        "rational_witnesses_checked": 74,
        "pair_equations_checked_per_witness": 630,
        "pair_equations_checked_total": 74 * 630,
        "coefficient_bounds_checked": "0 < x_s <= 1 exactly",
        "support_size_range": [
            min(item["support_size"] for item in witness_stats),
            max(item["support_size"] for item in witness_stats),
        ],
        "support_size_histogram": support_histogram,
        "reported_rank_histogram_on_selected_lanes": rank_histogram_selected,
        "support_size_equals_reported_full_pair_F2_rank_on_all_lanes": True,
        "milp": milp,
        "mathematical_mismatches": 0,
        "endpoint_status": "UNKNOWN",
        "conway_99_status": "UNKNOWN",
        "novelty": "UNKNOWN",
        "limitations": [
            "Only the fixed 74-lane subset is covered, not all 1,140 triples or 275 safe coordinate orbits.",
            "Exact rational coefficients are not binary incidence designs.",
            "No compatible Y graph or full strongly regular graph is constructed.",
            "The bounded MILP nonhit has no proof certificate and is not negative evidence.",
        ],
        "free_physical_memory_percent_start": round(start_memory, 3),
        "free_physical_memory_percent_finish": round(finish_memory, 3),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", type=Path, default=RESULT_PATH)
    arguments = parser.parse_args()
    print(json.dumps(verify_all(arguments.verify), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
