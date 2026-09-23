#!/usr/bin/env python3
"""Derive the all-n3 cube/Wagner four-root covariance inequality.

Only standard-library code is used.  No discovery Python is imported or
executed.  The Wave43 checker is parsed as static source to confirm the
independent N_9 transcription, and the Wave152 target JSON is consulted only
after the symbolic inequality has been reconstructed.
"""

from __future__ import annotations

import argparse
import ast
import ctypes
import hashlib
import itertools
import json
import math
import time
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TARGET = ROOT / "attempts" / "wave152-four-root-order8" / "simplified-mask12-cut-2.json"
SIX_SOURCE = ROOT / "verification" / "wave43-seven-deck-endpoint" / "independent_check.py"
OUTPUT = HERE / "exact-results.json"

TARGET_SHA256 = "8bed853973bb5964a3a9d4f37c8b808e6149701c00fd62c7e607f5e543cdb965"
SIX_SOURCE_SHA256 = "324a4b84c081c8d2ad8a6a11bae45e0327c03ee2158036156c27efa66fcf790b"

N = 99
K = 14
LAMBDA = 1
MU = 2
ROOT_MASK = 12
FLAG_PLUS = 21812
FLAG_MINUS = 22708
N9_MASK = 1884
CUBE_MASK = 2022000
WAGNER_MASK = 5683824
ENDPOINT_N3 = 4158
MIN_FREE_PERCENT = 15.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def memory_sample(label: str) -> dict[str, float | str]:
    class MemoryStatusEx(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("available_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("available_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
        "GlobalMemoryStatusEx failed",
    )
    percent = 100.0 * status.available_phys / status.total_phys
    require(percent >= MIN_FREE_PERCENT, f"free physical memory is {percent:.2f}%")
    return {
        "label": label,
        "free_physical_memory_percent": percent,
        "available_physical_gib": status.available_phys / 2**30,
        "total_physical_gib": status.total_phys / 2**30,
    }


@lru_cache(maxsize=None)
def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


@lru_cache(maxsize=None)
def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def adjacency_rows(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for position, (left, right) in enumerate(edges(order)):
        if mask >> position & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def locally_admissible(mask: int, order: int) -> bool:
    rows = adjacency_rows(mask, order)
    for left in range(order):
        for right in range(left + 1, order):
            common = (rows[left] & rows[right]).bit_count()
            if rows[left] >> right & 1:
                if common > LAMBDA:
                    return False
            elif common > MU:
                return False
    return True


def transform_mask(
    mask: int, order: int, permutation: Sequence[int]
) -> int:
    positions = edge_positions(order)
    result = 0
    for position, (left, right) in enumerate(edges(order)):
        if mask >> position & 1:
            image = tuple(sorted((permutation[left], permutation[right])))
            result |= 1 << positions[image]
    return result


@lru_cache(maxsize=None)
def canonical_unrooted(mask: int, order: int) -> int:
    """Complete canonicalization using the invariant degree partition."""
    rows = adjacency_rows(mask, order)
    groups: dict[int, list[int]] = {}
    for vertex, row in enumerate(rows):
        groups.setdefault(row.bit_count(), []).append(vertex)
    target_start = 0
    cells: list[tuple[dict[int, int], ...]] = []
    for degree in sorted(groups):
        vertices = groups[degree]
        targets = tuple(range(target_start, target_start + len(vertices)))
        target_start += len(vertices)
        cells.append(
            tuple(
                dict(zip(vertices, target_order, strict=True))
                for target_order in itertools.permutations(targets)
            )
        )
    best: int | None = None
    for choices in itertools.product(*cells):
        permutation = [0] * order
        for mapping in choices:
            for source, target in mapping.items():
                permutation[source] = target
        image = transform_mask(mask, order, permutation)
        best = image if best is None else min(best, image)
    require(best is not None, "empty canonicalization")
    return best


@lru_cache(maxsize=None)
def canonical_unrooted_full(mask: int, order: int) -> int:
    """Minimum over every relabelling, matching the Wave43 mask convention."""
    return min(
        transform_mask(mask, order, permutation)
        for permutation in itertools.permutations(range(order))
    )


def induced_mask(
    graph_mask: int, graph_order: int, chosen_vertices: Sequence[int]
) -> int:
    positions = edge_positions(graph_order)
    result = 0
    target_position = 0
    for left_index, left in enumerate(chosen_vertices):
        for right in chosen_vertices[left_index + 1 :]:
            if graph_mask >> positions[tuple(sorted((left, right)))] & 1:
                result |= 1 << target_position
            target_position += 1
    return result


def canonical_flag(mask: int) -> int:
    swapped = transform_mask(mask, 6, (0, 1, 2, 3, 5, 4))
    return min(mask, swapped)


def flag_value(mask: int) -> int:
    return {FLAG_PLUS: 1, FLAG_MINUS: -1}.get(canonical_flag(mask), 0)


def flag_orientations(mask: int) -> tuple[int, ...]:
    swapped = transform_mask(mask, 6, (0, 1, 2, 3, 5, 4))
    return tuple(sorted({mask, swapped}))


@lru_cache(maxsize=None)
def covering_pair_indices(
    complement_size: int,
) -> tuple[tuple[int, int], ...]:
    pairs = tuple(itertools.combinations(range(complement_size), 2))
    return tuple(
        (left, right)
        for left, first in enumerate(pairs)
        for right, second in enumerate(pairs)
        if len(set(first).union(second)) == complement_size
    )


def class_coefficients(graph_mask: int, order: int) -> tuple[int, int]:
    """Return the first- and second-moment coefficients for one class."""
    first = 0
    quadratic = 0
    vertices = tuple(range(order))
    product_pairs = covering_pair_indices(order - 4)
    for roots in itertools.permutations(vertices, 4):
        if induced_mask(graph_mask, order, roots) != ROOT_MASK:
            continue
        complement = tuple(vertex for vertex in vertices if vertex not in roots)
        free_pairs = tuple(itertools.combinations(complement, 2))
        values = [
            flag_value(induced_mask(graph_mask, order, roots + free_pair))
            for free_pair in free_pairs
        ]
        if order == 6:
            require(len(values) == 1, "order-six complement changed")
            first += values[0]
        quadratic += sum(
            values[left] * values[right] for left, right in product_pairs
        )
    return first, quadratic


def embed_flag_constraint(
    flag_mask: int, chosen: Sequence[int], order: int
) -> tuple[int, int]:
    """Return (present edges, all edges whose presence is fixed)."""
    require(len(chosen) == 6, "a flag constraint needs six vertices")
    positions = edge_positions(order)
    present = 0
    known = 0
    for local_position, (left, right) in enumerate(edges(6)):
        global_edge = tuple(sorted((chosen[left], chosen[right])))
        bit = 1 << positions[global_edge]
        known |= bit
        if flag_mask >> local_position & 1:
            present |= bit
    return present, known


def merge_constraints(
    left: tuple[int, int], right: tuple[int, int], order: int
) -> tuple[int, ...]:
    left_present, left_known = left
    right_present, right_known = right
    if (left_present ^ right_present) & (left_known & right_known):
        return ()
    present = left_present | right_present
    known = left_known | right_known
    unknown_positions = [
        position
        for position in range(math.comb(order, 2))
        if not (known >> position & 1)
    ]
    completions = []
    for extension in range(1 << len(unknown_positions)):
        graph = present
        for bit, position in enumerate(unknown_positions):
            if extension >> bit & 1:
                graph |= 1 << position
        if locally_admissible(graph, order):
            completions.append(graph)
    return tuple(completions)


def candidate_classes(order: int) -> tuple[int, ...]:
    """Exhaust all classes that can receive a nonzero flag product."""
    oriented = [
        (actual, sign)
        for flag, sign in ((FLAG_PLUS, 1), (FLAG_MINUS, -1))
        for actual in flag_orientations(flag)
    ]
    if order == 6:
        return tuple(
            sorted(
                {
                    canonical_unrooted_full(actual, 6)
                    for actual, _ in oriented
                    if locally_admissible(actual, 6)
                }
            )
        )

    complement = tuple(range(4, order))
    free_pairs = tuple(itertools.combinations(complement, 2))
    classes: set[int] = set()
    for left_index, right_index in covering_pair_indices(len(complement)):
        left_pair = free_pairs[left_index]
        right_pair = free_pairs[right_index]
        for left_flag, _ in oriented:
            left_constraint = embed_flag_constraint(
                left_flag, (0, 1, 2, 3) + left_pair, order
            )
            for right_flag, _ in oriented:
                right_constraint = embed_flag_constraint(
                    right_flag, (0, 1, 2, 3) + right_pair, order
                )
                for graph in merge_constraints(
                    left_constraint, right_constraint, order
                ):
                    classes.add(canonical_unrooted(graph, order))
    return tuple(sorted(classes))


def model_mask(order: int, graph_edges: Iterable[tuple[int, int]]) -> int:
    positions = edge_positions(order)
    result = 0
    for edge in graph_edges:
        result |= 1 << positions[tuple(sorted(edge))]
    return result


def named_order8_masks() -> dict[str, int]:
    cube = model_mask(
        8,
        (
            (vertex, vertex ^ (1 << bit))
            for vertex in range(8)
            for bit in range(3)
            if vertex < (vertex ^ (1 << bit))
        ),
    )
    wagner = model_mask(
        8,
        itertools.chain(
            ((vertex, (vertex + 1) % 8) for vertex in range(8)),
            ((vertex, vertex + 4) for vertex in range(4)),
        ),
    )
    return {
        "cube": canonical_unrooted(cube, 8),
        "wagner_mobius_ladder": canonical_unrooted(wagner, 8),
    }


def root_embedding_derivation() -> dict[str, int]:
    """Count ordered induced 2K2 roots directly from SRG parameters."""
    ordered_first_edges = N * K
    common_nonneighbors = N - (2 * K - LAMBDA)
    adjacent_to_unique_common_neighbor = K - 2
    remaining = common_nonneighbors - adjacent_to_unique_common_neighbor
    internal_degree_if_adjacent = K - 3
    internal_degree_if_not = K - 4
    ordered_second_edges = (
        adjacent_to_unique_common_neighbor * internal_degree_if_adjacent
        + remaining * internal_degree_if_not
    )
    root_embeddings = ordered_first_edges * ordered_second_edges
    return {
        "ordered_first_edges": ordered_first_edges,
        "common_nonneighbors_per_first_edge": common_nonneighbors,
        "common_nonneighbors_adjacent_to_unique_common_neighbor":
            adjacent_to_unique_common_neighbor,
        "remaining_common_nonneighbors": remaining,
        "internal_degree_if_adjacent": internal_degree_if_adjacent,
        "internal_degree_if_not_adjacent": internal_degree_if_not,
        "ordered_second_edges_per_first_edge": ordered_second_edges,
        "root_embedding_count": root_embeddings,
    }


def static_n9_formula_check() -> dict[str, object]:
    """Parse, but do not execute, the frozen Wave43 six-formula source."""
    source = SIX_SOURCE.read_text(encoding="utf-8")
    module = ast.parse(source)
    masks: tuple[int, ...] | None = None
    formula_text: str | None = None
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SOURCE_N_MASKS"
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            masks = tuple(map(int, value))
        if isinstance(node, ast.FunctionDef) and node.name == "six_formulae":
            returns = [
                child for child in ast.walk(node) if isinstance(child, ast.Return)
            ]
            require(len(returns) == 1, "six_formulae return structure changed")
            returned = returns[0].value
            require(isinstance(returned, ast.Tuple), "six_formulae is not a tuple")
            require(len(returned.elts) == 62, "six_formulae length changed")
            formula_text = ast.unparse(returned.elts[8])
    require(masks is not None and len(masks) == 62, "SOURCE_N_MASKS missing")
    require(masks[8] == N9_MASK, "N_9 mask changed")
    require(formula_text == "A(Q(b, 4), -1)", f"N_9 formula changed: {formula_text}")
    constant = Fraction(N * K * (K - 2) * (K - 4), 4)
    require(constant.denominator == 1, "N_9 constant is not integral")
    return {
        "source_index_one_based": 9,
        "canonical_mask": masks[8],
        "static_ast_formula": formula_text,
        "expanded_formula": f"{constant.numerator} - n3",
        "constant": constant.numerator,
        "n3_coefficient": -1,
    }


def derive() -> dict[str, object]:
    started = time.time()
    samples = [memory_sample("start")]
    require(sha256_file(TARGET) == TARGET_SHA256, "target hash changed")
    require(sha256_file(SIX_SOURCE) == SIX_SOURCE_SHA256, "six-source hash changed")

    require(canonical_flag(FLAG_PLUS) == FLAG_PLUS, "plus flag is not canonical")
    require(canonical_flag(FLAG_MINUS) == FLAG_MINUS, "minus flag is not canonical")
    require(canonical_unrooted_full(FLAG_PLUS, 6) == N9_MASK, "plus flag is not N_9")
    require(canonical_unrooted_full(FLAG_MINUS, 6) == N9_MASK, "minus flag is not N_9")
    require(locally_admissible(FLAG_PLUS, 6), "plus flag is inadmissible")
    require(locally_admissible(FLAG_MINUS, 6), "minus flag is inadmissible")

    n9_formula = static_n9_formula_check()
    root_count = root_embedding_derivation()
    require(root_count["root_embedding_count"] == 1_014_552, "root count changed")
    samples.append(memory_sample("fixed_data_derived"))

    candidates = {
        order: candidate_classes(order) for order in (6, 7, 8)
    }
    samples.append(memory_sample("candidate_unions_enumerated"))
    coefficients = {
        order: {
            mask: class_coefficients(mask, order)
            for mask in candidates[order]
        }
        for order in (6, 7, 8)
    }
    nonzero_first = {
        order: {
            mask: first
            for mask, (first, _) in coefficients[order].items()
            if first
        }
        for order in (6, 7, 8)
    }
    nonzero_quadratic = {
        order: {
            mask: quadratic
            for mask, (_, quadratic) in coefficients[order].items()
            if quadratic
        }
        for order in (6, 7, 8)
    }
    require(nonzero_first[6] == {}, "the first moment does not cancel")
    require(
        nonzero_quadratic[6] == {N9_MASK: 8},
        f"unexpected order-six terms: {nonzero_quadratic[6]}",
    )
    require(nonzero_quadratic[7] == {}, "unexpected order-seven terms")
    require(
        nonzero_quadratic[8] == {CUBE_MASK: 96, WAGNER_MASK: -32},
        f"unexpected order-eight terms: {nonzero_quadratic[8]}",
    )
    named_masks = named_order8_masks()
    require(named_masks == {
        "cube": CUBE_MASK,
        "wagner_mobius_ladder": WAGNER_MASK,
    }, "named order-eight mask identification failed")
    samples.append(memory_sample("coefficients_derived"))

    # R * (8*N9 + 96*Cube - 32*Wagner) >= 0, with first moment zero.
    raw_gcd_without_root_count = math.gcd(8, 96, 32)
    require(raw_gcd_without_root_count == 8, "symbolic gcd changed")
    symbolic = {
        "integer_form": "41580 - n3 + 12*cube8 - 4*wagner8 >= 0",
        "equivalent_upper_form":
            "n3 <= 41580 + 12*cube8 - 4*wagner8",
        "six_count_form": "N9 + 12*cube8 - 4*wagner8 >= 0",
        "N9": "41580 - n3",
        "coefficient_n3": -1,
        "coefficient_cube8": 12,
        "coefficient_wagner8": -4,
        "constant": 41580,
    }
    endpoint_n9 = int(n9_formula["constant"]) - ENDPOINT_N3
    require(endpoint_n9 == 37422, "endpoint N_9 changed")
    endpoint_integer = {
        "integer_form": "37422 + 12*cube8 - 4*wagner8 >= 0",
        "primitive_form": "18711 + 6*cube8 - 2*wagner8 >= 0",
        "constant_before_extra_endpoint_gcd": endpoint_n9,
        "primitive_constant": endpoint_n9 // 2,
        "extra_endpoint_gcd": 2,
    }

    # Only now compare with the stored endpoint target.
    target = json.loads(TARGET.read_text(encoding="utf-8"))
    stored_cut = target["cut"]
    stored_terms = {
        int(record["canonical_mask"]): int(record["coefficient"])
        for record in stored_cut["order8_coefficients"]
    }
    require(int(stored_cut["root_mask"]) == ROOT_MASK, "stored root changed")
    require(
        list(map(int, target["derivation"]["flag_masks"]))
        == [FLAG_PLUS, FLAG_MINUS],
        "stored flag pair changed",
    )
    require(int(stored_cut["root_embedding_count"]) == root_count["root_embedding_count"],
            "stored root count differs")
    require(int(stored_cut["constant"]) == endpoint_n9 // 2,
            "stored endpoint constant differs")
    require(stored_terms == {CUBE_MASK: 6, WAGNER_MASK: -2},
            "stored endpoint order-eight terms differ")
    require(stored_cut["order7_coefficients"] == [], "stored order-seven terms differ")
    require(int(stored_cut["projected_first_moment"]) == 0,
            "stored projected first moment differs")
    require(int(stored_cut["order6_quadratic_nonzeros"]) == 1,
            "stored order-six support differs")
    expected_endpoint_divisor = root_count["root_embedding_count"] * 16
    require(int(stored_cut["primitive_divisor"]) == expected_endpoint_divisor,
            "stored endpoint primitive divisor differs")

    # The inequality plus nonnegativity alone permits n3=4158 at cube=wagner=0.
    endpoint_zero_assignment_lhs = 41580 - ENDPOINT_N3
    require(endpoint_zero_assignment_lhs > 0, "endpoint zero assignment was excluded")
    samples.append(memory_sample("complete"))
    mathematical_certificate = {
        "root_embedding_derivation": root_count,
        "six_set_formula": n9_formula,
        "candidate_union_masks": {
            str(order): list(candidates[order]) for order in (6, 7, 8)
        },
        "first_moment_nonzeros": {
            str(order): {
                str(mask): value
                for mask, value in nonzero_first[order].items()
            }
            for order in (6, 7, 8)
        },
        "quadratic_coefficients_before_division": {
            str(order): {
                str(mask): value
                for mask, value in nonzero_quadratic[order].items()
            }
            for order in (6, 7, 8)
        },
        "named_order8_masks": named_masks,
        "covariance_identity_before_division": (
            "1014552 * (8*N9 + 96*cube8 - 32*wagner8) - 0^2 >= 0"
        ),
        "symbolic_inequality": symbolic,
        "endpoint_specialization": endpoint_integer,
        "strict_upper_bound_analysis": {
            "implies_strict_bound_below_4158": False,
            "endpoint_zero_assignment_lhs": endpoint_zero_assignment_lhs,
            "sufficient_endpoint_exclusion_condition_using_n3_mod_3": (
                "4*wagner8 - 12*cube8 >= 37424"
            ),
        },
    }
    core = {
        "format": "wave157-general-cube-wagner-symbolic-cut-v1",
        "claim_label": "DERIVED",
        "scope": (
            "A symbolic four-root covariance inequality for every hypothetical "
            "srg(99,14,1,2), expressed through n3 and two order-eight counts."
        ),
        "inputs": {
            "attempts/wave152-four-root-order8/simplified-mask12-cut-2.json":
                TARGET_SHA256,
            "verification/wave43-seven-deck-endpoint/independent_check.py":
                SIX_SOURCE_SHA256,
        },
        "parameters": {
            "n": N,
            "k": K,
            "lambda": LAMBDA,
            "mu": MU,
            "root_mask": ROOT_MASK,
            "plus_flag_mask": FLAG_PLUS,
            "minus_flag_mask": FLAG_MINUS,
        },
        "root_embedding_derivation": root_count,
        "six_set_formula": n9_formula,
        "candidate_union_counts": {
            str(order): len(candidates[order]) for order in (6, 7, 8)
        },
        "candidate_union_masks": {
            str(order): list(candidates[order]) for order in (6, 7, 8)
        },
        "first_moment_nonzeros": {
            str(order): {str(mask): value for mask, value in nonzero_first[order].items()}
            for order in (6, 7, 8)
        },
        "quadratic_coefficients_before_division": {
            str(order): {
                str(mask): value
                for mask, value in nonzero_quadratic[order].items()
            }
            for order in (6, 7, 8)
        },
        "named_order8_masks": named_masks,
        "covariance_identity_before_division":
            mathematical_certificate["covariance_identity_before_division"],
        "symbolic_inequality": symbolic,
        "endpoint_specialization": endpoint_integer,
        "stored_endpoint_comparison": {
            "matches_recovered_constant": True,
            "matches_recovered_order8_coefficients": True,
            "matches_recovered_divisor": True,
            "stored_cut_sha256": stored_cut["cut_sha256"],
        },
        "strict_upper_bound_analysis": {
            "implies_strict_bound_below_4158": False,
            "reason": (
                "At n3=4158, cube8=0 and wagner8=0 obey the inequality "
                "with positive left side 37422. Additional independent count "
                "relations would be required."
            ),
            "endpoint_zero_assignment_lhs": endpoint_zero_assignment_lhs,
            "sufficient_endpoint_exclusion_condition_using_n3_mod_3": (
                "4*wagner8 - 12*cube8 >= 37424"
            ),
        },
        "conclusion": {
            "symbolic_cut": "DERIVED",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "endpoint_n3_4158": "UNKNOWN",
            "graph_constructed": False,
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "This discovery package cannot independently verify itself.",
            "The inequality alone is compatible with the n3=4158 endpoint.",
            "The order-eight variables are induced class counts, not free graph choices.",
            "No graph existence or nonexistence result follows.",
        ],
        "resource_report": {
            "elapsed_seconds": time.time() - started,
            "minimum_free_physical_memory_percent": min(
                float(sample["free_physical_memory_percent"]) for sample in samples
            ),
            "samples": samples,
        },
        "mathematical_certificate_sha256": canonical_sha256(
            mathematical_certificate
        ),
    }
    return {**core, "result_sha256": canonical_sha256(core)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = derive()
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "claim_label": result["claim_label"],
                "inequality": result["symbolic_inequality"]["integer_form"],
                "strict_upper_bound_below_4158": result["conclusion"][
                    "strict_upper_bound_below_4158"
                ],
                "minimum_free_percent": result["resource_report"][
                    "minimum_free_physical_memory_percent"
                ],
                "output": str(args.output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
