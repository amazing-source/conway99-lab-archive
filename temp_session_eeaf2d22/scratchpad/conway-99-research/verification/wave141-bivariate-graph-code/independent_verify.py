"""Clean-room verifier for the sealed Wave141 bivariate graph-code package.

The verifier never imports or executes Wave141 or Wave21 Python modules.  It
uses the sealed Wave21 JSON table as a prerequisite, extracts the two frozen
deck dictionaries statically with ``ast.literal_eval``, and independently
rebuilds every graph class, deletion deck, signed shell, small transform, and
dimension calculation used below.
"""

from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
from math import comb, prod
from pathlib import Path
from typing import Iterable


N = 99
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts/wave141-bivariate-graph-code"
WAVE21_CODE = ROOT / "attempts/wave21-six-vertex-lp/exact_check.py"
WAVE21_RESULTS = ROOT / "attempts/wave21-six-vertex-lp/exact-results.json"
OUTPUT = HERE / "verification-results.json"

SEALED_DISCOVERY_MANIFEST = (
    "75933cca692f2678bdd74190290b91eb13f6492fce52bc88e896ef7485fe06f8"
)
SEALED_WAVE21 = {
    "exact_check.py":
        "0dd44ca37ca21aeaa757f3b2d7f7f9639907f22b95da39472ed9d836027a94a3",
    "exact-results.json":
        "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_discovery_manifest() -> dict:
    manifest = DISCOVERY / "package-manifest.sha256"
    entries = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, local_name = line.split(" ", 1)
        local_name = local_name.lstrip("*")
        path = DISCOVERY / local_name
        actual = sha256(path)
        entries.append(
            {
                "path": local_name,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "pass": expected == actual,
            }
        )
    manifest_hash = sha256(manifest)
    return {
        "manifest_sha256": manifest_hash,
        "expected_manifest_sha256": SEALED_DISCOVERY_MANIFEST,
        "manifest_pass": manifest_hash == SEALED_DISCOVERY_MANIFEST,
        "entry_count": len(entries),
        "entries_pass": all(entry["pass"] for entry in entries),
        "entries": entries,
    }


def audit_wave21_inputs() -> dict:
    observed = {
        "exact_check.py": sha256(WAVE21_CODE),
        "exact-results.json": sha256(WAVE21_RESULTS),
    }
    return {
        "expected": SEALED_WAVE21,
        "observed": observed,
        "pass": observed == SEALED_WAVE21,
    }


def literal_assignment(path: Path, name: str) -> object:
    """Read a top-level literal assignment without executing supplied code."""

    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        target_name = None
        value = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            target_name = target.id if isinstance(target, ast.Name) else None
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            target_name = node.target.id if isinstance(node.target, ast.Name) else None
            value = node.value
        if target_name == name and value is not None:
            return ast.literal_eval(value)
    raise KeyError(f"literal assignment {name!r} not found")


def graph_edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(combinations(range(order), 2))


@lru_cache(maxsize=None)
def permutation_maps(order: int) -> tuple[tuple[int, ...], ...]:
    edges = graph_edges(order)
    positions = {edge: index for index, edge in enumerate(edges)}
    answer = []
    for permutation in permutations(range(order)):
        answer.append(
            tuple(
                1 << positions[
                    tuple(sorted((permutation[left], permutation[right])))
                ]
                for left, right in edges
            )
        )
    return tuple(answer)


def permute_mask(mask: int, bit_map: tuple[int, ...]) -> int:
    answer = 0
    for index, new_bit in enumerate(bit_map):
        if (mask >> index) & 1:
            answer |= new_bit
    return answer


@lru_cache(maxsize=None)
def canonical_mask(mask: int, order: int) -> int:
    return min(permute_mask(mask, mapping) for mapping in permutation_maps(order))


def locally_admissible(mask: int, order: int) -> bool:
    edges = graph_edges(order)
    positions = {edge: index for index, edge in enumerate(edges)}
    adjacency = [0] * order
    for index, (left, right) in enumerate(edges):
        if (mask >> index) & 1:
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    for left, right in edges:
        common = (adjacency[left] & adjacency[right]).bit_count()
        allowed = 1 if (mask >> positions[(left, right)]) & 1 else 2
        if common > allowed:
            return False
    return True


@lru_cache(maxsize=None)
def admissible_classes(order: int) -> tuple[int, ...]:
    edge_count = len(graph_edges(order))
    remaining = {
        mask
        for mask in range(1 << edge_count)
        if locally_admissible(mask, order)
    }
    representatives = []
    while remaining:
        seed = next(iter(remaining))
        orbit = {
            permute_mask(seed, mapping)
            for mapping in permutation_maps(order)
        }
        representatives.append(min(orbit))
        remaining.difference_update(orbit)
    return tuple(sorted(representatives))


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    old_edges = graph_edges(order)
    new_positions = {
        edge: index
        for index, edge in enumerate(graph_edges(order - 1))
    }
    kept = [vertex for vertex in range(order) if vertex != deleted]
    relabel = {old: new for new, old in enumerate(kept)}
    answer = 0
    for index, (left, right) in enumerate(old_edges):
        if left == deleted or right == deleted or not ((mask >> index) & 1):
            continue
        new_edge = tuple(sorted((relabel[left], relabel[right])))
        answer |= 1 << new_positions[new_edge]
    return answer


def deck_vector(
    mask: int,
    order: int,
    lower_classes: tuple[int, ...],
) -> tuple[int, ...]:
    lower_index = {
        representative: index
        for index, representative in enumerate(lower_classes)
    }
    counts = [0] * len(lower_classes)
    for deleted in range(order):
        card = canonical_mask(delete_vertex(mask, order, deleted), order - 1)
        counts[lower_index[card]] += 1
    return tuple(counts)


def source_columns(
    rows: dict[int, dict[int, int]],
    lower_count: int,
    upper_count: int,
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(
            rows.get(lower, {}).get(upper, 0)
            for lower in range(1, lower_count + 1)
        )
        for upper in range(1, upper_count + 1)
    )


def verify_frozen_alignments(wave21: dict) -> dict:
    alignments = wave21["independent_graph_census"]["source_index_alignment"]
    l_map = tuple(alignments["L_to_canonical_positions_zero_based"])
    m_map = tuple(alignments["M_to_canonical_positions_zero_based"])
    n_map = tuple(alignments["N_to_canonical_positions_zero_based"])
    classes4 = admissible_classes(4)
    classes5 = admissible_classes(5)
    classes6 = admissible_classes(6)

    four_to_five = literal_assignment(WAVE21_CODE, "FOUR_TO_FIVE")
    five_to_six = literal_assignment(WAVE21_CODE, "FIVE_TO_SIX_RAW")
    if not isinstance(four_to_five, dict) or not isinstance(five_to_six, dict):
        raise TypeError("static deck tables are not dictionaries")
    corrected = {
        int(row): {int(column): int(value) for column, value in entries.items()}
        for row, entries in five_to_six.items()
    }
    corrected[7] = dict(corrected[7])
    corrected[7][23] = 1

    four_five_columns = source_columns(four_to_five, 9, 21)
    expected_four_five = []
    for source_upper in range(21):
        canonical_deck = deck_vector(
            classes5[m_map[source_upper]],
            5,
            classes4,
        )
        expected_four_five.append(
            tuple(canonical_deck[l_map[source_lower]] for source_lower in range(9))
        )

    five_six_columns = source_columns(corrected, 21, 62)
    expected_five_six = []
    for source_upper in range(62):
        canonical_deck = deck_vector(
            classes6[n_map[source_upper]],
            6,
            classes5,
        )
        expected_five_six.append(
            tuple(canonical_deck[m_map[source_lower]] for source_lower in range(21))
        )

    source_n3_mask = classes6[n_map[2]]
    edge_set = {
        edge
        for index, edge in enumerate(graph_edges(6))
        if (source_n3_mask >> index) & 1
    }
    triangles = [
        tuple(vertices)
        for vertices in combinations(range(6), 3)
        if all(tuple(sorted(edge)) in edge_set for edge in combinations(vertices, 2))
    ]
    if len(triangles) != 2 or set(triangles[0]) & set(triangles[1]):
        raise AssertionError("source N3 does not split into two triangles")
    cross_edges = [
        (left, right)
        for left in triangles[0]
        for right in triangles[1]
        if tuple(sorted((left, right))) in edge_set
    ]

    return {
        "class_counts": {
            "4": len(classes4),
            "5": len(classes5),
            "6": len(classes6),
        },
        "mapping_bijections": {
            "4": sorted(l_map) == list(range(9)),
            "5": sorted(m_map) == list(range(21)),
            "6": sorted(n_map) == list(range(62)),
        },
        "four_to_five_decks_pass": tuple(expected_four_five) == four_five_columns,
        "five_to_six_decks_pass": tuple(expected_five_six) == five_six_columns,
        "N23_repair": {
            "row": 7,
            "column": 23,
            "corrected_column_sum": sum(
                corrected[row].get(23, 0)
                for row in range(1, 22)
            ),
        },
        "N3": {
            "source_index": 3,
            "canonical_mask": source_n3_mask,
            "edge_count": source_n3_mask.bit_count(),
            "triangles": [list(triangle) for triangle in triangles],
            "cross_edges": [list(edge) for edge in cross_edges],
            "cross_edges_form_matching": (
                len(cross_edges) == 2
                and len({vertex for edge in cross_edges for vertex in edge}) == 4
            ),
            "signed_shell_sign": (-1) ** (6 + source_n3_mask.bit_count()),
        },
        "_classes": (classes4, classes5, classes6),
        "_maps": (l_map, m_map, n_map),
    }


def parse_affine(text: dict[str, str]) -> tuple[Fraction, Fraction]:
    return (
        Fraction(text["constant"]),
        Fraction(text["n3_coefficient"]),
    )


def descend_counts(
    upper_counts: list[tuple[Fraction, Fraction]],
    upper_classes: tuple[int, ...],
    lower_classes: tuple[int, ...],
    upper_order: int,
) -> list[tuple[Fraction, Fraction]]:
    totals = [
        [Fraction(0), Fraction(0)]
        for _ in lower_classes
    ]
    lower_index = {
        representative: index
        for index, representative in enumerate(lower_classes)
    }
    for upper_index, mask in enumerate(upper_classes):
        deck = [0] * len(lower_classes)
        for deleted in range(upper_order):
            card = canonical_mask(
                delete_vertex(mask, upper_order, deleted),
                upper_order - 1,
            )
            deck[lower_index[card]] += 1
        constant, coefficient = upper_counts[upper_index]
        for lower, multiplicity in enumerate(deck):
            totals[lower][0] += multiplicity * constant
            totals[lower][1] += multiplicity * coefficient
    extension_count = N - (upper_order - 1)
    return [
        (constant / extension_count, coefficient / extension_count)
        for constant, coefficient in totals
    ]


def signed_shell(
    order: int,
    classes: tuple[int, ...],
    counts: list[tuple[Fraction, Fraction]],
) -> tuple[Fraction, Fraction]:
    return (
        sum(
            (
                (-1) ** (order + mask.bit_count())
                * count[0]
                for mask, count in zip(classes, counts, strict=True)
            ),
            Fraction(0),
        ),
        sum(
            (
                (-1) ** (order + mask.bit_count())
                * count[1]
                for mask, count in zip(classes, counts, strict=True)
            ),
            Fraction(0),
        ),
    )


def signed_rows_from_wave21(wave21: dict, alignment: dict) -> dict:
    classes4, classes5, classes6 = alignment["_classes"]
    _, _, n_map = alignment["_maps"]
    frozen_forms = wave21["formula_tables"]["six"]
    counts6: list[tuple[Fraction, Fraction] | None] = [None] * len(classes6)
    for source_index, canonical_position in enumerate(n_map, 1):
        counts6[canonical_position] = parse_affine(frozen_forms[str(source_index)])
    if any(count is None for count in counts6):
        raise AssertionError("six-class affine alignment is incomplete")
    exact_counts6 = [count for count in counts6 if count is not None]

    class_by_order: dict[int, tuple[int, ...]] = {
        6: classes6,
        5: classes5,
        4: classes4,
    }
    counts_by_order: dict[int, list[tuple[Fraction, Fraction]]] = {
        6: exact_counts6
    }
    for upper_order in range(6, 0, -1):
        lower_order = upper_order - 1
        if lower_order not in class_by_order:
            class_by_order[lower_order] = admissible_classes(lower_order)
        counts_by_order[lower_order] = descend_counts(
            counts_by_order[upper_order],
            class_by_order[upper_order],
            class_by_order[lower_order],
            upper_order,
        )

    shells = {
        order: signed_shell(
            order,
            class_by_order[order],
            counts_by_order[order],
        )
        for order in range(7)
    }
    expected = {
        0: (Fraction(1), Fraction(0)),
        1: (Fraction(-99), Fraction(0)),
        2: (Fraction(3465), Fraction(0)),
        3: (Fraction(-56595), Fraction(0)),
        4: (Fraction(462924), Fraction(0)),
        5: (Fraction(-1821204), Fraction(0)),
        6: (Fraction(2024484), Fraction(512, 3)),
    }
    if shells != expected:
        raise AssertionError(f"signed-shell replay drift: {shells}")

    positive_constant = Fraction(0)
    negative_constant = Fraction(0)
    positive_slope = Fraction(0)
    negative_slope = Fraction(0)
    for mask, (constant, slope) in zip(classes6, exact_counts6, strict=True):
        sign = (-1) ** (6 + mask.bit_count())
        signed_constant = sign * constant
        signed_slope = sign * slope
        if signed_constant >= 0:
            positive_constant += signed_constant
        else:
            negative_constant += signed_constant
        if signed_slope >= 0:
            positive_slope += signed_slope
        else:
            negative_slope += signed_slope

    source_n3 = parse_affine(frozen_forms["3"])
    return {
        "shells": {
            str(order): {
                "constant": str(constant),
                "n3_coefficient": str(coefficient),
            }
            for order, (constant, coefficient) in shells.items()
        },
        "subset_identity": "q(A 1_S)=|S|+e(G[S]) mod 2",
        "affine_cancellation": {
            "positive_constant_sum": str(positive_constant),
            "negative_constant_sum": str(negative_constant),
            "constant_total": str(positive_constant + negative_constant),
            "positive_slope_sum": str(positive_slope),
            "negative_slope_sum": str(negative_slope),
            "slope_total": str(positive_slope + negative_slope),
        },
        "N3_source_formula": {
            "constant": str(source_n3[0]),
            "n3_coefficient": str(source_n3[1]),
            "sign": alignment["N3"]["signed_shell_sign"],
        },
        "all_count_totals": {
            str(order): {
                "constant": str(sum(value[0] for value in counts)),
                "coefficient": str(sum(value[1] for value in counts)),
                "expected_binomial": str(comb(N, order)),
            }
            for order, counts in counts_by_order.items()
        },
    }


def krawtchouk(n: int, degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * comb(weight, overlap)
        * comb(n - weight, degree - overlap)
        for overlap in range(
            max(0, degree - (n - weight)),
            min(weight, degree) + 1,
        )
    )


def binary_rank(rows: list[int], width: int) -> int:
    work = rows[:]
    rank = 0
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(rank, len(work))
                if (work[row] >> column) & 1
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for row in range(len(work)):
            if row != rank and ((work[row] >> column) & 1):
                work[row] ^= work[rank]
        rank += 1
    return rank


def matrix_vector_mod2(rows: list[int], vector: int) -> int:
    return sum(
        (((row & vector).bit_count() & 1) << index)
        for index, row in enumerate(rows)
    )


def bivariate_table(rows: list[int], n: int) -> list[list[int]]:
    table = [[0] * (n + 1) for _ in range(n + 1)]
    for vector in range(1 << n):
        output = matrix_vector_mod2(rows, vector)
        table[vector.bit_count()][output.bit_count()] += 1
    return table


def exact_transform_audit(rows: list[int], n: int) -> dict:
    table = bivariate_table(rows, n)
    rank = binary_rank(rows, n)
    image = Counter(
        matrix_vector_mod2(rows, vector).bit_count()
        for vector in range(1 << n)
    )
    # The enumeration above counts each image word |ker| times.
    image_enumerator = {
        weight: count // (1 << (n - rank))
        for weight, count in image.items()
    }
    transform_pass = True
    for i in range(n + 1):
        for j in range(n + 1):
            numerator = sum(
                table[a][b]
                * krawtchouk(n, i, b)
                * krawtchouk(n, j, a)
                for a in range(n + 1)
                for b in range(n + 1)
            )
            if numerator != (1 << n) * table[i][j]:
                transform_pass = False
    return {
        "order": n,
        "rank": rank,
        "table": table,
        "input_marginals_pass": all(
            sum(table[i]) == comb(n, i)
            for i in range(n + 1)
        ),
        "output_marginals_pass": all(
            sum(table[i][j] for i in range(n + 1))
            == (1 << (n - rank)) * image_enumerator.get(j, 0)
            for j in range(n + 1)
        ),
        "output_even_pass": all(
            table[i][j] == 0
            for i in range(n + 1)
            for j in range(1, n + 1, 2)
        ),
        "input_complement_pass": all(
            table[i] == table[n - i]
            for i in range(n + 1)
        ),
        "transform_pass": transform_pass,
    }


def complete_graph_control(n: int) -> list[int]:
    mask = (1 << n) - 1
    return [mask ^ (1 << index) for index in range(n)]


def rational_rank(rows: list[list[Fraction]]) -> int:
    if not rows:
        return 0
    work = [row[:] for row in rows]
    width = len(work[0])
    rank = 0
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(rank, len(work))
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [value / pivot_value for value in work[rank]]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                left - factor * right
                for left, right in zip(work[row], work[rank], strict=True)
            ]
        rank += 1
    return rank


