#!/usr/bin/env python3
"""Rebuild and size the cyclic-design matching/configuration relaxation."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool

from check_linear_systems import build_blocks


def main() -> int:
    blocks = build_blocks()
    pool = IDPool()

    matching_variables: dict[tuple[int, int], int] = {}
    through_point_block: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    matching_into: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    for first, second in combinations(range(77), 2):
        intersection = blocks[first] & blocks[second]
        if len(intersection) != 1:
            continue
        point = next(iter(intersection))
        variable = pool.id(("matching", point, first, second))
        matching_variables[first, second] = variable
        through_point_block[point, first].append(variable)
        through_point_block[point, second].append(variable)
        for other_point in blocks[second] - blocks[first]:
            matching_into[first, other_point].append(variable)
        for other_point in blocks[first] - blocks[second]:
            matching_into[second, other_point].append(variable)

    triples = [
        triple
        for triple in combinations(range(77), 3)
        if all(
            not (blocks[first] & blocks[second])
            for first, second in combinations(triple, 2)
        )
    ]
    triangle_variables = {
        triple: pool.id(("triangle",) + triple) for triple in triples
    }
    through_vertex: defaultdict[int, list[int]] = defaultdict(list)
    through_pair: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    triangle_into: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    for triple, variable in triangle_variables.items():
        for vertex in triple:
            through_vertex[vertex].append(variable)
        for pair in combinations(triple, 2):
            through_pair[pair].append(variable)
        for vertex in triple:
            for other in triple:
                if other != vertex:
                    for point in blocks[other]:
                        triangle_into[vertex, point].append(variable)

    assert all(
        len(variables) == len(set(variables))
        for variables in triangle_into.values()
    )

    formula = CNF()
    for point in range(22):
        for vertex, block in enumerate(blocks):
            if point in block:
                formula.extend(
                    CardEnc.equals(
                        through_point_block[point, vertex],
                        1,
                        vpool=pool,
                        encoding=EncType.seqcounter,
                    ).clauses
                )

    for vertex in range(77):
        formula.extend(
            CardEnc.equals(
                through_vertex[vertex],
                3,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )
    for variables in through_pair.values():
        formula.extend(
            CardEnc.atmost(
                variables,
                1,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses
        )

    outside_equations = 0
    for vertex, block in enumerate(blocks):
        for point in range(22):
            if point in block:
                continue
            literals = matching_into[vertex, point] + triangle_into[vertex, point]
            assert len(literals) == len(set(literals))
            formula.extend(
                CardEnc.equals(
                    literals,
                    2,
                    vpool=pool,
                    encoding=EncType.seqcounter,
                ).clauses
            )
            outside_equations += 1

    assert len(matching_variables) == 1_540
    assert len(triangle_variables) == 3_542
    assert outside_equations == 1_386
    assert pool.top == 445_599
    assert len(formula.clauses) == 892_122

    print("matching_variables", len(matching_variables))
    print("triangle_variables", len(triangle_variables))
    print("outside_ND_equations", outside_equations)
    print("total_variables", pool.top)
    print("clauses", len(formula.clauses))
    print("PASS cyclic-design relaxation sizing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
