"""Clean-room verifier for the sealed Wave157 cube/Wagner theorem.

The verifier parses static source definitions and independently enumerates
flag-pair unions.  It never imports or executes derive_symbolic_cut.py.
"""

from __future__ import annotations

import argparse
import ast
import ctypes
import functools
import gzip
import hashlib
import itertools
import json
import math
import re
import time
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
DISCOVERY = ROOT / "attempts/wave157-general-cube-wagner"
MANIFEST_PATH = DISCOVERY / "package-manifest.sha256"
INPUT_FREEZE_PATH = DISCOVERY / "input-freeze.sha256"
DISCOVERY_RESULTS_PATH = DISCOVERY / "exact-results.json"
STORED_CUT_PATH = (
    ROOT / "attempts/wave152-four-root-order8/simplified-mask12-cut-2.json"
)
FORMULA_SOURCE_PATH = (
    ROOT / "verification/wave43-seven-deck-endpoint/independent_check.py"
)

EXPECTED_MANIFEST_SHA256 = (
    "c4082726ff1c4237824982550da6346204c58a91dc932b1f3a2d382b8801e405"
)
EXPECTED_RESULTS_SHA256 = (
    "c52eaca24a9b1fe5e7465dcb51895d90597f249a4decc513d3658af65ec66e0e"
)
EXPECTED_INPUT_FREEZE_SHA256 = (
    "26df91df6c8714017ecf2fa277a323adf475d66cd286630d87057180fa1bc53f"
)

N = 99
K = 14
LAMBDA = 1
MU = 2
ROOT_MASK = 12
PLUS_FLAG_MASK = 21812
MINUS_FLAG_MASK = 22708


