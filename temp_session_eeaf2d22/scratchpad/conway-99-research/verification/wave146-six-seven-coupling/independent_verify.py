#!/usr/bin/env python3
"""Standard-library clean verifier for the sealed Wave146 rational witness.

No Wave146 Python module is imported.  The verifier independently rebuilds
the rooted-pattern filter, local supports, deletion/root multiplicities, and
all integer equalities, using only frozen upstream data tables.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


N = 99
K = 14
N3 = 4158
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts/wave146-six-seven-coupling"
DISCOVERY_RESULT = DISCOVERY / "exact-results.json"
DISCOVERY_MANIFEST = DISCOVERY / "package-manifest.sha256"
FROZEN_FINAL_MANIFEST = HERE / "discovery-final-manifest.frozen.sha256"
OUTPUT = HERE / "verification-results.json"
WAVE21_RESULT = ROOT / "attempts/wave21-six-vertex-lp/exact-results.json"
WAVE22_RESULT = ROOT / "attempts/wave22-full-seven-deck/exact-results.json"
WAVE22_WITNESS = ROOT / "attempts/wave22-full-seven-deck/witness.json"
WAVE141_RESULT = ROOT / "attempts/wave141-bivariate-graph-code/exact-results.json"
WAVE144_RESULT = ROOT / "attempts/wave144-sixset-odd-profile/exact-results.json"

FINAL_MANIFEST_SHA256 = (
    "6a4f1125d877f4bc1dfcfe522dea66e95216416bd09550fa36aadbcbeb1f2b17"
)
UPSTREAM_HASHES = {
    "attempts/wave21-six-vertex-lp/exact-results.json":
        "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b",
    "attempts/wave22-full-seven-deck/exact-results.json":
        "ca5d9d116f6a9d6e355600429652e2bf4474b73dcf281bbcb564420d820acbd2",
    "attempts/wave22-full-seven-deck/witness.json":
        "d74453faa91e42abbe2343d428296818ae051be579305277eff6f113fe66c47d",
    "attempts/wave141-bivariate-graph-code/exact-results.json":
        "351857e985a871e6d69c5662f90ad5cd6a608f92b1703e84ffb549a753cc8b2e",
    "attempts/wave144-sixset-odd-profile/exact-results.json":
        "6dbb544494511906ce6452eaa6addb20c8e3f8861abfd67d1a026d94baf2234b",
}

# Frozen Wave22 source-index alignment.  It is upstream data, not a Wave146
# model-builder output.  Canonicality, uniqueness, and local admissibility are
# independently checked below.
SOURCE_N_MASKS = (
    7100, 1883, 5941, 1916, 5907, 1749, 926, 1881, 1884, 956, 922,
    1880, 920, 5905, 671, 761, 701, 762, 63, 123, 691, 663, 694, 633,
    760, 126, 693, 246, 700, 31, 61, 121, 659, 122, 692, 0, 1, 3,
    36, 7, 44, 37, 35, 15, 102, 45, 39, 106, 616, 110, 107, 47,
    684, 655, 685, 617, 656, 657, 60, 662, 120, 632,
)


def demand(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        demand(len(digest) == 64 and relative not in result, "bad manifest")
        result[relative] = digest
    demand(bool(result), "empty manifest")
    return result


def verify_freezes() -> dict[str, str]:
    demand(sha256(FROZEN_FINAL_MANIFEST) == FINAL_MANIFEST_SHA256,
           "frozen final manifest changed")
    demand(sha256(DISCOVERY_MANIFEST) == FINAL_MANIFEST_SHA256,
           "live final manifest changed")
    frozen = parse_manifest(FROZEN_FINAL_MANIFEST)
    demand(frozen == parse_manifest(DISCOVERY_MANIFEST),
           "live/frozen manifest entries differ")
    for relative, expected in frozen.items():
        demand(sha256(ROOT / relative) == expected,
               f"discovery artifact drift: {relative}")
    observed = {relative: sha256(ROOT / relative) for relative in UPSTREAM_HASHES}
    demand(observed == UPSTREAM_HASHES, "upstream artifact drift")
    return observed


@lru_cache(maxsize=None)
def edge_list(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


@lru_cache(maxsize=None)
def permutation_maps(order: int) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    positions = {edge: index for index, edge in enumerate(edge_list(order))}
    output = []
    for permutation in itertools.permutations(range(order)):
        bit_positions = tuple(
            positions[tuple(sorted((permutation[u], permutation[v])))]
            for u, v in edge_list(order)
        )
        output.append((permutation, bit_positions))
    return tuple(output)


def relabel_mask(mask: int, bit_positions: tuple[int, ...]) -> int:
    result = 0
    for old_position, new_position in enumerate(bit_positions):
        if mask >> old_position & 1:
            result |= 1 << new_position
    return result


def canonical_mask(mask: int, order: int) -> int:
    return min(
        relabel_mask(mask, bit_positions)
        for _, bit_positions in permutation_maps(order)
    )


def adjacency(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for position, (u, v) in enumerate(edge_list(order)):
        if mask >> position & 1:
            rows[u] |= 1 << v
            rows[v] |= 1 << u
    return tuple(rows)


def locally_admissible(mask: int, order: int) -> bool:
    rows = adjacency(mask, order)
    for position, (u, v) in enumerate(edge_list(order)):
        common = (rows[u] & rows[v]).bit_count()
        if common > (1 if mask >> position & 1 else 2):
            return False
    return True


def extend_with_root(mask: int, pattern: int) -> int:
    positions7 = {edge: index for index, edge in enumerate(edge_list(7))}
    output = 0
    for position, edge in enumerate(edge_list(6)):
        if mask >> position & 1:
            output |= 1 << positions7[edge]
    for vertex in range(6):
        if pattern >> vertex & 1:
            output |= 1 << positions7[(vertex, 6)]
    return output


def local_rhs(mask: int) -> tuple[list[int], list[int], int]:
    rows = adjacency(mask, 6)
    degrees = [row.bit_count() for row in rows]
    pair_rhs = []
    for position, (u, v) in enumerate(edge_list(6)):
        target = 1 if mask >> position & 1 else 2
        pair_rhs.append(target - (rows[u] & rows[v]).bit_count())
    demand(min(pair_rhs) >= 0, "six-mask is not locally admissible")
    return degrees, pair_rhs, sum(degree & 1 for degree in degrees)


def root_condition(mask: int, pattern: int) -> bool:
    """Per-root lambda/mu caps plus the root contribution to old pairs."""

    rows = adjacency(mask, 6)
    _, pair_rhs, _ = local_rhs(mask)
    for vertex in range(6):
        common = (rows[vertex] & pattern).bit_count()
        if common > (1 if pattern >> vertex & 1 else 2):
            return False
    for pair_position, (u, v) in enumerate(edge_list(6)):
        if pattern >> u & 1 and pattern >> v & 1 and pair_rhs[pair_position] == 0:
            return False
    return True


def enumerate_support(
    mask: int,
    allowed: tuple[int, ...],
) -> tuple[list[int], dict[int, dict[int, int]]]:
    degrees, initial_pairs, inside_odd = local_rhs(mask)
    allowed_set = set(allowed)
    pair_index = {edge: i for i, edge in enumerate(edge_list(6))}
    candidates = []
    for size in range(6, 2, -1):
        for vertices in itertools.combinations(range(6), size):
            pattern = sum(1 << vertex for vertex in vertices)
            if pattern not in allowed_set:
                continue
            used = tuple(
                pair_index[pair] for pair in itertools.combinations(vertices, 2)
            )
            if all(initial_pairs[index] > 0 for index in used):
                candidates.append((pattern, vertices, used))

    remaining = initial_pairs[:]
    high_incidence = [0] * 6
    weights: set[int] = set()
    chosen = [0] * len(candidates)
    witnesses: dict[int, dict[int, int]] = {}

    def visit(position: int, high_total: int, odd_high: int) -> None:
        if position < len(candidates):
            _, vertices, used = candidates[position]
            for value in range(min(remaining[index] for index in used) + 1):
                chosen[position] = value
                for index in used:
                    remaining[index] -= value
                for vertex in vertices:
                    high_incidence[vertex] += value
                visit(
                    position + 1,
                    high_total + value,
                    odd_high + (value if len(vertices) & 1 else 0),
                )
                for index in used:
                    remaining[index] += value
                for vertex in vertices:
                    high_incidence[vertex] -= value
            chosen[position] = 0
            return

        pair_values = [0] * 15
        for pair_position, (u, v) in enumerate(edge_list(6)):
            pattern = (1 << u) | (1 << v)
            if pattern in allowed_set:
                pair_values[pair_position] = remaining[pair_position]
            elif remaining[pair_position]:
                return
        singletons = []
        for vertex in range(6):
            pair_degree = sum(
                pair_values[pair_index[tuple(sorted((vertex, other)))]]
                for other in range(6) if other != vertex
            )
            value = K - degrees[vertex] - high_incidence[vertex] - pair_degree
            if value < 0 or (value and (1 << vertex) not in allowed_set):
                return
            singletons.append(value)
        empty = 93 - high_total - sum(pair_values) - sum(singletons)
        if empty < 0 or (empty and 0 not in allowed_set):
            return
        weight = inside_odd + odd_high + sum(singletons)
        weights.add(weight)
        if weight not in witnesses:
            profile: dict[int, int] = {}
            if empty:
                profile[0] = empty
            for vertex, value in enumerate(singletons):
                if value:
                    profile[1 << vertex] = value
            for pair_position, value in enumerate(pair_values):
                if value:
                    u, v = edge_list(6)[pair_position]
                    profile[(1 << u) | (1 << v)] = value
            for candidate_index, value in enumerate(chosen):
                if value:
                    profile[candidates[candidate_index][0]] = value
            witnesses[weight] = profile

    visit(0, 0, 0)
    demand(bool(weights), "no seven-extendable local profile")
    return sorted(weights), witnesses


def delete_vertex(mask: int, order: int, removed: int) -> tuple[int, int]:
    """Return compressed card and removed vertex's neighbor pattern."""

    rows = adjacency(mask, order)
    survivors = [vertex for vertex in range(order) if vertex != removed]
    new_label = {old: new for new, old in enumerate(survivors)}
    positions = {edge: i for i, edge in enumerate(edge_list(order - 1))}
    card = 0
    pattern = 0
    for old in survivors:
        if rows[removed] >> old & 1:
            pattern |= 1 << new_label[old]
    for old_position, (u, v) in enumerate(edge_list(order)):
        if removed in (u, v) or not (mask >> old_position & 1):
            continue
        edge = tuple(sorted((new_label[u], new_label[v])))
        card |= 1 << positions[edge]
    return card, pattern


