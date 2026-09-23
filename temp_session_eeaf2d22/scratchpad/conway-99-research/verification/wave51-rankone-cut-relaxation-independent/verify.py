#!/usr/bin/env python3
"""Clean-room exact verification of the fixed Wave51 174-cut relaxation."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import itertools
import json
import math
import os
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUTPUT = HERE / "verification-result.json"
MIN_FREE_PERCENT = 15.0
RANK_PRIME = 2_147_483_647

W43 = ROOT / "attempts/wave43-seven-deck-endpoint/exact-results.json"
W44 = ROOT / "attempts/wave44-rooted-flags/row-system.json"
W45 = ROOT / "attempts/wave45-flag-moment/checkpoint-v1-seed0-17cuts-15witnesses.json"
W45_MANIFEST = ROOT / "verification/wave45-flag-moment/package-manifest.sha256"
W47 = ROOT / "attempts/wave47-three-root-moment/cuts.json"
W47_RESULT = ROOT / "verification/wave47-three-root-moment/verification-results.json"
W47_MANIFEST = ROOT / "verification/wave47-three-root-moment/package-manifest.sha256"
W49_SCOUT = ROOT / "attempts/wave49-five-root-moment/combined-sdp-result.json"
W49_COEFFICIENTS = (
    ROOT / "verification/wave49-five-root-moment/independent-coefficients.json"
)
W49_MANIFEST = ROOT / "verification/wave49-five-root-moment/package-manifest.sha256"
SOURCE_RESULT = ROOT / "verification/wave51-rankone-cut-relaxation/exact-result.json"
SOURCE_FREEZE = ROOT / "verification/wave51-rankone-cut-relaxation/input-freeze.sha256"
SOURCE_MANIFEST = (
    ROOT / "verification/wave51-rankone-cut-relaxation/package-manifest.sha256"
)
SOURCE_AGENT_REPORT = (
    ROOT / "agents/2026-07-27-wave51-rankone-cut-relaxation.md"
)

EXPECTED = {
    W43: "06b498a736a511a7d6f5912bd4686e5d4eb30f4041477e3ee9cbc1704f1757c8",
    W44: "fb81601a9c97fc6860702403e56da65c2ba8fd69ee6a61007a0da53cade1d722",
    W45: "96a50f9add4b12b2c86587da29ade8b9da34f88a7b7617c048ffb7139c12b64b",
    W45_MANIFEST: "d6e4d8b0b549318cd5d109718cff0bc94eb615956e7e3c5ade7d1e0362a10bf0",
    W47: "d2ea38ed74a1b9098c9cc8eae52f8d65723c2631335b0acedba647dc16aa313e",
    W47_RESULT: "1c80d2b70b8e6bef42d4d9df124cc82dc9baf642d36873c61e91e8f2acc99a43",
    W47_MANIFEST: "cec96a7cbc967bbbdc95215bc2086d3056d94966c95d7ca1d60fa731f17f58eb",
    W49_SCOUT: "1e41b1fd961714b24f69d1c31474f48b91dca88d938f5c97d5aa2424b8aac152",
    W49_COEFFICIENTS: "f3f1cd0bca98965a7893a8146ecee8dff755162f3b92eeb24e1dfbc003371d5f",
    W49_MANIFEST: "6c00c49b9ce2816866ae62d26a8f04b0dc3dddd26cec7eb8d4308386d406ac97",
    SOURCE_RESULT: "527656f5d2d6a03d71234dc0fb110422ddfade1ac8b5a1d175168e857073edfc",
    SOURCE_FREEZE: "815fbf63e1b09bdaedcaaa9002a52bbebc204955343deaaf14d5bcd6aad9b2b1",
    SOURCE_MANIFEST: "b54d0ab21b72348d4de8d023f9d1cab39055c17c6f838eb3ecb1430f4d95add0",
    SOURCE_AGENT_REPORT: "c7908dc1c8f17ce1865b4100eab3c7eca0e9b402fd9e207cf8cb2fadca756ab7",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def compact_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compact_hash(value: object) -> str:
    return hashlib.sha256(compact_bytes(value)).hexdigest()


def pretty_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def pretty_hash(value: object) -> str:
    return hashlib.sha256(pretty_bytes(value)).hexdigest()


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def free_memory_percent() -> float:
    if os.name == "nt":
        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullExtendedVirtual", ctypes.c_ulonglong),
            ]

        state = MemoryStatusEx()
        state.dwLength = ctypes.sizeof(state)
        require(
            bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state))),
            "GlobalMemoryStatusEx failed",
        )
        return 100.0 * state.ullAvailPhys / state.ullTotalPhys
    available = os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    total = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    return 100.0 * available / total


def memory_guard(stage: str) -> None:
    free = free_memory_percent()
    require(
        free >= MIN_FREE_PERCENT,
        f"{stage}: only {free:.2f}% physical memory is free",
    )


def checked_json(path: Path) -> dict[str, Any]:
    require(file_hash(path) == EXPECTED[path], f"frozen hash changed: {path}")
    value = json.loads(path.read_bytes())
    require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def validate_manifest(path: Path) -> int:
    require(file_hash(path) == EXPECTED[path], f"manifest hash changed: {path}")
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split("  ", 1)
        target = ROOT / relative
        require(target.is_file(), f"manifest target missing: {relative}")
        require(file_hash(target) == expected, f"manifest target changed: {relative}")
        count += 1
    return count


def edge_pairs(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


def relabel_mask(mask: int, order: int, permutation: tuple[int, ...]) -> int:
    positions = {pair: index for index, pair in enumerate(edge_pairs(order))}
    image = 0
    for index, (left, right) in enumerate(edge_pairs(order)):
        if (mask >> index) & 1:
            mapped = tuple(sorted((permutation[left], permutation[right])))
            image |= 1 << positions[mapped]
    return image


_CANONICAL_CACHE: dict[tuple[int, int], int] = {}


def canonical_mask(mask: int, order: int) -> int:
    key = (order, mask)
    if key not in _CANONICAL_CACHE:
        _CANONICAL_CACHE[key] = min(
            relabel_mask(mask, order, permutation)
            for permutation in itertools.permutations(range(order))
        )
    return _CANONICAL_CACHE[key]


def induced_mask(mask: int, order: int, subset: tuple[int, ...]) -> int:
    positions = {pair: index for index, pair in enumerate(edge_pairs(order))}
    induced = 0
    for bit, (left, right) in enumerate(edge_pairs(len(subset))):
        old_pair = tuple(sorted((subset[left], subset[right])))
        if (mask >> positions[old_pair]) & 1:
            induced |= 1 << bit
    return induced


def independent_order6_counts(
    endpoint: dict[str, Any], seven_classes: set[int]
) -> dict[int, int]:
    deletion_totals: dict[int, int] = defaultdict(int)
    total7 = 0
    seen: set[int] = set()
    for record in endpoint["certificate"]["support"]:
        mask = int(record["canonical_mask"])
        count = int(record["count"])
        require(mask in seven_classes, "Wave43 support mask is outside Wave44 classes")
        require(mask not in seen and count > 0, "malformed Wave43 support")
        seen.add(mask)
        total7 += count
        for subset in itertools.combinations(range(7), 6):
            child = induced_mask(mask, 7, subset)
            deletion_totals[canonical_mask(child, 6)] += count
    require(total7 == math.comb(99, 7), "Wave43 seven-deck total changed")
    require(
        all(value % 93 == 0 for value in deletion_totals.values()),
        "six-deck deletion total is not divisible by 93",
    )
    counts = {mask: value // 93 for mask, value in deletion_totals.items()}
    require(sum(counts.values()) == math.comb(99, 6), "six-deck total changed")
    return counts


def validate_wave44(
    row_system: dict[str, Any],
) -> tuple[list[int], list[tuple[list[int], int]], dict[str, Any]]:
    classes = [int(mask) for mask in row_system["classes"]]
    require(len(classes) == 208 and len(set(classes)) == 208, "class census changed")
    require(classes == sorted(classes), "class order changed")
    expected_counts = {"base": 81, "vertex": 7, "edge": 36, "nonedge": 46}
    require(set(row_system["families"]) == set(expected_counts), "family set changed")
    hashes: dict[str, str] = {}
    equations: list[tuple[list[int], int]] = []
    ordered_families: dict[str, Any] = {}
    for name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][name]
        require(set(family) == {"rows", "rhs"}, f"malformed Wave44 family {name}")
        rows = family["rows"]
        rhs = family["rhs"]
        require(
            len(rows) == expected_counts[name] and len(rhs) == expected_counts[name],
            f"Wave44 family census changed: {name}",
        )
        require(
            all(
                isinstance(row, list)
                and len(row) == 209
                and all(type(value) is int for value in row)
                for row in rows
            ),
            f"Wave44 row shape changed: {name}",
        )
        require(all(type(value) is int for value in rhs), f"noninteger RHS: {name}")
        ordered_families[name] = {"rows": rows, "rhs": rhs}
        hashes[name] = compact_hash(ordered_families[name])
        equations.extend(
            (list(map(int, row)), int(target))
            for row, target in zip(rows, rhs, strict=True)
        )
    hashes["combined"] = compact_hash(ordered_families)
    require(row_system["row_rhs_sha256"] == hashes, "Wave44 row hash table failed")
    require(len(equations) == 170, "Wave44 equation census changed")
    equation_catalog = [
        {"coefficients": row, "rhs": rhs} for row, rhs in equations
    ]
    return classes, equations, {
        "families": expected_counts,
        "equations": len(equations),
        "row_rhs_sha256": hashes,
        "ordered_equation_catalog_sha256": pretty_hash(equation_catalog),
    }


def sparse_pairs(records: Iterable[dict[str, Any]]) -> list[list[int]]:
    output: list[list[int]] = []
    for record in records:
        mask = int(record["canonical_mask"])
        coefficient = int(record["coefficient"])
        require(coefficient != 0, "stored sparse cut contains a zero coefficient")
        output.append([mask, coefficient])
    return output


def validate_cut_masks(
    pairs: list[list[int]], class_set: set[int], label: str
) -> None:
    masks = [record[0] for record in pairs]
    require(len(masks) == len(set(masks)), f"duplicate coefficient mask: {label}")
    require(all(mask in class_set for mask in masks), f"unknown class mask: {label}")
    require(masks == sorted(masks), f"coefficient order changed: {label}")


def validate_wave45(
    payload: dict[str, Any], classes: list[int]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    class_set = set(classes)
    cuts = payload["cuts"]
    require(isinstance(cuts, list) and len(cuts) == 17, "Wave45 cut census changed")
    normalized = []
    cut_hashes = []
    for cut in cuts:
        core = {
            "family": cut["family"],
            "direction": cut["direction"],
            "constant": cut["constant"],
            "coefficients": cut["coefficients"],
            "primitive_divisor": cut["primitive_divisor"],
            "sense": cut["sense"],
        }
        require(compact_hash(core) == cut["cut_sha256"], "Wave45 cut self-hash failed")
        require(cut["family"] == "vertex", "Wave45 family changed")
        require(len(cut["direction"]) == 17, "Wave45 direction width changed")
        require(
            cut["sense"] == "constant + sum(coefficient*x_mask) >= 0",
            "Wave45 cut sense changed",
        )
        pairs = sparse_pairs(cut["coefficients"])
        validate_cut_masks(pairs, class_set, f"Wave45/{cut['cut_sha256']}")
        require(
            math.gcd(abs(int(cut["constant"])), *(abs(value) for _, value in pairs))
            == 1,
            "Wave45 cut is not primitive",
        )
        cut_hashes.append(str(cut["cut_sha256"]))
        normalized.append(
            {
                "layer": "wave45",
                "id": str(cut["cut_sha256"]),
                "family": str(cut["family"]),
                "constant": int(cut["constant"]),
                "coefficients": pairs,
            }
        )
    require(len(set(cut_hashes)) == 17, "duplicate Wave45 cuts")
    return normalized, {
        "all_17_cut_self_hashes_valid": True,
        "selected_cut_hash_catalog_sha256": pretty_hash(cut_hashes),
    }


def wave47_core(cut: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": cut["family"],
        "root_pattern": cut["root_pattern"],
        "vector": cut["vector"],
        "primitive_divisor": cut["primitive_divisor"],
        "constant": cut["constant"],
        "coefficients": cut["coefficients"],
    }


def validate_wave47(
    payload: dict[str, Any],
    prior_verification: dict[str, Any],
    classes: list[int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    require(
        prior_verification["cuts"]["complete_ledger_exactly_equal_to_sealed"],
        "prior Wave47 ledger verification is absent",
    )
    require(
        prior_verification["cuts"]["all_2664_raw_quadratics_exactly_replayed"],
        "prior Wave47 raw replay is absent",
    )
    cuts = payload["cuts"]
    require(len(cuts) == 2657, "Wave47 ledger census changed")
    class_set = set(classes)
    all_hashes: list[str] = []
    by_pair: dict[tuple[str, str], list[int]] = defaultdict(list)
    selected_raw = []
    for cut in cuts:
        require(
            compact_hash(wave47_core(cut)) == cut["cut_sha256"],
            "Wave47 cut self-hash failed",
        )
        pairs = sparse_pairs(cut["coefficients"])
        validate_cut_masks(pairs, class_set, f"Wave47/{cut['cut_sha256']}")
        require(
            math.gcd(abs(int(cut["constant"])), *(abs(value) for _, value in pairs))
            == 1,
            "Wave47 cut is not primitive",
        )
        all_hashes.append(str(cut["cut_sha256"]))
        key = (str(cut["source"]), str(cut["family"]))
        by_pair[key].append(int(cut["source_direction_index"]))
        if int(cut["source_direction_index"]) == 0:
            selected_raw.append(cut)
    require(len(set(all_hashes)) == 2657, "Wave47 ledger has duplicate cut hashes")
    expected_families = {f"root_{bits:03b}" for bits in range(8)}
    sources = {source for source, _ in by_pair}
    families = {family for _, family in by_pair}
    require(len(sources) == 17, "Wave47 source census changed")
    require(families == expected_families, "Wave47 family set changed")
    require(len(by_pair) == 136, "Wave47 source/family coverage changed")
    require(
        all(indices.count(0) == 1 and min(indices) == 0 for indices in by_pair.values()),
        "Wave47 first-direction indexing changed",
    )
    require(len(selected_raw) == 136, "Wave47 selected cut census changed")
    normalized = []
    for cut in selected_raw:
        normalized.append(
            {
                "layer": "wave47",
                "id": str(cut["cut_sha256"]),
                "family": str(cut["family"]),
                "constant": int(cut["constant"]),
                "coefficients": sparse_pairs(cut["coefficients"]),
            }
        )
    selected_hashes = [str(cut["cut_sha256"]) for cut in selected_raw]
    return normalized, {
        "all_2657_cut_self_hashes_valid": True,
        "all_2657_cut_hashes_unique": True,
        "source_count": len(sources),
        "family_count": len(families),
        "source_family_pairs": len(by_pair),
        "selected_index_zero_cuts": len(selected_raw),
        "full_ledger_hash_catalog_sha256": pretty_hash(all_hashes),
        "selected_cut_hash_catalog_sha256": pretty_hash(selected_hashes),
    }


def quadratic(upper_entries: list[list[int]], vector: list[int]) -> int:
    total = 0
    for row, column, coefficient in upper_entries:
        row = int(row)
        column = int(column)
        multiplier = 1 if row == column else 2
        total += (
            multiplier
            * int(coefficient)
            * int(vector[row])
            * int(vector[column])
        )
    return total


def admissible_five_root_masks() -> set[int]:
    representatives = {
        canonical_mask(mask, 5)
        for mask in range(1 << len(edge_pairs(5)))
    }
    admissible = set()
    for mask in representatives:
        adjacency = [[False] * 5 for _ in range(5)]
        for bit, (left, right) in enumerate(edge_pairs(5)):
            if (mask >> bit) & 1:
                adjacency[left][right] = True
                adjacency[right][left] = True
        valid = True
        for left, right in edge_pairs(5):
            common = sum(
                adjacency[left][vertex] and adjacency[right][vertex]
                for vertex in range(5)
            )
            cap = 1 if adjacency[left][right] else 2
            if common > cap:
                valid = False
                break
        if valid:
            admissible.add(mask)
    return admissible


def validate_wave49(
    scout: dict[str, Any],
    coefficients: dict[str, Any],
    order6_counts: dict[int, int],
    classes: list[int],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    coefficient_core = {
        key: value
        for key, value in coefficients.items()
        if key != "payload_sha256_without_this_field"
    }
    require(
        compact_hash(coefficient_core)
        == coefficients["payload_sha256_without_this_field"],
        "Wave49 coefficient payload self-hash failed",
    )
    coefficient_families = coefficients["families"]
    require(len(coefficient_families) == 21, "Wave49 coefficient family count changed")
    family_lookup: dict[int, dict[str, Any]] = {}
    for family in coefficient_families:
        core = {
            key: value for key, value in family.items() if key != "payload_sha256"
        }
        require(compact_hash(core) == family["payload_sha256"], "Wave49 family self-hash failed")
        root_mask = int(family["root_mask"])
        require(root_mask not in family_lookup, "duplicate Wave49 coefficient root")
        dimension = int(family["dimension"])
        attachments = [int(value) for value in family["attachment_masks"]]
        require(
            len(attachments) == dimension and len(set(attachments)) == dimension,
            "Wave49 attachment catalog changed",
        )
        require(len(family["order7"]) == 208, "Wave49 order-seven record count changed")
        require(
            {int(record["canonical_mask"]) for record in family["order7"]}
            == set(classes),
            "Wave49 order-seven class coverage changed",
        )
        for record in family["order6"] + family["order7"]:
            for row, column, _ in record["upper_entries"]:
                require(
                    0 <= int(row) <= int(column) < dimension,
                    "Wave49 upper-triangle index is invalid",
                )
        family_lookup[root_mask] = family
    require(
        set(family_lookup) == admissible_five_root_masks(),
        "Wave49 root masks are not the 21 locally admissible five-vertex classes",
    )

    candidates = scout["solvers"][0]["candidate"]["wave49_families"]
    require(len(candidates) == 21, "Wave49 candidate direction count changed")
    require(
        len({int(candidate["root_mask"]) for candidate in candidates}) == 21,
        "duplicate Wave49 candidate root",
    )
    normalized = []
    direction_hashes = []
    checks = 0
    for candidate in candidates:
        root_mask = int(candidate["root_mask"])
        require(root_mask in family_lookup, "Wave49 candidate has an unknown root")
        family = family_lookup[root_mask]
        sealed = candidate["candidate_minimum_direction_exact_cut"]
        sealed_core = {
            key: value
            for key, value in sealed.items()
            if key != "payload_sha256_without_this_field"
        }
        require(
            pretty_hash(sealed_core) == sealed["payload_sha256_without_this_field"],
            "Wave49 selected direction payload self-hash failed",
        )
        vector = [int(value) for value in sealed["primitive_integer_vector"]]
        require(len(vector) == int(family["dimension"]), "Wave49 direction width changed")
        require(math.gcd(*(abs(value) for value in vector)) == 1, "Wave49 direction is not primitive")
        constant = sum(
            quadratic(record["upper_entries"], vector)
            * order6_counts.get(int(record["canonical_mask"]), 0)
            for record in family["order6"]
        )
        order7 = [
            [int(record["canonical_mask"]), quadratic(record["upper_entries"], vector)]
            for record in family["order7"]
        ]
        order7 = [record for record in order7 if record[1]]
        sealed_order7 = [
            [int(mask), int(value)]
            for mask, value in sealed["order7_count_coefficients"]
        ]
        require(constant == int(sealed["constant_raw_numerator"]), "Wave49 constant changed")
        require(order7 == sealed_order7, "Wave49 order-seven coefficients changed")
        require(int(sealed["normalization_denominator"]) > 0, "Wave49 cut sense changed")
        checks += 1 + len(family["order6"]) + len(family["order7"])
        direction_hashes.append(str(sealed["payload_sha256_without_this_field"]))
        normalized.append(
            {
                "layer": "wave49",
                "id": f"root5_{root_mask}",
                "family": f"root5_{root_mask}",
                "constant": constant,
                "coefficients": order7,
            }
        )
    require(checks == 5691, "Wave49 reconstruction-check census changed")
    return normalized, {
        "coefficient_payload_self_hash_valid": True,
        "all_21_family_self_hashes_valid": True,
        "all_21_direction_self_hashes_valid": True,
        "canonical_root_families": len(family_lookup),
        "selected_directions": len(normalized),
        "exact_reconstruction_checks": checks,
        "selected_direction_hash_catalog_sha256": pretty_hash(direction_hashes),
    }


def exact_slacks(
    cuts: list[dict[str, Any]],
    class_index: dict[int, int],
    vector: list[Fraction],
) -> list[Fraction]:
    slacks = []
    for cut in cuts:
        value = Fraction(int(cut["constant"]))
        for mask, coefficient in cut["coefficients"]:
            value += int(coefficient) * vector[class_index[int(mask)]]
        slacks.append(value)
    return slacks


def rank_mod_prime(
    rows: Iterable[dict[int, int]], columns: int, prime: int
) -> tuple[int, list[int]]:
    basis: dict[int, dict[int, int]] = {}
    for source in rows:
        row = {
            int(column): int(value) % prime
            for column, value in source.items()
            if int(value) % prime
        }
        while row:
            pivot = min(row)
            if pivot not in basis:
                inverse = pow(row[pivot], prime - 2, prime)
                row = {
                    column: (value * inverse) % prime
                    for column, value in row.items()
                    if (value * inverse) % prime
                }
                basis[pivot] = row
                break
            factor = row[pivot]
            pivot_row = basis[pivot]
            for column, value in pivot_row.items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    require(all(0 <= pivot < columns for pivot in basis), "modular pivot escaped")
    return len(basis), sorted(basis)


def reconstruct_and_verify() -> dict[str, Any]:
    memory_guard("start")
    initial_hashes = {path: file_hash(path) for path in EXPECTED}
    for path, expected in EXPECTED.items():
        require(initial_hashes[path] == expected, f"frozen input changed: {path}")
    manifest_entries = {
        W45_MANIFEST.relative_to(ROOT).as_posix(): validate_manifest(W45_MANIFEST),
        W47_MANIFEST.relative_to(ROOT).as_posix(): validate_manifest(W47_MANIFEST),
        W49_MANIFEST.relative_to(ROOT).as_posix(): validate_manifest(W49_MANIFEST),
        SOURCE_MANIFEST.relative_to(ROOT).as_posix(): validate_manifest(SOURCE_MANIFEST),
    }

    endpoint = checked_json(W43)
    row_system = checked_json(W44)
    wave45_payload = checked_json(W45)
    wave47_payload = checked_json(W47)
    wave47_verification = checked_json(W47_RESULT)
    wave49_scout = checked_json(W49_SCOUT)
    wave49_coefficients = checked_json(W49_COEFFICIENTS)
    source_result = checked_json(SOURCE_RESULT)

    classes, equations, equation_record = validate_wave44(row_system)
    class_index = {mask: index for index, mask in enumerate(classes)}
    order6_counts = independent_order6_counts(endpoint, set(classes))
    wave45, wave45_record = validate_wave45(wave45_payload, classes)
    wave47, wave47_record = validate_wave47(
        wave47_payload, wave47_verification, classes
    )
    wave49, wave49_record = validate_wave49(
        wave49_scout, wave49_coefficients, order6_counts, classes
    )
    cuts = wave45 + wave47 + wave49
    require(len(cuts) == 174, "selected cut total changed")

    catalog = [
        {
            key: cut[key]
            for key in ("layer", "id", "family", "constant", "coefficients")
        }
        for cut in cuts
    ]
    catalog_sha256 = pretty_hash(catalog)
    require(
        catalog_sha256 == source_result["cut_bundle"]["catalog_sha256"],
        "source package cut catalog differs from clean-room reconstruction",
    )
    require(
        source_result["cut_bundle"]["layers"]
        == {"wave45": 17, "wave47": 136, "wave49": 21},
        "source package layer census changed",
    )

    support = source_result["exact_certificate"]["support"]
    require(len(support) == 136, "stored support census changed")
    witness_by_mask: dict[int, Fraction] = {}
    for record in support:
        mask = int(record["canonical_mask"])
        value = Fraction(str(record["value"]))
        require(mask in class_index, "witness support uses an unknown class")
        require(mask not in witness_by_mask and value > 0, "malformed witness support")
        require(fraction_text(value) == str(record["value"]), "noncanonical fraction text")
        witness_by_mask[mask] = value
    vector = [witness_by_mask.get(mask, Fraction()) for mask in classes]
    y_value = Fraction(str(source_result["exact_certificate"]["y_h11_over_4"]))
    vector.append(y_value)
    require(y_value == 4158, "stored y value changed")
    require(Fraction(2079) <= y_value <= Fraction(4158), "stored y is out of bounds")
    require(all(value >= 0 for value in vector[:208]), "stored count is negative")

    residuals = [
        sum(int(coefficient) * value for coefficient, value in zip(row, vector))
        - int(rhs)
        for row, rhs in equations
    ]
    require(not any(residuals), "stored witness fails a Wave44 equation")
    slacks = exact_slacks(cuts, class_index, vector)
    require(all(slack >= 0 for slack in slacks), "stored witness violates a selected cut")
    tight_by_layer = {
        layer: sum(
            slack == 0
            for cut, slack in zip(cuts, slacks, strict=True)
            if cut["layer"] == layer
        )
        for layer in ("wave45", "wave47", "wave49")
    }
    positive_slacks = [slack for slack in slacks if slack > 0]
    require(tight_by_layer == {"wave45": 5, "wave47": 46, "wave49": 15}, "tight-cut census changed")
    require(len(positive_slacks) == 108, "positive-slack census changed")
    require(min(positive_slacks) == 133056, "minimum positive slack changed")
    denominator_digits = max(len(str(value.denominator)) for value in vector)
    require(denominator_digits == 272, "maximum denominator length changed")
    witness_text = [fraction_text(value) for value in vector]
    witness_sha256 = pretty_hash(witness_text)
    require(
        witness_sha256
        == source_result["exact_certificate"]["witness_vector_sha256"],
        "witness vector hash changed",
    )

    active_rows: list[dict[int, int]] = []
    for row, _ in equations:
        active_rows.append(
            {
                column: int(value)
                for column, value in enumerate(row)
                if int(value)
            }
        )
    zero_coordinates = [
        index for index, value in enumerate(vector[:208]) if value == 0
    ]
    active_rows.extend({index: 1} for index in zero_coordinates)
    active_rows.append({208: 1})
    for cut, slack in zip(cuts, slacks, strict=True):
        if slack != 0:
            continue
        active_rows.append(
            {
                class_index[int(mask)]: int(coefficient)
                for mask, coefficient in cut["coefficients"]
                if int(coefficient)
            }
        )
    active_rank, pivots = rank_mod_prime(active_rows, 209, RANK_PRIME)
    require(active_rank == 209, "active constraint coefficient rank is below 209")
    require(pivots == list(range(209)), "active rank does not cover every variable")

    memory_guard("finish")
    require(
        all(file_hash(path) == digest for path, digest in initial_hashes.items()),
        "a frozen source changed during clean-room replay",
    )

    slack_catalog = [fraction_text(value) for value in slacks]
    result = {
        "format": "wave51-rankone-cut-relaxation-independent-verification-v1",
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": (
            "Clean-room exact rational feasibility replay of the fixed Wave51 "
            "bundle of 170 Wave44 equations and 174 selected rank-one cuts."
        ),
        "source_status_audit": {
            "source_discovery_claim_label": source_result["claim_label"],
            "source_role": source_result["role"],
            "separation_violation_found": True,
            "reason": (
                "The source agent selected the finite bundle, constructed the "
                "witness, and labeled its own result verified."
            ),
            "effective_source_label_before_independent_replay": "CANDIDATE",
            "independent_label_after_clean_room_replay": "VERIFIED",
            "source_files_modified": False,
        },
        "inputs": [
            {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": digest,
            }
            for path, digest in EXPECTED.items()
        ],
        "input_integrity": {
            "all_14_frozen_sha256_checks_passed": True,
            "all_sources_unchanged_during_replay": True,
            "nested_manifest_entry_counts": manifest_entries,
        },
        "wave44": equation_record,
        "cuts": {
            "total": len(cuts),
            "layers": {"wave45": 17, "wave47": 136, "wave49": 21},
            "catalog_sha256": catalog_sha256,
            "wave45": wave45_record,
            "wave47": wave47_record,
            "wave49": wave49_record,
        },
        "exact_witness": {
            "support_size": len(witness_by_mask),
            "zero_coordinates": len(zero_coordinates),
            "y_h11_over_4": fraction_text(y_value),
            "maximum_denominator_digits": denominator_digits,
            "witness_vector_sha256": witness_sha256,
            "equation_checks": len(residuals),
            "all_equation_residuals_zero": True,
            "cut_checks": len(slacks),
            "all_cut_slacks_nonnegative": True,
            "tight_cuts": sum(slack == 0 for slack in slacks),
            "tight_cuts_by_layer": tight_by_layer,
            "strictly_positive_cuts": len(positive_slacks),
            "minimum_strictly_positive_slack": fraction_text(min(positive_slacks)),
            "slack_catalog_sha256": pretty_hash(slack_catalog),
            "all_208_counts_nonnegative": True,
            "y_bounds_satisfied": True,
        },
        "active_constraint_rank": {
            "method": (
                "Exact Gaussian elimination over a prime field. Rank 209 modulo "
                "a prime is a lower bound of 209 over Q, while 209 columns give "
                "the matching upper bound."
            ),
            "prime": RANK_PRIME,
            "rows": len(active_rows),
            "columns": 209,
            "rank": active_rank,
            "pivot_columns": pivots,
            "components": {
                "wave44_equations": 170,
                "zero_coordinate_equalities": len(zero_coordinates),
                "active_y_upper_bound": 1,
                "tight_cut_equalities": sum(slack == 0 for slack in slacks),
            },
        },
        "conclusion": {
            "fixed_174_cut_rational_relaxation": "EXACTLY_FEASIBLE",
            "farkas_infeasibility_certificate_for_this_fixed_bundle": "REFUTED",
            "reason": (
                "The displayed exact rational point satisfies every equality, "
                "bound, nonnegativity condition, and selected inequality."
            ),
            "full_verified_cut_ledger_feasibility": "UNKNOWN",
            "full_psd_system_feasibility": "UNKNOWN",
            "integer_count_feasibility": "UNKNOWN",
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "UNKNOWN",
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "This verifies one fixed finite 174-cut selection, not all stored directions.",
            "The witness is rational and aggregate, not integral and not a graph.",
            "Wave49 directions were selected by a numerical scout, but only their exact sealed integer cuts are used here.",
            "No full PSD matrix, complete-domain SAT instance, or graph realization is certified.",
        ],
        "resource_guard": {
            "minimum_free_physical_memory_percent": MIN_FREE_PERCENT,
            "guard_enforced_at_start_and_finish": True,
        },
    }
    return result


def compute() -> dict[str, Any]:
    result = reconstruct_and_verify()
    payload = pretty_bytes(result)
    OUTPUT.write_bytes(payload)
    print(
        "PASS_CLEAN_ROOM "
        f"equations={result['exact_witness']['equation_checks']} "
        f"cuts={result['exact_witness']['cut_checks']} "
        f"rank={result['active_constraint_rank']['rank']} "
        f"result_sha256={hashlib.sha256(payload).hexdigest()}"
    )
    return result


def validate() -> dict[str, Any]:
    stored_payload = OUTPUT.read_bytes()
    stored = json.loads(stored_payload)
    fresh = reconstruct_and_verify()
    require(stored == fresh, "stored independent result differs from fresh replay")
    print(
        "PASS_CLEAN_ROOM_REPLAY "
        f"equations={fresh['exact_witness']['equation_checks']} "
        f"cuts={fresh['exact_witness']['cut_checks']} "
        f"rank={fresh['active_constraint_rank']['rank']} "
        f"result_sha256={hashlib.sha256(stored_payload).hexdigest()}"
    )
    return fresh


def main() -> int:
    parser = argparse.ArgumentParser()
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--compute", action="store_true")
    actions.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.compute:
        compute()
    else:
        validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
