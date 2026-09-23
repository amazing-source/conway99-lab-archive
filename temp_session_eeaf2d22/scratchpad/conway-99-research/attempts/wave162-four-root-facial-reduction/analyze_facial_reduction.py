#!/usr/bin/env python3
"""Exact facial-reduction audit of the Wave152/Wave159 cut loop.

This is deliberately a lightweight audit.  It does not rebuild the four-root
moment matrices or run an optimizer.  It:

* replays all fifteen exact scalar covariance cuts on every stored exact
  fixed-slice witness;
* distinguishes zero quadratic values from matrix-kernel statements;
* checks whether the three Wave159 active functionals vary on the common
  stored affine slice;
* gives exact determinant-minor certificates for direction independence; and
* records the only facial reductions justified conditionally by PSD plus
  explicitly assumed active equalities.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
import subprocess
import time
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "facial-reduction-audit.json"
RESOURCE_OUTPUT = HERE / "resource-report.json"
INPUT_FREEZE = HERE / "input-freeze.sha256"

CUT_PATHS = (
    "attempts/wave152-four-root-order8/exact-cuts.json",
    "attempts/wave152-four-root-order8/iteration2-cuts.json",
    "attempts/wave152-four-root-order8/iteration3-mask13-cut.json",
    "attempts/wave152-four-root-order8/iteration4-three-cuts.json",
    "attempts/wave152-four-root-order8/simplified-mask12-cut.json",
    "attempts/wave152-four-root-order8/iteration5-three-cuts.json",
    "attempts/wave152-four-root-order8/simplified-mask12-cut-2.json",
    "attempts/wave159-four-root-cut-loop/fresh-two-cuts.json",
)

WITNESS_PATHS = (
    "attempts/wave152-four-root-order8/exact-witness-after-two-cuts.json",
    "attempts/wave152-four-root-order8/exact-witness-after-four-cuts.json",
    "attempts/wave152-four-root-order8/exact-witness-after-five-cuts.json",
    "attempts/wave152-four-root-order8/exact-witness-after-eight-cuts.json",
    "attempts/wave152-four-root-order8/exact-witness-after-thirteen-cuts.json",
    "attempts/wave159-four-root-cut-loop/exact-witness-after-fifteen-cuts.json",
)

EVALUATION_PATHS = (
    "attempts/wave152-four-root-order8/four-root-evaluation-after-two-cuts.json",
    "attempts/wave152-four-root-order8/four-root-evaluation-after-four-cuts.json",
    "attempts/wave152-four-root-order8/four-root-evaluation-after-five-cuts.json",
    "attempts/wave152-four-root-order8/four-root-evaluation-after-eight-cuts.json",
    "attempts/wave152-four-root-order8/four-root-evaluation-after-thirteen-cuts.json",
    "attempts/wave159-four-root-cut-loop/four-root-evaluation-after-fifteen-cuts.json",
)

CORE_AFFINE_INPUTS = (
    "attempts/wave150-order8-sdp-scout/endpoint_sdp.py",
    "attempts/wave150-order8-sdp-scout/exact_rank1_witness.py",
    "attempts/wave44-rooted-flags/row-system.json",
)

ROOT_DIMENSIONS = {3: 155, 12: 178, 13: 125}
MEMORY_FLOOR_PERCENT = 15.0


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def read_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def memory_record(label: str) -> dict[str, float | str]:
    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(MemoryStatusEx)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
        "GlobalMemoryStatusEx failed",
    )
    free_percent = 100.0 * status.ullAvailPhys / status.ullTotalPhys
    record: dict[str, float | str] = {
        "label": label,
        "free_physical_memory_percent": free_percent,
        "available_physical_gib": status.ullAvailPhys / 2**30,
        "total_physical_gib": status.ullTotalPhys / 2**30,
    }
    require(
        free_percent >= MEMORY_FLOOR_PERCENT,
        f"memory floor crossed at {label}: {free_percent:.3f}%",
    )
    return record


def load_cuts() -> list[dict[str, Any]]:
    cuts: list[dict[str, Any]] = []
    for relative in CUT_PATHS:
        payload = read_json(relative)
        cuts.extend(payload["cuts"] if "cuts" in payload else [payload["cut"]])
    require(len(cuts) == 15, "expected exactly fifteen cuts")
    hashes = [str(cut["cut_sha256"]) for cut in cuts]
    require(len(set(hashes)) == len(hashes), "duplicate cut hash")
    for cut in cuts:
        core = dict(cut)
        stored = str(core.pop("cut_sha256"))
        require(canonical_sha256(core) == stored, f"bad cut hash: {stored}")
        root = int(cut["root_mask"])
        require(
            len(cut["direction"]) == ROOT_DIMENSIONS[root],
            f"direction dimension mismatch for root {root}",
        )
    return cuts


def count_map(
    witness: dict[str, Any], key: str
) -> dict[int, Fraction]:
    return {
        int(record["canonical_mask"]): Fraction(str(record["count"]))
        for record in witness[key]
    }


def evaluate_cut(
    cut: dict[str, Any],
    x7: dict[int, Fraction],
    x8: dict[int, Fraction],
) -> Fraction:
    value = Fraction(str(cut["constant"]))
    value += sum(
        Fraction(str(record["coefficient"]))
        * x7.get(int(record["canonical_mask"]), Fraction(0))
        for record in cut["order7_coefficients"]
    )
    value += sum(
        Fraction(str(record["coefficient"]))
        * x8.get(int(record["canonical_mask"]), Fraction(0))
        for record in cut["order8_coefficients"]
    )
    return value


def dense_certificate_direction(block: dict[str, Any]) -> list[int]:
    certificate = block["negative_certificate"]
    require(certificate is not None, "missing negative certificate")
    direction = [0] * int(block["flag_count"])
    for index, value in zip(
        certificate["indices"], certificate["vector"], strict=True
    ):
        direction[int(index)] = int(value)
    return direction


def exact_rank_and_pivots(rows: Sequence[Sequence[int]]) -> tuple[int, list[int]]:
    if not rows:
        return 0, []
    width = len(rows[0])
    require(all(len(row) == width for row in rows), "ragged matrix")
    matrix = [[Fraction(value) for value in row] for row in rows]
    pivot_row = 0
    pivot_columns: list[int] = []
    for column in range(width):
        found = next(
            (
                row
                for row in range(pivot_row, len(matrix))
                if matrix[row][column]
            ),
            None,
        )
        if found is None:
            continue
        matrix[pivot_row], matrix[found] = matrix[found], matrix[pivot_row]
        pivot = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                left - factor * right
                for left, right in zip(
                    matrix[row], matrix[pivot_row], strict=True
                )
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    return pivot_row, pivot_columns


def bareiss_determinant(matrix: Sequence[Sequence[int]]) -> int:
    size = len(matrix)
    require(
        all(len(row) == size for row in matrix),
        "determinant matrix is not square",
    )
    if size == 0:
        return 1
    work = [list(map(int, row)) for row in matrix]
    sign = 1
    previous = 1
    for column in range(size - 1):
        if work[column][column] == 0:
            swap = next(
                (
                    row
                    for row in range(column + 1, size)
                    if work[row][column]
                ),
                None,
            )
            require(swap is not None, "singular determinant certificate")
            work[column], work[swap] = work[swap], work[column]
            sign *= -1
        pivot = work[column][column]
        for row in range(column + 1, size):
            for other in range(column + 1, size):
                numerator = (
                    work[row][other] * pivot
                    - work[row][column] * work[column][other]
                )
                require(
                    numerator % previous == 0,
                    "Bareiss division was not exact",
                )
                work[row][other] = numerator // previous
        previous = pivot
    return sign * work[-1][-1]


def independence_certificate(
    named_rows: Sequence[tuple[str, Sequence[int]]],
) -> dict[str, Any]:
    rows = [list(map(int, row)) for _, row in named_rows]
    rank, pivots = exact_rank_and_pivots(rows)
    require(rank == len(rows), "expected supplied directions to be independent")
    selected = pivots[:rank]
    minor = [[row[column] for column in selected] for row in rows]
    determinant = bareiss_determinant(minor)
    require(determinant != 0, "zero determinant independence certificate")
    return {
        "direction_labels": [label for label, _ in named_rows],
        "ambient_dimension": len(rows[0]),
        "rank": rank,
        "pivot_flag_indices": selected,
        "exact_minor_determinant": str(determinant),
    }


def file_label(relative: str) -> str:
    return Path(relative).stem


def freeze_inputs(paths: Iterable[str]) -> None:
    lines = [
        f"{sha256_file(ROOT / relative)}  {relative}"
        for relative in sorted(set(paths))
    ]
    INPUT_FREEZE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_audit() -> tuple[dict[str, Any], dict[str, Any]]:
    started = time.time()
    samples = [memory_record("start")]
    cuts = load_cuts()
    cut_by_hash = {str(cut["cut_sha256"]): cut for cut in cuts}

    witnesses: dict[str, dict[str, Any]] = {
        file_label(relative): read_json(relative) for relative in WITNESS_PATHS
    }
    witness_counts = {
        label: (
            count_map(witness, "x7_support"),
            count_map(witness, "x8_support"),
        )
        for label, witness in witnesses.items()
    }

    first_x7 = next(iter(witness_counts.values()))[0]
    require(
        all(x7 == first_x7 for x7, _ in witness_counts.values()),
        "stored fixed-slice witnesses do not share exact x7",
    )
    require(
        all(
            all(
                witness["inputs"].get(relative)
                == sha256_file(ROOT / relative)
                for relative in CORE_AFFINE_INPUTS
            )
            for witness in witnesses.values()
        ),
        "common affine input hash mismatch",
    )

    values: dict[str, dict[str, str]] = {}
    zero_hashes: dict[str, list[str]] = {}
    signs: dict[str, dict[str, int]] = {}
    for label, (x7, x8) in witness_counts.items():
        evaluated = {
            cut_hash: evaluate_cut(cut, x7, x8)
            for cut_hash, cut in cut_by_hash.items()
        }
        values[label] = {
            cut_hash: str(value) for cut_hash, value in evaluated.items()
        }
        zero_hashes[label] = sorted(
            cut_hash for cut_hash, value in evaluated.items() if value == 0
        )
        signs[label] = {
            cut_hash: (1 if value > 0 else -1 if value < 0 else 0)
            for cut_hash, value in evaluated.items()
        }

    final_label = "exact-witness-after-fifteen-cuts"
    final_active = zero_hashes[final_label]
    expected_final = sorted(witnesses[final_label]["active_cut_hashes"])
    require(final_active == expected_final, "Wave159 active-set replay mismatch")
    require(len(final_active) == 3, "expected three Wave159 active cuts")

    # Direct affine non-forcing certificates: the two stored points share the
    # exact x7 vector and frozen affine system, but the functional values differ.
    nonforcing: list[dict[str, Any]] = []
    labels = list(witnesses)
    for cut_hash in final_active:
        final_value = Fraction(values[final_label][cut_hash])
        require(final_value == 0, "final active value is not zero")
        comparison = next(
            (
                label
                for label in labels
                if label != final_label
                and Fraction(values[label][cut_hash]) != final_value
            ),
            None,
        )
        require(comparison is not None, f"no varying witness for {cut_hash}")
        comparison_value = Fraction(values[comparison][cut_hash])
        nonforcing.append(
            {
                "cut_sha256": cut_hash,
                "root_mask": int(cut_by_hash[cut_hash]["root_mask"]),
                "zero_witness": final_label,
                "comparison_witness": comparison,
                "zero_value": "0",
                "comparison_value": str(comparison_value),
                "difference": str(comparison_value),
                "conclusion": "NOT_FORCED_ZERO_BY_COMMON_STORED_AFFINE_EQUALITIES",
            }
        )

    universal_zero = sorted(
        set.intersection(*(set(hashes) for hashes in zero_hashes.values()))
    )
    require(not universal_zero, "unexpected universally zero stored cut")

    active_frequency = {
        cut_hash: sum(
            cut_hash in hashes for hashes in zero_hashes.values()
        )
        for cut_hash in cut_by_hash
    }

    final_active_by_root: dict[int, list[tuple[str, Sequence[int]]]] = {}
    for cut_hash in final_active:
        cut = cut_by_hash[cut_hash]
        root = int(cut["root_mask"])
        final_active_by_root.setdefault(root, []).append(
            (f"active:{cut_hash}", list(map(int, cut["direction"])))
        )

    evaluations: dict[str, Any] = {}
    latest_negative: dict[int, tuple[str, list[int]]] = {}
    for relative in EVALUATION_PATHS:
        payload = read_json(relative)
        label = file_label(relative)
        blocks = []
        for block in payload["root_blocks"]:
            certificate = block["negative_certificate"]
            if certificate is None:
                continue
            quadratic = int(certificate["quadratic_value_scaled"])
            require(quadratic < 0, "stored negative certificate is not negative")
            direction = dense_certificate_direction(block)
            direction_hash = canonical_sha256(direction)
            root = int(block["root_mask"])
            blocks.append(
                {
                    "root_mask": root,
                    "flag_count": int(block["flag_count"]),
                    "direction_support": sum(value != 0 for value in direction),
                    "direction_sha256": direction_hash,
                    "quadratic_value_scaled": str(quadratic),
                }
            )
            if label == "four-root-evaluation-after-fifteen-cuts":
                latest_negative[root] = (
                    f"fresh-negative:{direction_hash}",
                    direction,
                )
        evaluations[label] = blocks

    require(set(latest_negative) == {3, 12}, "unexpected latest negative roots")

    conditional_faces = []
    escape_certificates = []
    for root in sorted(final_active_by_root):
        active_rows = final_active_by_root[root]
        active_certificate = independence_certificate(active_rows)
        rank = int(active_certificate["rank"])
        dimension = ROOT_DIMENSIONS[root]
        reduced = dimension - rank
        conditional_faces.append(
            {
                "root_mask": root,
                "matrix_order": dimension,
                "assumed_active_direction_rank": rank,
                "reduced_psd_cone_order": reduced,
                "original_symmetric_dimension": dimension * (dimension + 1) // 2,
                "reduced_symmetric_dimension": reduced * (reduced + 1) // 2,
                "independence_certificate": active_certificate,
                "scope": (
                    "Valid only if a genuinely PSD feasible covariance block "
                    "also has every listed scalar quadratic form equal to zero."
                ),
            }
        )
        fresh = latest_negative[root]
        combined = [*active_rows, fresh]
        escape = independence_certificate(combined)
        escape["root_mask"] = root
        escape["conclusion"] = (
            "THE_LATEST_NEGATIVE_DIRECTION_IS_OUTSIDE_THE_SPAN_OF_THE_"
            "WAVE159_ACTIVE_DIRECTIONS"
        )
        escape_certificates.append(escape)

    samples.append(memory_record("complete"))
    resource = {
        "format": "wave162-resource-report-v1",
        "memory_floor_percent": MEMORY_FLOOR_PERCENT,
        "minimum_free_physical_memory_percent": min(
            float(sample["free_physical_memory_percent"]) for sample in samples
        ),
        "elapsed_seconds": time.time() - started,
        "samples": samples,
        "heavy_solve_run": False,
    }

    try:
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_commit = "UNKNOWN"

    audit = {
        "format": "wave162-four-root-facial-reduction-audit-v1",
        "claim_label": "DERIVED",
        "scope": (
            "Exact replay and facial-reduction audit of all fifteen stored "
            "four-root scalar cuts on six exact fixed-slice pseudowitnesses; "
            "no full four-root PSD solve and no graph claim."
        ),
        "git_commit_at_run": git_commit,
        "counts": {
            "cuts": len(cuts),
            "witnesses": len(witnesses),
            "evaluations": len(evaluations),
        },
        "common_affine_slice_evidence": {
            "all_x7_vectors_exactly_equal": True,
            "shared_x7_support": len(first_x7),
            "shared_core_input_hashes": {
                relative: sha256_file(ROOT / relative)
                for relative in CORE_AFFINE_INPUTS
            },
            "stored_all_rows_passed": {
                label: int(witness["exact_solve"]["all_rows_passed"])
                for label, witness in witnesses.items()
            },
            "limitation": (
                "Wave162 did not independently rebuild every base row; it "
                "uses the exact-solve replay records frozen in each witness."
            ),
        },
        "cut_metadata": {
            cut_hash: {
                "root_mask": int(cut["root_mask"]),
                "direction_support": sum(
                    int(value) != 0 for value in cut["direction"]
                ),
                "direction_sha256": canonical_sha256(
                    list(map(int, cut["direction"]))
                ),
            }
            for cut_hash, cut in cut_by_hash.items()
        },
        "exact_cut_values_by_witness": values,
        "cut_signs_by_witness": signs,
        "zero_cut_hashes_by_witness": zero_hashes,
        "active_frequency_across_six_witnesses": active_frequency,
        "universal_zero_cut_hashes": universal_zero,
        "wave159_active_cut_hashes": final_active,
        "affine_nonforcing_certificates": nonforcing,
        "stored_negative_blocks": evaluations,
        "conditional_psd_faces": conditional_faces,
        "latest_escape_direction_certificates": escape_certificates,
        "conclusion": {
            "unconditional_forced_four_root_face_found": False,
            "why": [
                "No retained scalar cut is zero on all six stored exact witnesses.",
                "Each of the three Wave159 active functionals varies exactly on the common stored affine slice.",
                "The Wave159 exact reconstruction explicitly imposed its active cuts as equalities, so their activeness is not an emergent dual certificate.",
                "Every stored evaluated witness has an exact negative four-root direction; none is a PSD feasible point from which zero quadratic values could be promoted to kernel vectors.",
                "At each persistent root, the newest negative direction is exactly independent of the Wave159 active direction span.",
            ],
            "conditional_reduction": (
                "If a true PSD solution were separately proved to make the "
                "three Wave159 cuts active, PSD zero-quadratic-form rigidity "
                "would reduce root 3 from S_+^155 to S_+^154 and root 12 "
                "from S_+^178 to S_+^176."
            ),
            "next_mathematical_requirement": (
                "Produce an exact conic dual exposing vector: a nonnegative "
                "combination of the full affine constraints and PSD blocks "
                "whose trace pairing is forced to zero (for facial reduction) "
                "or whose constant is strictly negative (for infeasibility). "
                "More sampled active eigenvector cuts cannot supply this."
            ),
            "endpoint_n3_4158": "UNKNOWN",
            "strict_upper_bound_below_4158": "NOT_PROVED",
            "Conway_99": "UNKNOWN",
        },
        "limitations": [
            "This discovery audit is not an independent verifier.",
            "Stored exact witnesses are count pseudowitnesses, not graphs.",
            "A zero quadratic value for an indefinite matrix is not a matrix-kernel certificate.",
            "The conditional faces are implications, not demonstrated faces of the unrestricted feasible set.",
            "No SDP or large solve was run because the task requested exact lightweight analysis and host memory has a 15 percent floor.",
        ],
    }
    return audit, resource


def main() -> int:
    freeze_inputs((*CUT_PATHS, *WITNESS_PATHS, *EVALUATION_PATHS))
    audit, resource = build_audit()
    OUTPUT.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    RESOURCE_OUTPUT.write_text(
        json.dumps(resource, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(audit["conclusion"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
