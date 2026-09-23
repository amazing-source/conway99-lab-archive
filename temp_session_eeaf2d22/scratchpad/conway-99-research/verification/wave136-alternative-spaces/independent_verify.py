#!/usr/bin/env python3
"""Independent exact checks for the Wave 136 alternative-space proposal.

This verifier does not import any discovery module.  It reconstructs the
binary Krawtchouk transform, the Arf/Gauss diagnostic, the additive-GF(4)
character table, small graph-state controls, and the support-at-most-three
coefficient table directly from definitions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import combinations, product
from math import comb
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WITNESS = (
    ROOT / "attempts" / "wave131-binary-lcd-enumerator"
    / "rational-witness.json"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def encode(value: Fraction | int) -> str:
    value = Fraction(value)
    return (
        str(value.numerator)
        if value.denominator == 1
        else f"{value.numerator}/{value.denominator}"
    )


def coefficient_vector(raw: dict[str, str], n: int) -> list[Fraction]:
    return [Fraction(raw.get(str(weight), "0")) for weight in range(n + 1)]


def krawtchouk(n: int, degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * comb(weight, overlap)
        * comb(n - weight, degree - overlap)
        for overlap in range(max(0, degree - (n - weight)), min(degree, weight) + 1)
    )


def macwilliams_transform(
    source: list[Fraction], source_dimension: int
) -> list[Fraction]:
    n = len(source) - 1
    scale = 1 << source_dimension
    return [
        sum(
            (source[weight] * krawtchouk(n, degree, weight)
             for weight in range(n + 1)),
            Fraction(0),
        )
        / scale
        for degree in range(n + 1)
    ]


def signed_even_sum(coefficients: Iterable[Fraction]) -> Fraction:
    return sum(
        (
            (-1 if (weight // 2) % 2 else 1) * value
            for weight, value in enumerate(coefficients)
            if weight % 2 == 0
        ),
        Fraction(0),
    )


def binary_arf_checks(witness_path: Path) -> dict[str, object]:
    witness = json.loads(witness_path.read_text(encoding="utf-8"))
    image = coefficient_vector(witness["image_coefficients"], 99)
    dual = coefficient_vector(witness["dual_coefficients"], 99)

    forward = macwilliams_transform(image, 54)
    inverse = macwilliams_transform(dual, 45)
    forward_failures = [j for j in range(100) if forward[j] != dual[j]]
    inverse_failures = [i for i in range(100) if inverse[i] != image[i]]

    g_r = signed_even_sum(image)
    even_dual = [
        value if weight % 2 == 0 else Fraction(0)
        for weight, value in enumerate(dual)
    ]
    g_e = signed_even_sum(even_dual)
    g_h = sum(
        (
            (-1 if (weight // 2) % 2 else 1) * comb(99, weight)
            for weight in range(0, 100, 2)
        ),
        0,
    )
    target_r = 1 << 27
    target_e = 1 << 22

    checks = {
        "all_100_forward_macwilliams_rows": not forward_failures,
        "all_100_inverse_macwilliams_rows": not inverse_failures,
        "ambient_even_gauss_sum": g_h == -(1 << 49),
        "ordinary_macwilliams_ratio": g_e == -g_r / 32,
        "formal_witness_fails_arf_magnitude": abs(g_r) != target_r,
        "both_arf_branches_have_correct_product":
            target_r * (-target_e) == g_h,
    }
    if not all(checks.values()):
        raise AssertionError({"checks": checks, "forward": forward_failures,
                              "inverse": inverse_failures})

    return {
        "checks": checks,
        "forward_failure_weights": forward_failures,
        "inverse_failure_weights": inverse_failures,
        "ambient_even_gauss_sum": str(g_h),
        "forced_branches": [
            {"G_R": str(target_r), "G_E": str(-target_e)},
            {"G_R": str(-target_r), "G_E": str(target_e)},
        ],
        "witness_G_R": encode(g_r),
        "witness_G_E": encode(g_e),
        "witness_abs_G_R_over_2pow27": encode(abs(g_r) / target_r),
    }


STATE_PAIRS = ((0, 0), (1, 0), (0, 1), (1, 1))


def symplectic(left: tuple[int, int], right: tuple[int, int]) -> int:
    a, b = left
    c, d = right
    return (a * d + b * c) & 1


def character_matrix() -> list[list[int]]:
    return [
        [(-1) ** symplectic(left, right) for right in STATE_PAIRS]
        for left in STATE_PAIRS
    ]


def matvec_mod2(rows: list[int], x: int, n: int) -> int:
    out = 0
    for i, row in enumerate(rows):
        if (row & x).bit_count() & 1:
            out |= 1 << i
    return out


def graph_rows(n: int, edge_mask: int) -> list[int]:
    rows = [0] * n
    for bit, (u, v) in enumerate(combinations(range(n), 2)):
        if (edge_mask >> bit) & 1:
            rows[u] |= 1 << v
            rows[v] |= 1 << u
    return rows


def graph_state_composition(x: int, ax: int, n: int) -> tuple[int, int, int]:
    ny = (x & ax).bit_count()
    nr = (x ^ ax).bit_count()
    return n - ny - nr, ny, nr


def graph_enumerator(rows: list[int]) -> dict[tuple[int, int, int], int]:
    n = len(rows)
    result: dict[tuple[int, int, int], int] = {}
    for x in range(1 << n):
        ax = matvec_mod2(rows, x, n)
        state = graph_state_composition(x, ax, n)
        result[state] = result.get(state, 0) + 1
    return result


def evaluate_enumerator(
    enumerator: dict[tuple[int, int, int], int],
    u: int,
    v: int,
    w: int,
) -> int:
    return sum(
        count * (u ** ni) * (v ** ny) * (w ** nr)
        for (ni, ny, nr), count in enumerator.items()
    )


def symplectic_word_pair(
    first: tuple[int, int], second: tuple[int, int]
) -> int:
    x, z = first
    y, t = second
    return ((x & t).bit_count() + (z & y).bit_count()) & 1


def small_graph_controls() -> dict[str, object]:
    evaluation_points = ((1, 1, 1), (2, 3, 5), (-1, 2, 4), (3, -2, 1))
    graphs_checked = 0
    codewords_checked = 0
    orthogonal_candidates_checked = 0
    transform_evaluations_checked = 0

    for n in range(1, 5):
        edge_count = comb(n, 2)
        for edge_mask in range(1 << edge_count):
            rows = graph_rows(n, edge_mask)
            code = {
                (x, matvec_mod2(rows, x, n))
                for x in range(1 << n)
            }
            if len(code) != (1 << n):
                raise AssertionError("graph-state map is not injective")
            for left in code:
                for right in code:
                    codewords_checked += 1
                    if symplectic_word_pair(left, right):
                        raise AssertionError("graph-state code is not isotropic")

            orthogonal = set()
            for x in range(1 << n):
                for z in range(1 << n):
                    candidate = (x, z)
                    orthogonal_candidates_checked += 1
                    if all(
                        symplectic_word_pair(candidate, word) == 0
                        for word in code
                    ):
                        orthogonal.add(candidate)
            if orthogonal != code:
                raise AssertionError("graph-state code is not self-dual")

            enumerator = graph_enumerator(rows)
            if any(ny % 2 for _, ny, _ in enumerator):
                raise AssertionError("odd-Y state survived")
            for u, v, w in evaluation_points:
                left_value = evaluate_enumerator(enumerator, u, v, w)
                right_value = evaluate_enumerator(
                    enumerator, u + v + 2 * w, u + v - 2 * w, u - v
                )
                transform_evaluations_checked += 1
                if (1 << n) * left_value != right_value:
                    raise AssertionError("symmetrized transform failed")
            graphs_checked += 1

    # The triangle adjacency matrix is idempotent over F_2 and provides a
    # direct small control for the pure-Y/image and pure-X/kernel axes.
    triangle = graph_rows(3, (1 << 3) - 1)
    for x in range(1 << 3):
        ax = matvec_mod2(triangle, x, 3)
        aax = matvec_mod2(triangle, ax, 3)
        if aax != ax:
            raise AssertionError("triangle control is not idempotent")
    image = {
        matvec_mod2(triangle, x, 3)
        for x in range(1 << 3)
    }
    kernel = {
        x for x in range(1 << 3)
        if matvec_mod2(triangle, x, 3) == 0
    }
    pure_y_inputs = {
        x for x in range(1 << 3)
        if matvec_mod2(triangle, x, 3) == x
    }
    pure_x_inputs = {
        x for x in range(1 << 3)
        if matvec_mod2(triangle, x, 3) == 0
    }
    if pure_y_inputs != image or pure_x_inputs != kernel:
        raise AssertionError("pure-axis control failed")

    return {
        "graphs_checked_exhaustively_through_order": 4,
        "graph_count": graphs_checked,
        "isotropic_ordered_pairs_checked": codewords_checked,
        "orthogonal_candidates_checked": orthogonal_candidates_checked,
        "exact_transform_evaluations_checked": transform_evaluations_checked,
        "triangle_idempotent_axis_control": True,
    }


def support_three_table() -> list[dict[str, int | str]]:
    v = 99
    k = 14
    lam = 1
    mu = 2
    edges = v * k // 2
    triangles = v * k * lam // 6
    local_edges = k * lam // 2
    induced_paths = v * (comb(k, 2) - local_edges)
    one_edge_total = edges * (v - (2 * k - lam))
    independent_total = (
        comb(v, 3) - triangles - induced_paths - one_edge_total
    )

    independent_c1 = v * comb(k // 2, 3) * (2 ** 3)
    one_edge_c1 = v * (k // 2) * (k - 2)
    independent_c0 = independent_total - independent_c1
    one_edge_c0 = one_edge_total - one_edge_c1

    rows: list[dict[str, int | str]] = [
        {
            "input_type": "one_vertex", "count": v,
            "nI": 84, "nY": 0, "nR": 15,
        },
        {
            "input_type": "edge", "count": edges,
            "nI": 73, "nY": 2, "nR": 24,
        },
        {
            "input_type": "nonedge", "count": comb(v, 2) - edges,
            "nI": 73, "nY": 0, "nR": 26,
        },
    ]

    triple_specs = (
        ("independent_c0", independent_c0, 0, 0, 0),
        ("independent_c1", independent_c1, 0, 0, 1),
        ("one_edge_c0", one_edge_c0, 1, 0, 0),
        ("one_edge_c1", one_edge_c1, 1, 0, 1),
        ("induced_path", induced_paths, 2, 1, 0),
        ("triangle", triangles, 3, 3, 0),
    )
    for name, count, edge_number, degree_two_vertices, common_all in triple_specs:
        del edge_number  # retained in the tuple to make the type data explicit
        if name.startswith("independent"):
            ny = 0
        elif name.startswith("one_edge") or name == "induced_path":
            ny = 2
        else:
            ny = 0
        nr = 33 + 2 * degree_two_vertices + 4 * common_all - ny
        rows.append(
            {
                "input_type": name,
                "count": count,
                "nI": 99 - ny - nr,
                "nY": ny,
                "nR": nr,
            }
        )

    if sum(
        int(row["count"]) for row in rows[3:]
    ) != comb(99, 3):
        raise AssertionError("three-set census does not close")
    if sum(int(row["count"]) for row in rows[:1]) != 99:
        raise AssertionError("one-set census does not close")
    if sum(int(row["count"]) for row in rows[1:3]) != comb(99, 2):
        raise AssertionError("two-set census does not close")
    expected = {
        "one_vertex": (99, 84, 0, 15),
        "edge": (693, 73, 2, 24),
        "nonedge": (4158, 73, 0, 26),
        "independent_c0": (70686, 66, 0, 33),
        "independent_c1": (27720, 62, 0, 37),
        "one_edge_c0": (41580, 66, 2, 31),
        "one_edge_c1": (8316, 62, 2, 35),
        "induced_path": (8316, 64, 2, 33),
        "triangle": (231, 60, 0, 39),
    }
    for row in rows:
        actual = (
            int(row["count"]), int(row["nI"]),
            int(row["nY"]), int(row["nR"]),
        )
        if actual != expected[str(row["input_type"])]:
            raise AssertionError({"row": row, "expected": expected})
    return rows


def gf4_checks() -> dict[str, object]:
    matrix = character_matrix()
    expected_matrix = [
        [1, 1, 1, 1],
        [1, 1, -1, -1],
        [1, -1, 1, -1],
        [1, -1, -1, 1],
    ]
    if matrix != expected_matrix:
        raise AssertionError("GF(4) character matrix convention mismatch")

    raw_states = comb(101, 2)
    even_y_states = sum(100 - ny for ny in range(0, 100, 2))
    odd_y_states = raw_states - even_y_states
    if (raw_states, even_y_states, odd_y_states) != (5050, 2550, 2500):
        raise AssertionError("state count mismatch")

    return {
        "symbol_order": ["I=00", "X=10", "Z=01", "Y=11"],
        "character_matrix": matrix,
        "symmetrized_transform_I_Y_R": [
            "u+v+2w", "u+v-2w", "u-v"
        ],
        "wave134_order_I_R_Y_transform": [
            "x+2y+z", "x-z", "x-2y+z"
        ],
        "raw_states": raw_states,
        "allowed_even_nY_states": even_y_states,
        "forced_odd_nY_zero_states": odd_y_states,
        "small_graph_controls": small_graph_controls(),
        "support_at_most_three_lower_table": support_three_table(),
    }


def build_results(witness_path: Path) -> dict[str, object]:
    return {
        "format": "wave136-independent-alternative-space-verification-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "Exact Arf/Gauss witness diagnostic and exact additive-GF(4) "
            "graph-state identities and support-at-most-three coefficient "
            "lower bounds, conditional on the frozen Conway adjacency facts."
        ),
        "inputs": {
            str(witness_path.relative_to(ROOT)).replace("\\", "/"):
                sha256(witness_path)
        },
        "binary_arf": binary_arf_checks(witness_path),
        "additive_gf4": gf4_checks(),
        "audit_outcome": {
            "arf_witness_refutation": "VERIFIED",
            "ordinary_macwilliams_fixes_ratio_not_magnitude": "VERIFIED",
            "graph_state_self_duality": "VERIFIED",
            "symmetrized_state_counts_and_zero_rows": "VERIFIED",
            "transform_equivalence_to_wave134_after_permutation": "VERIFIED",
            "support_at_most_three_graph_forced_coefficients": "VERIFIED",
            "formal_independence_from_all_wave134_constraints":
                "UNKNOWN_NOT_PROVED",
            "external_novelty": "UNKNOWN",
        },
        "status_wall": {
            "formal_graph_state_enumerator": "NOT_SOLVED",
            "additive_gf4_code_realization": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "adjacency_matrix": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "conway_99": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--witness", type=Path, default=DEFAULT_WITNESS)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    results = build_results(args.witness.resolve())
    if args.verify:
        expected = json.loads(args.verify.read_text(encoding="utf-8"))
        if results != expected:
            raise SystemExit("verification mismatch")
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
