#!/usr/bin/env python3
"""Independent verification of the Wave 81 graphicality refinement.

This module treats the previously verified 43+7 histogram rows as its
conditional input domain.  It does not import either Wave 81 checker.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import os
from collections import Counter
from pathlib import Path
from typing import Iterable


EXPECTED_DISCOVERY_RESULTS_SHA256 = (
    "b9cde2a059c15c3efe5e0f7cd5508e5a68238869c675189ca479c5d206d33707"
)
EXPECTED_SOURCE_VERIFIER_MANIFEST_SHA256 = (
    "311b7a0f8fbb330bf98c9d64d3517b9602ac86c818f830bb10f2bcc09091b0af"
)
EXPECTED_SOURCE_VERIFIER_RESULTS_SHA256 = (
    "348fa25953bcc4df6055cb028ce45aa5f63df2cd2d3a86f3d89bb109f702ea28"
)

TYPE_VALUES = {
    "X0": tuple(range(2, 9)),
    "X1": tuple(range(0, 6)),
    "X2": tuple(range(0, 4)),
}
TYPE_SIZES = {"X0": 11, "X1": 64, "X2": 8}
PAIR_NAMES = (
    "X0_induced",
    "X0_X1",
    "X0_X2",
    "X1_induced",
    "X1_X2",
    "X2_induced",
)


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0
    import ctypes

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("avail_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("avail_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("avail_virtual", ctypes.c_ulonglong),
            ("avail_extended", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise OSError("GlobalMemoryStatusEx failed")
    return 100.0 * status.avail_phys / status.total_phys


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def expand_histogram(histogram: Iterable[int], values: Iterable[int]) -> list[int]:
    return [
        value
        for value, multiplicity in zip(values, histogram)
        for _ in range(multiplicity)
    ]


def run_length_encode(sequence: Iterable[int]) -> list[list[int]]:
    return [
        [degree, multiplicity]
        for degree, multiplicity in sorted(
            Counter(sequence).items(), reverse=True
        )
    ]


def erdos_gallai(degrees: Iterable[int]) -> tuple[bool, dict[str, int] | None]:
    """Exact simple-graph test, returning the first failed inequality."""

    sequence = sorted(degrees, reverse=True)
    n = len(sequence)
    if any(not isinstance(value, int) or value < 0 or value >= n for value in sequence):
        return False, {"kind": "bounds"}
    if sum(sequence) % 2:
        return False, {"kind": "parity"}
    for k in range(1, n + 1):
        lhs = sum(sequence[:k])
        rhs = k * (k - 1) + sum(min(k, value) for value in sequence[k:])
        if lhs > rhs:
            return False, {"kind": "inequality", "k": k, "lhs": lhs, "rhs": rhs}
    return True, None


def havel_hakimi(degrees: Iterable[int]) -> bool:
    """Separate greedy realization test for a simple degree sequence."""

    pending = list(degrees)
    if any(not isinstance(value, int) or value < 0 for value in pending):
        return False
    while pending:
        pending.sort(reverse=True)
        demand = pending.pop(0)
        if demand == 0:
            return True
        if demand > len(pending):
            return False
        for index in range(demand):
            pending[index] -= 1
            if pending[index] < 0:
                return False
    return True


def gale_ryser(left: Iterable[int], right: Iterable[int]) -> tuple[bool, dict[str, int] | None]:
    """Exact bigraphicality test, returning the first failed inequality."""

    left_sequence = sorted(left, reverse=True)
    right_sequence = sorted(right, reverse=True)
    n_left, n_right = len(left_sequence), len(right_sequence)
    if (
        any(not isinstance(value, int) or value < 0 or value > n_right for value in left_sequence)
        or any(
            not isinstance(value, int) or value < 0 or value > n_left
            for value in right_sequence
        )
    ):
        return False, {"kind": "bounds"}
    if sum(left_sequence) != sum(right_sequence):
        return False, {
            "kind": "sum",
            "left": sum(left_sequence),
            "right": sum(right_sequence),
        }
    for k in range(1, n_left + 1):
        lhs = sum(left_sequence[:k])
        rhs = sum(min(k, value) for value in right_sequence)
        if lhs > rhs:
            return False, {"kind": "inequality", "k": k, "lhs": lhs, "rhs": rhs}
    return True, None


def bipartite_havel_hakimi(left: Iterable[int], right: Iterable[int]) -> bool:
    """Independent greedy bigraphicality test."""

    left_pending = list(left)
    right_pending = list(right)
    if any(
        not isinstance(value, int) or value < 0
        for value in left_pending + right_pending
    ):
        return False
    while left_pending:
        left_pending.sort(reverse=True)
        demand = left_pending.pop(0)
        right_pending.sort(reverse=True)
        if demand > len(right_pending):
            return False
        for index in range(demand):
            right_pending[index] -= 1
            if right_pending[index] < 0:
                return False
    return not any(right_pending)


@functools.lru_cache(maxsize=None)
def simple_degree_oracle(n: int) -> frozenset[tuple[int, ...]]:
    """Enumerate every simple graph once and retain its degree multiset."""

    if n > 6:
        raise ValueError("tiny oracle is restricted to at most six vertices")
    edges = tuple(itertools.combinations(range(n), 2))
    found_sequences: set[tuple[int, ...]] = set()
    for mask in range(1 << len(edges)):
        found = [0] * n
        for bit, (u, v) in enumerate(edges):
            if (mask >> bit) & 1:
                found[u] += 1
                found[v] += 1
        found_sequences.add(tuple(sorted(found, reverse=True)))
    return frozenset(found_sequences)


def brute_force_simple_graphical(degrees: Iterable[int]) -> bool:
    """Tiny-instance oracle used only by hostile tests."""

    target = tuple(sorted(degrees, reverse=True))
    return target in simple_degree_oracle(len(target))


@functools.lru_cache(maxsize=None)
def bipartite_degree_oracle(
    n_left: int, n_right: int
) -> frozenset[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Enumerate every tiny bipartite graph once."""

    if n_left * n_right > 12:
        raise ValueError("tiny oracle is restricted to at most twelve cells")
    found_pairs: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()
    for mask in range(1 << (n_left * n_right)):
        found_left = [0] * n_left
        found_right = [0] * n_right
        for i in range(n_left):
            for j in range(n_right):
                if (mask >> (i * n_right + j)) & 1:
                    found_left[i] += 1
                    found_right[j] += 1
        found_pairs.add(
            (
                tuple(sorted(found_left, reverse=True)),
                tuple(sorted(found_right, reverse=True)),
            )
        )
    return frozenset(found_pairs)