def transform_subset(pattern: int, permutation: tuple[int, ...]) -> int:
    return sum(
        1 << permutation[vertex]
        for vertex in range(6)
        if pattern >> vertex & 1
    )


def canonical_root_pattern(card: int, canonical_card: int, pattern: int) -> int:
    candidates = [
        transform_subset(pattern, permutation)
        for permutation, bit_positions in permutation_maps(6)
        if relabel_mask(card, bit_positions) == canonical_card
    ]
    demand(bool(candidates), "card has no map to its canonical representative")
    return min(candidates)


def fraction_formula(form: dict[str, str], n3: int, h11: Fraction = Fraction(0)) -> Fraction:
    return (
        Fraction(form["constant"])
        + Fraction(form["n3_coefficient"]) * n3
        + Fraction(form["h11_coefficient"]) * h11
    )


def kraw(degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * math.comb(weight, overlap)
        * math.comb(N - weight, degree - overlap)
        for overlap in range(max(0, degree - (N - weight)), min(weight, degree) + 1)
    )


@lru_cache(maxsize=1)
def build_structure() -> dict[str, Any]:
    wave144 = json.loads(WAVE144_RESULT.read_text(encoding="utf-8"))
    prior_supports = {
        int(record["source_class"]): list(map(int, record["attainable_weights"]))
        for record in wave144["class_profiles"]
    }
    demand(len(SOURCE_N_MASKS) == len(set(SOURCE_N_MASKS)) == 62,
           "six-class source map is not a 62-element bijection")
    possible: dict[int, tuple[int, ...]] = {}
    supports: dict[int, list[int]] = {}
    local_witnesses: dict[int, dict[int, dict[int, int]]] = {}
    equivalence_checks = 0
    for source, mask in enumerate(SOURCE_N_MASKS, 1):
        demand(canonical_mask(mask, 6) == mask, f"six mask {source} noncanonical")
        demand(locally_admissible(mask, 6), f"six mask {source} inadmissible")
        patterns = []
        for pattern in range(64):
            by_formula = root_condition(mask, pattern)
            by_graph = locally_admissible(extend_with_root(mask, pattern), 7)
            demand(by_formula == by_graph,
                   f"root-filter mismatch at source {source}, pattern {pattern}")
            equivalence_checks += 1
            if by_formula:
                patterns.append(pattern)
        possible[source] = tuple(patterns)
        supports[source], local_witnesses[source] = enumerate_support(
            mask, possible[source]
        )

    removed = {
        source: sorted(set(prior_supports[source]) - set(supports[source]))
        for source in range(1, 63)
    }
    affected = {source: cells for source, cells in removed.items() if cells}
    demand(len(affected) == 16 and sum(map(len, affected.values())) == 25,
           "16-class/25-cell removal result differs")
    endpoint_cells = {
        (int(row["source_class"]), int(row["output_weight"]))
        for row in wave144["aggregate_endpoint_certificate"]["nonzero_cells"]
    }
    unsupported_endpoint = sorted(
        (source, weight)
        for source, weight in endpoint_cells
        if weight not in supports[source]
    )
    demand(len(endpoint_cells) == 65 and not unsupported_endpoint,
           "a Wave144 endpoint cell is locally unsupported")

    seven_payload = json.loads(WAVE22_WITNESS.read_text(encoding="utf-8"))
    classes7 = tuple(int(row["canonical_mask"]) for row in seven_payload["classes"])
    demand(len(classes7) == len(set(classes7)) == 208, "seven-class list differs")
    demand(classes7 == tuple(sorted(classes7)), "seven classes not sorted")
    for mask in classes7:
        demand(locally_admissible(mask, 7), f"inadmissible seven class {mask}")
        demand(canonical_mask(mask, 7) == mask, f"noncanonical seven class {mask}")

    source_by_mask = {mask: source for source, mask in enumerate(SOURCE_N_MASKS, 1)}
    deck_vectors: dict[int, Counter[int]] = {}
    root_vectors: dict[int, Counter[tuple[int, int]]] = {}
    root_keys: set[tuple[int, int]] = set()
    for mask in classes7:
        deck: Counter[int] = Counter()
        roots: Counter[tuple[int, int]] = Counter()
        for removed_vertex in range(7):
            card, pattern = delete_vertex(mask, 7, removed_vertex)
            canonical_card = canonical_mask(card, 6)
            demand(canonical_card in source_by_mask, "unknown six-card")
            source = source_by_mask[canonical_card]
            orbit = canonical_root_pattern(card, canonical_card, pattern)
            demand(root_condition(canonical_card, orbit),
                   "seven class produced forbidden root type")
            deck[source] += 1
            roots[(source, orbit)] += 1
        demand(sum(deck.values()) == sum(roots.values()) == 7,
               "seven deletion multiplicity total differs")
        deck_vectors[mask] = deck
        root_vectors[mask] = roots
        root_keys.update(roots)

    x_root_keys = {
        (source, canonical_root_pattern(SOURCE_N_MASKS[source - 1],
                                        SOURCE_N_MASKS[source - 1], pattern))
        for source in range(1, 63)
        for pattern in possible[source]
    }
    demand(root_keys == x_root_keys and len(root_keys) == 944,
           "root orbit universe differs")

    # The discovery's deterministic repaired fixed profiles use the first
    # witness found by this same explicitly stated descending-size/lexicographic
    # cell order.  Reconstruct their rooted totals and an exact deck identity.
    fixed_required: Counter[tuple[int, int]] = Counter()
    endpoint_counts = {
        (int(row["source_class"]), int(row["output_weight"])): int(row["count"])
        for row in wave144["aggregate_endpoint_certificate"]["nonzero_cells"]
    }
    for (source, weight), six_count in endpoint_counts.items():
        mask = SOURCE_N_MASKS[source - 1]
        for pattern, local_count in local_witnesses[source][weight].items():
            orbit = canonical_root_pattern(mask, mask, pattern)
            fixed_required[(source, orbit)] += six_count * local_count
    fixed_identity_defect = (
        fixed_required[(38, 8)] - 2 * fixed_required[(37, 12)]
    )
    demand(
        all(
            vector.get((38, 8), 0) == 2 * vector.get((37, 12), 0)
            for vector in root_vectors.values()
        ),
        "claimed fixed-profile deck identity is not columnwise exact",
    )
    demand(abs(fixed_identity_defect) == 3076026288,
           "fixed repaired-profile identity defect differs")

    labels = [f"seven:{mask}" for mask in classes7] + ["h11_over_4"]
    b_labels: dict[tuple[int, int], str] = {}
    x_labels: dict[tuple[int, int, int], str] = {}
    for source in range(1, 63):
        for weight in supports[source]:
            b_label = f"b:{source}:{weight}"
            b_labels[(source, weight)] = b_label
            labels.append(b_label)
            for pattern in possible[source]:
                x_label = f"x:{source}:{weight}:{pattern}"
                x_labels[(source, weight, pattern)] = x_label
                labels.append(x_label)
    demand(len(b_labels) == 343 and len(labels) == 13973,
           "independent variable universe differs")
    return {
        "wave144": wave144,
        "prior_supports": prior_supports,
        "possible": possible,
        "supports": supports,
        "local_witnesses": local_witnesses,
        "affected": affected,
        "endpoint_cells": endpoint_cells,
        "classes7": classes7,
        "deck_vectors": deck_vectors,
        "root_vectors": root_vectors,
        "root_keys": tuple(sorted(root_keys)),
        "labels": labels,
        "b_labels": b_labels,
        "x_labels": x_labels,
        "equivalence_checks": equivalence_checks,
        "fixed_identity_defect": fixed_identity_defect,
    }


