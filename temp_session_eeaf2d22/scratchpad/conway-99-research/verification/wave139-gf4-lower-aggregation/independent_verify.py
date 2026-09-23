"""Independent Wave145 audit of the Wave139 GF(4) lower-bound aggregation."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from math import comb
from pathlib import Path
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts" / "wave139-gf4-n3-bound"
WAVE136 = (
    ROOT / "verification" / "wave136-alternative-spaces"
    / "independent-results.json"
)
WAVE131 = (
    ROOT / "verification" / "wave131-binary-lcd-enumerator"
    / "independent-results.json"
)
OUTPUT = HERE / "verification-results.json"

N = 99
TARGET_STATE = (41, 4, 54)
TARGET_LOWER = 708
DISCOVERY_MANIFEST_SHA256 = (
    "fa1d00ddc9ab25d00126bc82f32d7e0c5a703c4a7efe355ed49dc111dda2058d"
)
DISCOVERY_MODEL_SHA256 = (
    "75f517bfc613db18940c952f8757bd6b73d97e7ff86602eeea072806b546744c"
)
FROZEN_INPUTS = {
    "AGENTS.md": (
        "4d3e4590a8634cafaf5d87f288be211497f60a8f5ab40094a83f555724e469b3"
    ),
    "attempts/wave139-gf4-n3-bound/package-manifest.sha256": (
        DISCOVERY_MANIFEST_SHA256
    ),
    "verification/wave136-alternative-spaces/independent-results.json": (
        "7129891b17e307dd0d881f759d609dc027a75858647777d7fda7f112acbdf7d3"
    ),
    "verification/wave131-binary-lcd-enumerator/independent-results.json": (
        "65b365a1779c4e1fcfc6d0d3b0f38abaf9ed98798c7cc0d26a6fa64495149087"
    ),
    "verification/wave131-binary-lcd-enumerator/verification-report.md": (
        "64c0f636c916cb0d3efbb6d0a4899b95b90f65915ca8de963200254ed080c9d8"
    ),
}
TYPE_SIZE = {
    "one_vertex": 1,
    "edge": 2,
    "nonedge": 2,
    "independent_c0": 3,
    "independent_c1": 3,
    "one_edge_c0": 3,
    "one_edge_c1": 3,
    "induced_path": 3,
    "triangle": 3,
}
CORRECT_PURE_Y_ZERO_WEIGHTS = {2, 4, 6, 94, 96, 98}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def verify_frozen_inputs() -> dict:
    rows = {}
    for relative, expected in FROZEN_INPUTS.items():
        path = ROOT / relative
        actual = sha256(path)
        rows[relative] = {
            "expected_sha256": expected,
            "actual_sha256": actual,
            "pass": actual == expected,
        }
    return {"files": rows, "pass": all(row["pass"] for row in rows.values())}


def verify_discovery_manifest() -> dict:
    manifest = DISCOVERY / "package-manifest.sha256"
    entries = []
    failures = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        relative = relative.strip().replace("\\", "/")
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError:
            failures.append(f"path escapes repository: {relative}")
            continue
        if not path.is_file():
            failures.append(f"missing: {relative}")
            continue
        actual = sha256(path)
        if actual != expected:
            failures.append(f"hash mismatch: {relative}")
        entries.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "pass": actual == expected,
            }
        )
    return {
        "manifest_sha256": sha256(manifest),
        "manifest_pass": sha256(manifest) == DISCOVERY_MANIFEST_SHA256,
        "entry_count": len(entries),
        "entries_pass": not failures,
        "failures": failures,
    }


def load_discovery_model() -> ModuleType:
    path = DISCOVERY / "gf4_model.py"
    if sha256(path) != DISCOVERY_MODEL_SHA256:
        raise AssertionError("Wave139 model is not the frozen source")
    spec = importlib.util.spec_from_file_location("wave139_frozen_model", path)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load Wave139 model")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def support_rows() -> list[dict]:
    wave136 = load_json(WAVE136)
    rows = []
    for row in wave136["additive_gf4"]["support_at_most_three_lower_table"]:
        state = (row["nI"], row["nY"], row["nR"])
        input_size = TYPE_SIZE[row["input_type"]]
        n_x = input_size - row["nY"]
        n_z = row["nR"] - n_x
        output_weight = row["nY"] + n_z
        rows.append(
            {
                **row,
                "state": list(state),
                "input_size": input_size,
                "nX": n_x,
                "nZ": n_z,
                "output_weight": output_weight,
            }
        )
    return rows


def forced_axis_bounds() -> tuple[dict[int, int], dict[int, int]]:
    wave131 = load_json(WAVE131)["forced_distributions"]
    image = {
        0: 1,
        **{
            int(weight): int(value)
            for weight, value in wave131["image_forced_lower"].items()
        },
    }
    dual = {
        0: 1,
        99: 1,
        **{
            int(weight): int(value)
            for weight, value in wave131["dual_forced_lower"].items()
        },
        **{
            int(weight): int(value)
            for weight, value in wave131[
                "dual_complement_forced_lower"
            ].items()
        },
    }
    return image, dual


def corrected_lower_bounds() -> dict[tuple[int, int, int], int]:
    """Sum certified disjoint word families, except their shared zero word."""
    lower: dict[tuple[int, int, int], int] = {}
    for row in support_rows():
        state = tuple(row["state"])
        lower[state] = lower.get(state, 0) + row["count"]

    image, dual = forced_axis_bounds()
    lower[(N, 0, 0)] = 1
    for weight, value in image.items():
        if weight:
            state = (N - weight, weight, 0)
            lower[state] = lower.get(state, 0) + value
    for weight, value in dual.items():
        if weight:
            state = (N - weight, 0, weight)
            lower[state] = lower.get(state, 0) + value

    # The size-six target words are distinct from all size-at-most-three
    # words and from both pure axes.  There is no current state collision.
    lower[TARGET_STATE] = lower.get(TARGET_STATE, 0) + TARGET_LOWER
    return lower


def aggregation_audit() -> dict:
    model = load_discovery_model()
    discovery = model.lower_bounds()
    corrected = corrected_lower_bounds()
    rows = support_rows()
    image, dual = forced_axis_bounds()

    collisions = []
    for row in rows:
        state = tuple(row["state"])
        if state in {
            (N - weight, 0, weight)
            for weight in dual
            if weight != 0
        }:
            pure_weight = state[2]
            mixed = row["count"]
            pure = dual[pure_weight]
            collisions.append(
                {
                    "state": list(state),
                    "input_type": row["input_type"],
                    "mixed_lower": mixed,
                    "pure_X_kernel_lower": pure,
                    "discovery_max_lower": discovery[state],
                    "correct_sum_lower": mixed + pure,
                    "discovery_deficit": mixed + pure - discovery[state],
                }
            )

    family_checks = []
    for row in rows:
        family_checks.append(
            {
                "input_type": row["input_type"],
                "state": row["state"],
                "input_size": row["input_size"],
                "output_weight": row["output_weight"],
                "mixed_vs_pure_X_disjoint": row["output_weight"] > 0,
                "mixed_vs_pure_Y_disjoint": row["nR"] > 0,
            }
        )

    current_zeros = sorted(model.PURE_Y_ZERO_WEIGHTS)
    return {
        "family_model": {
            "graph_state_words": "(x,Ax)",
            "mixed_support_at_most_three": "(x,Ax), 1<=wt(x)<=3",
            "pure_Y_image": "(y,y), y in im(A)",
            "pure_X_kernel": "(k,0), k in ker(A)",
            "pure_axis_intersection": "only (0,0)",
            "injectivity": "x -> (x,Ax) is injective from its first component",
        },
        "support_rows": rows,
        "family_disjointness_checks": family_checks,
        "all_nonzero_families_pairwise_disjoint": (
            all(
                row["mixed_vs_pure_X_disjoint"]
                and row["mixed_vs_pure_Y_disjoint"]
                for row in family_checks
            )
            and {
                (N - weight, weight, 0) for weight in image
            }.intersection(
                {(N - weight, 0, weight) for weight in dual}
            )
            == {(N, 0, 0)}
        ),
        "collisions_requiring_sum": collisions,
        "collision_count": len(collisions),
        "discovery_zero_state_lower": discovery[(N, 0, 0)],
        "correct_zero_state_lower": corrected[(N, 0, 0)],
        "zero_is_not_double_counted": corrected[(N, 0, 0)] == 1,
        "discovery_pure_Y_zero_weights": current_zeros,
        "correct_pure_Y_zero_weights": sorted(
            CORRECT_PURE_Y_ZERO_WEIGHTS
        ),
        "unsupported_discovery_zero_weights": sorted(
            set(current_zeros) - CORRECT_PURE_Y_ZERO_WEIGHTS
        ),
        "corrected_lower_bound_count": len(corrected),
    }


def quaternary_krawtchouk(degree: int, weight: int, length: int) -> int:
    return sum(
        (-1) ** s
        * 3 ** (degree - s)
        * comb(weight, s)
        * comb(length - weight, degree - s)
        for s in range(
            max(0, degree - (length - weight)),
            min(degree, weight) + 1,
        )
    )


def graph_rows(length: int, edge_mask: int) -> list[int]:
    edges = [
        (left, right)
        for left in range(length)
        for right in range(left + 1, length)
    ]
    rows = [0] * length
    for index, (left, right) in enumerate(edges):
        if (edge_mask >> index) & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return rows


def matrix_vector(rows: list[int], vector: int) -> int:
    result = 0
    for index, row in enumerate(rows):
        if (row & vector).bit_count() & 1:
            result |= 1 << index
    return result


def explicit_shadow_distributions(rows: list[int]) -> tuple[list[int], list[int]]:
    length = len(rows)
    all_one = (1 << length) - 1
    odd_degree_vector = sum(
        (row.bit_count() & 1) << index for index, row in enumerate(rows)
    )
    shadow_shift_z = all_one ^ odd_degree_vector
    ordinary = [0] * (length + 1)
    shadow = [0] * (length + 1)
    for x in range(1 << length):
        ax = matrix_vector(rows, x)
        ordinary[(x | ax).bit_count()] += 1
        shadow[(x | (ax ^ shadow_shift_z)).bit_count()] += 1
    return ordinary, shadow


def transform_shadow(ordinary: list[int]) -> tuple[list[int], list[int]]:
    length = len(ordinary) - 1
    shadow = []
    numerators = []
    for degree in range(length + 1):
        numerator = sum(
            (-1) ** weight
            * quaternary_krawtchouk(degree, weight, length)
            * count
            for weight, count in enumerate(ordinary)
        )
        if numerator % (1 << length):
            raise AssertionError("shadow transform is not integral")
        numerators.append(numerator)
        shadow.append(numerator // (1 << length))
    return shadow, numerators


def shadow_audit(max_order: int = 5) -> dict:
    graph_count = 0
    transform_coefficients = 0
    failures = []
    triangle = None
    for length in range(1, max_order + 1):
        edge_count = comb(length, 2)
        for edge_mask in range(1 << edge_count):
            rows = graph_rows(length, edge_mask)
            ordinary, explicit = explicit_shadow_distributions(rows)
            transformed, _ = transform_shadow(ordinary)
            graph_count += 1
            transform_coefficients += length + 1
            if transformed != explicit:
                failures.append(
                    {
                        "length": length,
                        "edge_mask": edge_mask,
                        "ordinary": ordinary,
                        "explicit": explicit,
                        "transformed": transformed,
                    }
                )
            if length == 3 and edge_mask == 7:
                triangle = {
                    "ordinary": ordinary,
                    "explicit_shadow": explicit,
                    "transformed_shadow": transformed,
                }
    return {
        "primary_formula": (
            "S_j=2^-n sum_t (-1)^t K_j^(4)(t) H_t"
        ),
        "krawtchouk_definition": (
            "K_j^(4)(t)=[z^j](1+3z)^(n-t)(1-z)^t"
        ),
        "rains_source": "https://arxiv.org/abs/quant-ph/9611001",
        "source_location": "Theorem 8 and Theorem 10",
        "graph_specific_shadow_coset": (
            "(0,1+d mod 2)+{(x,Ax)}; for degree 14 this is "
            "(0,1)+{(x,Ax)}"
        ),
        "coset_derivation": (
            "wt(x,Ax)=(1+d mod 2) dot x, and the symplectic product "
            "of (0,1+d mod 2) with (x,Ax) equals the same parity"
        ),
        "exhaustive_simple_graph_order_max": max_order,
        "graphs_checked": graph_count,
        "transform_coefficients_checked": transform_coefficients,
        "failure_count": len(failures),
        "failures": failures,
        "triangle_control": triangle,
        "formula_and_normalization_pass": not failures,
    }


def pure_y_zero_audit() -> dict:
    high_rows = []
    for weight in (94, 96, 98):
        complement_weight = N - weight
        high_rows.append(
            {
                "image_weight": weight,
                "complement_weight": complement_weight,
                "row_union_upper": 14 * complement_weight,
                "contradiction": weight > 14 * complement_weight,
            }
        )
    return {
        "verified_image_minimum_lower": 8,
        "minimum_forces_zero": [2, 4, 6],
        "unsupported_from_minimum_eight": [8, 10, 12],
        "high_weight_argument": (
            "If y is in im(A), then Ay=y.  Put z=1+y.  Since A1=0, "
            "Az=y, while wt(Az)<=14 wt(z)."
        ),
        "high_weight_checks": high_rows,
        "correct_zero_weights": sorted(CORRECT_PURE_Y_ZERO_WEIGHTS),
    }


def build_results() -> dict:
    frozen = verify_frozen_inputs()
    sealed = verify_discovery_manifest()
    aggregation = aggregation_audit()
    zeros = pure_y_zero_audit()
    shadows = shadow_audit()
    collisions = aggregation["collisions_requiring_sum"]
    all_checks = (
        frozen["pass"]
        and sealed["manifest_pass"]
        and sealed["entries_pass"]
        and sealed["entry_count"] == 12
        and aggregation["all_nonzero_families_pairwise_disjoint"]
        and aggregation["collision_count"] == 5
        and all(
            row["correct_sum_lower"]
            > row["discovery_max_lower"]
            for row in collisions
        )
        and aggregation["unsupported_discovery_zero_weights"] == [8, 10, 12]
        and all(row["contradiction"] for row in zeros["high_weight_checks"])
        and shadows["formula_and_normalization_pass"]
    )
    return {
        "format": "wave145-wave139-gf4-lower-aggregation-audit-v1",
        "claim_label": "REFUTED",
        "scope": (
            "Wave139 lower-bound aggregation, pure-Y zero rows, and the "
            "ordinary Hamming quantum-shadow convention"
        ),
        "frozen_inputs": frozen,
        "sealed_discovery_package": sealed,
        "aggregation": aggregation,
        "pure_Y_zero_audit": zeros,
        "quantum_shadow_audit": shadows,
        "verdict": {
            "wave139_max_aggregation": "REFUTED_UNDERCOUNT",
            "corrected_sum_aggregation": "VERIFIED",
            "pure_Y_zero_8_10_12": "VETO_UNSUPPORTED",
            "quantum_shadow_formula": "VERIFIED",
            "all_audit_checks_pass": all_checks,
        },
        "status_wall": {
            "corrected_formal_enumerator_feasibility": "UNKNOWN",
            "exact_rational_upper_bound": "NOT_FOUND",
            "adjacency_matrix": "NOT_CONSTRUCTED_OR_EXCLUDED",
            "Conway_99": "UNKNOWN",
            "external_novelty": "UNKNOWN",
        },
    }


def main() -> None:
    payload = build_results()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not payload["verdict"]["all_audit_checks_pass"]:
        raise SystemExit("Wave145 independent audit failed")
    print("Wave145 aggregation/shadow audit: PASS_WITH_WAVE139_VETO")


if __name__ == "__main__":
    main()