def brute_force_bigraphical(left: Iterable[int], right: Iterable[int]) -> bool:
    """Tiny-instance oracle used only by hostile tests."""

    target_left = tuple(sorted(left, reverse=True))
    target_right = tuple(sorted(right, reverse=True))
    return (target_left, target_right) in bipartite_degree_oracle(
        len(target_left), len(target_right)
    )


def canonical_histograms(source_row: dict[str, object]) -> dict[str, tuple[int, ...]]:
    keys = {
        "X0": "X0_a_histogram_for_a_2_through_8",
        "X1": "X1_a_histogram_for_a_0_through_5",
        "X2": "X2_a_histogram_for_a_0_through_3",
    }
    answer: dict[str, tuple[int, ...]] = {}
    for vertex_type, key in keys.items():
        raw = source_row[key]
        if not isinstance(raw, list) or not all(isinstance(value, int) for value in raw):
            raise AssertionError(f"malformed {vertex_type} histogram")
        histogram = tuple(raw)
        if len(histogram) != len(TYPE_VALUES[vertex_type]):
            raise AssertionError(f"wrong {vertex_type} histogram width")
        if any(value < 0 for value in histogram):
            raise AssertionError(f"negative {vertex_type} histogram entry")
        if sum(histogram) != TYPE_SIZES[vertex_type]:
            raise AssertionError(f"wrong {vertex_type} population")
        answer[vertex_type] = histogram
    return answer


def reconstruct_sequences(
    histograms: dict[str, tuple[int, ...]]
) -> dict[str, tuple[list[int], ...]]:
    a0 = expand_histogram(histograms["X0"], TYPE_VALUES["X0"])
    a1 = expand_histogram(histograms["X1"], TYPE_VALUES["X1"])
    a2 = expand_histogram(histograms["X2"], TYPE_VALUES["X2"])
    return {
        "X0_induced": ([a - 2 for a in a0],),
        "X0_X1": ([16 - 2 * a for a in a0], [a + 1 for a in a1]),
        "X0_X2": (a0, [a + 4 for a in a2]),
        "X1_induced": ([11 - 2 * a for a in a1],),
        "X1_X2": (a1, [6 - 2 * a for a in a2]),
        "X2_induced": (a2,),
    }


