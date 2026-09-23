#!/usr/bin/env python3
"""Clean-room exact checks for the Wave 32 rooted-vector reduction.

This module imports no discovery code.  It checks finite arithmetic,
Gram-matrix, incidence-count, design, tensor-constant, reflection-scalar,
and hostile partial-control consequences using the Python standard library.
The human audit supplies the theorem bridges that cannot be instantiated
without a Conway-99 graph.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Iterable


REPO = Path(__file__).resolve().parents[2]
DISCOVERY_V1: dict[str, str] = {
    "agents/2026-07-24-wave32-rooted-proof.md":
        "ded47e87b82ec9a6c897b90b23e9dcac5c957678ecb0e01dcc92d16b4d4cc927",
    "attempts/wave32-rooted-vector/exact_check.py":
        "41e077321fa691a3916da50e992a09d43d4f2d252cae39030bc2d7663bd60e97",
    "attempts/wave32-rooted-vector/test_exact_check.py":
        "38b7023a66c4b3305cfb080d27cbf39dd5330dab79eaa85eb7c0fcbd3104dd76",
    "attempts/wave32-rooted-vector/exact-results.json":
        "6ff9844994c2605266feaad96b4a4ebaf193b5be437bd9e4b21dbf7b98860d99",
    "attempts/wave32-rooted-vector/input-freeze.sha256":
        "778473a5e3c872bf2c8d539b165d58d2d1329dd1224b515f6012fd628499b289",
    "attempts/wave32-rooted-vector/failed-routes.md":
        "5a45f61c3033bdd19b6f9f651931efa0a1852fc96e97fc2a9e0525d90724a706",
    "attempts/wave32-rooted-vector/run-report.yaml":
        "19d7aa1e6da04d6de618e14901121fd9543b081688ccc5f7aae85cf95634abcf",
    "attempts/wave32-rooted-vector/artifact-manifest.sha256":
        "a2dd5896871dda4d0dc54b56d9cb081993079ad03241113e1a36bb0ab972d291",
}
DISCOVERY_V2_MANIFEST: dict[str, str] = {
    "agents/2026-07-24-wave32-rooted-proof.md":
        "04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0",
    "attempts/wave32-rooted-vector/exact_check.py":
        "c753cbda03f8db54f9ad618040c87084cdafa3ce151a5810f72428815a511642",
    "attempts/wave32-rooted-vector/test_exact_check.py":
        "7f0528ab5485d78c33f24d05d9cd773ed5a5951c44052e4a3489075d33d7c7cc",
    "attempts/wave32-rooted-vector/exact-results.json":
        "9fa31703b5c4721476b1b88f217d7455615c0d92c0d6db7f150abadfc069c2a0",
    "attempts/wave32-rooted-vector/input-freeze.sha256":
        "778473a5e3c872bf2c8d539b165d58d2d1329dd1224b515f6012fd628499b289",
    "attempts/wave32-rooted-vector/failed-routes.md":
        "444b36cb1bd3d1f604687b2a7d3d3c855fa1590689d0cc1ff18f9da288f17c19",
    "attempts/wave32-rooted-vector/correction-ledger.md":
        "dd95a3d5af1156bfbdac89f2eac0decd15426b2a2261ff334a115f72ab69a2ce",
    "attempts/wave32-rooted-vector/run-report.yaml":
        "6ca9ddcbc94b23cc64c0bf0ebb2a4a7ecab413a8db579680dc785ebceee3c137",
}
FROZEN: dict[str, str] = {
    "AGENTS.md":
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3",
    "agents/2026-07-24-wave32-rooted-proof.md":
        "04990231e3b42cded363e39ffea771556e52ec66fe03a97164ae99f40ddbefe0",
    "attempts/wave32-rooted-vector/exact_check.py":
        "c753cbda03f8db54f9ad618040c87084cdafa3ce151a5810f72428815a511642",
    "attempts/wave32-rooted-vector/test_exact_check.py":
        "7f0528ab5485d78c33f24d05d9cd773ed5a5951c44052e4a3489075d33d7c7cc",
    "attempts/wave32-rooted-vector/exact-results.json":
        "9fa31703b5c4721476b1b88f217d7455615c0d92c0d6db7f150abadfc069c2a0",
    "attempts/wave32-rooted-vector/input-freeze.sha256":
        "778473a5e3c872bf2c8d539b165d58d2d1329dd1224b515f6012fd628499b289",
    "attempts/wave32-rooted-vector/failed-routes.md":
        "444b36cb1bd3d1f604687b2a7d3d3c855fa1590689d0cc1ff18f9da288f17c19",
    "attempts/wave32-rooted-vector/correction-ledger.md":
        "dd95a3d5af1156bfbdac89f2eac0decd15426b2a2261ff334a115f72ab69a2ce",
    "attempts/wave32-rooted-vector/run-report.yaml":
        "6ca9ddcbc94b23cc64c0bf0ebb2a4a7ecab413a8db579680dc785ebceee3c137",
    "attempts/wave32-rooted-vector/artifact-manifest.sha256":
        "ba6c7099e06e24fe2feee4d19021dac9ddf49cbfe99acdd54f905a6c40728b8e",
    "verification/2026-07-22-n3-side-incidence-audit.md":
        "9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787",
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/wave28-glue-discriminant/audit.md":
        "5c1dc7978d571a9471837b45a36663c7c457b6434800776501e4967146956b86",
    "verification/wave31-sign-commutant/audit.md":
        "f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0",
}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)
        .encode("utf-8")
        + b"\n"
    )


def verify_frozen() -> dict[str, str]:
    observed = {name: file_sha256(REPO / name) for name in FROZEN}
    if observed != FROZEN:
        raise AssertionError(f"frozen input drift: {observed}")
    return observed


def verify_discovery_v2_manifest() -> dict[str, object]:
    manifest_path = REPO / "attempts/wave32-rooted-vector/artifact-manifest.sha256"
    entries: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        if name in entries:
            raise AssertionError(f"duplicate discovery manifest entry: {name}")
        entries[name] = digest
    if entries != DISCOVERY_V2_MANIFEST:
        raise AssertionError(f"discovery v2 manifest content drift: {entries}")
    observed = {name: file_sha256(REPO / name) for name in entries}
    if observed != entries:
        raise AssertionError(f"discovery v2 manifest replay failed: {observed}")
    manifest_sha = file_sha256(manifest_path)
    if manifest_sha != FROZEN[
        "attempts/wave32-rooted-vector/artifact-manifest.sha256"
    ]:
        raise AssertionError("discovery v2 manifest container hash drift")
    return {
        "status": "PASS",
        "entry_count": len(entries),
        "manifest_sha256": manifest_sha,
        "entries": entries,
    }


def verify_discovery_v2_repairs() -> dict[str, object]:
    payload = json.loads(
        (REPO / "attempts/wave32-rooted-vector/exact-results.json")
        .read_text(encoding="utf-8")
    )
    remaining = payload["hostile_partial_control"][
        "outside_remaining_degree_distribution"
    ]
    hostile_q3 = payload["hostile_eigenvalue_minus_three"]
    if remaining != {"10": 42, "12": 28, "14": 15}:
        raise AssertionError(f"discovery v2 residual-degree repair failed: {remaining}")
    if not (
        hostile_q3["eigenvalue_magnitude"] == 3
        and hostile_q3["coordinate_bound_abs_values"] == [0, 1, 2]
        and hostile_q3["surviving_distribution_count"] == 3
        and any(
            "3*m<=positive_mass" in statement
            for statement in hostile_q3["proof_inequalities"]
        )
    ):
        raise AssertionError(f"discovery v2 hostile-q3 repair failed: {hostile_q3}")
    ledger = (
        REPO / "attempts/wave32-rooted-vector/correction-ledger.md"
    ).read_text(encoding="utf-8")
    retained_v1 = {
        name: digest
        for name, digest in DISCOVERY_V1.items()
        if name.endswith((
            "exact_check.py",
            "test_exact_check.py",
            "exact-results.json",
            "artifact-manifest.sha256",
        ))
    }
    if any(digest not in ledger for digest in retained_v1.values()):
        raise AssertionError("discovery correction ledger lost a designated v1 hash")
    return {
        "status": "PASS",
        "remaining_degree_distribution": remaining,
        "hostile_q3": {
            "eigenvalue_magnitude": hostile_q3["eigenvalue_magnitude"],
            "coordinate_bound_abs_values":
                hostile_q3["coordinate_bound_abs_values"],
            "surviving_distribution_count":
                hostile_q3["surviving_distribution_count"],
        },
        "ledger_retained_v1_hashes": retained_v1,
    }


def det_bareiss(matrix: list[list[int]]) -> int:
    """Exact determinant for a square integer matrix."""
    n = len(matrix)
    if n == 0:
        return 1
    work = [row[:] for row in matrix]
    sign = 1
    denominator = 1
    for column in range(n - 1):
        pivot = next(
            (row for row in range(column, n) if work[row][column]),
            None,
        )
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        for row in range(column + 1, n):
            for col in range(column + 1, n):
                numerator = (
                    work[row][col] * pivot_value
                    - work[row][column] * work[column][col]
                )
                if numerator % denominator:
                    raise AssertionError("Bareiss division was not exact")
                work[row][col] = numerator // denominator
        denominator = pivot_value
        for row in range(column + 1, n):
            work[row][column] = 0
    return sign * work[n - 1][n - 1]


def principal_psd(matrix: list[list[int]]) -> bool:
    n = len(matrix)
    return all(
        det_bareiss([[matrix[i][j] for j in subset] for i in subset]) >= 0
        for size in range(1, n + 1)
        for subset in itertools.combinations(range(n), size)
    )


def maximal_minor_gcd(matrix: list[list[int]]) -> int:
    """GCD of full-column-rank maximal minors."""
    rows = len(matrix)
    cols = len(matrix[0])
    values = []
    for chosen in itertools.combinations(range(rows), cols):
        values.append(
            abs(det_bareiss([[matrix[i][j] for j in range(cols)] for i in chosen]))
        )
    result = 0
    for value in values:
        result = math.gcd(result, value)
    return result


def primitive_image_controls() -> dict[str, object]:
    primitive = [[1, 0], [0, 1], [1, 1]]
    nonprimitive = [[2, 0], [0, 1], [0, 0]]
    primitive_index = maximal_minor_gcd(primitive)
    nonprimitive_index = maximal_minor_gcd(nonprimitive)
    # Explicit ambient preimages for the standard coordinate functionals.
    right_preimages = [[1, 0, 0], [0, 1, 0]]
    transpose_images = [
        [
            sum(primitive[row][col] * vector[row] for row in range(3))
            for col in range(2)
        ]
        for vector in right_preimages
    ]
    if primitive_index != 1 or transpose_images != [[1, 0], [0, 1]]:
        raise AssertionError("primitive transpose-surjectivity control failed")
    if nonprimitive_index != 2:
        raise AssertionError("nonprimitive Smith-index control failed")
    # First coordinate of X^T c is always even in the hostile control.
    hostile_target_has_preimage = any(
        [
            2 * c0,
            c1,
        ] == [1, 0]
        for c0 in range(-3, 4)
        for c1 in range(-3, 4)
    )
    if hostile_target_has_preimage:
        raise AssertionError("nonprimitive hostile target unexpectedly lifted")
    return {
        "theorem_bridge": (
            "For a primitive column lattice, Smith invariants are all one; "
            "the same invariants govern X^T, hence X^T is onto."
        ),
        "primitive_maximal_minor_gcd": primitive_index,
        "explicit_transpose_images": transpose_images,
        "hostile_nonprimitive_maximal_minor_gcd": nonprimitive_index,
        "hostile_target_r": [1, 0],
        "hostile_target_has_integral_preimage": hostile_target_has_preimage,
        "root_image_consequence": "choose X^T c=r, then y=XSr=XSX^T c=Mc",
    }


def projector_transport() -> dict[str, object]:
    eigenvalues = (14, 3, -4)
    projector = {
        value: Fraction(27 - 9 * value + (99 if value == 14 else 0), 63)
        for value in eigenvalues
    }
    if projector != {14: Fraction(0), 3: Fraction(0), -4: Fraction(1)}:
        raise AssertionError("minus-four projector coefficients failed")
    # For an incidence column n with column sum three:
    # (J/3)n=1, while (9I-3A)n vanishes entrywise modulo three.
    sample_incidence_column = [1, 1, 1] + [0] * 96
    j_over_three_times_column = sum(sample_incidence_column) // 3
    if j_over_three_times_column != 1:
        raise AssertionError("incidence column-sum normalization failed")
    return {
        "projector_values": {str(key): str(value) for key, value in projector.items()},
        "incidence_column_sum": sum(sample_incidence_column),
        "J_over_3_times_incidence_column": j_over_three_times_column,
        "derived_identity": "NM=(9I-3A)N+J_(99x231)",
        "mod_3_column": [1] * 99,
        "transported_root": {
            "z": "Ny",
            "Az": "-4z",
            "sum_z": 0,
            "norm_z_squared": 126,
            "N_transpose_z": "3y",
        },
    }


def residue_screen(norm_z_squared: int = 126) -> dict[str, object]:
    rows = []
    for residue in (-1, 0, 1):
        sum_k = -33 * residue
        numerator = norm_z_squared + 99 * residue * residue
        integral = numerator % 9 == 0
        norm_k = numerator // 9 if integral else None
        lower = abs(sum_k)
        accepted = bool(integral and norm_k is not None and norm_k >= lower)
        rows.append({
            "residue": residue,
            "sum_k": sum_k,
            "norm_k_squared": norm_k,
            "absolute_sum_lower_bound": lower,
            "accepted_by_integer_norm_bound": accepted,
        })
    if norm_z_squared == 126:
        retained = [row["residue"] for row in rows if row["accepted_by_integer_norm_bound"]]
        if retained != [0]:
            raise AssertionError(f"nonzero residue was not excluded: {rows}")
    return {"norm_z_squared": norm_z_squared, "cases": rows}


def all_norm14_distributions() -> list[dict[int, int]]:
    values = list(range(-3, 4))
    answers: list[dict[int, int]] = []

    def search(
        position: int,
        count_left: int,
        sum_left: int,
        norm_left: int,
        chosen: list[int],
    ) -> None:
        if position == len(values):
            if count_left == sum_left == norm_left == 0:
                answers.append({
                    value: count
                    for value, count in zip(values, chosen)
                    if count
                })
            return
        value = values[position]
        cap = count_left
        if value:
            cap = min(cap, norm_left // (value * value))
        for count in range(cap + 1):
            search(
                position + 1,
                count_left - count,
                sum_left - value * count,
                norm_left - value * value * count,
                chosen + [count],
            )

    search(0, 99, 0, 14, [])
    answers.sort(key=lambda item: tuple(item.get(value, 0) for value in values))
    return answers


def allowed_amplitudes(eigenvalue_magnitude: int) -> list[int]:
    coefficient = 2 * eigenvalue_magnitude - 1
    return [
        magnitude
        for magnitude in range(4)
        if 14 - magnitude * magnitude >= coefficient * magnitude
    ]


def amplitude_screen() -> dict[str, object]:
    distributions = all_norm14_distributions()
    allowed_four = allowed_amplitudes(4)
    allowed_three = allowed_amplitudes(3)
    def passes(item: dict[int, int], eigenvalue_magnitude: int, allowed: list[int]) -> bool:
        maximum = max(abs(value) for value in item)
        positive_mass = sum(
            value * count for value, count in item.items() if value > 0
        )
        return (
            maximum in allowed
            and eigenvalue_magnitude * maximum <= positive_mass
        )
    survivors_four = [
        item for item in distributions if passes(item, 4, allowed_four)
    ]
    survivors_three = [
        item for item in distributions if passes(item, 3, allowed_three)
    ]
    expected = [{-1: 7, 0: 85, 1: 7}]
    if len(distributions) != 12 or survivors_four != expected:
        raise AssertionError(
            f"integer amplitude census failed: {len(distributions)}, {survivors_four}"
        )
    hostile_witness = {-1: 6, 0: 88, 1: 4, 2: 1}
    if hostile_witness not in survivors_three:
        raise AssertionError("minus-three hostile amplitude witness was lost")
    return {
        "raw_distribution_count": len(distributions),
        "minus_four_allowed_absolute_values": allowed_four,
        "minus_four_survivors": [
            {str(key): value for key, value in item.items()}
            for item in survivors_four
        ],
        "minus_three_allowed_absolute_values": allowed_three,
        "minus_three_survivor_count": len(survivors_three),
        "minus_three_hostile_witness": {
            str(key): value for key, value in hostile_witness.items()
        },
        "necessary_inequalities": [
            "14-a^2 >= (2q-1)|a| for eigenvalue -q",
            "q*max_abs <= positive_mass <= 7",
        ],
    }


def root_pattern_census() -> dict[str, object]:
    moments = []
    tensor = []
    extreme = []
    for plus_two in range(15):
        for plus_one in range(43):
            for minus_one in range(43):
                for minus_two in range(15):
                    nonzero = plus_two + plus_one + minus_one + minus_two
                    if nonzero > 231:
                        continue
                    if 2 * plus_two + plus_one - minus_one - 2 * minus_two:
                        continue
                    if 4 * plus_two + plus_one + minus_one + 4 * minus_two != 42:
                        continue
                    record = {
                        "plus_2": plus_two,
                        "plus_1": plus_one,
                        "zero": 231 - nonzero,
                        "minus_1": minus_one,
                        "minus_2": minus_two,
                        "cube_sum": 8 * plus_two + plus_one - minus_one - 8 * minus_two,
                    }
                    moments.append(record)
                    if record["cube_sum"] ** 2 <= 8 * 60:
                        tensor.append(record)
                        if plus_two <= 3 and minus_two <= 3:
                            extreme.append(record)
    final = [
        record for record in extreme
        if record["plus_2"] == record["minus_2"] == 0
    ]
    counts = {
        "moment_only": len(moments),
        "tensor_energy": len(tensor),
        "extreme_fiber": len(extreme),
        "no_extreme_coordinates": len(final),
    }
    if counts != {
        "moment_only": 46,
        "tensor_energy": 32,
        "extreme_fiber": 16,
        "no_extreme_coordinates": 1,
    }:
        raise AssertionError(f"root-pattern census failed: {counts}")
    return {"counts": counts, "final_pattern": final[0]}


def extreme_fiber_census(pair_alphabet: tuple[int, ...] = (-2, -1)) -> dict[str, object]:
    counts: dict[str, int] = {}
    witnesses: dict[str, list[list[list[int]]]] = {}
    for size in range(1, 5):
        pairs = list(itertools.combinations(range(size), 2))
        accepted = []
        for off_diagonal in itertools.product(pair_alphabet, repeat=len(pairs)):
            gram = [[2 if i == j else 0 for j in range(size)] for i in range(size)]
            for (left, right), value in zip(pairs, off_diagonal):
                gram[left][right] = gram[right][left] = value
            if principal_psd(gram):
                accepted.append(gram)
        counts[str(size)] = len(accepted)
        witnesses[str(size)] = accepted
    if pair_alphabet == (-2, -1):
        if counts != {"1": 1, "2": 2, "3": 1, "4": 0}:
            raise AssertionError(f"extreme Gram census failed: {counts}")
        triple = witnesses["3"][0]
        if [sum(row) for row in triple] != [0, 0, 0]:
            raise AssertionError("unique triple does not have zero sum")
    return {
        "pair_alphabet": list(pair_alphabet),
        "psd_counts": counts,
        "size_three_gram": witnesses["3"][0] if witnesses["3"] else None,
        "size_four_survives": bool(witnesses["4"]),
    }


def fano_complement() -> list[list[int]]:
    """Complement of the seven-point Fano incidence matrix."""
    result = []
    for normal in range(1, 8):
        line = [
            1 if (normal & point).bit_count() % 2 == 0 else 0
            for point in range(1, 8)
        ]
        result.append([1 - entry for entry in line])
    return result


def design_forcing(mu: int = 2) -> dict[str, object]:
    rows = []
    for t in range(11):
        lower = 42 + 7 * t
        upper = t + mu * (21 - t)
        rows.append({
            "same_sign_edges": t,
            "coarse_opposite_common_neighbor_lower": lower,
            "lambda_mu_upper": upper,
            "passes": lower <= upper,
        })
    passing = [row["same_sign_edges"] for row in rows if row["passes"]]
    if mu == 2 and passing != [0]:
        raise AssertionError(f"lambda/mu saturation failed: {rows}")
    matrix = fano_complement()
    row_sums = [sum(row) for row in matrix]
    column_sums = [sum(matrix[row][col] for row in range(7)) for col in range(7)]
    row_intersections = [
        sum(matrix[i][col] * matrix[j][col] for col in range(7))
        for i, j in itertools.combinations(range(7), 2)
    ]
    column_intersections = [
        sum(matrix[row][i] * matrix[row][j] for row in range(7))
        for i, j in itertools.combinations(range(7), 2)
    ]
    if not (
        row_sums == [4] * 7
        and column_sums == [4] * 7
        and row_intersections == [2] * 21
        and column_intersections == [2] * 21
    ):
        raise AssertionError("Fano-complement equations failed")
    return {
        "mu": mu,
        "count_rows": rows,
        "passing_same_sign_edge_counts": passing,
        "cross_matrix": matrix,
        "row_sums": row_sums,
        "column_sums": column_sums,
        "same_side_intersections": sorted(set(row_intersections)),
        "matrix_equation": "C C^T=2I+2J",
        "complement": "the unique 2-(7,3,1) Fano-plane design",
    }


def outside_triangle_census() -> dict[str, object]:
    support_vertices = 14
    support_cross_edges = 7 * 4
    support_outside_incidences = support_vertices * (14 - 4)
    outside_with_pair = support_outside_incidences // 2
    outside_without_support = 85 - outside_with_pair
    cross_nonedges = 7 * 7 - support_cross_edges
    edge_completions = support_cross_edges
    nonedge_completions = 2 * cross_nonedges
    one_support_positive = 7 * (7 - 4)
    one_support_negative = one_support_positive
    two_support_triangles = support_cross_edges
    disjoint_triangles = 231 - (
        one_support_positive
        + one_support_negative
        + two_support_triangles
    )
    values = (
        [1] * one_support_positive
        + [-1] * one_support_negative
        + [0] * (two_support_triangles + disjoint_triangles)
    )
    if not (
        outside_with_pair == 70
        and outside_without_support == 15
        and edge_completions == 28
        and nonedge_completions == 42
        and values.count(1) == values.count(-1) == 21
        and values.count(0) == 189
    ):
        raise AssertionError("outside or triangle census failed")
    return {
        "outside_support_incidences": support_outside_incidences,
        "outside_types": {
            "support_edge_completion": edge_completions,
            "support_nonedge_completion": nonedge_completions,
            "no_support_neighbor": outside_without_support,
        },
        "triangle_types": {
            "one_positive_support": one_support_positive,
            "one_negative_support": one_support_negative,
            "two_opposite_support": two_support_triangles,
            "disjoint_from_support": disjoint_triangles,
        },
        "root_triangle_pattern": {
            "plus_1": values.count(1),
            "zero": values.count(0),
            "minus_1": values.count(-1),
        },
        "identity": "N^T k=y, so each triangle value is its signed support sum",
    }


def _perfect_matching_avoiding_groups(
    vertices: list[int],
    group: dict[int, int],
) -> list[tuple[int, int]]:
    if not vertices:
        return []
    first = vertices[0]
    for index in range(1, len(vertices)):
        second = vertices[index]
        if group[first] == group[second]:
            continue
        rest = vertices[1:index] + vertices[index + 1:]
        try:
            return [(first, second)] + _perfect_matching_avoiding_groups(rest, group)
        except ValueError:
            pass
    raise ValueError("no group-avoiding perfect matching")


def hostile_partial_control() -> dict[str, object]:
    cross = fano_complement()
    adjacency = [set() for _ in range(99)]

    def connect(left: int, right: int) -> None:
        if left == right:
            raise AssertionError("loop")
        adjacency[left].add(right)
        adjacency[right].add(left)

    edge_completion_ids: list[int] = []
    nonedge_ids: dict[tuple[int, int, int], int] = {}
    cursor = 14
    for p in range(7):
        for r in range(7):
            if cross[p][r]:
                connect(p, 7 + r)
                edge_completion_ids.append(cursor)
                connect(cursor, p)
                connect(cursor, 7 + r)
                cursor += 1
    if cursor != 42:
        raise AssertionError("edge-completion allocation failed")
    for p in range(7):
        for r in range(7):
            if cross[p][r]:
                continue
            for copy in range(2):
                nonedge_ids[(p, r, copy)] = cursor
                connect(cursor, p)
                connect(cursor, 7 + r)
                cursor += 1
    if cursor != 84:
        raise AssertionError("nonedge-completion allocation failed")
    no_support_ids = list(range(84, 99))

    matching_edges: set[tuple[int, int]] = set()
    for p in range(7):
        entries = [
            nonedge_ids[(p, r, copy)]
            for r in range(7)
            if not cross[p][r]
            for copy in range(2)
        ]
        groups = {
            nonedge_ids[(p, r, copy)]: r
            for r in range(7)
            if not cross[p][r]
            for copy in range(2)
        }
        for left, right in _perfect_matching_avoiding_groups(entries, groups):
            matching_edges.add(tuple(sorted((left, right))))
            connect(left, right)
    for r in range(7):
        entries = [
            nonedge_ids[(p, r, copy)]
            for p in range(7)
            if not cross[p][r]
            for copy in range(2)
        ]
        groups = {
            nonedge_ids[(p, r, copy)]: p
            for p in range(7)
            if not cross[p][r]
            for copy in range(2)
        }
        for left, right in _perfect_matching_avoiding_groups(entries, groups):
            edge = tuple(sorted((left, right)))
            if edge in matching_edges:
                raise AssertionError("positive/negative matching collision")
            matching_edges.add(edge)
            connect(left, right)
    if len(matching_edges) != 42:
        raise AssertionError("singleton-triangle edge count failed")

    support = set(range(14))
    degrees = [len(neighbors) for neighbors in adjacency]
    if degrees[:14] != [14] * 14:
        raise AssertionError("support degrees not saturated")
    common_by_support_pair: dict[str, list[int]] = {"edge": [], "nonedge": []}
    for left, right in itertools.combinations(range(14), 2):
        common = len(adjacency[left] & adjacency[right])
        category = "edge" if right in adjacency[left] else "nonedge"
        common_by_support_pair[category].append(common)
    if set(common_by_support_pair["edge"]) != {1}:
        raise AssertionError("support-edge lambda failed")
    if set(common_by_support_pair["nonedge"]) != {2}:
        raise AssertionError("support-nonedge mu failed")

    for support_vertex in support:
        for neighbor in adjacency[support_vertex]:
            if len(adjacency[support_vertex] & adjacency[neighbor]) != 1:
                raise AssertionError("support-incident edge lacks unique triangle")

    signed = [1] * 7 + [-1] * 7 + [0] * 85
    if [
        sum(signed[neighbor] for neighbor in adjacency[vertex])
        for vertex in range(99)
    ] != [-4 * value for value in signed]:
        raise AssertionError("partial signed eigenvector failed")

    edge_completion_degrees = [degrees[vertex] for vertex in edge_completion_ids]
    nonedge_completion_degrees = [
        degrees[vertex] for vertex in sorted(nonedge_ids.values())
    ]
    no_support_degrees = [degrees[vertex] for vertex in no_support_ids]
    current_degree_histogram = {
        str(value): degrees.count(value) for value in sorted(set(degrees))
    }
    remaining = {
        "support_edge_completion": 14 - edge_completion_degrees[0],
        "support_nonedge_completion": 14 - nonedge_completion_degrees[0],
        "no_support_neighbor": 14 - no_support_degrees[0],
    }
    if remaining != {
        "support_edge_completion": 12,
        "support_nonedge_completion": 10,
        "no_support_neighbor": 14,
    }:
        raise AssertionError(f"remaining-degree correction failed: {remaining}")
    edge_count = sum(degrees) // 2
    if edge_count != 210:
        raise AssertionError(f"partial edge count failed: {edge_count}")
    return {
        "status": "PARTIAL_LOCAL_CONTROL_NOT_EXTENDIBILITY_EVIDENCE",
        "vertex_count": 99,
        "edge_count": edge_count,
        "current_degree_histogram": current_degree_histogram,
        "support_degrees": degrees[:14],
        "support_pair_common_neighbors": {
            key: sorted(set(values)) for key, values in common_by_support_pair.items()
        },
        "outside_support_degree_histogram": {
            "0": 15,
            "2": 70,
        },
        "singleton_triangle_matching_edges": len(matching_edges),
        "correct_remaining_degrees": remaining,
        "candidate_v1_stated_remaining_degrees": [8, 12, 14],
        "candidate_v1_correction": [10, 12, 14],
        "discovery_v2_remaining_degree_distribution": {
            "10": 42,
            "12": 28,
            "14": 15,
        },
    }


def tensor_schur_constraints() -> dict[str, object]:
    orthogonal_dimension = 43
    trace_lift = Fraction(3, orthogonal_dimension + 2)
    if trace_lift != Fraction(1, 15):
        raise AssertionError("trace-lift coefficient failed")
    # 60 >= (3+1/15)w2 + 3A2 = 46/15 w2 + 3A2.
    w_coefficient = Fraction(46, 15)
    g_bound_multiplier = Fraction(23, 30)  # coefficient on g2=4w2
    if w_coefficient / 4 != g_bound_multiplier:
        raise AssertionError("double-contraction coefficient failed")
    max_g_numerator = Fraction(60, 1) / g_bound_multiplier
    if max_g_numerator != Fraction(1800, 23):
        raise AssertionError("double-contraction bound failed")
    # H2=4w2+2A2.  The worst ratio to the norm budget is 30/23.
    ratio_w = Fraction(4, 1) / w_coefficient
    ratio_a = Fraction(2, 3)
    if max(ratio_w, ratio_a) != Fraction(30, 23):
        raise AssertionError("first-contraction optimization failed")

    possible_h2 = [
        value for value in range(1, 79)
        if value % 4 == 2 and 23 * value <= 1800
    ]
    possible_g2 = [
        value for value in range(0, 79)
        if value % 8 == 6 and 23 * value <= 1800
    ]
    f_values = [(1134 - value) // 8 for value in possible_g2]
    if possible_g2 != [6, 14, 22, 30, 38, 46, 54, 62, 70, 78]:
        raise AssertionError("g2 list failed")
    if f_values != list(range(141, 131, -1)):
        raise AssertionError("f list failed")

    # Independently rebuild the incidence constants for v=Np:
    v_norm_squared = 14 * 3 * 3 + 42 * 2 * 2
    v_sum = 14 * 3 + 42 * 2
    fixed_adjacency_quadratic = 2 * (28 * 3 * 3 + 84 * 3 * 2)
    constant = (
        3 * v_norm_squared
        + Fraction(v_sum * v_sum, 9)
        - fixed_adjacency_quadratic
    )
    if (
        v_norm_squared != 294
        or v_sum != 126
        or fixed_adjacency_quadratic != 1512
        or constant != 1134
    ):
        raise AssertionError("incidence contraction constants failed")

    # D=(W-M)/2 has even diagonal 6, so y^TDy is even and
    # H2=21*42+2*y^TDy is 2 mod 4.
    base_h2 = 21 * 42
    if base_h2 % 4 != 2:
        raise AssertionError("H2 base congruence failed")
    hostile_odd_diagonal_congruence = (base_h2 + 2) % 4
    if hostile_odd_diagonal_congruence != 0:
        raise AssertionError("odd-diagonal hostile control failed")
    return {
        "orthogonal_dimension": orthogonal_dimension,
        "minimum_trace_lift_norm_factor": str(trace_lift),
        "tensor_budget": "60 >= (46/15)w2+3A2",
        "double_contraction_bound": "23g2<=1800",
        "first_contraction_bound": "23H2<=1800",
        "H2_mod_4": base_h2 % 4,
        "possible_H2": possible_h2,
        "incidence_constants": {
            "norm_Np_squared": v_norm_squared,
            "sum_Np": v_sum,
            "fixed_Np_A_Np": fixed_adjacency_quadratic,
            "g2_formula": "1134-8f",
        },
        "possible_g2": possible_g2,
        "corresponding_f": f_values,
        "A4_identity": "y^T(MWM)y=(My)^T W(My)=441 y^T W y",
        "hostile_odd_D_diagonal_changes_H2_mod_4_to": hostile_odd_diagonal_congruence,
    }


def reflection_constraints() -> dict[str, object]:
    y_norm = 42
    coefficient = Fraction(1, 21)
    # (I-c yy^T)^2=I+(-2c+c^2||y||^2)yy^T.
    involution_error = -2 * coefficient + coefficient * coefficient * y_norm
    hostile_error = -2 * Fraction(1, 42) + Fraction(1, 42) ** 2 * y_norm
    if involution_error != 0 or hostile_error == 0:
        raise AssertionError("coordinate reflection coefficient failed")
    z_norm = 126
    vertex_coefficient = Fraction(1, 63)
    vertex_error = (
        -2 * vertex_coefficient
        + vertex_coefficient * vertex_coefficient * z_norm
    )
    if vertex_error:
        raise AssertionError("vertex reflection coefficient failed")
    if Fraction(9, 63) != Fraction(1, 7):
        raise AssertionError("z=3k reflection scaling failed")
    return {
        "coordinate_reflection": "I-yy^T/21",
        "coordinate_involution_error": str(involution_error),
        "hostile_denominator_42_error": str(hostile_error),
        "vertex_reflection": "I-zz^T/63=I-kk^T/7",
        "vertex_involution_error": str(vertex_error),
        "factorization_identity": "y^T X=21r^T => H_r X=X-y r^T",
        "commutant_identity": "y in im(E) => H_r E=E H_r and H_r M H_r=M",
        "not_coordinate_permutation_witness": "off-diagonal support entries are +/-1/21",
    }


def build_results() -> dict[str, object]:
    frozen = verify_frozen()
    discovery_manifest = verify_discovery_v2_manifest()
    discovery_repairs = verify_discovery_v2_repairs()
    primitive = primitive_image_controls()
    transport = projector_transport()
    residues = residue_screen()
    hostile_norm = residue_screen(198)
    amplitudes = amplitude_screen()
    patterns = root_pattern_census()
    fibers = extreme_fiber_census()
    hostile_fibers = extreme_fiber_census((-2, -1, 0))
    design = design_forcing()
    hostile_design = design_forcing(3)
    outside = outside_triangle_census()
    partial = hostile_partial_control()
    tensor = tensor_schur_constraints()
    reflection = reflection_constraints()
    return {
        "schema_version": 1,
        "claim_label": "VERIFIED",
        "overall_status": "VERIFIED_SCOPED_V2_WITH_V1_CORRECTION_RETAINED",
        "frozen_inputs": frozen,
        "discovery_chronology": {
            "v1": {
                "status": "SUPERSEDED_PREPUBLICATION_AFTER_NONBLOCKING_DEFECT",
                "frozen_hashes": DISCOVERY_V1,
                "defect": (
                    "partial-control metadata said remaining degrees "
                    "8,12,14; independent reconstruction gave 10,12,14"
                ),
            },
            "v2": {
                "status": "CORRECTED_BYTES_VERIFIED",
                "manifest_replay": discovery_manifest,
                "repair_replay": discovery_repairs,
                "repairs": [
                    "remaining degree distribution is 10^42,12^28,14^15",
                    "hostile q=3 metadata is parameter-derived",
                ],
            },
        },
        "primitive_image_bridge": primitive,
        "projector_incidence_transport": transport,
        "mod_3_residue_screen": residues,
        "hostile_norm_198_residue_screen": hostile_norm,
        "integer_minus_four_amplitude": amplitudes,
        "root_pattern_census": patterns,
        "matrix_only_extreme_fibers": fibers,
        "hostile_relaxed_extreme_alphabet": hostile_fibers,
        "support_design": design,
        "hostile_mu_3_design_count": hostile_design,
        "outside_and_triangle_census": outside,
        "hostile_partial_control": partial,
        "tensor_schur_A4": tensor,
        "root_reflection": reflection,
        "obligations": [
            {"id": "frozen_bytes", "status": "PASS"},
            {"id": "discovery_v2_manifest_replay", "status": "PASS"},
            {"id": "primitive_XT_surjectivity_and_y_in_MZ", "status": "PASS"},
            {"id": "NM_mod_3_transport", "status": "PASS"},
            {"id": "nonzero_residue_exclusion", "status": "PASS"},
            {"id": "minus_four_amplitude_and_7_plus_7", "status": "PASS"},
            {"id": "Fano_complement_support", "status": "PASS"},
            {"id": "outside_census_and_21_189_21_pattern", "status": "PASS"},
            {"id": "matrix_only_32_to_16", "status": "PASS"},
            {"id": "tensor_Schur_A4_constraints", "status": "PASS"},
            {"id": "root_reflection_scope", "status": "PASS"},
            {
                "id": "candidate_v1_partial_control_remaining_degree_text",
                "status": "FAIL",
                "impact": "NONBLOCKING_HISTORICAL_REPAIRED_IN_V2",
                "correction": "8 must be 10; exact remaining degrees are 10,12,14",
            },
            {
                "id": "discovery_v2_partial_control_remaining_degrees",
                "status": "PASS",
            },
            {
                "id": "discovery_v2_hostile_q3_metadata",
                "status": "PASS",
            },
            {"id": "partial_control_extendibility", "status": "UNKNOWN"},
            {"id": "root_exclusion", "status": "UNKNOWN"},
            {"id": "rooted_endpoint", "status": "UNKNOWN"},
            {"id": "n3_708", "status": "UNKNOWN"},
            {"id": "Conway_99", "status": "UNKNOWN"},
            {"id": "novelty", "status": "UNKNOWN"},
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = canonical_json(build_results())
    if args.output:
        args.output.write_bytes(encoded)
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