def replay(payload: dict[str, Any]) -> dict[str, Any]:
    upstream = verify_freezes()
    structure = build_structure()
    labels = structure["labels"]
    index = {label: position for position, label in enumerate(labels)}
    values = {label: Fraction(0) for label in labels}
    support = payload.get("candidate", {}).get("support")
    demand(isinstance(support, list), "candidate support missing")
    prior_position = -1
    seen: set[str] = set()
    for record in support:
        demand(
            isinstance(record, dict)
            and set(record) == {"label", "numerator", "denominator"},
            "malformed support entry",
        )
        label = record["label"]
        numerator = record["numerator"]
        denominator = record["denominator"]
        demand(isinstance(label, str) and label in index and label not in seen,
               "unknown or duplicate candidate label")
        demand(type(numerator) is int and type(denominator) is int and denominator > 0,
               "bad rational scalar")
        value = Fraction(numerator, denominator)
        demand(value > 0, "sparse support must be strictly positive")
        demand(index[label] > prior_position, "support is not in canonical order")
        prior_position = index[label]
        seen.add(label)
        values[label] = value
    support_blob = json.dumps(
        support, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    support_digest = hashlib.sha256(support_blob).hexdigest()
    demand(support_digest == payload["candidate"]["support_sha256"],
           "candidate support digest mismatch")
    demand(len(support) == 2998, "positive-support size differs")
    demand(max(value.denominator for value in values.values()) == 4,
           "maximum denominator differs")
    demand(all(value >= 0 for value in values.values()), "negative candidate value")

    equality_count = 0
    nonzero_count = 0

    def check(entries: Iterable[tuple[str, int]], target: int | Fraction, label: str) -> None:
        nonlocal equality_count, nonzero_count
        filtered = [(variable, coefficient) for variable, coefficient in entries if coefficient]
        actual = sum(
            (values[variable] * coefficient for variable, coefficient in filtered),
            Fraction(0),
        )
        demand(actual == Fraction(target),
               f"exact row failure {label}: {actual} != {target}")
        equality_count += 1
        nonzero_count += len(filtered)

    wave21 = json.loads(WAVE21_RESULT.read_text(encoding="utf-8"))
    six_formulas = wave21["formula_tables"]["six"]
    seven_formulas = wave21["formula_tables"]["seven"]
    marginals: dict[int, int] = {}
    for source in range(1, 63):
        marginal = fraction_formula(six_formulas[str(source)], N3)
        demand(marginal.denominator == 1 and marginal >= 0, "bad six marginal")
        marginals[source] = marginal.numerator

    # Independently reconstructed complete deletion deck.
    for source in range(1, 63):
        check(
            (
                (f"seven:{mask}", vector.get(source, 0))
                for mask, vector in structure["deck_vectors"].items()
            ),
            93 * marginals[source],
            f"deck:{source}",
        )

    y_value = values["h11_over_4"]
    demand(Fraction(2079) <= y_value <= Fraction(4158), "h11/4 out of range")
    wave22 = json.loads(WAVE22_RESULT.read_text(encoding="utf-8"))
    h_records = wave22["hamiltonian_alignment"]["source_H_records"]
    demand(len(h_records) == 19, "Hamiltonian source list differs")
    for record in h_records:
        source = int(record["source_index"])
        mask = int(record["canonical_mask"])
        form = seven_formulas[str(source)]
        constant = (
            Fraction(form["constant"])
            + Fraction(form["n3_coefficient"]) * N3
        )
        y_coefficient = 4 * Fraction(form["h11_coefficient"])
        demand(constant.denominator == y_coefficient.denominator == 1,
               "Hamiltonian row is not integral in h11/4")
        check(
            (
                (f"seven:{mask}", 1),
                ("h11_over_4", -y_coefficient.numerator),
            ),
            constant,
            f"hamiltonian:{source}",
        )

    # B-class marginals and global weight moments.
    for source in range(1, 63):
        check(
            (
                (structure["b_labels"][(source, weight)], 1)
                for weight in structure["supports"][source]
            ),
            marginals[source],
            f"class-marginal:{source}",
        )
    wave141 = json.loads(WAVE141_RESULT.read_text(encoding="utf-8"))
    low_rows = {
        int(t): {int(weight): int(count) for weight, count in row.items()}
        for t, row in wave141["exact_low_input_rows"].items()
    }
    all_b = tuple(structure["b_labels"].items())
    for degree in range(4):
        rhs = sum(
            kraw(6, weight) * count
            for weight, count in low_rows[degree].items()
        )
        check(
            (
                (label, kraw(degree, source_weight[1]))
                for source_weight, label in all_b
            ),
            rhs,
            f"reciprocity:{degree}",
        )
    check(
        (
            (label, (-1) ** (source_weight[1] // 2))
            for source_weight, label in all_b
        ),
        2734116,
        "signed-S6",
    )

    # Aggregate local profile equations for every surviving B cell.
    root_x_labels: dict[tuple[int, int], list[str]] = defaultdict(list)
    for source in range(1, 63):
        mask = SOURCE_N_MASKS[source - 1]
        degrees, pair_rhs, inside_odd = local_rhs(mask)
        for weight in structure["supports"][source]:
            b_label = structure["b_labels"][(source, weight)]
            patterns = structure["possible"][source]
            x_for = lambda pattern: structure["x_labels"][(source, weight, pattern)]
            check(
                [(x_for(pattern), 1) for pattern in patterns] + [(b_label, -93)],
                0,
                f"cell-total:{source}:{weight}",
            )
            for vertex in range(6):
                check(
                    [
                        (x_for(pattern), 1)
                        for pattern in patterns if pattern >> vertex & 1
                    ] + [(b_label, -(K - degrees[vertex]))],
                    0,
                    f"cell-degree:{source}:{weight}:{vertex}",
                )
            for pair_position, (u, v) in enumerate(edge_list(6)):
                check(
                    [
                        (x_for(pattern), 1)
                        for pattern in patterns
                        if pattern >> u & 1 and pattern >> v & 1
                    ] + [(b_label, -pair_rhs[pair_position])],
                    0,
                    f"cell-pair:{source}:{weight}:{u}:{v}",
                )
            check(
                [
                    (x_for(pattern), 1)
                    for pattern in patterns if pattern.bit_count() & 1
                ] + [(b_label, -(weight - inside_odd))],
                0,
                f"cell-odd:{source}:{weight}",
            )
            for pattern in patterns:
                orbit = canonical_root_pattern(mask, mask, pattern)
                root_x_labels[(source, orbit)].append(x_for(pattern))

    for key in structure["root_keys"]:
        entries = [(label, 1) for label in root_x_labels[key]]
        entries.extend(
            (f"seven:{mask}", -vector.get(key, 0))
            for mask, vector in structure["root_vectors"].items()
        )
        check(entries, 0, f"root-link:{key[0]}:{key[1]}")

    demand(equality_count == 8981, "independent equality count differs")
    demand(
        nonzero_count == 110269,
        f"independent matrix nonzero count differs: {nonzero_count}",
    )
    demand(payload["model"] == {
        "verification": "PASS",
        "variables": 13973,
        "equalities": 8981,
        "matrix_nonzeros": 110269,
        "positive_variables": 2998,
        "maximum_denominator": 4,
        "h11_over_4": "4158",
        "h11": "16632",
    }, "stored model summary differs")
    demand(y_value == 4158, "candidate h11/4 differs")
    demand(payload["conclusion"]["one_root_six_to_seven_relaxation"]
           == "EXACT_RATIONAL_FEASIBLE", "conclusion label differs")

    removed = structure["affected"]
    return {
        "format": "wave146-independent-verification-v1",
        "verdict": "PASS_RATIONAL_RELAXATION",
        "claim_label": "VERIFIED",
        "discovery_manifest_sha256": FINAL_MANIFEST_SHA256,
        "discovery_manifest_entries_checked": len(parse_manifest(FROZEN_FINAL_MANIFEST)),
        "superseded_partial_freeze_sha256":
            "a783701cd4b1dd1b20c60f16985444836950a56e33b5b39de336d27efe06c88b",
        "upstream_hashes": upstream,
        "root_condition_derivation": (
            "For each u, |N_H(u) intersect P| <= 1 when u in P and <= 2 "
            "otherwise; for each u,v in P the old pair residual is positive."
        ),
        "root_filter_vs_direct_seven_graph_checks": structure["equivalence_checks"],
        "classes_with_removed_weights": len(removed),
        "total_removed_weight_cells": sum(map(len, removed.values())),
        "removed_weights_by_source": {str(k): v for k, v in removed.items()},
        "wave144_endpoint_positive_cells": len(structure["endpoint_cells"]),
        "wave144_endpoint_unsupported_cells": 0,
        "fixed_repaired_profile_identity": {
            "equation": "R_(38,8) = 2 R_(37,12)",
            "defect_left_minus_right": structure["fixed_identity_defect"],
            "absolute_defect": abs(structure["fixed_identity_defect"]),
            "verdict": "EXACTLY_REFUTED_FIXED_PROFILE_ONLY",
        },
        "upstream_seven_classes_revalidated": len(structure["classes7"]),
        "root_orbit_types_reconstructed": len(structure["root_keys"]),
        "six_weight_cells": len(structure["b_labels"]),
        "variables": len(labels),
        "equalities_replayed": equality_count,
        "integer_matrix_nonzeros_reconstructed": nonzero_count,
        "positive_rational_coordinates_replayed": len(support),
        "maximum_denominator": 4,
        "support_sha256": support_digest,
        "h11": 16632,
        "semantics": {
            "necessary_for_every_graph": True,
            "automorphism_handling": (
                "Canonical pattern coordinates may depend on a chosen "
                "isomorphism, but root links sum complete Aut(H) orbits, "
                "making the double count invariant."
            ),
            "graph_realization": "NOT_ESTABLISHED",
            "order_eight_overlap_consistency": "NOT_ESTABLISHED",
        },
        "conclusion": (
            "The complete one-root six-to-seven rational aggregate relaxation "
            "is exactly feasible at n3=4158, so it gives no stricter bound."
        ),
    }


def main() -> int:
    payload = json.loads(DISCOVERY_RESULT.read_text(encoding="utf-8"))
    result = replay(payload)
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
