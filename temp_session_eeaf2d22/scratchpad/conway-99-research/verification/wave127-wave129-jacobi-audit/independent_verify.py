"""Independent exact audit of the sealed Wave 127 and Wave 129 packages.

No discovery module or verification routine is imported.  The verifier
checks the sealed Fourier-column caches directly, rebuilds every finite
constraint row, and evaluates each rational candidate with Fraction
arithmetic.  It also reconstructs the modular dimensions and exact ranks of
the Eisenstein-product spanning families.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import pickle
from collections import Counter
from fractions import Fraction
from pathlib import Path


Q = Fraction
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
W127 = ROOT / "attempts" / "wave127-independent-jacobi-certificate"
W129 = ROOT / "attempts" / "wave129-jacobi-stress"
MODEL_VERSION = "wave127-fricke-eigen-model-v1"
LEVEL = 7
WEIGHT = 22
INDEX_L = 10
INDEX_K = 70
QDISC = 16
CHARACTER = (0, 1, 1, -1, 1, -1, -1)
MANIFESTS = {
    W127 / "MANIFEST.sha256":
        "f4a1039928dcbd21e8de81f199265c80631182ec53f51d8c7e657259ee2f5fe4",
    W129 / "MANIFEST.sha256":
        "93e1f208faec2187ed3339e131af670d181a63a9518e6fd39ef0939540d79e5b",
}
CACHE_PATHS = {
    10: W127 / "columns-cutoff10.pkl",
    12: W127 / "columns-cutoff12.pkl",
    14: W127 / "columns-cutoff14.pkl",
    16: W127 / "columns-cutoff16.pkl",
    18: W129 / "columns-cutoff18.pkl",
    20: W129 / "columns-cutoff20.pkl",
    28: W129 / "columns-cutoff28.pkl",
}
CANDIDATE_PATHS = {
    10: W127 / "exact-candidate-cutoff10.json",
    12: W127 / "exact-candidate-cutoff12.json",
    14: W127 / "exact-candidate-cutoff14.json",
    16: W127 / "exact-candidate-cutoff16.json",
    18: W129 / "exact-candidate-cutoff18.json",
    20: W129 / "exact-candidate-cutoff20.json",
    28: W129 / "exact-candidate-cutoff28.json",
}
SAVED_VERIFICATIONS = {
    10: W127 / "verification-cutoff10.json",
    12: W127 / "verification-cutoff12.json",
    14: W127 / "verification-cutoff14.json",
    16: W127 / "verification-cutoff16.json",
    18: W129 / "verification-cutoff18.json",
    20: W129 / "verification-cutoff20.json",
}
EXPECTED_COUNTS = {
    10: (282, 320, 263),
    12: (304, 436, 300),
    14: (326, 562, 332),
    16: (346, 700, 344),
    18: (366, 846, 381),
    20: (386, 1000, 396),
}
EXPECTED_DIMENSIONS = [15, 17, 17, 19, 21, 21, 23, 25, 25, 27, 29]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def canonical(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def free_memory_percent() -> float:
    if os.name != "nt":
        return 100.0

    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("length", ctypes.c_ulong),
            ("load", ctypes.c_ulong),
            ("total_phys", ctypes.c_ulonglong),
            ("available_phys", ctypes.c_ulonglong),
            ("total_page", ctypes.c_ulonglong),
            ("available_page", ctypes.c_ulonglong),
            ("total_virtual", ctypes.c_ulonglong),
            ("available_virtual", ctypes.c_ulonglong),
            ("available_extended", ctypes.c_ulonglong),
        ]

    state = MemoryStatus()
    state.length = ctypes.sizeof(state)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state))),
        "GlobalMemoryStatusEx failed",
    )
    return 100.0 * state.available_phys / state.total_phys


def preinspect_manifests() -> dict[str, object]:
    details: dict[str, object] = {}
    for manifest, expected_hash in MANIFESTS.items():
        require(sha256(manifest) == expected_hash, f"manifest drift: {manifest}")
        entries = 0
        for line in manifest.read_text(encoding="utf-8").splitlines():
            expected, name = line.split("  ", 1)
            require(
                sha256(manifest.parent / name) == expected,
                f"sealed entry drift: {manifest.parent / name}",
            )
            entries += 1
        details[manifest.parent.name] = {
            "manifest_sha256": expected_hash,
            "entries_checked": entries,
        }
    require(
        details["wave127-independent-jacobi-certificate"]["entries_checked"] == 55,
        "Wave127 manifest count drift",
    )
    require(
        details["wave129-jacobi-stress"]["entries_checked"] == 16,
        "Wave129 manifest count drift",
    )
    return details


def bernoulli_numbers(limit: int) -> list[Q]:
    values = [Q(0)] * (limit + 1)
    values[0] = Q(1)
    for n in range(1, limit + 1):
        values[n] = -sum(
            Q(math.comb(n + 1, j)) * values[j] for j in range(n)
        ) / Q(n + 1)
    return values


BERNOULLI = bernoulli_numbers(42)


def character(n: int) -> int:
    return CHARACTER[n % LEVEL]


def bernoulli_polynomial(degree: int, x: Q) -> Q:
    return sum(
        Q(math.comb(degree, j))
        * BERNOULLI[j]
        * x ** (degree - j)
        for j in range(degree + 1)
    )


def generalized_bernoulli(degree: int) -> Q:
    return Q(LEVEL ** (degree - 1)) * sum(
        Q(character(a)) * bernoulli_polynomial(degree, Q(a, LEVEL))
        for a in range(1, LEVEL + 1)
    )


def odd_eisenstein(weight: int, orientation: str, qmax: int) -> list[Q]:
    series = [Q(0)] * (qmax + 1)
    if orientation == "C":
        series[0] = -generalized_bernoulli(weight) / Q(2 * weight)
    else:
        require(orientation == "T", "unknown Eisenstein orientation")
    for divisor in range(1, qmax + 1):
        power = divisor ** (weight - 1)
        for n in range(divisor, qmax + 1, divisor):
            series[n] += (
                Q(character(divisor)) * power
                if orientation == "C"
                else Q(character(n // divisor)) * power
            )
    return series


def series_product(a: list[Q], b: list[Q], qmax: int) -> list[Q]:
    return [
        sum(a[j] * b[n - j] for j in range(n + 1))
        for n in range(qmax + 1)
    ]


def rational_rank(rows: list[list[Q]]) -> int:
    work = [row[:] for row in rows]
    if not work:
        return 0
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (r for r in range(pivot_row, len(work)) if work[r][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for r in range(len(work)):
            if r == pivot_row or work[r][column] == 0:
                continue
            scale = work[r][column]
            work[r] = [
                work[r][j] - scale * work[pivot_row][j]
                for j in range(len(work[r]))
            ]
        pivot_row += 1
        if pivot_row == len(work):
            break
    return pivot_row


def modular_form_audit() -> dict[str, object]:
    rows: list[dict[str, int]] = []
    total = 0
    fricke_products = 0
    for c in range(11):
        weight = WEIGHT + 2 * c
        dimension = 1 + 2 * (weight // 3)
        sturm = 2 * weight // 3
        series = {
            (odd, orientation): odd_eisenstein(odd, orientation, sturm)
            for odd in range(3, weight - 1, 2)
            for orientation in ("C", "T")
        }
        products: list[list[Q]] = []
        for left in range(3, weight - 2, 2):
            right = weight - left
            if right < 3 or right % 2 == 0:
                continue
            for left_orientation in ("C", "T"):
                for right_orientation in ("C", "T"):
                    products.append(
                        series_product(
                            series[left, left_orientation],
                            series[right, right_orientation],
                            sturm,
                        )
                    )
                    left_exponent = (
                        (left - 1) // 2
                        if left_orientation == "C"
                        else (1 - left) // 2
                    )
                    right_exponent = (
                        (right - 1) // 2
                        if right_orientation == "C"
                        else (1 - right) // 2
                    )
                    # The first Fricke map contributes -7^(a+b).
                    # Flipping C/T negates both exponents; a second map
                    # contributes the reciprocal with a second minus sign.
                    require(
                        (-Q(LEVEL) ** (left_exponent + right_exponent))
                        * (-Q(LEVEL) ** (-left_exponent - right_exponent))
                        == 1,
                        "raw Fricke product is not an involution",
                    )
                    fricke_products += 1
        rank = rational_rank(
            [[product[n] for product in products] for n in range(sturm + 1)]
        )
        require(rank == dimension, f"modular product rank drift at weight {weight}")
        rows.append(
            {
                "c": c,
                "weight": weight,
                "dimension": dimension,
                "sturm_bound": sturm,
                "product_rank": rank,
            }
        )
        total += dimension
    require([row["dimension"] for row in rows] == EXPECTED_DIMENSIONS,
            "modular dimensions drift")
    require(total == 239, "Jacobi module dimension drift")
    return {
        "dimension_formula": "dim M_w(Gamma0(7)) = 1 + 2 floor(w/3)",
        "rows": rows,
        "total_dimension": total,
        "raw_product_fricke_involutions_checked": fricke_products,
        "weak_jacobi_decomposition": (
            "direct sum c=0..10 M_(22+2c)(Gamma0(7)) A^c B^(10-c)"
        ),
    }


def load_cache(cutoff: int) -> dict[str, object]:
    require(free_memory_percent() >= 15.0, "host memory floor reached")
    with CACHE_PATHS[cutoff].open("rb") as handle:
        payload = pickle.load(handle)
    require(payload.get("version") == MODEL_VERSION, "cache version drift")
    require(payload.get("qmax") == cutoff, "cache cutoff drift")
    require(len(payload.get("columns", [])) == 239, "column count drift")
    require(
        payload["module"]["dimensions_by_c"] == EXPECTED_DIMENSIONS,
        "cache module dimensions drift",
    )
    require(payload["module"]["total_dimension"] == 239, "cache dimension drift")
    require(
        payload["module"]["A_q0"] == {"-1": "1", "0": "-2", "1": "1"},
        "A normalization drift",
    )
    require(
        payload["module"]["B_q0"] == {"-1": "1", "0": "10", "1": "1"},
        "B normalization drift",
    )
    counts = Counter(column["c"] for column in payload["columns"])
    require(
        [counts[c] for c in range(11)] == EXPECTED_DIMENSIONS,
        "cache c-block dimensions drift",
    )
    for column in payload["columns"]:
        c = column["c"]
        require(column["weight"] == 22 + 2 * c, "column weight drift")
        require(column["fricke_eigenvalue"] in (-1, 1), "bad Fricke eigenvalue")
        for side in ("L", "K"):
            require(
                all(value and n <= cutoff for (n, _r), value in column[side].items()),
                "unclean or over-cutoff cached coefficient",
            )
            require(
                all(
                    column[side].get((n, -r), Q(0)) == value
                    for (n, r), value in column[side].items()
                ),
                "elliptic parity symmetry drift",
            )
        require(
            all(r % 7 == 0 for n, r in column["K"]),
            "K elliptic exponents are not seven-scaled",
        )
    return payload


def compare_truncation(lower: dict[str, object], upper: dict[str, object]) -> int:
    lower_cutoff = lower["qmax"]
    comparisons = 0
    for left, right in zip(lower["columns"], upper["columns"], strict=True):
        for key in ("c", "weight", "basis_index", "pivot_q", "fricke_eigenvalue"):
            require(left[key] == right[key], f"cross-cache metadata drift: {key}")
        for side in ("L", "K"):
            truncated = {
                key: value
                for key, value in right[side].items()
                if key[0] <= lower_cutoff
            }
            require(left[side] == truncated, "cross-cache coefficient drift")
            comparisons += len(truncated)
    return comparisons


def check_fricke_q0(columns: list[dict[str, object]]) -> int:
    comparisons = 0
    for column in columns:
        c = column["c"]
        eigenvalue = column["fricke_eigenvalue"]
        scale = -Q(1, 7 ** (3 + c))
        require(
            all(r % 7 == 0 for n, r in column["K"] if n == 0),
            "K q0 exponent is not seven-scaled",
        )
        radii = {
            r for n, r in column["L"] if n == 0
        } | {
            r // 7 for n, r in column["K"] if n == 0
        }
        for r in radii:
            require(
                column["K"].get((0, 7 * r), Q(0))
                == scale
                * eigenvalue
                * column["L"].get((0, r), Q(0)),
                "q0 Fricke factor mismatch",
            )
            comparisons += 1
    return comparisons


def coefficient_value(
    columns: list[dict[str, object]],
    solution: list[Q],
    side: str,
    key: tuple[int, int],
) -> Q:
    return sum(
        solution[j] * column[side].get(key, Q(0))
        for j, column in enumerate(columns)
    )


def verify_candidate(
    cutoff: int, columns: list[dict[str, object]]
) -> dict[str, object]:
    candidate = json.loads(CANDIDATE_PATHS[cutoff].read_text(encoding="utf-8"))
    require(candidate.get("classification") == "EXACT_RATIONAL_FEASIBLE",
            f"cutoff {cutoff} is not an exact candidate")
    solution = [Q(value) for value in candidate.get("solution", [])]
    require(len(solution) == 239, f"cutoff {cutoff} solution length drift")
    failed_equalities: list[str] = []
    failed_inequalities: list[str] = []
    tight: list[str] = []
    equality_count = 0
    inequality_count = 0

    for side in ("L", "K"):
        value = coefficient_value(columns, solution, side, (0, 0))
        equality_count += 1
        if value != 2079:
            failed_equalities.append(f"{side}:constant")

        keys = sorted(
            {
                key
                for column in columns
                for key in column[side]
                if key[0] <= cutoff
            }
        )
        index = INDEX_L if side == "L" else INDEX_K
        for n, r in keys:
            label_suffix = ""
            forced_zero = False
            if r * r > 4 * index * n:
                forced_zero = True
                label_suffix = "hol"
            elif side == "K" and (
                1 <= n <= 6 or (7 <= n <= 10 and abs(r) > 28)
            ):
                forced_zero = True
                label_suffix = "graph"
            value = coefficient_value(columns, solution, side, (n, r))
            if forced_zero:
                equality_count += 1
                if value:
                    failed_equalities.append(
                        f"{side}:zero:n{n}:r{r}:{label_suffix}"
                    )
            else:
                inequality_count += 1
                label = f"{side}:positive:n{n}:r{r}"
                if value < 0:
                    failed_inequalities.append(label)
                elif value == 0:
                    tight.append(label)

        moment_multiplier = 10 if side == "L" else 70
        for n in range(1, cutoff + 1):
            radii = sorted(
                {
                    r
                    for column in columns
                    for nn, r in column[side]
                    if nn == n
                }
            )
            if not radii:
                continue
            row = [
                sum(
                    (11 * r * r - moment_multiplier * n)
                    * column[side].get((n, r), Q(0))
                    for r in radii
                )
                for column in columns
            ]
            if not any(row):
                continue
            equality_count += 1
            value = sum(row[j] * solution[j] for j in range(239))
            if value:
                failed_equalities.append(f"{side}:moment:n{n}")

    expected_equalities, expected_inequalities, expected_tight = EXPECTED_COUNTS[
        cutoff
    ]
    require(equality_count == expected_equalities, "equality count mismatch")
    require(inequality_count == expected_inequalities, "inequality count mismatch")
    require(len(tight) == expected_tight, "tight count mismatch")
    require(tight == candidate.get("tight_inequalities"), "tight label mismatch")
    require(not failed_equalities, f"failed equality at cutoff {cutoff}")
    require(not failed_inequalities, f"failed inequality at cutoff {cutoff}")

    saved = json.loads(SAVED_VERIFICATIONS[cutoff].read_text(encoding="utf-8"))
    require(
        saved.get("classification") == "VERIFIED_EXACT_RATIONAL_FEASIBLE",
        "saved verification status drift",
    )
    require(saved.get("equalities") == equality_count, "saved equality count drift")
    require(
        saved.get("inequalities") == inequality_count,
        "saved inequality count drift",
    )
    require(
        saved.get("tight_inequalities") == len(tight),
        "saved tight count drift",
    )
    return {
        "classification": "VERIFIED_EXACT_RATIONAL_FEASIBLE",
        "variables": len(solution),
        "equalities_checked": equality_count,
        "inequalities_checked": inequality_count,
        "tight_inequalities": len(tight),
        "failed_equalities": 0,
        "failed_inequalities": 0,
        "candidate_sha256": sha256(CANDIDATE_PATHS[cutoff]),
        "cache_sha256": sha256(CACHE_PATHS[cutoff]),
    }


def audit_q28(columns: list[dict[str, object]]) -> dict[str, object]:
    candidate = json.loads(CANDIDATE_PATHS[28].read_text(encoding="utf-8"))
    status = json.loads((W129 / "STATUS.json").read_text(encoding="utf-8"))
    row = status["finite_exact_feasibility"]["28"]
    require(
        candidate.get("classification") == "EXACT_PRIMAL_RECOVERY_FAILED",
        "q28 candidate classification drift",
    )
    require(not candidate.get("solution"), "q28 unexpectedly contains a solution")
    require(row["classification"] == "UNKNOWN", "q28 status inflation")
    require(not row["exact_farkas_certificate"], "q28 unexpectedly has Farkas proof")
    require(
        row["equalities"] == 454 and row["inequalities"] == 1686,
        "q28 row counts drift",
    )
    require(len(columns) == 239, "q28 column count drift")
    return {
        "classification": "UNKNOWN",
        "variables": 239,
        "equalities": 454,
        "inequalities": 1686,
        "independent_equalities": 139,
        "deduplicated_inequalities": 510,
        "affine_free_dimension": 100,
        "exact_primal_certificate": False,
        "exact_farkas_certificate": False,
        "reason": (
            "Floating feasibility plus failed exact recovery proves neither "
            "exact feasibility nor infeasibility."
        ),
        "candidate_sha256": sha256(CANDIDATE_PATHS[28]),
        "cache_sha256": sha256(CACHE_PATHS[28]),
    }


def build_results() -> dict[str, object]:
    initial_memory = free_memory_percent()
    require(initial_memory >= 15.0, "memory floor before audit")
    seals = preinspect_manifests()
    module = modular_form_audit()

    finite: dict[str, object] = {}
    cross_cache_comparisons = 0
    fricke_q0_comparisons = 0
    previous: dict[str, object] | None = None
    for cutoff in (10, 12, 14, 16, 18, 20, 28):
        cache = load_cache(cutoff)
        fricke_q0_comparisons += check_fricke_q0(cache["columns"])
        if previous is not None:
            cross_cache_comparisons += compare_truncation(previous, cache)
        if cutoff <= 20:
            finite[str(cutoff)] = verify_candidate(cutoff, cache["columns"])
        else:
            finite[str(cutoff)] = audit_q28(cache["columns"])
        previous = cache
        require(free_memory_percent() >= 15.0, "memory floor during audit")

    # Independently derive the block factor:
    # qdisc/2 - 11 - c = 8 - 11 - c = -3-c.
    exponents = {str(c): QDISC // 2 - 11 - c for c in range(11)}
    require(exponents == {str(c): -3 - c for c in range(11)},
            "Fricke exponent derivation drift")
    require(
        all(finite[str(c)]["classification"] == "VERIFIED_EXACT_RATIONAL_FEASIBLE"
            for c in (10, 12, 14, 16, 18, 20)),
        "finite candidate verdict drift",
    )
    require(finite["28"]["classification"] == "UNKNOWN", "q28 must stay UNKNOWN")

    return {
        "format": "wave127-wave129-independent-audit-v1",
        "claim_label": "VERIFIED",
        "scope": (
            "Exact feasibility only for the finite rank-28, discriminant-16, "
            "level-7 Jacobi necessary-condition relaxations at cutoffs "
            "10,12,14,16,18,20; cutoff 28 remains UNKNOWN."
        ),
        "preinspection": seals,
        "module_audit": module,
        "fricke_audit": {
            "normalized_operator": (
                "(f|W7)(tau)=7^(-w/2) tau^(-w) f(-1/(7 tau))"
            ),
            "block_factor": "h_c = -7^(-3-c) (f_c|W7)",
            "exponents_by_c": exponents,
            "q0_exact_comparisons": fricke_q0_comparisons,
            "cross_cache_exact_coefficients_compared": cross_cache_comparisons,
            "all_cache_truncations_match": True,
        },
        "cutoffs": finite,
        "status_wall": {
            "cutoff_28": "UNKNOWN",
            "rank28_excluded": False,
            "rank28_realized": False,
            "graph_constructed": False,
            "lattice_constructed": False,
            "Conway_99": "UNKNOWN",
            "literature_novelty": "UNKNOWN",
        },
        "memory": {
            "floor_percent": 15,
            "floor_respected": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", type=Path)
    args = parser.parse_args()
    rendered = canonical(build_results())
    if args.verify:
        require(
            args.verify.read_text(encoding="utf-8") == rendered,
            "independent-results.json drift",
        )
    if args.output:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    if not args.output and not args.verify:
        print(rendered, end="")


if __name__ == "__main__":
    main()