def small_transform_constraint_rank(n: int, complement_reduced: bool) -> int:
    outputs = tuple(range(0, n + 1, 2))
    inputs = (
        tuple(range((n + 1) // 2))
        if complement_reduced
        else tuple(range(n + 1))
    )
    variables = tuple(product(inputs, outputs))
    position = {pair: index for index, pair in enumerate(variables)}
    equations = []
    for target_i in range(n + 1):
        for target_j in range(n + 1):
            row = [Fraction(0)] * len(variables)
            if target_j % 2 == 0:
                lhs_i = min(target_i, n - target_i) if complement_reduced else target_i
                row[position[(lhs_i, target_j)]] += 1
            for source_i, source_j in variables:
                multiplicity = 2 if complement_reduced else 1
                coefficient = krawtchouk(n, target_i, source_j)
                if complement_reduced:
                    coefficient *= (
                        krawtchouk(n, target_j, source_i)
                        + krawtchouk(n, target_j, n - source_i)
                    )
                    multiplicity = 1
                else:
                    coefficient *= krawtchouk(n, target_j, source_i)
                row[position[(source_i, source_j)]] -= Fraction(
                    multiplicity * coefficient,
                    1 << n,
                )
            equations.append(row)
    return rational_rank(equations)


def bivariate_and_d8_results() -> dict:
    controls = []
    for n in (3, 5):
        rows = complete_graph_control(n)
        mask = (1 << n) - 1
        symmetric = all(
            ((rows[i] >> j) & 1) == ((rows[j] >> i) & 1)
            for i in range(n)
            for j in range(n)
        )
        square = [
            matrix_vector_mod2(rows, rows[index])
            for index in range(n)
        ]
        audit = exact_transform_audit(rows, n)
        invariant_dimension = ((n + 1) ** 2 + 2 * (n + 1)) // 8
        allowed_dimension = (n + 1) * ((n + 1) // 2)
        complement_dimension = allowed_dimension // 2
        audit.update(
            {
                "matrix": f"adjacency(K{n})",
                "symmetric": symmetric,
                "even_rows": all(row.bit_count() % 2 == 0 for row in rows),
                "idempotent_mod_2": square == rows,
                "kills_one": matrix_vector_mod2(rows, mask) == 0,
                "D8_invariant_dimension": invariant_dimension,
                "direct_transform_rank_even_output": (
                    small_transform_constraint_rank(n, False)
                ),
                "expected_transform_rank_even_output": (
                    allowed_dimension - invariant_dimension
                ),
                "direct_transform_rank_after_complement": (
                    small_transform_constraint_rank(n, True)
                ),
                "expected_transform_rank_after_complement": (
                    complement_dimension - invariant_dimension
                ),
            }
        )
        controls.append(audit)

    side = N + 1
    burnside_traces = {
        "identity": side * side,
        "quarter_turn": 0,
        "half_turn": 0,
        "three_quarter_turn": 0,
        "axis_reflection_1": 0,
        "axis_reflection_2": 0,
        "diagonal_reflection_1": side,
        "diagonal_reflection_2": side,
    }
    invariant = sum(burnside_traces.values()) // 8
    output_even_dimension = side * (side // 2)
    complement_dimension = output_even_dimension // 2
    return {
        "definition": "B[i,j]=#{x: wt(x)=i, wt(Ax)=j}",
        "marginals_and_symmetries": {
            "input": "sum_j B[i,j]=binom(n,i)",
            "output": "sum_i B[i,j]=2^(n-rank(A))*A_j",
            "output_even": "B[i,j]=0 for odd j",
            "input_complement": "B[i,j]=B[n-i,j] when A1=0",
            "transform": (
                "B[i,j]=2^-n sum_(a,b) K_i(b) K_j(a) B[a,b]"
            ),
        },
        "small_controls": controls,
        "D8": {
            "side": side,
            "Burnside_traces": burnside_traces,
            "invariant_dimension": invariant,
            "output_even_dimension": output_even_dimension,
            "combined_equality_rank": output_even_dimension - invariant,
            "input_complement_dimension": complement_dimension,
            "additional_rank_after_input_complement": (
                complement_dimension - invariant
            ),
        },
    }


def exact_low_rows() -> dict:
    edges = N * 14 // 2
    nonedges = comb(N, 2) - edges

    triangles = N * 14 * 1 // 6
    induced_paths = N * comb(14, 2) - 3 * triangles
    one_edge_total = edges * 72
    one_edge_triple_common = edges * 12
    one_edge_no_triple_common = one_edge_total - one_edge_triple_common
    independent_total = (
        comb(N, 3)
        - triangles
        - induced_paths
        - one_edge_total
    )
    independent_with_common = N * (comb(7, 3) * (2**3))
    independent_without_common = independent_total - independent_with_common

    row3 = {
        "30": independent_without_common,
        "32": one_edge_no_triple_common,
        "34": induced_paths + independent_with_common,
        "36": triangles + one_edge_triple_common,
    }
    expected = {
        "0": {"0": 1},
        "1": {"14": N},
        "2": {"24": nonedges, "26": edges},
        "3": row3,
    }
    if any(
        sum(row.values()) != comb(N, int(input_weight))
        for input_weight, row in expected.items()
    ):
        raise AssertionError("low-row marginal failed")
    return {
        "rows": expected,
        "triple_derivation": {
            "triangles": triangles,
            "induced_paths": induced_paths,
            "one_edge_total": one_edge_total,
            "one_edge_with_common_neighbor": one_edge_triple_common,
            "independent_total": independent_total,
            "independent_with_common_neighbor": independent_with_common,
        },
        "exactness_boundary": (
            "Rows 0 through 3 are exact.  For larger subsets, full output "
            "weight generally needs embedding/common-neighbor data; only "
            "the signed mod-4 shell is derived here."
        ),
    }


def n3_output_weight(alignment: dict) -> dict:
    # Inside N3 the degrees are 3,3,3,3,2,2.  An outside vertex cannot meet
    # an edge of either triangle, so it has at most two neighbors in N3.
    inside_degree_distribution = {3: 4, 2: 2}
    outside_neighbor_sum = 14 * 6 - 2 * 8
    all_pair_moment = 6 * 5 - 8
    inside_pair_moment = 4 * comb(3, 2) + 2 * comb(2, 2)
    outside_pair_moment = all_pair_moment - inside_pair_moment
    outside_two = outside_pair_moment
    outside_one = outside_neighbor_sum - 2 * outside_two
    outside_zero = (N - 6) - outside_one - outside_two
    output_weight = 4 + outside_one
    return {
        "inside_degree_distribution": {
            str(key): value
            for key, value in inside_degree_distribution.items()
        },
        "outside_neighbor_profile": {
            "0": outside_zero,
            "1": outside_one,
            "2": outside_two,
        },
        "output_weight_wt_A1S": output_weight,
        "consequence": "Each N3 six-set contributes to B[6,56], so B[6,56]>=n3.",
        "N3_sign_matches": (-1) ** (output_weight // 2)
        == alignment["N3"]["signed_shell_sign"],
    }


def build_results() -> dict:
    package = audit_discovery_manifest()
    wave21_audit = audit_wave21_inputs()
    if not package["manifest_pass"] or not package["entries_pass"]:
        raise AssertionError("sealed Wave141 package hash audit failed")
    if not wave21_audit["pass"]:
        raise AssertionError("frozen Wave21 prerequisite drift")

    wave21 = json.loads(WAVE21_RESULTS.read_text(encoding="utf-8"))
    alignment = verify_frozen_alignments(wave21)
    signed = signed_rows_from_wave21(wave21, alignment)
    bivariate = bivariate_and_d8_results()
    low_rows = exact_low_rows()
    n3_detail = n3_output_weight(alignment)

    # Remove internal non-JSON routing objects after all independent checks.
    public_alignment = {
        key: value
        for key, value in alignment.items()
        if not key.startswith("_")
    }

    rational_upper = Fraction(
        3 * (comb(N, 6) - 2024484),
        512,
    )
    multiple_three_upper = (int(rational_upper) // 3) * 3

    discovery_results = json.loads(
        (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
    )
    discovery_projection = {
        "D8_invariant_dimension": discovery_results[
            "D8_equality_space"
        ]["invariant_dimension"],
        "D8_equality_rank": discovery_results[
            "D8_equality_space"
        ]["combined_output_parity_and_transform_rank"],
        "D8_reduced_rank": discovery_results[
            "D8_equality_space"
        ]["rank_after_input_complement_reduction"],
        "low_rows": discovery_results["exact_low_input_rows"],
        "signed_rows": discovery_results["signed_input_rows_S0_through_S6"],
        "nonnegative_multiple_three_upper": discovery_results[
            "elementary_nonnegativity_only_bound"
        ]["multiple_of_3_upper"],
    }
    independent_projection = {
        "D8_invariant_dimension": bivariate["D8"]["invariant_dimension"],
        "D8_equality_rank": bivariate["D8"]["combined_equality_rank"],
        "D8_reduced_rank": bivariate["D8"][
            "additional_rank_after_input_complement"
        ],
        "low_rows": low_rows["rows"],
        "signed_rows": [
            {
                "input_weight": str(order),
                **signed["shells"][str(order)],
            }
            for order in range(7)
        ],
        "nonnegative_multiple_three_upper": multiple_three_upper,
    }

    return {
        "format": "wave141-independent-verification-v1",
        "verdict": "PASS",
        "sealed_package": package,
        "wave21_prerequisite": wave21_audit,
        "bivariate_transform": bivariate,
        "locally_admissible_alignment": public_alignment,
        "signed_rows": signed,
        "exact_low_rows": low_rows,
        "N3_output_detail": n3_detail,
        "nonnegativity_only_bound": {
            "rational_upper": str(rational_upper),
            "integer_upper": int(rational_upper),
            "multiple_of_3_upper": multiple_three_upper,
            "known_upper": 4158,
            "improves_known_upper": False,
        },
        "discovery_exact_projection_matches": (
            discovery_projection == independent_projection
        ),
        "numerical_scout": {
            "evidentiary_status": "NONE",
            "accepted_as_feasible": False,
            "accepted_as_infeasible": False,
            "reason": (
                "No exact rational primal or Farkas dual; active-row points "
                "violate inactive transform equations and later statuses "
                "are floating UNKNOWN."
            ),
        },
        "scope_boundary": {
            "full_output_weight_by_six_vertex_class": "NOT_DERIVED",
            "signed_output_shell_by_six_vertex_class": "VERIFIED",
            "formal_rational_feasibility": "UNKNOWN",
            "formal_integral_feasibility": "UNKNOWN",
            "graph_realizability": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    result = build_results()
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "sealed_manifest_pass": result["sealed_package"][
                    "manifest_pass"
                ],
                "discovery_exact_projection_matches": result[
                    "discovery_exact_projection_matches"
                ],
                "D8_dimension": result["bivariate_transform"]["D8"][
                    "invariant_dimension"
                ],
                "S6": result["signed_rows"]["shells"]["6"],
                "Conway_99": result["scope_boundary"]["Conway_99"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
