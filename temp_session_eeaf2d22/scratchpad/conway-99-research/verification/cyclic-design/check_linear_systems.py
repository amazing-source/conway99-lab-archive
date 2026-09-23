#!/usr/bin/env python3
"""Exact linear checks for the restricted cyclic alpha-22 design."""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path


CERTIFICATE = Path(__file__).with_name("cyclic-2-22-4-2.json")


def orbit(block: tuple[int, ...], modulus: int) -> set[tuple[int, ...]]:
    return {
        tuple(sorted((point + shift) % modulus for point in block))
        for shift in range(modulus)
    }


def build_blocks() -> list[frozenset[int]]:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    modulus = certificate["group_order"]
    blocks: set[tuple[int, ...]] = set()
    for raw in certificate["full_orbit_base_blocks"]:
        blocks.update(orbit(tuple(raw), modulus))
    blocks.update(orbit(tuple(certificate["short_orbit_base_block"]), modulus))
    result = [frozenset(block) for block in sorted(blocks)]
    assert len(result) == certificate["block_count"] == 77
    return result


def integer_rows(
    blocks: list[frozenset[int]],
    edge_index: dict[tuple[int, int], int],
) -> list[tuple[list[int], int]]:
    rows: list[tuple[list[int], int]] = []
    for first, block in enumerate(blocks):
        for point in range(22):
            support = []
            for second, other in enumerate(blocks):
                if first == second or point not in other:
                    continue
                edge = tuple(sorted((first, second)))
                if edge in edge_index:
                    support.append(edge_index[edge])
            rows.append((support, 1 if point in block else 2))
    return rows


def modular_rank(
    rows: list[tuple[list[int], int]], prime: int
) -> tuple[int, bool]:
    basis: dict[int, tuple[dict[int, int], int]] = {}
    for support, integer_rhs in rows:
        row = {column: 1 for column in support}
        rhs = integer_rhs % prime
        while row:
            pivot = max(row)
            if pivot not in basis:
                inverse = pow(row[pivot], -1, prime)
                normalized = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                basis[pivot] = (normalized, rhs * inverse % prime)
                break
            factor = row[pivot]
            old_row, old_rhs = basis[pivot]
            for column, value in old_row.items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
            rhs = (rhs - factor * old_rhs) % prime
        else:
            if rhs:
                return len(basis), False
    return len(basis), True


def main() -> int:
    blocks = build_blocks()
    admissible_pairs = [
        (first, second)
        for first, second in combinations(range(len(blocks)), 2)
        if len(blocks[first] & blocks[second]) <= 1
    ]
    edge_index = {
        pair: index for index, pair in enumerate(admissible_pairs)
    }
    rows = integer_rows(blocks, edge_index)
    disjoint_triples = sum(
        all(not (blocks[first] & blocks[second]) for first, second in combinations(triple, 2))
        for triple in combinations(range(len(blocks)), 3)
    )

    assert len(admissible_pairs) == 2_695
    assert len(rows) == 1_694
    assert disjoint_triples == 3_542
    print("edge_variables", len(admissible_pairs))
    print("linear_equations", len(rows))
    print("pairwise_disjoint_block_triples", disjoint_triples)

    expected_ranks = {2: 1_386, 3: 1_463, 5: 1_463, 7: 1_463}
    for prime, expected_rank in expected_ranks.items():
        rank, consistent = modular_rank(rows, prime)
        assert rank == expected_rank
        assert consistent
        print(f"mod_{prime}_rank", rank, "CONSISTENT")

    print("PASS cyclic-design linear checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
