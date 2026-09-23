"""Clean-room verifier for the sealed Wave143 binary S6 projection.

The mathematical model is rebuilt here.  No Wave143 Python module is imported
or executed.  Exact JSON witnesses are treated only as submitted points to be
checked against independently generated Krawtchouk, MacWilliams, Arf, shadow,
and integer-lattice equations.
"""

from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
from math import comb
from pathlib import Path
from typing import Any, Iterable

from flint import fmpz_mat

sys.set_int_max_str_digits(0)


N = 99
IMAGE_DIMENSION = 54
DUAL_DIMENSION = 45
IMAGE_ORDER = 1 << IMAGE_DIMENSION
DUAL_ORDER = 1 << DUAL_DIMENSION
GAUSS_MAGNITUDE = 1 << 27
DISCOVERY_MANIFEST_SHA256 = (
    "91e1053b886f05d8457bb14a5acaf87c02afe73ad087e98203cc779012571a61"
)
WAVE21_RESULTS_SHA256 = (
    "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b"
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts/wave143-binary-s6-projection"
WAVE21_RESULTS = ROOT / "attempts/wave21-six-vertex-lp/exact-results.json"
OUTPUT = HERE / "verification-results.json"

IMAGE_WEIGHTS = (0,) + tuple(range(14, 94, 2))
SIGNED_CONSTANTS = {
    0: Fraction(1),
    1: Fraction(-99),
    2: Fraction(3465),
    3: Fraction(-56595),
    4: Fraction(462924),
    5: Fraction(-1821204),
}
S6_CONSTANT = Fraction(2024484)
S6_SLOPE = Fraction(512, 3)
SHADOW_RADIUS = comb(N, 6)
RAW_SHADOW_N3_MIN = Fraction(3 * (-SHADOW_RADIUS - 2024484), 512)
WEAK_N3_MIN = Fraction(0)
WEAK_N3_MAX = Fraction(3 * (SHADOW_RADIUS - 2024484), 512)

IMAGE_LOWER = {
    14: 99,
    24: 4158,
    26: 693,
    30: 70686,
    32: 41580,
    34: 36036,
    36: 8547,
}
DUAL_LOWER = {
    15: 99,
    24: 693,
    26: 4158,
    31: 41580,
    33: 79002,
    35: 8316,
    37: 27720,
    39: 231,
    60: 231,
    62: 27720,
    64: 8316,
    66: 79002,
    68: 41580,
    73: 4158,
    75: 693,
    84: 99,
    99: 1,
}
EXPECTED_PAIR_TABLES = {
    "dual_closed_neighborhood_rows": {
        "15": {"intersection_15": 99},
        "ordered_distinct": {
            "intersection_2": 8316,
            "intersection_3": 1386,
        },
    },
    "image_neighborhood_rows": {
        "14": {"intersection_14": 99},
        "ordered_distinct": {
            "intersection_1": 1386,
            "intersection_2": 8316,
        },
    },
    "mixed_neighborhood_closed": {
        "ordered_diagonal": {"intersection_14": 99},
        "ordered_off_diagonal": {"intersection_2": 9702},
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, dict):
        if set(value) == {"numerator", "denominator"}:
            return Fraction(int(value["numerator"]), int(value["denominator"]))
        if set(value) == {"num", "den"}:
            return Fraction(int(value["num"]), int(value["den"]))
    raise TypeError(f"unsupported exact rational encoding: {value!r}")


def qtext(value: Fraction | int) -> str:
    return str(Fraction(value))


@lru_cache(maxsize=None)
def krawtchouk(degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * comb(weight, overlap)
        * comb(N - weight, degree - overlap)
        for overlap in range(
            max(0, degree - (N - weight)),
            min(weight, degree) + 1,
        )
    )


def phase(weight: int) -> int:
    if weight % 2:
        raise ValueError("the Arf phase is used only at even image weights")
    return -1 if weight % 4 == 2 else 1


def parse_coefficient_map(raw: dict[str, Any]) -> list[Fraction]:
    answer = [Fraction(0)] * (N + 1)
    for weight, value in raw.items():
        index = int(weight)
        if not 0 <= index <= N:
            raise ValueError(f"weight {index} lies outside 0..{N}")
        answer[index] = fraction(value)
    return answer


def forward_dual(image: list[Fraction]) -> list[Fraction]:
    return [
        sum(
            image[weight] * krawtchouk(degree, weight)
            for weight in range(N + 1)
        )
        / IMAGE_ORDER
        for degree in range(N + 1)
    ]


def signed_moment(image: list[Fraction], degree: int) -> Fraction:
    return sum(
        phase(weight) * image[weight] * krawtchouk(degree, weight)
        for weight in range(0, N + 1, 2)
    )


def find_map(payload: dict[str, Any], names: Iterable[str]) -> dict[str, Any]:
    for name in names:
        value = payload.get(name)
        if isinstance(value, dict):
            return value
    ordinary = payload.get("ordinary")
    if isinstance(ordinary, dict):
        for name in names:
            value = ordinary.get(name)
            if isinstance(value, dict):
                return value
    raise KeyError(f"none of {tuple(names)!r} is an exact coefficient map")


def find_scalar(payload: dict[str, Any], names: Iterable[str]) -> Any:
    for name in names:
        if name in payload:
            return payload[name]
    metadata = payload.get("metadata")
    if isinstance(metadata, dict):
        for name in names:
            if name in metadata:
                return metadata[name]
    raise KeyError(f"none of {tuple(names)!r} appears in witness")


def audit_split_table(
    raw: dict[str, Any],
    ordinary: list[Fraction],
    root_weight: int,
    odd_factor: int,
    forced: dict[int, dict[int, int]],
) -> dict[str, Any]:
    rows = {
        int(weight): {
            int(intersection): fraction(value)
            for intersection, value in entries.items()
        }
        for weight, entries in raw.items()
    }
    failures = []
    for weight, coefficient in enumerate(ordinary):
        entries = rows.get(weight, {})
        lower = max(0, weight + root_weight - N)
        upper = min(weight, root_weight)
        if any(
            intersection < lower or intersection > upper
            for intersection in entries
        ):
            failures.append(f"intersection range failed at shell {weight}")
        if any(value < 0 for value in entries.values()):
            failures.append(f"negative entry at shell {weight}")
        if sum(entries.values(), Fraction(0)) != N * coefficient:
            failures.append(f"row sum failed at shell {weight}")
        if (
            sum(
                intersection * value
                for intersection, value in entries.items()
            )
            != root_weight * weight * coefficient
        ):
            failures.append(f"first moment failed at shell {weight}")
        if (
            sum(
                value
                for intersection, value in entries.items()
                if intersection % 2
            )
            != odd_factor * weight * coefficient
        ):
            failures.append(f"odd-intersection count failed at shell {weight}")
        for intersection, minimum in forced.get(weight, {}).items():
            if entries.get(intersection, Fraction(0)) < minimum:
                failures.append(
                    f"forced entry ({weight},{intersection})<{minimum}"
                )
    return {
        "pass": not failures,
        "failures": failures,
        "row_count": len(rows),
        "nonintegral_entry_count": sum(
            value.denominator != 1
            for entries in rows.values()
            for value in entries.values()
        ),
    }


def audit_split_systems(
    payload: dict[str, Any],
    image: list[Fraction],
    dual: list[Fraction],
) -> dict[str, Any]:
    submitted = payload.get("split_enumerators")
    if not isinstance(submitted, dict):
        return {
            "pass": False,
            "failures": ["missing split_enumerators"],
            "systems": {},
        }
    specifications = {
        "image_vs_neighborhood": (
            image,
            14,
            1,
            {14: {14: 99, 1: 1386, 2: 8316}},
        ),
        "image_vs_closed": (
            image,
            15,
            0,
            {14: {14: 99, 2: 9702}},
        ),
        "dual_vs_closed": (
            dual,
            15,
            1,
            {15: {15: 99, 2: 8316, 3: 1386}},
        ),
        "dual_vs_neighborhood": (
            dual,
            14,
            0,
            {15: {14: 99, 2: 9702}},
        ),
    }
    systems = {}
    failures = []
    for name, (ordinary, root, odd_factor, forced) in specifications.items():
        if not isinstance(submitted.get(name), dict):
            systems[name] = {
                "pass": False,
                "failures": ["missing system"],
            }
        else:
            systems[name] = audit_split_table(
                submitted[name],
                ordinary,
                root,
                odd_factor,
                forced,
            )
        if not systems[name]["pass"]:
            failures.append(name)
    return {
        "pass": not failures,
        "failures": failures,
        "systems": systems,
    }


def audit_point(path: Path, expected_sign: int, expected_n3: Fraction) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    image = parse_coefficient_map(
        find_map(payload, ("image_coefficients", "A", "image"))
    )
    try:
        submitted_dual = parse_coefficient_map(
            find_map(payload, ("dual_coefficients", "B", "dual"))
        )
    except KeyError:
        submitted_dual = None
    dual = forward_dual(image)
    submitted_sign = int(find_scalar(payload, ("sign", "arf_sign", "epsilon")))
    submitted_n3 = fraction(find_scalar(payload, ("n3", "n_3")))

    failures: list[str] = []
    if submitted_sign != expected_sign:
        failures.append(
            f"submitted sign {submitted_sign} != filename sign {expected_sign}"
        )
    if submitted_n3 != expected_n3:
        failures.append(
            f"submitted n3 {submitted_n3} != expected {expected_n3}"
        )
    if submitted_dual is not None and submitted_dual != dual:
        failures.append("submitted dual map differs from exact forward transform")
    if image[0] != 1 or sum(image) != IMAGE_ORDER:
        failures.append("image normalization/size failed")
    if dual[0] != 1 or sum(dual) != DUAL_ORDER:
        failures.append("dual normalization/size failed")
    if any(value < 0 for value in image):
        failures.append("negative image coefficient")
    if any(value < 0 for value in dual):
        failures.append("negative dual coefficient")
    if any(image[weight] for weight in range(1, N + 1, 2)):
        failures.append("odd image support")
    if any(image[weight] for weight in range(1, 14)):
        failures.append("image support below 14")
    if any(image[weight] for weight in (94, 96, 98)):
        failures.append("Wave132 high-weight cut failed")
    if any(dual[weight] for weight in range(1, 15)):
        failures.append("strengthened formal dual-distance-15 slice failed")
    if any(dual[weight] != dual[N - weight] for weight in range(N + 1)):
        failures.append("dual complement symmetry failed")
    for weight, lower in IMAGE_LOWER.items():
        if image[weight] < lower:
            failures.append(f"image lower bound A_{weight}>={lower} failed")
    for weight, lower in DUAL_LOWER.items():
        if dual[weight] < lower:
            failures.append(f"dual lower bound B_{weight}>={lower} failed")

    inverse_failures = []
    for degree in range(N + 1):
        inverse = sum(
            dual[weight] * krawtchouk(degree, weight)
            for weight in range(N + 1)
        )
        if inverse != DUAL_ORDER * image[degree]:
            inverse_failures.append(degree)
    if inverse_failures:
        failures.append(f"inverse MacWilliams failed at {inverse_failures}")

    signed_rows: dict[str, Any] = {}
    gauss = Fraction(expected_sign * GAUSS_MAGNITUDE)
    exact_targets = dict(SIGNED_CONSTANTS)
    exact_targets[6] = S6_CONSTANT + S6_SLOPE * expected_n3
    for degree, target in exact_targets.items():
        observed = signed_moment(image, degree)
        expected = gauss * target
        passed = observed == expected
        if not passed:
            failures.append(
                f"signed row {degree}: {qtext(observed)} != {qtext(expected)}"
            )
        signed_rows[str(degree)] = {
            "observed": qtext(observed),
            "expected": qtext(expected),
            "normalized_target": qtext(target),
            "pass": passed,
        }

    shadow_rows: dict[str, Any] = {}
    shadow_failures = []
    for degree in range(N + 1):
        observed = signed_moment(image, degree)
        bound = GAUSS_MAGNITUDE * comb(N, degree)
        passed = -bound <= observed <= bound
        if not passed:
            shadow_failures.append(degree)
        shadow_rows[str(degree)] = {
            "observed": qtext(observed),
            "absolute_bound": str(bound),
            "pass": passed,
        }
    if shadow_failures:
        failures.append(f"shadow bounds failed at {shadow_failures}")

    split_systems = audit_split_systems(payload, image, dual)
    if not split_systems["pass"]:
        failures.append(
            f"distinguished split systems failed: {split_systems['failures']}"
        )
    pair_tables_pass = (
        payload.get("distinguished_pair_tables") == EXPECTED_PAIR_TABLES
    )
    if not pair_tables_pass:
        failures.append("distinguished pair tables differ from exact target")

    try:
        display_path = str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        display_path = str(path)
    return {
        "path": display_path,
        "sha256": sha256(path),
        "expected_sign": expected_sign,
        "submitted_sign": submitted_sign,
        "expected_n3": qtext(expected_n3),
        "submitted_n3": qtext(submitted_n3),
        "pass": not failures,
        "failures": failures,
        "forward_rows_checked": N + 1,
        "inverse_rows_checked": N + 1,
        "image_nonintegral_count": sum(x.denominator != 1 for x in image),
        "dual_nonintegral_count": sum(x.denominator != 1 for x in dual),
        "signed_rows": signed_rows,
        "shadow_rows": shadow_rows,
        "shadow_row_count": len(shadow_rows),
        "split_systems": split_systems,
        "distinguished_pair_tables_pass": pair_tables_pass,
    }


def graph_edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(combinations(range(order), 2))


@lru_cache(maxsize=None)
def permutation_bit_maps(order: int) -> tuple[tuple[int, ...], ...]:
    edges = graph_edges(order)
    positions = {edge: index for index, edge in enumerate(edges)}
    maps = []
    for permutation in permutations(range(order)):
        maps.append(
            tuple(
                1 << positions[
                    tuple(sorted((permutation[left], permutation[right])))
                ]
                for left, right in edges
            )
        )
    return tuple(maps)


def permute_mask(mask: int, bit_map: tuple[int, ...]) -> int:
    answer = 0
    for index, image_bit in enumerate(bit_map):
        if (mask >> index) & 1:
            answer |= image_bit
    return answer


@lru_cache(maxsize=None)
def canonical_mask(mask: int, order: int) -> int:
    return min(
        permute_mask(mask, mapping)
        for mapping in permutation_bit_maps(order)
    )


def locally_admissible(mask: int, order: int) -> bool:
    edges = graph_edges(order)
    adjacency = [0] * order
    for index, (left, right) in enumerate(edges):
        if (mask >> index) & 1:
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    for index, (left, right) in enumerate(edges):
        common = (adjacency[left] & adjacency[right]).bit_count()
        maximum = 1 if (mask >> index) & 1 else 2
        if common > maximum:
            return False
    return True


def six_classes() -> tuple[int, ...]:
    representatives = {
        canonical_mask(mask, 6)
        for mask in range(1 << comb(6, 2))
        if locally_admissible(mask, 6)
    }
    return tuple(sorted(representatives))


def independently_derive_s6() -> dict[str, Any]:
    if sha256(WAVE21_RESULTS) != WAVE21_RESULTS_SHA256:
        raise AssertionError("the frozen Wave21 prerequisite has drifted")
    payload = json.loads(WAVE21_RESULTS.read_text(encoding="utf-8"))
    classes = six_classes()
    alignment = payload["independent_graph_census"][
        "source_index_alignment"
    ]["N_to_canonical_positions_zero_based"]
    formulas = payload["formula_tables"]["six"]
    if len(classes) != 62 or sorted(alignment) != list(range(62)):
        raise AssertionError("six-class census/alignment drift")

    constant = Fraction(0)
    slope = Fraction(0)
    positive_constant = Fraction(0)
    negative_constant = Fraction(0)
    for source_index in range(1, 63):
        mask = classes[alignment[source_index - 1]]
        sign = (-1) ** (6 + mask.bit_count())
        form = formulas[str(source_index)]
        signed_constant = sign * fraction(form["constant"])
        signed_slope = sign * fraction(form["n3_coefficient"])
        constant += signed_constant
        slope += signed_slope
        if signed_constant >= 0:
            positive_constant += signed_constant
        else:
            negative_constant += signed_constant
    if (constant, slope) != (S6_CONSTANT, S6_SLOPE):
        raise AssertionError(f"independent S6 drift: {(constant, slope)!r}")
    return {
        "wave21_sha256": WAVE21_RESULTS_SHA256,
        "class_count": len(classes),
        "alignment_bijective": True,
        "identity": (
            "S6=sum_|T|=6 (-1)^(6+e(T))="
            "2024484+(512/3)n3"
        ),
        "constant": qtext(constant),
        "n3_coefficient": qtext(slope),
        "positive_constant_sum": qtext(positive_constant),
        "negative_constant_sum": qtext(negative_constant),
    }


def equality_system(sign: int) -> tuple[list[list[int]], list[int], list[int]]:
    rows: list[list[int]] = []
    rhs: list[int] = []
    n3_column: list[int] = []

    rows.append([int(weight == 0) for weight in IMAGE_WEIGHTS])
    rhs.append(1)
    n3_column.append(0)
    rows.append([1] * len(IMAGE_WEIGHTS))
    rhs.append(IMAGE_ORDER)
    n3_column.append(0)
    for degree in range(1, 15):
        rows.append([krawtchouk(degree, weight) for weight in IMAGE_WEIGHTS])
        rhs.append(0)
        n3_column.append(0)
    for degree in range(6):
        rows.append(
            [
                phase(weight) * krawtchouk(degree, weight)
                for weight in IMAGE_WEIGHTS
            ]
        )
        rhs.append(sign * GAUSS_MAGNITUDE * int(SIGNED_CONSTANTS[degree]))
        n3_column.append(0)

    # Clear the only denominator in S6:
    # 3 M6 = sign*2^27*(3*2024484 + 512*n3).
    rows.append(
        [
            3 * phase(weight) * krawtchouk(6, weight)
            for weight in IMAGE_WEIGHTS
        ]
    )
    rhs.append(sign * GAUSS_MAGNITUDE * 3 * int(S6_CONSTANT))
    n3_column.append(-sign * GAUSS_MAGNITUDE * 512)
    return rows, rhs, n3_column


def nonzero_hnf_rows(matrix: fmpz_mat) -> list[list[int]]:
    hnf = matrix.hnf()
    return [
        [int(hnf[row, column]) for column in range(hnf.ncols())]
        for row in range(hnf.nrows())
        if any(hnf[row, column] for column in range(hnf.ncols()))
    ]


def stable_rows_hash(rows: list[list[int]]) -> str:
    encoded = (
        json.dumps(rows, separators=(",", ":"), ensure_ascii=True) + "\n"
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def integral_equality_projection(sign: int) -> dict[str, Any]:
    rows, rhs, n3_column = equality_system(sign)
    coefficient_matrix = fmpz_mat(rows)
    column_generators = coefficient_matrix.transpose()
    basis = nonzero_hnf_rows(column_generators)

    def member(vector: list[int]) -> bool:
        augmented = fmpz_mat(column_generators.table() + [vector])
        return nonzero_hnf_rows(augmented) == basis

    fixed_rhs = lambda n3: [
        value - coefficient * n3
        for value, coefficient in zip(rhs, n3_column, strict=True)
    ]
    residues = {residue: member(fixed_rhs(residue)) for residue in range(3)}
    base_member = member(fixed_rhs(0))
    step_member = member(
        [
            -3 * coefficient
            for coefficient in n3_column
        ]
    )
    if residues != {0: True, 1: False, 2: False}:
        raise AssertionError(f"unexpected equality-lattice residues: {residues}")
    if not base_member or not step_member:
        raise AssertionError("failed to certify the full 3Z equality projection")

    augmented_all = fmpz_mat(
        [
            row + [coefficient]
            for row, coefficient in zip(rows, n3_column, strict=True)
        ]
    )
    return {
        "sign": sign,
        "equation_rows": len(rows),
        "image_variables": len(IMAGE_WEIGHTS),
        "coefficient_rank": coefficient_matrix.rank(),
        "augmented_variable_rank": augmented_all.rank(),
        "column_lattice_hnf_nonzero_rows": len(basis),
        "column_lattice_hnf_canonical_json_sha256": stable_rows_hash(basis),
        "residue_membership_mod_3": {
            str(key): value for key, value in residues.items()
        },
        "zero_rhs_member": base_member,
        "three_step_member": step_member,
        "exact_projection": "n3 in 3Z",
        "necessity_proof": (
            "Reducing the cleared S6 equation modulo 3 gives "
            "2^27*512*n3=0 mod 3, hence 3 divides n3."
        ),
        "sufficiency_proof": (
            "Exact HNF membership certifies the n3=0 right side and the "
            "n3-to-n3+3 right-side step in the image-variable column lattice."
        ),
        "scope": "equalities only; nonnegativity and graph realization omitted",
    }


def full_lattice_system(
    sign: int,
) -> tuple[list[list[int]], list[int], list[str], tuple[str, ...]]:
    names = (
        tuple(f"A_{weight}" for weight in IMAGE_WEIGHTS)
        + tuple(f"D_{degree}" for degree in range(N + 1))
        + ("k",)
    )
    width = len(names)
    rows: list[list[int]] = []
    rhs: list[int] = []
    labels: list[str] = []

    def blank() -> list[int]:
        return [0] * width

    row = blank()
    row[0] = 1
    rows.append(row)
    rhs.append(1)
    labels.append("A0")

    row = blank()
    for index in range(len(IMAGE_WEIGHTS)):
        row[index] = 1
    rows.append(row)
    rhs.append(IMAGE_ORDER)
    labels.append("image_size")

    for degree in range(N + 1):
        row = blank()
        for index, weight in enumerate(IMAGE_WEIGHTS):
            row[index] = krawtchouk(degree, weight)
        row[len(IMAGE_WEIGHTS) + degree] = -IMAGE_ORDER
        rows.append(row)
        rhs.append(0)
        labels.append(f"MacWilliams_{degree}")

    for degree, multiplier in SIGNED_CONSTANTS.items():
        row = blank()
        for index, weight in enumerate(IMAGE_WEIGHTS):
            row[index] = phase(weight) * krawtchouk(degree, weight)
        rows.append(row)
        rhs.append(sign * GAUSS_MAGNITUDE * int(multiplier))
        labels.append(f"signed_M{degree}")

    # This version uses k=n3/3, so S6=2024484+512*k.
    row = blank()
    for index, weight in enumerate(IMAGE_WEIGHTS):
        row[index] = phase(weight) * krawtchouk(6, weight)
    row[-1] = -sign * GAUSS_MAGNITUDE * 512
    rows.append(row)
    rhs.append(sign * GAUSS_MAGNITUDE * int(S6_CONSTANT))
    labels.append("signed_M6_target")
    return rows, rhs, labels, names


def canonical_matrix_digest(
    rows: list[list[int]],
    rhs: list[int],
    labels: list[str],
) -> str:
    payload = json.dumps(
        {"rows": rows, "rhs": rhs, "labels": labels},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def extended_gcd(values: list[int]) -> tuple[int, list[int]]:
    gcd_value = 0
    coefficients: list[int] = []
    for value in values:
        if not coefficients:
            gcd_value = abs(value)
            coefficients = [
                0 if value == 0 else (1 if value > 0 else -1)
            ]
            continue
        old_r, remainder = gcd_value, abs(value)
        old_s, new_s = 1, 0
        old_t, new_t = 0, 1
        while remainder:
            quotient = old_r // remainder
            old_r, remainder = remainder, old_r - quotient * remainder
            old_s, new_s = new_s, old_s - quotient * new_s
            old_t, new_t = new_t, old_t - quotient * new_t
        coefficients = [old_s * item for item in coefficients]
        coefficients.append(old_t * (1 if value >= 0 else -1))
        gcd_value = old_r
    return gcd_value, coefficients


def vector_digest(vector: list[int]) -> dict[str, Any]:
    encoded = ",".join(str(value) for value in vector).encode("ascii")
    return {
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "nonzero_coordinates": sum(value != 0 for value in vector),
        "maximum_decimal_digits": max(
            len(str(abs(value))) for value in vector
        ),
        "k": str(vector[-1]),
    }


def reconstruct_full_lattice(sign: int) -> dict[str, Any]:
    rows, rhs, labels, names = full_lattice_system(sign)
    matrix = fmpz_mat(rows)
    hnf, transform = matrix.transpose().hnf(transform=True)
    rank = matrix.rank()
    if rank != len(rows):
        raise AssertionError("full equality rows are not independent")
    nonzero_hnf = fmpz_mat(
        rank,
        hnf.ncols(),
        [
            hnf[row, column]
            for row in range(rank)
            for column in range(hnf.ncols())
        ],
    )
    coefficients = nonzero_hnf.transpose().solve(
        fmpz_mat(len(rhs), 1, rhs)
    )
    nonzero_transform = fmpz_mat(
        rank,
        transform.ncols(),
        [
            transform[row, column]
            for row in range(rank)
            for column in range(transform.ncols())
        ],
    )
    particular_q = coefficients.transpose() * nonzero_transform
    particular = []
    for column in range(particular_q.ncols()):
        value = particular_q[0, column]
        if value.denominator != 1:
            raise AssertionError("HNF particular solution is nonintegral")
        particular.append(int(value.numerator))
    particular_pass = (
        matrix * fmpz_mat(len(particular), 1, particular)
        == fmpz_mat(len(rhs), 1, rhs)
    )
    if not particular_pass or particular[-1] != 0:
        raise AssertionError("HNF particular solution replay failed")
    return {
        "_matrix": matrix,
        "_transform": transform,
        "_particular": particular,
        "sign": sign,
        "unknown_count": len(names),
        "equation_count": len(rows),
        "rank": rank,
        "nullity": transform.nrows() - rank,
        "canonical_matrix_sha256": canonical_matrix_digest(
            rows, rhs, labels
        ),
        "particular_k0": vector_digest(particular),
        "particular_replay_pass": particular_pass,
    }


def audit_full_lattice_certificate() -> dict[str, Any]:
    plus = reconstruct_full_lattice(1)
    minus = reconstruct_full_lattice(-1)
    plus_transform = plus["_transform"]
    plus_matrix = plus["_matrix"]
    null_rows = range(plus["rank"], plus_transform.nrows())
    k_column = plus_transform.ncols() - 1
    k_values = [
        int(plus_transform[row, k_column])
        for row in null_rows
    ]
    projection_gcd, bezout = extended_gcd(k_values)
    delta = [0] * plus_transform.ncols()
    for coefficient, row in zip(
        bezout,
        range(plus["rank"], plus_transform.nrows()),
        strict=True,
    ):
        if coefficient:
            for column in range(plus_transform.ncols()):
                delta[column] += (
                    coefficient * int(plus_transform[row, column])
                )
    if projection_gcd != 1 or delta[-1] != 1:
        raise AssertionError("full equality lattice does not project onto all k")
    zero_plus = fmpz_mat(plus_matrix.nrows(), 1)
    plus_step_pass = (
        plus_matrix * fmpz_mat(len(delta), 1, delta) == zero_plus
    )
    minus_delta = [-value for value in delta]
    minus_delta[-1] = 1
    minus_matrix = minus["_matrix"]
    zero_minus = fmpz_mat(minus_matrix.nrows(), 1)
    minus_step_pass = (
        minus_matrix * fmpz_mat(len(minus_delta), 1, minus_delta)
        == zero_minus
    )
    if not plus_step_pass or not minus_step_pass:
        raise AssertionError("reconstructed homogeneous step failed replay")

    submitted = json.loads(
        (DISCOVERY / "lattice-certificate.json").read_text(encoding="utf-8")
    )
    independent_records = {
        "matrix_sha256": {
            "plus": plus["canonical_matrix_sha256"],
            "minus": minus["canonical_matrix_sha256"],
        },
        "particular_solutions_k0": {
            "plus": plus["particular_k0"],
            "minus": minus["particular_k0"],
        },
        "homogeneous_steps_delta_k1": {
            "plus": vector_digest(delta),
            "minus": vector_digest(minus_delta),
        },
    }
    comparisons = {
        "matrix_plus": (
            independent_records["matrix_sha256"]["plus"]
            == submitted["matrix_sha256"]["plus"]
        ),
        "matrix_minus": (
            independent_records["matrix_sha256"]["minus"]
            == submitted["matrix_sha256"]["minus"]
        ),
    }
    for family in (
        "particular_solutions_k0",
        "homogeneous_steps_delta_k1",
    ):
        for branch in ("plus", "minus"):
            for field in (
                "sha256",
                "nonzero_coordinates",
                "maximum_decimal_digits",
                "k",
            ):
                comparisons[f"{family}_{branch}_{field}"] = (
                    independent_records[family][branch][field]
                    == submitted[family][branch][field]
                )
    comparison_pass = all(comparisons.values())
    if not comparison_pass:
        raise AssertionError(
            f"submitted HNF reconstruction metadata drift: {comparisons}"
        )

    for internal in ("_matrix", "_transform", "_particular"):
        del plus[internal]
        del minus[internal]
    return {
        "submitted_certificate_sha256": sha256(
            DISCOVERY / "lattice-certificate.json"
        ),
        "unknown_count": plus["unknown_count"],
        "equation_count": plus["equation_count"],
        "rank": plus["rank"],
        "nullity": plus["nullity"],
        "kernel_projection_gcd_in_k": projection_gcd,
        "exact_projection": "all k in Z, equivalently n3 in 3Z",
        "plus": plus,
        "minus": minus,
        "homogeneous_steps_delta_k1": {
            "plus": {
                **vector_digest(delta),
                "replay_pass": plus_step_pass,
            },
            "minus": {
                **vector_digest(minus_delta),
                "replay_pass": minus_step_pass,
            },
        },
        "submitted_hash_and_metadata_comparisons": comparisons,
        "submitted_hashes_critically_reconstructed": comparison_pass,
        "scope": (
            "109 equality rows with integral A,D,k and n3=3k; "
            "dual-distance zeros, inequalities, and nonnegativity omitted"
        ),
    }


def weak_projection_proof() -> dict[str, Any]:
    return {
        "shadow_degree": 6,
        "binomial_radius": SHADOW_RADIUS,
        "derivation": (
            "|M6|<=2^27*C(99,6) and "
            "M6=epsilon*2^27*(2024484+(512/3)n3)"
        ),
        "raw_two_sided_shadow_n3_min": qtext(RAW_SHADOW_N3_MIN),
        "exact_n3_min": qtext(WEAK_N3_MIN),
        "exact_n3_max": qtext(WEAK_N3_MAX),
        "minimum_proof": "the formal model explicitly imposes n3>=0",
        "maximum_proof": (
            "the sign-appropriate upper side of the degree-6 shadow row"
        ),
        "same_for_both_Arf_signs": True,
        "strictly_weaker_than_target_count_interval": True,
        "target_count_interval": "708<=n3<=4158",
    }


def audit_input_freeze() -> dict[str, Any]:
    freeze = DISCOVERY / "input-freeze.sha256"
    entries = []
    failures = []
    for line_number, line in enumerate(
        freeze.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        pieces = line.split(maxsplit=1)
        if len(pieces) != 2:
            failures.append(f"malformed input-freeze line {line_number}")
            continue
        expected, relative = pieces
        target = (DISCOVERY / relative.lstrip("*")).resolve()
        observed = sha256(target) if target.is_file() else None
        passed = expected == observed
        if not passed:
            failures.append(f"input drift: {relative}")
        entries.append(
            {
                "path": str(target.relative_to(ROOT)).replace("\\", "/"),
                "expected_sha256": expected,
                "observed_sha256": observed,
                "pass": passed,
            }
        )
    return {
        "path": "attempts/wave143-binary-s6-projection/input-freeze.sha256",
        "sha256": sha256(freeze),
        "entry_count": len(entries),
        "entries": entries,
        "pass": not failures,
        "failures": failures,
    }


def audit_manifest() -> dict[str, Any]:
    manifest = DISCOVERY / "package-manifest.sha256"
    observed_manifest = sha256(manifest)
    entries = []
    failures = []
    for line_number, line in enumerate(
        manifest.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        pieces = line.split(maxsplit=1)
        if len(pieces) != 2:
            failures.append(f"malformed manifest line {line_number}")
            continue
        expected, relative = pieces
        relative = relative.lstrip("*")
        target = DISCOVERY / relative
        observed = sha256(target) if target.is_file() else None
        passed = observed == expected
        if not passed:
            failures.append(f"manifest mismatch: {relative}")
        entries.append(
            {
                "path": (
                    f"attempts/wave143-binary-s6-projection/{relative}"
                ),
                "expected_sha256": expected,
                "observed_sha256": observed,
                "pass": passed,
            }
        )
    if observed_manifest != DISCOVERY_MANIFEST_SHA256:
        failures.append("final discovery manifest hash differs from frozen hash")
    return {
        "expected_manifest_sha256": DISCOVERY_MANIFEST_SHA256,
        "observed_manifest_sha256": observed_manifest,
        "entry_count": len(entries),
        "entries": entries,
        "pass": not failures,
        "failures": failures,
    }


def build_results() -> dict[str, Any]:
    manifest = audit_manifest()
    if not manifest["pass"]:
        raise AssertionError(f"sealed package audit failed: {manifest['failures']}")
    input_freeze = audit_input_freeze()
    if not input_freeze["pass"]:
        raise AssertionError(f"input freeze failed: {input_freeze['failures']}")
    s6 = independently_derive_s6()
    lattice = {
        str(sign): integral_equality_projection(sign)
        for sign in (-1, 1)
    }
    full_lattice = audit_full_lattice_certificate()
    point_specs = (
        ("witness-plus-n3-708.json", 1, Fraction(708), "target_endpoint"),
        ("witness-plus-n3-4158.json", 1, Fraction(4158), "target_endpoint"),
        ("witness-minus-n3-708.json", -1, Fraction(708), "target_endpoint"),
        ("witness-minus-n3-4158.json", -1, Fraction(4158), "target_endpoint"),
        (
            "projection-optimum-plus-min.json",
            1,
            WEAK_N3_MIN,
            "weak_minimum",
        ),
        (
            "projection-optimum-plus-max.json",
            1,
            WEAK_N3_MAX,
            "weak_maximum",
        ),
        (
            "projection-optimum-minus-min.json",
            -1,
            WEAK_N3_MIN,
            "weak_minimum",
        ),
        (
            "projection-optimum-minus-max.json",
            -1,
            WEAK_N3_MAX,
            "weak_maximum",
        ),
    )
    points = []
    for filename, sign, n3, role in point_specs:
        audit = audit_point(DISCOVERY / filename, sign, n3)
        audit["role"] = role
        points.append(audit)
    point_failures = [
        point["path"] for point in points if not point["pass"]
    ]
    if point_failures:
        raise AssertionError(f"submitted exact points failed: {point_failures}")

    integer_scout = json.loads(
        (DISCOVERY / "integer-scout.json").read_text(encoding="utf-8")
    )
    timeout_safely_unknown = (
        integer_scout.get("claim_label") == "UNKNOWN"
        and integer_scout.get("negative_inference_allowed") is False
        and len(integer_scout.get("results", [])) == 4
        and all(
            result.get("status") == "UNKNOWN_HARD_TIMEOUT"
            for result in integer_scout.get("results", [])
        )
    )
    if not timeout_safely_unknown:
        raise AssertionError("integral timeout telemetry was overstated or drifted")
    return {
        "format": "wave143-clean-room-verification-v1",
        "verdict": "PASS_WITH_SCOPE_CORRECTION",
        "manifest": manifest,
        "input_freeze": input_freeze,
        "independent_s6_derivation": s6,
        "weak_projection_proof": weak_projection_proof(),
        "integral_equality_lattice": lattice,
        "full_109_by_142_lattice_reconstruction": full_lattice,
        "points": points,
        "point_summary": {
            "count": len(points),
            "all_pass": True,
            "ordinary_MacWilliams_rows": len(points) * 200,
            "shadow_rows_t6_through_t99": len(points) * 94,
            "distinguished_split_systems": len(points) * 4,
            "target_endpoint_points": 4,
            "weak_optimum_points": 4,
        },
        "integral_scout": {
            "sha256": sha256(DISCOVERY / "integer-scout.json"),
            "safely_unknown": timeout_safely_unknown,
            "negative_inference_accepted": False,
        },
        "premise_audit": {
            "target_forced": [
                "binary image code im(A) is even and has dimension 54",
                "dual code ker(A) has dimension 45 and contains 1",
                "available target arguments prove d(im A)>=8 and d(ker A)>=8",
                "the S6 signed-shell identity follows conditionally from the frozen six-vertex census",
            ],
            "strengthened_formal_slice": [
                "B_1=...=B_14=0, equivalently formal dual distance at least 15",
                "all endpoint and optimum witnesses verified here live in that stronger slice",
            ],
            "nonimplication": (
                "Failure of this strengthened slice would not by itself refute "
                "the target graph unless dual distance at least 15 is separately proved."
            ),
            "verifier_veto": (
                "Any target-graph or Conway-99 implication that uses the "
                "unproved d(ker A)>=15 strengthening is vetoed."
            ),
            "equality_lattice_scope_correction": (
                "The 109-by-142 HNF layer omits the D_1=...=D_14=0 "
                "conditions as well as all inequalities; it is weaker than "
                "the rational Wave143 slice."
            ),
        },
        "scope_boundary": {
            "formal_rational_strengthened_projection": "VERIFIED",
            "formal_integral_equality_projection": "VERIFIED_AS_3Z",
            "integral_nonnegative_enumerator": "UNKNOWN_HARD_TIMEOUT",
            "binary_code": "UNKNOWN",
            "graph": "UNKNOWN",
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
                "manifest": result["manifest"]["pass"],
                "S6": result["independent_s6_derivation"]["identity"],
                "lattice": {
                    sign: data["exact_projection"]
                    for sign, data in result["integral_equality_lattice"].items()
                },
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
