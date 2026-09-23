#!/usr/bin/env python3
"""Standard-library verifier for the cyclic 2-(22,4,2) certificate."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path


CERTIFICATE = Path(__file__).with_name("cyclic-2-22-4-2.json")


def translate(block: tuple[int, ...], shift: int, modulus: int) -> tuple[int, ...]:
    return tuple(sorted((point + shift) % modulus for point in block))


def orbit(block: tuple[int, ...], modulus: int) -> list[tuple[int, ...]]:
    return sorted({translate(block, shift, modulus) for shift in range(modulus)})


def difference_counts(block: tuple[int, ...], modulus: int) -> list[int]:
    counts = [0] * modulus
    for first in block:
        for second in block:
            if first != second:
                counts[(first - second) % modulus] += 1
    return counts


def main() -> int:
    raw = CERTIFICATE.read_bytes()
    certificate = json.loads(raw)
    modulus = certificate["group_order"]
    full_bases = [
        tuple(block) for block in certificate["full_orbit_base_blocks"]
    ]
    short_base = tuple(certificate["short_orbit_base_block"])

    full_orbits = [orbit(block, modulus) for block in full_bases]
    short_orbit = orbit(short_base, modulus)
    assert all(len(item) == modulus for item in full_orbits)
    assert len(short_orbit) == certificate["short_orbit_size"] == 11

    full_differences = [difference_counts(block, modulus) for block in full_bases]
    short_differences = difference_counts(short_base, modulus)
    combined_differences = [
        2 * sum(counts[difference] for counts in full_differences)
        + short_differences[difference]
        for difference in range(1, modulus)
    ]
    assert (
        combined_differences
        == certificate["ordered_difference_check_d_1_through_21"]
        == [4] * (modulus - 1)
    )

    blocks = sorted(
        {block for item in full_orbits for block in item} | set(short_orbit)
    )
    assert len(blocks) == certificate["block_count"] == 77
    assert all(len(block) == 4 for block in blocks)

    point_counts = Counter(point for block in blocks for point in block)
    pair_counts = Counter(pair for block in blocks for pair in combinations(block, 2))
    intersection_histogram = Counter(
        len(set(first) & set(second)) for first, second in combinations(blocks, 2)
    )
    assert set(point_counts) == set(range(modulus))
    assert set(point_counts.values()) == {certificate["point_replication"]} == {14}
    assert len(pair_counts) == modulus * (modulus - 1) // 2
    assert set(pair_counts.values()) == {certificate["pair_multiplicity"]} == {2}
    assert {
        str(key): value for key, value in sorted(intersection_histogram.items())
    } == certificate["block_intersection_histogram"]

    print("PASS cyclic 2-(22,4,2) certificate")
    print("certificate_sha256", hashlib.sha256(raw).hexdigest())
    print("blocks", len(blocks))
    print("intersection_histogram", dict(sorted(intersection_histogram.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