def test_pair_sequences(
    sequences: dict[str, tuple[list[int], ...]]
) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for name in PAIR_NAMES:
        sides = sequences[name]
        if len(sides) == 1:
            primary, witness = erdos_gallai(sides[0])
            secondary = havel_hakimi(sides[0])
            criterion = "Erdos-Gallai"
        else:
            primary, witness = gale_ryser(sides[0], sides[1])
            secondary = bipartite_havel_hakimi(sides[0], sides[1])
            criterion = "Gale-Ryser"
        if primary != secondary:
            raise AssertionError(f"independent criteria disagree for {name}")
        result[name] = {
            "graphical": primary,
            "criterion": criterion,
            "witness": witness,
            "degree_sequences_rle": [
                run_length_encode(side) for side in sides
            ],
            "degree_sums": [sum(side) for side in sides],
        }
    return result


def load_frozen_inputs(repo: Path) -> tuple[dict[str, object], dict[str, object], dict[str, str]]:
    discovery_results = (
        repo / "attempts" / "wave81-norm16-labeled-design" / "exact-results.json"
    )
    source_manifest = (
        repo
        / "verification"
        / "wave81-norm16-labeled-design"
        / "package-manifest.sha256"
    )
    source_results = (
        repo
        / "verification"
        / "wave81-norm16-labeled-design"
        / "independent-results.json"
    )
    observed = {
        "attempts/wave81-norm16-labeled-design/exact-results.json": sha256(
            discovery_results
        ),
        "verification/wave81-norm16-labeled-design/package-manifest.sha256": sha256(
            source_manifest
        ),
        "verification/wave81-norm16-labeled-design/independent-results.json": sha256(
            source_results
        ),
    }
    expected = {
        "attempts/wave81-norm16-labeled-design/exact-results.json": (
            EXPECTED_DISCOVERY_RESULTS_SHA256
        ),
        "verification/wave81-norm16-labeled-design/package-manifest.sha256": (
            EXPECTED_SOURCE_VERIFIER_MANIFEST_SHA256
        ),
        "verification/wave81-norm16-labeled-design/independent-results.json": (
            EXPECTED_SOURCE_VERIFIER_RESULTS_SHA256
        ),
    }
    if observed != expected:
        raise AssertionError("frozen Wave81 inputs changed")
    return (
        json.loads(discovery_results.read_text(encoding="utf-8")),
        json.loads(source_results.read_text(encoding="utf-8")),
        observed,
    )


