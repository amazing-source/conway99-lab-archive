"""Independent verifier for the Wave 60 three-component incidence reduction.

This implementation is intentionally self-contained.  It imports no discovery
module and reconstructs every exact count from the mathematical specification.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


N_LOCAL = 12
FIBRES = tuple(range(3))
COORDS = tuple(range(4))
PERMS3 = tuple(itertools.permutations(FIBRES))
PERMS4 = tuple(itertools.permutations(COORDS))
MATCHINGS4 = (
    ((0, 1), (2, 3)),
    ((0, 2), (1, 3)),
    ((0, 3), (1, 2)),
)


def vertex(fibre: int, coordinate: int) -> int:
    return 4 * fibre + coordinate


def adjacency_from_edges(n: int, edges: list[tuple[int, int]]) -> tuple[int, ...]:
    rows = [0] * n
    for u, v in edges:
        if not (0 <= u < v < n):
            raise ValueError(f"bad edge {(u, v)}")
        if (rows[u] >> v) & 1:
            raise ValueError(f"duplicate edge {(u, v)}")
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    return tuple(rows)


def edges_from_adjacency(rows: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return tuple(
        (u, v)
        for u in range(len(rows))
        for v in range(u + 1, len(rows))
        if (rows[u] >> v) & 1
    )


PAIR_INDEX = {
    (u, v): i
    for i, (u, v) in enumerate(
        (pair for pair in itertools.combinations(range(N_LOCAL), 2))
    )
}


def edge_code_after_map(
    edges: tuple[tuple[int, int], ...], mapping: tuple[int, ...]
) -> int:
    code = 0
    for u, v in edges:
        a, b = mapping[u], mapping[v]
        if a > b:
            a, b = b, a
        code |= 1 << PAIR_INDEX[(a, b)]
    return code


def within_fibre_mapping(
    p0: tuple[int, ...], p1: tuple[int, ...], p2: tuple[int, ...]
) -> tuple[int, ...]:
    ps = (p0, p1, p2)
    return tuple(vertex(f, ps[f][i]) for f in FIBRES for i in COORDS)


WITHIN_FIBRE_MAPS = tuple(
    within_fibre_mapping(p0, p1, p2)
    for p0 in PERMS4
    for p1 in PERMS4
    for p2 in PERMS4
)


def canonical_code(rows: tuple[int, ...]) -> int:
    edges = edges_from_adjacency(rows)
    return min(edge_code_after_map(edges, mapping) for mapping in WITHIN_FIBRE_MAPS)


def make_normalized_component(
    matching1: tuple[tuple[int, int], ...],
    matching2: tuple[tuple[int, int], ...],
    cross12: tuple[int, ...],
) -> tuple[int, ...]:
    edges: list[tuple[int, int]] = []
    for a, b in MATCHINGS4[0]:
        edges.append((vertex(0, a), vertex(0, b)))
    for a, b in matching1:
        edges.append((vertex(1, a), vertex(1, b)))
    for a, b in matching2:
        edges.append((vertex(2, a), vertex(2, b)))
    for i in COORDS:
        edges.append((vertex(0, i), vertex(1, i)))
        edges.append((vertex(0, i), vertex(2, i)))
        edges.append((vertex(1, i), vertex(2, cross12[i])))
    return adjacency_from_edges(N_LOCAL, sorted(tuple(sorted(e)) for e in edges))


def is_connected(rows: tuple[int, ...]) -> bool:
    reached = 1
    frontier = 1
    while frontier:
        neighbours = 0
        bits = frontier
        while bits:
            low = bits & -bits
            u = low.bit_length() - 1
            neighbours |= rows[u]
            bits ^= low
        frontier = neighbours & ~reached
        reached |= frontier
    return reached.bit_count() == len(rows)


def triangle_count(rows: tuple[int, ...]) -> int:
    count = 0
    for u, v in edges_from_adjacency(rows):
        count += (rows[u] & rows[v]).bit_count()
    return count // 3


def four_cycle_count(rows: tuple[int, ...]) -> int:
    opposite_pair_choices = 0
    for u, v in itertools.combinations(range(len(rows)), 2):
        common = (rows[u] & rows[v]).bit_count()
        opposite_pair_choices += common * (common - 1) // 2
    if opposite_pair_choices % 2:
        raise AssertionError("four-cycle double count was odd")
    return opposite_pair_choices // 2


def passes_component_spec(rows: tuple[int, ...]) -> bool:
    if {r.bit_count() for r in rows} != {3}:
        return False
    if not is_connected(rows) or triangle_count(rows):
        return False
    for u, v in itertools.combinations(range(N_LOCAL), 2):
        adjacent = (rows[u] >> v) & 1
        common = (rows[u] & rows[v]).bit_count()
        if adjacent and common:
            return False
        if not adjacent:
            cap = 1 if u // 4 == v // 4 else 2
            if common > cap:
                return False
    return True


def classify_components() -> tuple[
    list[tuple[int, ...]],
    list[tuple[int, ...]],
    Counter[int],
    list[tuple[int, ...]],
]:
    normalized: list[tuple[int, ...]] = []
    accepted: list[tuple[int, ...]] = []
    c4_distribution: Counter[int] = Counter()
    for m1 in MATCHINGS4:
        for m2 in MATCHINGS4:
            for p12 in PERMS4:
                rows = make_normalized_component(m1, m2, p12)
                normalized.append(rows)
                if passes_component_spec(rows):
                    accepted.append(rows)
                    c4_distribution[four_cycle_count(rows)] += 1
    by_code: dict[int, tuple[int, ...]] = {}
    for rows in accepted:
        by_code.setdefault(canonical_code(rows), rows)
    types = [by_code[code] for code in sorted(by_code)]
    return normalized, accepted, c4_distribution, types


def permute_fibres(rows: tuple[int, ...], p: tuple[int, ...]) -> tuple[int, ...]:
    mapping = tuple(vertex(p[f], i) for f in FIBRES for i in COORDS)
    edges = []
    for u, v in edges_from_adjacency(rows):
        a, b = mapping[u], mapping[v]
        edges.append(tuple(sorted((a, b))))
    return adjacency_from_edges(N_LOCAL, sorted(edges))


def simultaneous_fibre_action(
    types: list[tuple[int, ...]]
) -> dict[tuple[int, ...], tuple[int, ...]]:
    code_to_type = {canonical_code(rows): i for i, rows in enumerate(types)}
    action: dict[tuple[int, ...], tuple[int, ...]] = {}
    for p in PERMS3:
        mapping = []
        for rows in types:
            image_code = canonical_code(permute_fibres(rows, p))
            mapping.append(code_to_type[image_code])
        action[p] = tuple(mapping)
    return action


def triples_and_safe_orbits(
    type_count: int, action: dict[tuple[int, ...], tuple[int, ...]]
) -> tuple[list[tuple[int, int, int]], list[tuple[tuple[int, int, int], ...]]]:
    triples = list(itertools.combinations_with_replacement(range(type_count), 3))
    remaining = set(triples)
    orbits: list[tuple[tuple[int, int, int], ...]] = []
    while remaining:
        triple = min(remaining)
        orbit = {
            tuple(sorted(mapping[i] for i in triple)) for mapping in action.values()
        }
        orbits.append(tuple(sorted(orbit)))
        remaining.difference_update(orbit)
    return triples, sorted(orbits, key=lambda orbit: orbit[0])


def local_gram(rows: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    gram: list[list[int]] = [[0] * N_LOCAL for _ in range(N_LOCAL)]
    for u in range(N_LOCAL):
        for v in range(N_LOCAL):
            common = (rows[u] & rows[v]).bit_count()
            same_fibre = int(u // 4 == v // 4)
            gram[u][v] = (
                12 * int(u == v)
                - ((rows[u] >> v) & 1)
                + 2
                - same_fibre
                - common
            )
    return tuple(tuple(row) for row in gram)


def global_gram(type_triple: tuple[int, int, int], types: list[tuple[int, ...]]):
    n = 36
    neighbours = [0] * n
    for component, type_index in enumerate(type_triple):
        offset = 12 * component
        for u, row in enumerate(types[type_index]):
            bits = row
            while bits:
                low = bits & -bits
                v = low.bit_length() - 1
                neighbours[offset + u] |= 1 << (offset + v)
                bits ^= low
    gram = [[0] * n for _ in range(n)]
    for u in range(n):
        for v in range(n):
            common = (neighbours[u] & neighbours[v]).bit_count()
            same_fibre = int((u % 12) // 4 == (v % 12) // 4)
            gram[u][v] = (
                12 * int(u == v)
                - ((neighbours[u] >> v) & 1)
                + 2
                - same_fibre
                - common
            )
    return tuple(tuple(row) for row in gram), tuple(neighbours)


def rank_f2(matrix: tuple[tuple[int, ...], ...]) -> int:
    rows = []
    for row in matrix:
        packed = 0
        for j, value in enumerate(row):
            if value & 1:
                packed |= 1 << j
        rows.append(packed)
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] >> column & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and (rows[i] >> column) & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def pair_category(u: int, v: int) -> str:
    fu, fv = u // 4, v // 4
    if fu == fv:
        return f"A{fu}"
    missing = ({0, 1, 2} - {fu, fv}).pop()
    return f"B{missing}"


ROW_PATTERNS = (
    (2, 0, 0),
    (0, 2, 0),
    (0, 0, 2),
    (0, 1, 1),
    (1, 0, 1),
    (1, 1, 0),
)


def row_pattern_category(row: tuple[int, int, int]) -> str:
    if 2 in row:
        return f"A{row.index(2)}"
    return f"B{row.index(0)}"


FORMAL_PATTERNS = tuple(
    rows
    for rows in itertools.product(ROW_PATTERNS, repeat=3)
    if all(sum(rows[c][f] for c in range(3)) == 2 for f in FIBRES)
)


def local_pair_data(rows: tuple[int, ...]):
    gram = local_gram(rows)
    supports: dict[str, list[tuple[int, int]]] = {
        f"{letter}{f}": [] for letter in ("A", "B") for f in FIBRES
    }
    target_multiplicities: Counter[str] = Counter()
    for u, v in itertools.combinations(range(N_LOCAL), 2):
        category = pair_category(u, v)
        if gram[u][v] > 0:
            supports[category].append((u, v))
        target_multiplicities[category] += gram[u][v]
    return gram, supports, target_multiplicities


def candidate_count_formula(
    triple: tuple[int, int, int], supports_by_type: list[dict[str, list]]
) -> tuple[int, tuple[tuple[tuple[int, int, int], ...], int], ...]:
    by_pattern = []
    total = 0
    for pattern in FORMAL_PATTERNS:
        count = 1
        for component, row in enumerate(pattern):
            category = row_pattern_category(row)
            count *= len(supports_by_type[triple[component]][category])
        by_pattern.append((pattern, count))
        total += count
    return total, tuple(by_pattern)


def brute_aligned_candidates(
    type_index: int,
    types: list[tuple[int, ...]],
    supports_by_type: list[dict[str, list[tuple[int, int]]]],
) -> tuple[int, dict[str, int], int]:
    triple = (type_index,) * 3
    gram, neighbours = global_gram(triple, types)
    pattern_counts: dict[str, int] = {}
    first_mask = 0
    for pattern in FORMAL_PATTERNS:
        option_lists = []
        for component, row in enumerate(pattern):
            category = row_pattern_category(row)
            option_lists.append(supports_by_type[type_index][category])
        count = 0
        for local_pairs in itertools.product(*option_lists):
            selected = []
            for component, pair in enumerate(local_pairs):
                selected.extend(12 * component + u for u in pair)
            mask = sum(1 << u for u in selected)
            if len(selected) != 6 or mask.bit_count() != 6:
                raise AssertionError("component pairs did not form a six-set")
            for component in range(3):
                if sum(1 for u in selected if u // 12 == component) != 2:
                    raise AssertionError("bad component profile")
            for fibre in range(3):
                if sum(1 for u in selected if (u % 12) // 4 == fibre) != 2:
                    raise AssertionError("bad fibre profile")
            for u in range(36):
                mixed_cut = int((mask >> u) & 1) + (neighbours[u] & mask).bit_count()
                if mixed_cut > 2:
                    raise AssertionError("formula candidate violated mixed cut")
            for u, v in itertools.combinations(selected, 2):
                if gram[u][v] <= 0:
                    raise AssertionError("formula candidate used a zero Gram pair")
            count += 1
            if not first_mask:
                first_mask = mask
        key = "/".join("".join(map(str, row)) for row in pattern)
        pattern_counts[key] = count
    return sum(pattern_counts.values()), pattern_counts, first_mask


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check_discovery_manifest(repo: Path) -> tuple[int, list[str]]:
    manifest = repo / "attempts/wave60-c3-incidence-design/package-manifest.sha256"
    failures = []
    checked = 0
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        expected, rel = line.split(maxsplit=1)
        path = repo / rel.strip()
        checked += 1
        if not path.is_file():
            failures.append(f"missing:{rel.strip()}")
        elif sha256(path) != expected.lower():
            failures.append(f"hash:{rel.strip()}")
    return checked, failures


def find_unsafe_independent_fibre_witness(
    triples: list[tuple[int, int, int]],
    action: dict[tuple[int, ...], tuple[int, ...]],
) -> dict[str, object]:
    maps = tuple(action.values())
    for triple in triples:
        safe = {tuple(sorted(mapping[i] for i in triple)) for mapping in maps}
        for m0 in maps:
            for m1 in maps:
                for m2 in maps:
                    image = tuple(sorted((m0[triple[0]], m1[triple[1]], m2[triple[2]])))
                    if image not in safe:
                        return {
                            "source": list(triple),
                            "unsafe_independent_image": list(image),
                            "safe_orbit_size": len(safe),
                        }
    raise AssertionError("no unsafe independent-fibre witness found")


def reconstruct(repo: Path) -> dict[str, object]:
    normalized, accepted, c4_distribution, types = classify_components()
    if len(normalized) != 216:
        raise AssertionError(len(normalized))
    if len(accepted) != 50:
        raise AssertionError(len(accepted))
    if dict(sorted(c4_distribution.items())) != {2: 6, 4: 30, 6: 14}:
        raise AssertionError(c4_distribution)
    if len(types) != 18:
        raise AssertionError(len(types))

    action = simultaneous_fibre_action(types)
    triples, orbits = triples_and_safe_orbits(len(types), action)
    if len(triples) != 1140 or len(orbits) != 275:
        raise AssertionError((len(triples), len(orbits)))

    gram_by_type = []
    supports_by_type = []
    target_categories_by_type = []
    local_ranks = []
    for rows in types:
        gram, supports, targets = local_pair_data(rows)
        if any(value not in (0, 1, 2, 10) for row in gram for value in row):
            raise AssertionError("unexpected local Gram entry")
        if any(gram[u][u] != 10 for u in range(12)):
            raise AssertionError("bad diagonal")
        if sum(gram[u][v] for u, v in itertools.combinations(range(12), 2)) != 60:
            raise AssertionError("local pair targets do not force sixty columns")
        if any(sum(gram[u][v] for v in range(12) if v != u) != 10 for u in range(12)):
            raise AssertionError("local pair targets do not force row sum ten")
        expected_categories = {
            "A0": 4,
            "A1": 4,
            "A2": 4,
            "B0": 16,
            "B1": 16,
            "B2": 16,
        }
        if dict(targets) != expected_categories:
            raise AssertionError(("bad target category marginals", targets))
        gram_by_type.append(gram)
        supports_by_type.append(supports)
        target_categories_by_type.append(dict(targets))
        local_ranks.append(rank_f2(gram))

    rank_distribution: Counter[int] = Counter()
    candidate_distribution: Counter[int] = Counter()
    candidate_counts = []
    for triple in triples:
        gram, _ = global_gram(triple, types)
        if any(gram[i][i] % 2 for i in range(36)):
            raise AssertionError("target Gram was not alternating mod 2")
        rank = rank_f2(gram)
        rank_distribution[rank] += 1
        count, _ = candidate_count_formula(triple, supports_by_type)
        candidate_counts.append(count)
        candidate_distribution[count] += 1
    expected_ranks = {14: 67, 16: 415, 18: 412, 20: 185, 22: 51, 24: 10}
    if dict(sorted(rank_distribution.items())) != expected_ranks:
        raise AssertionError(rank_distribution)

    discovery_census = json.loads(
        (repo / "attempts/wave60-c3-incidence-design/component-census.json").read_text(
            encoding="utf-8"
        )
    )
    discovery_type4_edges = [
        tuple(edge)
        for edge in discovery_census["component_census"]["types"][4]["edges"]
    ]
    discovery_type4_rows = adjacency_from_edges(12, discovery_type4_edges)
    independent_type4 = {
        canonical_code(rows): i for i, rows in enumerate(types)
    }[canonical_code(discovery_type4_rows)]

    aligned_formula_total, aligned_formula_patterns = candidate_count_formula(
        (independent_type4,) * 3, supports_by_type
    )
    aligned_brute_total, aligned_brute_patterns, first_candidate = (
        brute_aligned_candidates(independent_type4, types, supports_by_type)
    )
    if aligned_formula_total != 20928 or aligned_brute_total != 20928:
        raise AssertionError((aligned_formula_total, aligned_brute_total))
    if len(FORMAL_PATTERNS) != 21 or any(not count for count in aligned_brute_patterns.values()):
        raise AssertionError("formal pattern support")
    formula_pattern_map = {
        "/".join("".join(map(str, row)) for row in pattern): count
        for pattern, count in aligned_formula_patterns
    }
    if formula_pattern_map != aligned_brute_patterns:
        raise AssertionError("formula and brute pattern counts differ")
    if min(candidate_counts) != 15936 or max(candidate_counts) != 27200:
        raise AssertionError((min(candidate_counts), max(candidate_counts)))

    # Hostile mutations: triangle injection, invalid pattern, zero pair,
    # alternating-matrix violation, and the unsafe independent fibre action.
    valid_edges = list(edges_from_adjacency(types[0]))
    triangle_mutation = None
    for centre in range(12):
        ns = [v for v in range(12) if types[0][centre] >> v & 1]
        for a, b in itertools.combinations(ns, 2):
            if not (types[0][a] >> b) & 1:
                triangle_mutation = adjacency_from_edges(
                    12, sorted(valid_edges + [tuple(sorted((a, b)))])
                )
                break
        if triangle_mutation is not None:
            break
    if triangle_mutation is None or passes_component_spec(triangle_mutation):
        raise AssertionError("triangle mutation escaped")

    if ((2, 0, 0), (2, 0, 0), (2, 0, 0)) in FORMAL_PATTERNS:
        raise AssertionError("wrong-fibre pattern escaped")

    zero_pair = next(
        (u, v)
        for u, v in itertools.combinations(range(12), 2)
        if gram_by_type[independent_type4][u][v] == 0
    )
    if any(
        zero_pair in pairs or (zero_pair[1], zero_pair[0]) in pairs
        for pairs in supports_by_type[independent_type4].values()
    ):
        raise AssertionError("zero Gram pair escaped support filter")

    aligned_gram, _ = global_gram((independent_type4,) * 3, types)
    diagonal_mutation = [list(row) for row in aligned_gram]
    diagonal_mutation[0][0] ^= 1
    if not any(diagonal_mutation[i][i] & 1 for i in range(36)):
        raise AssertionError("alternating mutation was not detected")

    for rows in types:
        code = canonical_code(rows)
        for p in (PERMS3[0], PERMS3[-1]):
            image = permute_fibres(rows, p)
            # Undo the fibre permutation before checking the within-fibre code.
            inverse = tuple(p.index(i) for i in FIBRES)
            if canonical_code(permute_fibres(image, inverse)) != code:
                raise AssertionError("canonicalization mutation")

    unsafe_witness = find_unsafe_independent_fibre_witness(triples, action)
    manifest_checked, manifest_failures = check_discovery_manifest(repo)
    if manifest_failures:
        raise AssertionError(manifest_failures)

    aaa_count = sum(
        1
        for pattern in FORMAL_PATTERNS
        if all(row_pattern_category(row).startswith("A") for row in pattern)
    )
    abb_count = sum(
        1
        for pattern in FORMAL_PATTERNS
        if sum(row_pattern_category(row).startswith("A") for row in pattern) == 1
    )
    bbb_count = sum(
        1
        for pattern in FORMAL_PATTERNS
        if all(row_pattern_category(row).startswith("B") for row in pattern)
    )
    if (aaa_count, abb_count, bbb_count) != (6, 9, 6):
        raise AssertionError((aaa_count, abb_count, bbb_count))

    result: dict[str, object] = {
        "format": "wave60-c3-incidence-design-independent-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "conditional exact component classification, safe coordinate orbit "
            "reduction, F2 necessary filter, column support, and marginal reduction"
        ),
        "component_classification": {
            "coordinate_normalized": len(normalized),
            "accepted": len(accepted),
            "accepted_C4_distribution": {
                str(k): v for k, v in sorted(c4_distribution.items())
            },
            "fibre_preserving_types": len(types),
        },
        "safe_coordinate_reduction": {
            "multisets": len(triples),
            "simultaneous_fibre_orbits": len(orbits),
            "orbit_size_distribution": {
                str(k): v for k, v in sorted(Counter(map(len, orbits)).items())
            },
            "unsafe_independent_fibre_witness": unsafe_witness,
            "target_automorphism_assumed": False,
        },
        "f2_filter": {
            "kernel_indicator_span_dimension": 5,
            "rank_B_upper_bound": 31,
            "alternating_target_rank_upper_bound": 30,
            "target_rank_distribution": {
                str(k): v for k, v in sorted(rank_distribution.items())
            },
            "rejected_triples": 0,
            "conclusion": "REDUNDANT",
        },
        "candidate_support": {
            "formal_patterns": len(FORMAL_PATTERNS),
            "pattern_classes": {"AAA": aaa_count, "ABB": abb_count, "BBB": bbb_count},
            "minimum_over_1140": min(candidate_counts),
            "maximum_over_1140": max(candidate_counts),
            "zero_support_triples": sum(count == 0 for count in candidate_counts),
            "count_distribution": {
                str(k): v for k, v in sorted(candidate_distribution.items())
            },
            "aligned_discovery_type_4_maps_to_independent_type": independent_type4,
            "aligned_formula_count": aligned_formula_total,
            "aligned_bruteforce_count": aligned_brute_total,
            "aligned_pattern_counts": aligned_brute_patterns,
            "first_candidate_mask_hex": f"{first_candidate:09x}",
        },
        "marginal_reduction": {
            "local_pair_target_sum_per_component": 60,
            "local_pair_target_row_sums": 10,
            "category_target_multiplicities": target_categories_by_type[0],
            "aligned_ledger_equations": [
                "x_AAA + x_ABB + x_BBB = 60",
                "3*x_AAA + x_ABB = 36",
                "x_ABB = 36 - 3*x_AAA",
                "x_BBB = 24 + 2*x_AAA",
                "0 <= x_AAA <= 12",
            ],
            "tested_discovery_ledgers": [0, 6, 12],
        },
        "hostile_mutations": {
            "triangle_injection_rejected": True,
            "wrong_fibre_pattern_rejected": True,
            "zero_gram_pair_rejected": list(zero_pair),
            "odd_diagonal_target_rejected_as_nonalternating": True,
            "unsafe_independent_fibre_action_not_used": True,
        },
        "discovery_manifest": {
            "entries_checked": manifest_checked,
            "failures": manifest_failures,
        },
        "bounded_search_status": {
            "sat": "UNKNOWN_NON_EVIDENTIARY",
            "local_search": "UNKNOWN_NON_EVIDENTIARY",
            "reason": (
                "no SAT model, checked UNSAT proof, exhaustive certificate, "
                "or emitted local-search best-state matrix is supplied"
            ),
        },
        "endpoint_status": "UNKNOWN",
        "limitations": [
            "No 36 by 60 incidence matrix is constructed.",
            "No one of the 275 safe coordinate orbits is excluded.",
            "The F2 rank condition eliminates no component triple.",
            "Discovery SAT and local-search telemetry remain UNKNOWN.",
            "No compatible Y graph or full strongly regular graph is constructed.",
        ],
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    result = reconstruct(repo)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