class VerificationError(AssertionError):
    """Raised when a frozen claim fails closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def free_memory_percent() -> float:
    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("memory_load", ctypes.c_ulong),
            ("total_physical", ctypes.c_ulonglong),
            ("available_physical", ctypes.c_ulonglong),
            ("total_page_file", ctypes.c_ulonglong),
            ("available_page_file", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended_virtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.length = ctypes.sizeof(MemoryStatus)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
        "GlobalMemoryStatusEx failed",
    )
    return 100.0 * status.available_physical / status.total_physical


def memory_checkpoint(samples: list[dict], label: str) -> None:
    free = free_memory_percent()
    samples.append({"label": label, "free_physical_memory_percent": free})
    require(free >= 15.0, f"physical-memory floor breached at {label}: {free:.2f}%")


def parse_manifest(path: Path) -> list[tuple[str, Path]]:
    entries = []
    seen = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        require(match is not None, f"malformed manifest line {line_number}")
        expected, relative_text = match.groups()
        relative = Path(relative_text)
        require(not relative.is_absolute(), "absolute path in manifest")
        target = (ROOT / relative).resolve()
        require(ROOT in target.parents, "manifest path escapes repository")
        require(target not in seen, "duplicate manifest target")
        seen.add(target)
        entries.append((expected, target))
    require(entries, "empty manifest")
    return entries


def verify_manifest(path: Path) -> int:
    entries = parse_manifest(path)
    for expected, target in entries:
        require(target.is_file(), f"missing manifest target: {target}")
        require(sha256(target) == expected, f"hash mismatch: {target}")
    return len(entries)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@functools.lru_cache(maxsize=None)
def edge_pairs(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


@functools.lru_cache(maxsize=None)
def pair_index(order: int) -> dict[tuple[int, int], int]:
    return {pair: index for index, pair in enumerate(edge_pairs(order))}


def edges_from_mask(mask: int, order: int) -> tuple[tuple[int, int], ...]:
    require(0 <= mask < 1 << math.comb(order, 2), "mask outside graph universe")
    return tuple(
        pair for index, pair in enumerate(edge_pairs(order)) if mask >> index & 1
    )


def mask_from_edges(order: int, edges: Iterable[tuple[int, int]]) -> int:
    mask = 0
    seen = set()
    for endpoints in edges:
        require(len(endpoints) == 2, "malformed edge")
        edge = tuple(sorted(endpoints))
        require(edge[0] != edge[1] and 0 <= edge[0] < edge[1] < order, "bad edge")
        require(edge not in seen, "duplicate edge")
        seen.add(edge)
        mask |= 1 << pair_index(order)[edge]
    return mask


def transform_mask(mask: int, order: int, permutation: Sequence[int]) -> int:
    return mask_from_edges(
        order,
        (
            tuple(sorted((permutation[left], permutation[right])))
            for left, right in edges_from_mask(mask, order)
        ),
    )


@functools.lru_cache(maxsize=None)
def canonical_mask(mask: int, order: int) -> int:
    return min(
        transform_mask(mask, order, permutation)
        for permutation in itertools.permutations(range(order))
    )


def canonical_isomorphism(mask: int, order: int) -> tuple[int, tuple[int, ...]]:
    best_mask = None
    best_permutation = None
    for permutation in itertools.permutations(range(order)):
        moved = transform_mask(mask, order, permutation)
        if best_mask is None or moved < best_mask:
            best_mask = moved
            best_permutation = permutation
    require(best_mask is not None and best_permutation is not None, "no isomorphism")
    return best_mask, best_permutation


def adjacency(mask: int, order: int) -> tuple[frozenset[int], ...]:
    rows = [set() for _ in range(order)]
    for left, right in edges_from_mask(mask, order):
        rows[left].add(right)
        rows[right].add(left)
    return tuple(frozenset(row) for row in rows)


def locally_admissible(mask: int, order: int) -> bool:
    rows = adjacency(mask, order)
    for left, right in edge_pairs(order):
        common = len(rows[left] & rows[right])
        cap = LAMBDA if right in rows[left] else MU
        if common > cap:
            return False
    return True


FREE_SWAP = (0, 1, 2, 3, 5, 4)
PLUS_ORBIT = frozenset(
    (PLUS_FLAG_MASK, transform_mask(PLUS_FLAG_MASK, 6, FREE_SWAP))
)
MINUS_ORBIT = frozenset(
    (MINUS_FLAG_MASK, transform_mask(MINUS_FLAG_MASK, 6, FREE_SWAP))
)


def flag_constraints(
    constraints: dict[tuple[int, int], int],
    sign: int,
    free_pair: tuple[int, int],
    orientation: int,
) -> dict[tuple[int, int], int] | None:
    flag_mask = PLUS_FLAG_MASK if sign == 1 else MINUS_FLAG_MASK
    image = (0, 1, 2, 3, free_pair[orientation], free_pair[1 - orientation])
    for index, (left, right) in enumerate(edge_pairs(6)):
        host_pair = tuple(sorted((image[left], image[right])))
        value = (flag_mask >> index) & 1
        if host_pair in constraints and constraints[host_pair] != value:
            return None
        constraints[host_pair] = value
    return constraints


def enumerate_union_classes(order: int) -> tuple[int, ...]:
    """Merge all oriented signed flag pairs and complete unseen edges."""

    outside = tuple(range(4, order))
    free_pairs = tuple(itertools.combinations(outside, 2))
    labelled_masks = set()
    for first_pair, second_pair in itertools.product(free_pairs, repeat=2):
        if set(first_pair) | set(second_pair) != set(outside):
            continue
        for first_sign, second_sign in itertools.product((1, -1), repeat=2):
            for first_orientation, second_orientation in itertools.product((0, 1), repeat=2):
                constraints = flag_constraints(
                    {}, first_sign, first_pair, first_orientation
                )
                if constraints is None:
                    continue
                constraints = flag_constraints(
                    constraints,
                    second_sign,
                    second_pair,
                    second_orientation,
                )
                if constraints is None:
                    continue
                unknown = [
                    pair for pair in edge_pairs(order) if pair not in constraints
                ]
                for completion in range(1 << len(unknown)):
                    edges = [pair for pair, value in constraints.items() if value]
                    edges.extend(
                        pair
                        for index, pair in enumerate(unknown)
                        if completion >> index & 1
                    )
                    mask = mask_from_edges(order, edges)
                    if locally_admissible(mask, order):
                        labelled_masks.add(mask)
    return tuple(sorted({canonical_mask(mask, order) for mask in labelled_masks}))


def induced_mask(
    host_mask: int, host_order: int, vertices: Sequence[int]
) -> int:
    host_edges = set(edges_from_mask(host_mask, host_order))
    return mask_from_edges(
        len(vertices),
        (
            (left, right)
            for left, right in edge_pairs(len(vertices))
            if tuple(sorted((vertices[left], vertices[right]))) in host_edges
        ),
    )


def flag_value(
    host_mask: int,
    host_order: int,
    roots: Sequence[int],
    free_pair: tuple[int, int],
) -> int:
    flag = induced_mask(host_mask, host_order, tuple(roots) + free_pair)
    if flag in PLUS_ORBIT:
        return 1
    if flag in MINUS_ORBIT:
        return -1
    return 0


def covariance_coefficient(mask: int, order: int) -> dict:
    first = 0
    quadratic = 0
    root_embeddings = 0
    positive_products = 0
    negative_products = 0
    zero_products = 0
    for roots in itertools.permutations(range(order), 4):
        if induced_mask(mask, order, roots) != ROOT_MASK:
            continue
        root_embeddings += 1
        outside = tuple(vertex for vertex in range(order) if vertex not in roots)
        free_pairs = tuple(itertools.combinations(outside, 2))
        values = {
            pair: flag_value(mask, order, roots, pair) for pair in free_pairs
        }
        if order == 6:
            first += sum(values.values())
        for first_pair, second_pair in itertools.product(free_pairs, repeat=2):
            if set(first_pair) | set(second_pair) != set(outside):
                continue
            product = values[first_pair] * values[second_pair]
            quadratic += product
            if product > 0:
                positive_products += 1
            elif product < 0:
                negative_products += 1
            else:
                zero_products += 1
    return {
        "first": first,
        "quadratic": quadratic,
        "root_embeddings": root_embeddings,
        "positive_products": positive_products,
        "negative_products": negative_products,
        "zero_products": zero_products,
    }


def parse_six_set_source() -> dict:
    """Read the frozen source AST without importing or executing it."""

    tree = ast.parse(FORMULA_SOURCE_PATH.read_text(encoding="utf-8"))
    source_masks = None
    six_function = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SOURCE_N_MASKS"
            for target in node.targets
        ):
            source_masks = ast.literal_eval(node.value)
        if isinstance(node, ast.FunctionDef) and node.name == "six_formulae":
            six_function = node
    require(
        isinstance(source_masks, tuple)
        and len(source_masks) == 62
        and len(set(source_masks)) == 62,
        "SOURCE_N_MASKS is not the frozen 62-class correspondence",
    )
    require(six_function is not None, "six_formulae definition missing")

    assignments = {
        node.targets[0].id: node.value
        for node in six_function.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
    }
    expected_common = ast.parse("n * k * (k - 2)", mode="eval").body
    expected_b = ast.parse("common * (k - 4)", mode="eval").body
    require(
        ast.dump(assignments.get("common"), include_attributes=False)
        == ast.dump(expected_common, include_attributes=False),
        "common definition changed",
    )
    require(
        ast.dump(assignments.get("b"), include_attributes=False)
        == ast.dump(expected_b, include_attributes=False),
        "b definition changed",
    )
    return_node = next(
        (node for node in six_function.body if isinstance(node, ast.Return)), None
    )
    require(
        return_node is not None
        and isinstance(return_node.value, ast.Tuple)
        and len(return_node.value.elts) == 62,
        "six_formulae return tuple changed",
    )
    ninth = return_node.value.elts[8]
    expected_ninth = ast.parse("A(Q(b, 4), -1)", mode="eval").body
    require(
        ast.dump(ninth, include_attributes=False)
        == ast.dump(expected_ninth, include_attributes=False),
        "ninth six-set formula changed",
    )
    common = N * K * (K - 2)
    b_value = common * (K - 4)
    return {
        "source_index_one_based": 9,
        "canonical_mask": source_masks[8],
        "common": common,
        "b": b_value,
        "constant": b_value // 4,
        "n3_coefficient": -1,
        "static_ast_formula": "A(Q(b, 4), -1)",
    }


def named_graphs() -> dict:
    cube_edges = [
        (vertex, vertex ^ (1 << bit))
        for vertex in range(8)
        for bit in range(3)
        if vertex < (vertex ^ (1 << bit))
    ]
    wagner_edges = [(vertex, (vertex + 1) % 8) for vertex in range(8)]
    wagner_edges.extend((vertex, vertex + 4) for vertex in range(4))
    output = {}
    for name, edges in (("cube", cube_edges), ("wagner_mobius_ladder", wagner_edges)):
        labelled = mask_from_edges(8, edges)
        canonical, permutation = canonical_isomorphism(labelled, 8)
        rows = adjacency(labelled, 8)
        require(all(len(row) == 3 for row in rows), f"{name} is not cubic")
        output[name] = {
            "labelled_mask": labelled,
            "canonical_mask": canonical,
            "canonical_isomorphism": list(permutation),
        }
    return output


def root_embedding_derivation() -> dict:
    ordered_first_edges = N * K
    common_nonneighbors = N - (2 * K - LAMBDA)
    adjacent_to_common_neighbor = K - 2
    remaining = common_nonneighbors - adjacent_to_common_neighbor
    degree_if_adjacent = K - 3
    degree_if_not_adjacent = K - 4
    ordered_second_edges = (
        adjacent_to_common_neighbor * degree_if_adjacent
        + remaining * degree_if_not_adjacent
    )
    root_count = ordered_first_edges * ordered_second_edges
    return {
        "ordered_first_edges": ordered_first_edges,
        "common_nonneighbors_per_first_edge": common_nonneighbors,
        "common_nonneighbors_adjacent_to_unique_common_neighbor": adjacent_to_common_neighbor,
        "remaining_common_nonneighbors": remaining,
        "internal_degree_if_adjacent": degree_if_adjacent,
        "internal_degree_if_not_adjacent": degree_if_not_adjacent,
        "ordered_second_edges_per_first_edge": ordered_second_edges,
        "root_embedding_count": root_count,
    }


def build_certificate(check_memory: bool = True) -> dict:
    samples: list[dict] = []
    if check_memory:
        memory_checkpoint(samples, "start")

    require(edges_from_mask(ROOT_MASK, 4) == ((0, 3), (1, 2)), "root edges changed")
    require(
        edges_from_mask(PLUS_FLAG_MASK, 6)
        == ((0, 3), (0, 5), (1, 2), (1, 5), (2, 4), (3, 4), (4, 5)),
        "plus flag edges changed",
    )
    require(
        edges_from_mask(MINUS_FLAG_MASK, 6)
        == ((0, 3), (0, 5), (1, 2), (1, 4), (2, 5), (3, 4), (4, 5)),
        "minus flag edges changed",
    )
    require(canonical_mask(PLUS_FLAG_MASK, 6) == 1884, "plus flag is not N9")
    require(canonical_mask(MINUS_FLAG_MASK, 6) == 1884, "minus flag is not N9")

    union_classes = {}
    coefficients = {}
    for order in (6, 7, 8):
        classes = enumerate_union_classes(order)
        union_classes[str(order)] = list(classes)
        coefficients[str(order)] = {
            str(mask): covariance_coefficient(mask, order) for mask in classes
        }
        if check_memory:
            memory_checkpoint(samples, f"order_{order}_complete")

    require(union_classes == {"6": [1884], "7": [], "8": [2022000, 5683824]}, "union census mismatch")
    require(coefficients["6"]["1884"] == {
        "first": 0, "quadratic": 8, "root_embeddings": 8,
        "positive_products": 8, "negative_products": 0, "zero_products": 0,
    }, "N9 coefficient mismatch")
    require(coefficients["8"]["2022000"] == {
        "first": 0, "quadratic": 96, "root_embeddings": 48,
        "positive_products": 96, "negative_products": 0, "zero_products": 192,
    }, "cube coefficient mismatch")
    require(coefficients["8"]["5683824"] == {
        "first": 0, "quadratic": -32, "root_embeddings": 16,
        "positive_products": 0, "negative_products": 32, "zero_products": 64,
    }, "Wagner coefficient mismatch")

    names = named_graphs()
    require(names["cube"]["canonical_mask"] == 2022000, "cube name mismatch")
    require(
        names["wagner_mobius_ladder"]["canonical_mask"] == 5683824,
        "Wagner name mismatch",
    )
    formula = parse_six_set_source()
    require(formula["canonical_mask"] == 1884, "ninth formula is not N9")
    require(formula["constant"] == 41580, "N9 constant mismatch")
    roots = root_embedding_derivation()
    require(roots["root_embedding_count"] == 1014552, "root count mismatch")

    raw_terms = [
        roots["root_embedding_count"] * 8,
        roots["root_embedding_count"] * 96,
        roots["root_embedding_count"] * -32,
    ]
    symbolic_gcd = math.gcd(*(abs(value) for value in raw_terms))
    require(symbolic_gcd == 8 * roots["root_embedding_count"], "raw gcd mismatch")
    primitive_six = [value // symbolic_gcd for value in raw_terms]
    require(primitive_six == [1, 12, -4], "primitive covariance cut mismatch")

    endpoint_n3 = 4158
    endpoint_n9 = formula["constant"] - endpoint_n3
    endpoint_terms = [endpoint_n9, 12, -4]
    endpoint_gcd = math.gcd(*(abs(value) for value in endpoint_terms))
    require(endpoint_gcd == 2, "endpoint gcd mismatch")
    endpoint_primitive = [value // endpoint_gcd for value in endpoint_terms]
    require(endpoint_primitive == [18711, 6, -2], "endpoint primitive cut mismatch")

    zero_assignment_lhs = endpoint_n9
    require(zero_assignment_lhs > 0, "endpoint zero assignment should satisfy cut")
    sufficient_comparison = endpoint_n9 + 2
    resulting_upper = formula["constant"] - sufficient_comparison
    require(
        sufficient_comparison == 37424 and resulting_upper == 4156,
        "strict-bound threshold arithmetic changed",
    )

    if check_memory:
        memory_checkpoint(samples, "complete")
    return {
        "parameters": {
            "n": N, "k": K, "lambda": LAMBDA, "mu": MU,
            "root_mask": ROOT_MASK,
            "plus_flag_mask": PLUS_FLAG_MASK,
            "minus_flag_mask": MINUS_FLAG_MASK,
        },
        "union_classes": union_classes,
        "coefficients": coefficients,
        "named_graphs": names,
        "root_embedding_derivation": roots,
        "six_set_formula": formula,
        "covariance": {
            "root_count": roots["root_embedding_count"],
            "raw_coefficients": {"N9": 8, "cube8": 96, "wagner8": -32},
            "first_moment": 0,
            "raw_gcd": symbolic_gcd,
            "primitive_coefficients": {"N9": 1, "cube8": 12, "wagner8": -4},
        },
        "symbolic_inequality": {
            "constant": 41580,
            "coefficient_n3": -1,
            "coefficient_cube8": 12,
            "coefficient_wagner8": -4,
        },
        "endpoint": {
            "n3": endpoint_n3,
            "N9": endpoint_n9,
            "integer_terms": endpoint_terms,
            "extra_gcd": endpoint_gcd,
            "primitive_terms": endpoint_primitive,
            "total_divisor": symbolic_gcd * endpoint_gcd,
        },
        "strict_bound": {
            "endpoint_zero_assignment_lhs": zero_assignment_lhs,
            "theorem_alone_excludes_endpoint": False,
            "sufficient_comparison": sufficient_comparison,
            "resulting_upper_before_mod3": resulting_upper,
            "conditional_upper_using_n3_mod3": 4155,
        },
        "memory_samples": samples,
    }


def verify_discovery_payload(payload: dict, certificate: dict, stored_cut: dict) -> None:
    require(payload.get("claim_label") == "DERIVED", "discovery status changed")
    require(payload.get("parameters") == certificate["parameters"], "parameter mismatch")
    require(
        payload.get("candidate_union_masks") == certificate["union_classes"],
        "candidate union masks mismatch",
    )
    require(
        payload.get("candidate_union_counts")
        == {order: len(masks) for order, masks in certificate["union_classes"].items()},
        "candidate union counts mismatch",
    )
    require(
        payload.get("named_order8_masks")
        == {
            "cube": certificate["named_graphs"]["cube"]["canonical_mask"],
            "wagner_mobius_ladder": certificate["named_graphs"]["wagner_mobius_ladder"]["canonical_mask"],
        },
        "named graph masks mismatch",
    )
    require(
        payload.get("root_embedding_derivation")
        == certificate["root_embedding_derivation"],
        "root embedding derivation mismatch",
    )
    formula = certificate["six_set_formula"]
    require(
        payload.get("six_set_formula")
        == {
            "canonical_mask": formula["canonical_mask"],
            "constant": formula["constant"],
            "expanded_formula": "41580 - n3",
            "n3_coefficient": formula["n3_coefficient"],
            "source_index_one_based": formula["source_index_one_based"],
            "static_ast_formula": formula["static_ast_formula"],
        },
        "six-set formula mismatch",
    )
    require(
        payload.get("quadratic_coefficients_before_division")
        == {
            "6": {"1884": 8},
            "7": {},
            "8": {"2022000": 96, "5683824": -32},
        },
        "quadratic coefficient table mismatch",
    )
    require(
        payload.get("first_moment_nonzeros") == {"6": {}, "7": {}, "8": {}},
        "first moment is not zero",
    )
    symbolic = certificate["symbolic_inequality"]
    require(
        payload.get("symbolic_inequality", {}).get("constant") == symbolic["constant"]
        and payload["symbolic_inequality"].get("coefficient_n3") == symbolic["coefficient_n3"]
        and payload["symbolic_inequality"].get("coefficient_cube8") == symbolic["coefficient_cube8"]
        and payload["symbolic_inequality"].get("coefficient_wagner8") == symbolic["coefficient_wagner8"],
        "symbolic inequality mismatch",
    )
    endpoint = certificate["endpoint"]
    require(
        payload.get("endpoint_specialization")
        == {
            "constant_before_extra_endpoint_gcd": endpoint["N9"],
            "extra_endpoint_gcd": endpoint["extra_gcd"],
            "integer_form": "37422 + 12*cube8 - 4*wagner8 >= 0",
            "primitive_constant": endpoint["primitive_terms"][0],
            "primitive_form": "18711 + 6*cube8 - 2*wagner8 >= 0",
        },
        "endpoint specialization mismatch",
    )
    require(
        stored_cut["cut"]["root_embedding_count"]
        == certificate["root_embedding_derivation"]["root_embedding_count"],
        "stored root count mismatch",
    )
    require(stored_cut["cut"]["constant"] == "18711", "stored constant mismatch")
    require(stored_cut["cut"]["primitive_divisor"] == str(endpoint["total_divisor"]), "stored divisor mismatch")
    require(
        stored_cut["cut"]["order8_coefficients"]
        == [
            {"canonical_mask": 2022000, "coefficient": "6"},
            {"canonical_mask": 5683824, "coefficient": "-2"},
        ],
        "stored order-eight coefficients mismatch",
    )
    strict = payload.get("strict_upper_bound_analysis", {})
    require(
        strict.get("endpoint_zero_assignment_lhs")
        == certificate["strict_bound"]["endpoint_zero_assignment_lhs"],
        "endpoint zero-assignment analysis mismatch",
    )
    require(strict.get("implies_strict_bound_below_4158") is False, "strict bound inflated")
    require(
        strict.get("sufficient_endpoint_exclusion_condition_using_n3_mod_3")
        == "4*wagner8 - 12*cube8 >= 37424",
        "sufficient comparison mismatch",
    )
    conclusion = payload.get("conclusion", {})
    require(conclusion.get("strict_upper_bound_below_4158") == "NOT_PROVED", "strict status inflated")
    require(conclusion.get("endpoint_n3_4158") == "UNKNOWN", "endpoint status inflated")
    require(conclusion.get("graph_constructed") is False, "graph status inflated")
    require(conclusion.get("Conway_99") == "UNKNOWN", "Conway-99 status inflated")
    require(
        all("novel" not in key.lower() for key in conclusion),
        "novelty must not be certified",
    )


def run_verification() -> dict:
    started = time.perf_counter()
    samples: list[dict] = []
    memory_checkpoint(samples, "preflight")
    require(sha256(MANIFEST_PATH) == EXPECTED_MANIFEST_SHA256, "manifest changed")
    discovery_entries = verify_manifest(MANIFEST_PATH)
    require(sha256(DISCOVERY_RESULTS_PATH) == EXPECTED_RESULTS_SHA256, "results changed")
    require(sha256(INPUT_FREEZE_PATH) == EXPECTED_INPUT_FREEZE_SHA256, "input freeze changed")
    frozen_inputs = verify_manifest(INPUT_FREEZE_PATH)
    memory_checkpoint(samples, "inputs_verified")

    certificate = build_certificate(check_memory=True)
    payload = read_json(DISCOVERY_RESULTS_PATH)
    stored_cut = read_json(STORED_CUT_PATH)
    verify_discovery_payload(payload, certificate, stored_cut)
    memory_checkpoint(samples, "payload_compared")
    elapsed = time.perf_counter() - started
    all_samples = samples + certificate["memory_samples"]
    return {
        "claim_label": "VERIFIED",
        "verdict": (
            "VERIFIED_WITH_SCOPE: exact general cube/Wagner covariance "
            "inequality for every hypothetical srg(99,14,1,2)"
        ),
        "discovery_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "discovery_results_sha256": EXPECTED_RESULTS_SHA256,
        "discovery_manifest_entries_verified": discovery_entries,
        "frozen_inputs_verified": frozen_inputs,
        "union_classes": certificate["union_classes"],
        "named_graphs": certificate["named_graphs"],
        "root_embedding_count": certificate["root_embedding_derivation"]["root_embedding_count"],
        "quadratic_coefficients": certificate["covariance"]["raw_coefficients"],
        "symbolic_inequality": "41580 - n3 + 12*cube8 - 4*wagner8 >= 0",
        "endpoint_primitive_inequality": "18711 + 6*cube8 - 2*wagner8 >= 0",
        "strict_upper_bound_below_4158": "UNKNOWN",
        "endpoint_n3_4158": "UNKNOWN",
        "graph": "UNKNOWN",
        "Conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
        "hostile_tests": "run separately by test_independent_verifier.py",
        "elapsed_seconds": elapsed,
        "minimum_free_physical_memory_percent": min(
            sample["free_physical_memory_percent"] for sample in all_samples
        ),
        "memory_samples": all_samples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact", action="store_true")
    arguments = parser.parse_args()
    result = run_verification()
    print(
        json.dumps(
            result,
            sort_keys=True,
            indent=None if arguments.compact else 2,
            separators=(",", ":") if arguments.compact else None,
        )
    )


if __name__ == "__main__":
    main()
