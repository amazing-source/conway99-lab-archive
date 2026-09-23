"""Standard-library exact replay for the Wave134 derived checkpoint."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import product
from math import comb, gcd, prod
from pathlib import Path


N = 99
HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = HERE / "exact-results.json"


@lru_cache(maxsize=None)
def kraw(degree: int, negative: int, length: int) -> int:
    if degree < 0 or degree > length:
        return 0
    return sum(
        (-1) ** overlap
        * comb(negative, overlap)
        * comb(length - negative, degree - overlap)
        for overlap in range(
            max(0, degree - (length - negative)),
            min(negative, degree) + 1,
        )
    )


def transform_coefficient(source, target) -> int:
    a, b, c = source
    _, r, s = target
    return (
        (1 << r)
        * kraw(r, c, a + c)
        * kraw(s, b, N - r)
    )


def representative(state):
    a, b, c = state
    return max(a, c), b, min(a, c)


def add(table, state, count):
    table[representative(state)] += count


TRIPLE_TYPES = (
    (70686, 0, 0, (2, 2, 2)),
    (27720, 0, 1, (2, 2, 2)),
    (41580, 1, 0, (1, 2, 2)),
    (8316, 1, 1, (1, 2, 2)),
    (8316, 2, 0, (1, 1, 2)),
    (231, 3, 0, (1, 1, 1)),
)


def membership_counts(weights, pairs=(), triple=0):
    size = len(weights)
    if size == 0:
        return {0: N}
    if size == 1:
        return {0: N - weights[0], 1: weights[0]}
    if size == 2:
        common = pairs[0]
        return {
            0: N - weights[0] - weights[1] + common,
            1: weights[0] - common,
            2: weights[1] - common,
            3: common,
        }
    p12, p13, p23 = pairs
    result = {
        7: triple,
        3: p12 - triple,
        5: p13 - triple,
        6: p23 - triple,
        1: weights[0] - p12 - p13 + triple,
        2: weights[1] - p12 - p23 + triple,
        4: weights[2] - p13 - p23 + triple,
    }
    result[0] = N - sum(result.values())
    return result


def composition(masks, coefficients):
    symbols = [0, 0, 0, 0]
    for mask, count in masks.items():
        symbol = sum(
            coefficient
            for index, coefficient in enumerate(coefficients)
            if mask & (1 << index)
        ) % 4
        symbols[symbol] += count
    return symbols[0], symbols[1] + symbols[3], symbols[2]


def forced_primal():
    result = defaultdict(int)
    add(result, (99, 0, 0), 1)
    masks = membership_counts((14,))
    for coefficients in product((1, 2, 3), repeat=1):
        add(result, composition(masks, coefficients), 99)
    for support_count, intersection in ((693, 1), (4158, 2)):
        masks = membership_counts((14, 14), (intersection,))
        for coefficients in product((1, 2, 3), repeat=2):
            add(result, composition(masks, coefficients), support_count)
    for support_count, _edges, common, intersections in TRIPLE_TYPES:
        masks = membership_counts((14, 14, 14), intersections, common)
        for coefficients in product((1, 2, 3), repeat=3):
            add(result, composition(masks, coefficients), support_count)
    return dict(result)


def forced_dual():
    result = defaultdict(int)
    add(result, (99, 0, 0), 1)
    masks = membership_counts((15,))
    for coefficients in product((1, 2, 3), repeat=1):
        if sum(coefficients) % 2 == 0:
            add(result, composition(masks, coefficients), 99)
    for support_count, intersection in ((693, 3), (4158, 2)):
        masks = membership_counts((15, 15), (intersection,))
        for coefficients in product((1, 2, 3), repeat=2):
            if sum(coefficients) % 2 == 0:
                add(result, composition(masks, coefficients), support_count)
    internal_universal = {0: 0, 1: 0, 2: 1, 3: 3}
    for support_count, edges, common, intersections in TRIPLE_TYPES:
        closed_pairs = tuple(3 if value == 1 else 2 for value in intersections)
        closed_triple = common + internal_universal[edges]
        masks = membership_counts(
            (15, 15, 15), closed_pairs, closed_triple
        )
        for coefficients in product((1, 2, 3), repeat=3):
            if sum(coefficients) % 2 == 0:
                add(result, composition(masks, coefficients), support_count)
    return dict(result)


def primal_states():
    result = []
    for b in [0] + list(range(8, 94, 2)):
        remaining = N - b
        for c in range((remaining + 1) // 2):
            if b == 0 and 1 <= c <= 6:
                continue
            result.append((remaining - c, b, c))
    return result


def dual_states():
    result = []
    for b in [0] + list(range(8, 92, 2)):
        remaining = N - b
        for c in range((remaining + 1) // 2):
            if b == 0 and 1 <= c <= 7:
                continue
            result.append((remaining - c, b, c))
    return result


def forbidden_dual_states():
    result = []
    for b in (2, 4, 6, 92, 94, 96, 98):
        remaining = N - b
        for c in range((remaining + 1) // 2):
            result.append((remaining - c, b, c))
    result.extend((N - c, 0, c) for c in range(1, 8))
    return result


def parse_orbits(table):
    result = {}
    for key, text in table.items():
        state = tuple(int(value) for value in key.split(","))
        result[state] = Fraction(text)
    return result


def verify_rational(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("classification") != "EXACT_RATIONAL_FEASIBLE":
        raise AssertionError("witness is not classified exact rational")
    sources = primal_states()
    targets = dual_states()
    source_set = set(sources)
    target_set = set(targets)
    primal = parse_orbits(payload["primal_orbits"])
    dual = parse_orbits(payload["dual_orbits"])
    if not set(primal).issubset(source_set):
        raise AssertionError("invalid primal state")
    if not set(dual).issubset(target_set):
        raise AssertionError("invalid dual state")
    primal = {state: primal.get(state, Fraction(0)) for state in sources}
    dual = {state: dual.get(state, Fraction(0)) for state in targets}
    if any(value < 0 for value in primal.values()):
        raise AssertionError("negative primal coefficient")
    if any(value < 0 for value in dual.values()):
        raise AssertionError("negative dual coefficient")
    if primal[(99, 0, 0)] != 1:
        raise AssertionError("wrong primal zero coefficient")
    if sum(primal.values()) != 1 << 108:
        raise AssertionError("wrong primal orbit total")
    if sum(dual.values()) != 1 << 88:
        raise AssertionError("wrong dual orbit total")
    for state, lower in forced_primal().items():
        if primal[state] < lower:
            raise AssertionError(f"primal lower failed at {state}")
    for state, lower in forced_dual().items():
        if dual[state] < lower:
            raise AssertionError(f"dual lower failed at {state}")

    nonzero_primal = {
        state: value for state, value in primal.items() if value
    }
    for target in targets:
        transformed = sum(
            transform_coefficient(source, target) * value
            for source, value in nonzero_primal.items()
        ) / (1 << 108)
        if transformed != dual[target]:
            raise AssertionError(f"transform mismatch at {target}")
    for target in forbidden_dual_states():
        transformed = sum(
            transform_coefficient(source, target) * value
            for source, value in nonzero_primal.items()
        ) / (1 << 108)
        if transformed:
            raise AssertionError(f"forbidden dual row nonzero at {target}")
    return {
        "classification": "EXACT_RATIONAL_FEASIBLE",
        "witness_file": path.name,
        "nonzero_primal_orbits": len(nonzero_primal),
        "nonzero_dual_orbits": sum(value != 0 for value in dual.values()),
        "forward_rows_checked": len(targets),
        "zero_rows_checked": len(forbidden_dual_states()),
    }


def derive(witness: Path | None) -> dict:
    smith = [1] * 45 + [3] * 9 + [6] + [12] * 43 + [84]
    assert len(smith) == N
    assert all(right % left == 0 for left, right in zip(smith, smith[1:]))
    assert all(84 % value == 0 for value in smith)
    assert sum(value % 2 != 0 for value in smith) == 54
    assert sum(value % 3 != 0 for value in smith) == 45
    assert sum(value % 7 != 0 for value in smith) == 98
    assert prod(smith) == (1 << 89) * (3**54) * 7
    image_orders = [4 // gcd(value, 4) for value in smith]
    c_free = sum(value == 4 for value in image_orders)
    c_torsion = sum(value == 2 for value in image_orders)
    assert (c_free, c_torsion) == (54, 1)
    c_order = prod(image_orders)
    d_order = 4**N // c_order
    assert c_order == 1 << 109
    assert d_order == 1 << 89
    assert d_order == 4**44 * 2

    primal = forced_primal()
    dual = forced_dual()
    assert len(primal) == 42
    assert 2 * sum(primal.values()) == 8557760
    assert len(dual) == 22
    assert 2 * sum(dual.values()) == 4126784
    assert len(primal_states()) == 1119
    assert len(dual_states()) == 1114
    assert len(forbidden_dual_states()) == 161
    assert comb(N + 2, 2) == 5050

    # Independent direct check for the transformed all-zero monomial:
    # (x+2y+z)^99.
    for b in range(N + 1):
        for c in range(N - b + 1):
            target = (N - b - c, b, c)
            expected = comb(N, b) * comb(N - b, c) * (1 << b)
            assert transform_coefficient((N, 0, 0), target) == expected

    rational = (
        verify_rational(witness)
        if witness is not None and witness.exists()
        else {"classification": "UNKNOWN_NOT_RUN_CORRECTED_MODEL"}
    )
    claim_labels = ["DERIVED", "UNKNOWN"]
    if rational["classification"] == "EXACT_RATIONAL_FEASIBLE":
        claim_labels.insert(1, "CANDIDATE")
    return {
        "format": "wave134-z4-derived-checkpoint-v1",
        "claim_labels": claim_labels,
        "scope": "conditional full-problem Z4 symmetrized-enumerator lane",
        "smith_replay": {
            "invariant_factors": {
                "1": 45,
                "3": 9,
                "6": 1,
                "12": 43,
                "84": 1,
            },
            "rank_F2": 54,
            "rank_F3": 45,
            "rank_F7": 98,
            "determinant_absolute": str(prod(smith)),
        },
        "code_types": {
            "C": {"type": "4^54 2^1", "order": str(c_order)},
            "Cperp": {"type": "4^44 2^1", "order": str(d_order)},
            "extra_torsion_word": "2*1",
            "coefficient_symmetry": "(n0,nodd,n2)<->(n2,nodd,n0)",
        },
        "transform": {
            "raw_states": 5050,
            "primal_orbits": len(primal_states()),
            "allowed_dual_orbits": len(dual_states()),
            "forbidden_dual_orbits": len(forbidden_dual_states()),
            "zero_monomial_rows_checked": 5050,
        },
        "forced_words": {
            "primal_orbits": {
                ",".join(map(str, state)): value
                for state, value in sorted(primal.items())
            },
            "primal_expanded_compositions": 84,
            "primal_distinct_words": 8557760,
            "dual_orbits": {
                ",".join(map(str, state)): value
                for state, value in sorted(dual.items())
            },
            "dual_expanded_compositions": 44,
            "dual_distinct_words": 4126784,
        },
        "rational_relaxation": rational,
        "boundaries": {
            "integral_feasibility": "UNKNOWN",
            "Z4_code_realizability": "UNKNOWN",
            "graph_realizability": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--witness", type=Path)
    args = parser.parse_args()
    result = derive(args.witness)
    if args.verify:
        stored = json.loads(args.verify.read_text(encoding="utf-8"))
        if result != stored:
            raise SystemExit("FAIL: regenerated result differs")
        print("PASS: canonical Wave134 derived checkpoint verified")
        return
    output = args.write or DEFAULT_OUTPUT
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