def build_results() -> dict[str, object]:
    repo = Path(__file__).resolve().parents[2]
    discovery, source_verifier, input_hashes = load_frozen_inputs(repo)
    closure = discovery["outside_type_degree_closure"]
    if not isinstance(closure, dict):
        raise AssertionError("missing histogram closure")
    source_rows = closure["surviving_histograms"]
    if not isinstance(source_rows, dict) or set(source_rows) != {"0", "1"}:
        raise AssertionError("unexpected surviving-t index")
    if {t: len(rows) for t, rows in source_rows.items()} != {"0": 43, "1": 7}:
        raise AssertionError("conditional domain is not 43+7")

    row_records: list[dict[str, object]] = []
    seen_histograms: set[tuple[tuple[int, ...], ...]] = set()
    pair_counts = {
        name: {"checked": 0, "graphical": 0, "nongraphical": 0}
        for name in PAIR_NAMES
    }
    survivor_counts = {"0": 0, "1": 0}
    rejections: list[dict[str, object]] = []

    for t_text in ("0", "1"):
        rows = source_rows[t_text]
        if not isinstance(rows, list):
            raise AssertionError("histogram lane is not a list")
        for source_index, source_row in enumerate(rows):
            if not isinstance(source_row, dict):
                raise AssertionError("histogram row is not a mapping")
            histograms = canonical_histograms(source_row)
            key = tuple(histograms[name] for name in ("X0", "X1", "X2"))
            if key in seen_histograms:
                raise AssertionError("duplicate histogram triple")
            seen_histograms.add(key)
            sequences = reconstruct_sequences(histograms)
            checks = test_pair_sequences(sequences)
            failed = [name for name in PAIR_NAMES if not checks[name]["graphical"]]
            for name in PAIR_NAMES:
                pair_counts[name]["checked"] += 1
                bucket = "graphical" if checks[name]["graphical"] else "nongraphical"
                pair_counts[name][bucket] += 1
            row_id = f"t{t_text}-row-{source_index + 1:02d}"
            if not failed:
                survivor_counts[t_text] += 1
            else:
                rejections.append(
                    {
                        "row_id": row_id,
                        "t": int(t_text),
                        "source_index_zero_based": source_index,
                        "failed_pairs": failed,
                        "histograms": {
                            name: list(histograms[name])
                            for name in ("X0", "X1", "X2")
                        },
                        "failed_expanded_sequences": {
                            name: [
                                sorted(side, reverse=True)
                                for side in sequences[name]
                            ]
                            for name in failed
                        },
                        "failure_witnesses": {
                            name: checks[name]["witness"] for name in failed
                        },
                    }
                )
            row_records.append(
                {
                    "row_id": row_id,
                    "t": int(t_text),
                    "source_index_zero_based": source_index,
                    "histograms": {
                        name: list(histograms[name])
                        for name in ("X0", "X1", "X2")
                    },
                    "pair_checks": checks,
                    "all_six_graphical": not failed,
                }
            )

    source_extension = source_verifier["outside_histograms"][
        "verifier_derived_strengthening"
    ]
    target_sequences = sorted(
        tuple(row["X0_induced_degrees"])
        for row in source_extension["rejections"]
    )
    our_sequences = sorted(
        tuple(row["failed_expanded_sequences"]["X0_induced"][0])
        for row in rejections
    )
    target_counts = source_extension["counts_after_all_type_graphical_tests"]
    if target_sequences != our_sequences:
        raise AssertionError("rejected sequences differ from source verifier claim")
    if survivor_counts != {"0": target_counts["0"], "1": target_counts["1"]}:
        raise AssertionError("survivor counts differ from source verifier claim")

    expected_rejections = sorted(
        [
            (4, 3, 1, 1, 1, 0, 0, 0, 0, 0, 0),
            (4, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0),
            (3, 3, 3, 1, 0, 0, 0, 0, 0, 0, 0),
        ]
    )
    if our_sequences != expected_rejections:
        raise AssertionError("unexpected exact rejection set")
    if any(row["t"] != 0 or row["failed_pairs"] != ["X0_induced"] for row in rejections):
        raise AssertionError("an unexpected lane or type-pair test failed")
    if survivor_counts != {"0": 40, "1": 7}:
        raise AssertionError("unexpected strengthened endpoint")
    if len(row_records) != 50 or len(seen_histograms) != 50:
        raise AssertionError("histogram domain was not exhausted exactly once")
    if any(record["checked"] != 50 for record in pair_counts.values()):
        raise AssertionError("not every type pair was checked for every row")

    return {
        "format": "wave81-norm16-graphical-refinement-verification-v1",
        "claim_label": "VERIFIED",
        "conditional_scope": (
            "The previously verified Wave81 43+7 outside type-degree "
            "histogram domain in the conditional Wave78 norm-16 branch"
        ),
        "inputs": {"sha256": input_hashes},
        "domain_audit": {
            "t_keys_in_order": [0, 1],
            "rows_by_t": {"0": 43, "1": 7},
            "rows_total": len(row_records),
            "unique_histogram_triples": len(seen_histograms),
            "row_indexing": "zero-based source index; row_id is one-based",
            "type_sizes": TYPE_SIZES,
            "six_type_pair_subgraphs": list(PAIR_NAMES),
        },
        "algorithms": {
            "induced_primary": "Erdos-Gallai inequalities",
            "induced_cross_check": "Havel-Hakimi reduction",
            "bipartite_primary": "Gale-Ryser inequalities",
            "bipartite_cross_check": "bipartite Havel-Hakimi reduction",
            "checker_disagreements": 0,
            "tiny_oracles": (
                "brute-force simple graphs through n=6 and bipartite "
                "graphs through 3x3 are exercised by the test suite"
            ),
        },
        "pair_census": pair_counts,
        "counts_before": {"0": 43, "1": 7},
        "counts_after_all_six_graphical_tests": survivor_counts,
        "rejections": rejections,
        "row_certificates": row_records,
        "source_claim_comparison": {
            "exact_rejection_sequences_match": True,
            "survivor_counts_match": True,
            "only_X0_induced_failed": True,
            "no_t1_row_removed": True,
        },
        "endpoint": {
            "refinement_verified": True,
            "norm16_excluded": False,
            "conway_status": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
        "limitations": [
            "Conditional on the frozen and previously verified 43+7 histogram domain.",
            "Individual graphicality does not realize the six subgraphs simultaneously.",
            "No vertex-by-vertex common-neighbor system is solved here.",
            "No 83-vertex outside graph is constructed.",
            "Conway-99 and novelty remain UNKNOWN.",
        ],
    }


def canonical_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    free = free_memory_percent()
    if free < 15.0:
        raise SystemExit(f"refusing to run below memory floor ({free:.1f}% free)")
    encoded = canonical_json(build_results())
    if args.output:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    elif args.verify:
        if args.verify.read_text(encoding="utf-8") != encoded:
            raise SystemExit("independent result mismatch")
        print("PASS")
    elif args.json:
        print(encoded, end="")
    else:
        result = build_results()
        print(
            "PASS "
            f"rows={result['domain_audit']['rows_total']} "
            "rejected=3 survivors=40+7"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
