#!/usr/bin/env python3
"""Clean-room exact checks for the Wave 34 rootless actual-incidence track.

This module uses only Python's standard library.  It does not import, inspect,
or execute any Wave 34 discovery artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from itertools import permutations
from math import comb
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]

EXPECTED_INPUTS = {
    "AGENTS.md": "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "CONJECTURE.md": "7b4e67a28dbae58dffbf8f06a5fcb0241b12c34807dcb145ef2ff5c70d4c1c58",
    "verification/wave34-continuation-protocol.md": "60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4",
    "agents/2026-07-24-wave33-rootless-motif.md": "a22b261b49c355296fd4299b3b97da215e16209f00eeae9a2d6d15addfd27c87",
    "verification/wave33-rootless-motif/audit.md": "a761d48419664b3db8605ca2a7dd203c2a1ce6ccd1e96d1ac2c028b1c5209bc9",
    "verification/wave33-rootless-motif/precomparison-results.json": "68911c124a039b32b2eb5fe4c1f9886c033e17129b8b97d7a428c4bda7968253",
    "verification/wave33-rootless-motif/independent-reconstruction.md": "6a4fd85e0f87ed98cafdd581523f468f17c7818c134dd8aaba5230bd15de1c2c",
    "verification/wave33-rootless-motif/comparison-results.json": "8b7b27fd67f12bb82cb6eebf645d0c46324d7227e51bdeb0093fbcdf9d753872",
    "verification/wave33-rootless-motif/public-input-freeze.sha256": "cc1296bcd8816a9a6a15f295fec1edf1f60ac745fe9ac380325098ccd753a166",
    "verification/wave33-rootless-motif/run-report.yaml": "112ad3f84429acc426742c34e338663a7f25c5958abba067f5dbd35d7245a1fd",
    "verification/wave33-rootless-motif/precomparison-run-report.yaml": "df0518ec5007ab546e634e52e4fce91ca82d957ffb69dec358d5a6a16ab62873",
    "verification/2026-07-23-wave20-global-schur-audit.md": "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave25-n3-708-strictness/2026-07-23T215549Z-audit.md": "642255098bf424654e1a3a8c926a924ae8bf068cd422f0f367f64f9e402648de",
    "verification/wave31-sign-commutant/audit.md": "f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0",
    "agents/2026-07-24-wave31-survivor-proof.md": "075566744e2622a4dfa402a125d394aef16dfcb3fc53b172176dce88bd951aaa",
    "agents/2026-07-24-wave32-indecomposable-proof.md": "5e0e0ce6e33cd8f943d8026c2b9b01b74d9668234d4c9b2c46da6c0c9921b8ef",
    "verification/wave32-indecomposable/audit.md": "15285e618b3a38c91c5d2e373dcb859720a2062d9ca108cd79cae12506a53f44",
    "verification/wave32-indecomposable/independent-results.json": "4b90ef54358a14abc92c925c8e0f94ed9510b4f80857fde5aa4e2abf4ba89e2a",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_inputs() -> dict[str, object]:
    actual = {name: sha256(ROOT / name) for name in EXPECTED_INPUTS}
    mismatches = {
        name: {"expected": EXPECTED_INPUTS[name], "actual": actual[name]}
        for name in EXPECTED_INPUTS
        if actual[name] != EXPECTED_INPUTS[name]
    }
    freeze_path = Path(__file__).resolve().parent / "input-freeze.sha256"
    freeze_entries: dict[str, str] = {}
    for line in freeze_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(maxsplit=1)
        freeze_entries[name] = digest
    freeze_matches = freeze_entries == EXPECTED_INPUTS
    return {
        "all_match": not mismatches and freeze_matches,
        "entry_count": len(EXPECTED_INPUTS),
        "hashes": actual,
        "mismatches": mismatches,
        "freeze_file_matches_expected": freeze_matches,
    }


def outside_board(r: int, mu: int = 2) -> list[list[int]]:
    """Common-neighbor board outside two disjoint base triangles."""
    if not 0 <= r <= 3:
        raise ValueError("r must be in {0,1,2,3}")
    board: list[list[int]] = []
    for i in range(3):
        row: list[int] = []
        for j in range(3):
            adjacent = i == j and i < r
            total = 1 if adjacent else mu
            internal = int(j < r and j != i) + int(i < r and i != j)
            row.append(total - internal)
        board.append(row)
    return board


def weighted_permanent(board: list[list[int]]) -> int:
    return sum(
        board[0][p[0]] * board[1][p[1]] * board[2][p[2]]
        for p in permutations(range(3))
    )


def moved_permutation(q: int, n: int = 12) -> tuple[int, ...]:
    """One permutation with exactly q moved points, when one exists."""
    if q == 1 or not 0 <= q <= n:
        raise ValueError("a permutation cannot have exactly one moved point")
    p = list(range(n))
    if q >= 2:
        for i in range(q - 1):
            p[i] = i + 1
        p[q - 1] = 0
    return tuple(p)


def fixed_points(p: tuple[int, ...]) -> tuple[int, ...]:
    if sorted(p) != list(range(len(p))):
        raise ValueError("not a permutation")
    return tuple(i for i, image in enumerate(p) if i == image)


def disjoint_matchings() -> tuple[tuple[tuple[int, int], ...], ...]:
    """Three pairwise edge-disjoint perfect matchings on twelve labels."""
    return (
        ((0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11)),
        ((0, 2), (1, 3), (4, 6), (5, 7), (8, 10), (9, 11)),
        ((0, 3), (1, 2), (4, 7), (5, 6), (8, 11), (9, 10)),
    )


def validate_matchings(
    matchings: tuple[tuple[tuple[int, int], ...], ...], n: int = 12
) -> None:
    for matching in matchings:
        flat = [v for edge in matching for v in edge]
        if sorted(flat) != list(range(n)):
            raise ValueError("not a perfect matching")


def matching_maps(
    matchings: tuple[tuple[tuple[int, int], ...], ...], n: int = 12
) -> tuple[tuple[int, ...], ...]:
    validate_matchings(matchings, n)
    maps = []
    for matching in matchings:
        mate = [-1] * n
        for u, v in matching:
            mate[u] = v
            mate[v] = u
        maps.append(tuple(mate))
    return tuple(maps)


def fixed_fibre_relation_counts(
    fixed: Iterable[int],
    matchings: tuple[tuple[tuple[int, int], ...], ...],
) -> dict[int, int]:
    fixed_tuple = tuple(sorted(fixed))
    edge_sets = [{tuple(sorted(edge)) for edge in matching} for matching in matchings]
    counts = {r: 0 for r in range(4)}
    for i, u in enumerate(fixed_tuple):
        for v in fixed_tuple[i + 1 :]:
            multiplicity = sum((u, v) in edges for edges in edge_sets)
            counts[multiplicity] += 1
    return counts


def fibre_profiles() -> list[dict[str, object]]:
    matchings = disjoint_matchings()
    maps = matching_maps(matchings)
    profiles = []
    for q in [0, *range(2, 13)]:
        p = moved_permutation(q)
        fixed = fixed_points(p)
        counts = fixed_fibre_relation_counts(fixed, matchings)
        weighted_degree = []
        fixed_set = set(fixed)
        for i in fixed:
            weighted_degree.append(sum(mate[i] in fixed_set for mate in maps))
        profiles.append(
            {
                "q": q,
                "fixed_points": len(fixed),
                "R2_degree": 3 * q,
                "R3_degree": 12 - q,
                "relations_among_R3_neighbours": {
                    f"R{r}": counts[r] for r in range(4)
                },
                "root_motif_count_centered_here": counts[2],
                "maximum_weighted_relation_degree": max(weighted_degree, default=0),
                "laplacian_psd_decomposition": "3I-L_F=sum_{matching alpha}(I-A_alpha)[F]",
            }
        )
    return profiles


def fibre_r2_candidate_cap(
    p: tuple[int, ...],
    matchings: tuple[tuple[tuple[int, int], ...], ...],
) -> int:
    """Maximum compatible fixed transversal index for an AB-defect.

    The two fibre vertices in the R2 triangle can meet a disjoint fixed
    transversal only through their same-fibre mates.  Their two singleton
    index sets therefore have intersection of size at most one.
    """
    maps = matching_maps(matchings)
    fixed = set(fixed_points(p))
    maximum = 0
    for i in range(len(p)):
        if p[i] == i:
            continue
        candidate_a = {maps[0][i]} & fixed
        candidate_b = {maps[1][i]} & fixed
        maximum = max(maximum, len(candidate_a & candidate_b))
    return maximum


def tight_r2_candidate_witness() -> dict[str, object]:
    """A local fibre package attaining the compatible-index cap one.

    This does not realize an SRG.  Choosing the defect triangle's Z-vertex
    adjacent to c_2 would close the unique candidate and hence violate the
    rootless global premise.
    """
    p = moved_permutation(2)
    matchings = (
        ((0, 2), (1, 3), (4, 5), (6, 7), (8, 9), (10, 11)),
        ((0, 2), (1, 4), (3, 5), (6, 8), (7, 10), (9, 11)),
        ((0, 3), (1, 5), (2, 4), (6, 9), (7, 11), (8, 10)),
    )
    fixed = fixed_points(p)
    counts = fixed_fibre_relation_counts(fixed, matchings)
    return {
        "q": 2,
        "defect_index": 0,
        "unique_compatible_fixed_index": 2,
        "compatible_index_cap": fibre_r2_candidate_cap(p, matchings),
        "relations_among_fixed_transversals": {
            f"R{r}": counts[r] for r in range(4)
        },
        "centered_root_motifs_before_Z_closure": counts[2],
        "scope": "local matching-and-holonomy control, not a graph",
    }


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def projector_codegree_caps(max_off_diagonal: int = 1) -> dict[int, dict[str, object]]:
    """Schur-complement caps for common -2 neighbours of a pair.

    The base rows have norm four and inner product s.  After projecting each
    common -2 row off their span, its residual norm is d and pairwise residual
    inner products are at most c.  Nonnegativity of the squared norm of the
    residual sum gives the exact displayed caps for the endpoint alphabet.
    """
    result: dict[int, dict[str, object]] = {}
    for s in (1, 0, -1, -2):
        projection_sq = Fraction(8, 4 + s)
        diagonal = Fraction(4) - projection_sq
        off_upper = Fraction(max_off_diagonal) - projection_sq
        maximum = 0
        for m in range(1, 100):
            upper_sum_norm = m * diagonal + m * (m - 1) * off_upper
            if upper_sum_norm < 0:
                break
            maximum = m
        result[s] = {
            "projection_squared_norm": fraction_text(projection_sq),
            "residual_diagonal": fraction_text(diagonal),
            "residual_off_diagonal_upper_bound": fraction_text(off_upper),
            "maximum_common_R3": maximum,
        }
    return result


def bareiss_determinant(matrix: list[list[int]]) -> int:
    """Exact fraction-free determinant."""
    n = len(matrix)
    if n == 0:
        return 1
    a = [row[:] for row in matrix]
    sign = 1
    previous = 1
    for k in range(n - 1):
        if a[k][k] == 0:
            swap = next((i for i in range(k + 1, n) if a[i][k]), None)
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign *= -1
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * pivot - a[i][k] * a[k][j]) // previous
        previous = pivot
        for i in range(k + 1, n):
            a[i][k] = 0
        for j in range(k + 1, n):
            a[k][j] = 0
    return sign * a[-1][-1]


def r0_biclique_gram(m: int) -> list[list[int]]:
    """Gram for an R0 base pair and m pairwise-R0 common R3 rows."""
    n = m + 2
    gram = [[0] * n for _ in range(n)]
    for i in range(n):
        gram[i][i] = 4
    gram[0][1] = gram[1][0] = 1
    for i in range(2, n):
        gram[0][i] = gram[i][0] = -2
        gram[1][i] = gram[i][1] = -2
    for i in range(2, n):
        for j in range(i + 1, n):
            gram[i][j] = gram[j][i] = 1
    return gram


def matrix_vector(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def endpoint_counts() -> dict[str, object]:
    triangle_count = 231
    sum_q = 472
    ordered = {
        "Gamma": triangle_count * 18,
        "R0": triangle_count * 20 + sum_q,
        "R1": triangle_count * 180 - 3 * sum_q,
        "R2": 3 * sum_q,
        "R3": triangle_count * 12 - sum_q,
    }
    unordered = {key: value // 2 for key, value in ordered.items()}
    if sum(unordered.values()) != comb(triangle_count, 2):
        raise AssertionError("endpoint pair census does not close")
    return {
        "triangle_count": triangle_count,
        "sum_q": sum_q,
        "sum_R3_degrees": ordered["R3"],
        "ordered": ordered,
        "unordered": unordered,
    }


def local_r0_lower(b: int) -> int:
    # Each of the three perfect matchings has at most floor(b/2) edges
    # internal to the fixed-point set.  Every non-R0 pair uses at least one
    # such edge (R1, R2, and R3 use one, two, and three respectively).
    return max(0, comb(b, 2) - 3 * (b // 2))


def global_r0_wedge_lower() -> dict[str, object]:
    pointwise = []
    for b in range(13):
        g = local_r0_lower(b)
        affine = 7 * b - 40
        pointwise.append({"b": b, "g": g, "affine_floor": affine, "passes": g >= affine})
    if not all(row["passes"] for row in pointwise):
        raise AssertionError("affine lower bound failed")

    triangle_count = 231
    sum_b = 2300
    lower = 7 * sum_b - 40 * triangle_count

    # A sharp scalar witness: 226 fibres with b=10 and five with b=8.
    witness = {8: 5, 10: 226}
    witness_vertices = sum(witness.values())
    witness_sum_b = sum(b * count for b, count in witness.items())
    witness_value = sum(local_r0_lower(b) * count for b, count in witness.items())
    if (witness_vertices, witness_sum_b, witness_value) != (
        triangle_count,
        sum_b,
        lower,
    ):
        raise AssertionError("sharp scalar witness failed")

    r0_pairs = 2546

    def ceil_div(a: int, b: int) -> int:
        return -(-a // b)

    occupancy = {
        "pairs_with_codegree_at_least_1": ceil_div(lower, 5),
        "pairs_with_codegree_at_least_2": ceil_div(lower - r0_pairs, 4),
        "pairs_with_codegree_at_least_3": ceil_div(lower - 2 * r0_pairs, 3),
    }

    # Convexity of c -> binom(c,2): spread the forced R0 codegree sum as
    # evenly as possible.  The average lies between two and three.
    base_codegree, remainder = divmod(lower, r0_pairs)
    if base_codegree + bool(remainder) > 5:
        raise AssertionError("codegree cap cannot hold the forced wedge sum")
    choose2_sum = (
        (r0_pairs - remainder) * comb(base_codegree, 2)
        + remainder * comb(base_codegree + 1, 2)
    )
    if choose2_sum % 2:
        raise AssertionError("four-cycle double count must be even")
    four_cycle_lower = choose2_sum // 2

    # The R3 graph has 231 vertices and degree sum 2300.  Convexity gives the
    # minimum wedge count at ten vertices of degree nine and 221 of degree ten.
    base_degree, degree_remainder = divmod(sum_b, triangle_count)
    total_r3_wedges = (
        (triangle_count - degree_remainder) * comb(base_degree, 2)
        + degree_remainder * comb(base_degree + 1, 2)
    )
    r3_edges = sum_b // 2
    trace_fourth_lower = (
        2 * r3_edges + 4 * total_r3_wedges + 8 * four_cycle_lower
    )
    return {
        "pointwise_values": pointwise,
        "sum_b": sum_b,
        "minimum_R0_centered_wedges": lower,
        "sharp_scalar_witness_b_counts": {str(k): v for k, v in witness.items()},
        "R0_pair_count": r0_pairs,
        "codegree_cap": 5,
        "forced_occupancy": occupancy,
        "minimum_sum_binom_R0_codegree_2": choose2_sum,
        "R3_four_cycle_lower": four_cycle_lower,
        "minimum_total_R3_wedges": total_r3_wedges,
        "R3_adjacency_trace_fourth_lower": trace_fourth_lower,
    }


def build_results() -> dict[str, object]:
    input_validation = validate_inputs()
    if not input_validation["all_match"]:
        raise RuntimeError(f"frozen input mismatch: {input_validation['mismatches']}")

    boards = {
        f"R{r}": {
            "board": outside_board(r),
            "weighted_transversal_candidates": weighted_permanent(outside_board(r)),
        }
        for r in range(4)
    }
    caps = projector_codegree_caps()
    profiles = fibre_profiles()
    matchings = disjoint_matchings()
    fibre_candidate_caps = {
        str(q): fibre_r2_candidate_cap(moved_permutation(q), matchings)
        for q in [0, *range(2, 13)]
    }
    tight_candidate = tight_r2_candidate_witness()
    if tight_candidate["compatible_index_cap"] != 1:
        raise AssertionError("R2 compatible-index cap witness failed")
    determinants = {
        str(m): bareiss_determinant(r0_biclique_gram(m)) for m in range(7)
    }
    kernel = [2, 2, 1, 1, 1, 1, 1]
    if matrix_vector(r0_biclique_gram(5), kernel) != [0] * 7:
        raise AssertionError("m=5 equality kernel failed")

    counts = endpoint_counts()
    r0_lower = global_r0_wedge_lower()

    return {
        "schema_version": 1,
        "role": "clean_room_independent_verifier_precomparison",
        "claim_label": "DERIVED_PRECOMPARISON",
        "scope": (
            "Necessary actual-incidence, fibre-overlap, and projector-PSD "
            "consequences under the frozen n3=708 rootless endpoint premises"
        ),
        "independence": {
            "wave34_discovery_files_inspected": False,
            "wave34_discovery_code_imported_or_executed": False,
            "candidate_comparison_performed": False,
            "git_used": False,
        },
        "input_validation": input_validation,
        "one_leg_incidence_transport": {
            "definition": "K=N*M",
            "exact_identity": "K=9N-3AN+J",
            "entry_values": {
                "vertex_in_triangle": 4,
                "outside_vertex_adjacent_to_triangle": -2,
                "outside_vertex_nonadjacent_to_triangle": 1,
            },
            "column_census": {"4": 3, "-2": 36, "1": 60},
            "column_gram": "K^T K=63M",
            "row_gram": "K K^T=21(27I-9A+J)",
        },
        "wave33_boards": boards,
        "triangle_centred_fibres": {
            "fibre_sizes": [12, 12, 12],
            "zero_fibre_size": 60,
            "same_fibre_graph": "three copies of 6K2",
            "cross_fibre_graph": "one perfect matching for each fibre pair",
            "holonomy": (
                "after two cross matchings are normalized, the third is a "
                "permutation pi on twelve labels"
            ),
            "R3_degree": "|Fix(pi)|=12-q",
            "R2_degree": "3q, where q is the number of moved points of pi",
            "forbidden_q_values": [1],
            "allowed_q_values_with_local_controls": [0, *range(2, 13)],
            "rootless_local_profiles": profiles,
            "R2_pair_common_R3_compatible_index_cap": 1,
            "zero_closure_control_compatible_index_counts": fibre_candidate_caps,
            "compatible_index_cap_one_witness": tight_candidate,
            "motif_normalization": (
                "for a fixed centre T, two fixed labels form the forbidden "
                "R2 pair iff exactly two of the three same-fibre matchings "
                "pair those labels"
            ),
        },
        "projector_common_R3_caps": {
            "derivation": (
                "Schur complement of two norm-four M-frame rows against "
                "common rows having inner product -2 to both"
            ),
            "by_base_inner_product": {str(s): row for s, row in caps.items()},
            "by_disjoint_relation_psd_only": {
                "R0": caps[1]["maximum_common_R3"],
                "R1": caps[0]["maximum_common_R3"],
                "R2": caps[-1]["maximum_common_R3"],
                "R3": caps[-2]["maximum_common_R3"],
            },
            "actual_incidence_improvements": {
                "Gamma": 0,
                "R0": 5,
                "R1": 1,
                "R2": 1,
                "R3": 1,
            },
            "closure": (
                "if a pair has at least two common R3 triangles, the pair and "
                "every pair inside its common-neighbour set are necessarily R0"
            ),
            "R0_biclique_gram_determinants_m_0_through_6": determinants,
            "R0_codegree_5_kernel": kernel,
            "R0_codegree_5_kernel_identity": "2x+2y+z1+...+z5=0",
        },
        "endpoint_global_overlap": {
            "pair_census": counts,
            "q_distribution_consequence": (
                "sum q=472 and q!=1 force at least one triangle with q>=3"
            ),
            "rootless_R2_codegrees": "all zero",
            "mixed_trace": (
                "tr(A_R2 A_R3^2)=2 times the number of R2 pairs whose unique "
                "compatible closure is realized"
            ),
            "unrestricted_trace_cap_from_projector": 2
            * counts["unordered"]["R2"],
            "rootless_trace": 0,
            "R0_wedge_lower": r0_lower,
        },
        "status": {
            "one_leg_transport": "DERIVED",
            "q_not_equal_1": "DERIVED",
            "R2_four_candidates_reduce_to_at_most_one": "DERIVED",
            "projector_codegree_caps": "DERIVED",
            "rootless_local_matching_normal_form": "DERIVED",
            "global_R0_wedge_lower_6860": "DERIVED",
            "actual_motif_forcing": "UNKNOWN",
            "rootless_endpoint": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = json.dumps(build_results(), indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
