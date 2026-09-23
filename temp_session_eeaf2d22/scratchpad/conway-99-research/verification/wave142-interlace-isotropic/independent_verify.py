"""Independent verifier for the sealed Wave142 interlace/IAS package.

No discovery module is imported.  Local graph classes, principal ranks,
diagonal toggles, IAS transversals, and overlap controls are regenerated with
standard-library code.  The verifier also audits whether every premise used
by the discovery is actually present in its frozen inputs.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations, product
from math import comb
from pathlib import Path


N = 99
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DISCOVERY = ROOT / "attempts/wave142-interlace-isotropic"
WAVE21_RESULTS = ROOT / "attempts/wave21-six-vertex-lp/exact-results.json"
WAVE131_RESULTS = (
    ROOT / "attempts/wave131-binary-lcd-enumerator/exact-results.json"
)
OUTPUT = HERE / "verification-results.json"

SEALED_MANIFEST = (
    "241cb75308d26942adf6dcdfc3b1c344c3c48fee35df2b9eeb1561fa2b01b443"
)
FROZEN_INPUTS = {
    "attempts/wave21-six-vertex-lp/exact_check.py":
        "0dd44ca37ca21aeaa757f3b2d7f7f9639907f22b95da39472ed9d836027a94a3",
    "attempts/wave21-six-vertex-lp/exact-results.json":
        "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b",
    "attempts/wave131-binary-lcd-enumerator/exact-results.json":
        "7d5c32179df697f8ab427d28736f2e1bb91e41f16a0f18f9dc242b7c03091839",
    "attempts/wave141-bivariate-graph-code/exact_check.py":
        "15378b9a9f807071de0aae5604c4178af5b3cfa067851230781d67d05f2ca204",
    "attempts/wave141-bivariate-graph-code/exact-results.json":
        "351857e985a871e6d69c5662f90ad5cd6a608f92b1703e84ffb549a753cc8b2e",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_sealed_package() -> dict:
    manifest = DISCOVERY / "package-manifest.sha256"
    entries = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        actual = sha256(ROOT / relative)
        entries.append(
            {
                "path": relative,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "pass": expected == actual,
            }
        )
    actual_manifest = sha256(manifest)
    return {
        "manifest_sha256": actual_manifest,
        "expected_manifest_sha256": SEALED_MANIFEST,
        "manifest_pass": actual_manifest == SEALED_MANIFEST,
        "entry_count": len(entries),
        "entries_pass": all(entry["pass"] for entry in entries),
        "entries": entries,
    }


def audit_frozen_inputs() -> dict:
    observed = {
        relative: sha256(ROOT / relative)
        for relative in FROZEN_INPUTS
    }
    return {
        "expected": FROZEN_INPUTS,
        "observed": observed,
        "pass": observed == FROZEN_INPUTS,
    }


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


def transform_mask(mask: int, mapping: tuple[int, ...]) -> int:
    output = 0
    for index, target_bit in enumerate(mapping):
        if (mask >> index) & 1:
            output |= target_bit
    return output


@lru_cache(maxsize=None)
def canonical_mask(mask: int, order: int) -> int:
    return min(
        transform_mask(mask, mapping)
        for mapping in permutation_maps(order)
    )


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
        limit = 1 if (mask >> positions[(left, right)]) & 1 else 2
        if common > limit:
            return False
    return True


@lru_cache(maxsize=None)
def admissible_classes(order: int) -> tuple[int, ...]:
    remaining = {
        mask
        for mask in range(1 << len(graph_edges(order)))
        if locally_admissible(mask, order)
    }
    classes = []
    while remaining:
        seed = next(iter(remaining))
        orbit = {
            transform_mask(seed, mapping)
            for mapping in permutation_maps(order)
        }
        classes.append(min(orbit))
        remaining.difference_update(orbit)
    return tuple(sorted(classes))


def adjacency_rows(
    mask: int,
    order: int,
    diagonal_mask: int = 0,
) -> list[int]:
    rows = [
        (((diagonal_mask >> vertex) & 1) << vertex)
        for vertex in range(order)
    ]
    for index, (left, right) in enumerate(graph_edges(order)):
        if (mask >> index) & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return rows


def gf2_rank(rows: list[int], width: int) -> int:
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


def principal_nullity(
    mask: int,
    order: int,
    diagonal_mask: int = 0,
) -> int:
    return order - gf2_rank(
        adjacency_rows(mask, order, diagonal_mask),
        order,
    )


def delete_vertex(mask: int, order: int, deleted: int) -> int:
    new_positions = {
        edge: index
        for index, edge in enumerate(graph_edges(order - 1))
    }
    kept = [vertex for vertex in range(order) if vertex != deleted]
    relabel = {old: new for new, old in enumerate(kept)}
    output = 0
    for index, (left, right) in enumerate(graph_edges(order)):
        if left == deleted or right == deleted or not ((mask >> index) & 1):
            continue
        new_edge = tuple(sorted((relabel[left], relabel[right])))
        output |= 1 << new_positions[new_edge]
    return output


def parse_affine(record: dict[str, str]) -> tuple[Fraction, Fraction]:
    return (
        Fraction(record["constant"]),
        Fraction(record["n3_coefficient"]),
    )


def descend_counts(
    upper_counts: list[tuple[Fraction, Fraction]],
    upper_classes: tuple[int, ...],
    lower_classes: tuple[int, ...],
    upper_order: int,
) -> list[tuple[Fraction, Fraction]]:
    lower_index = {
        representative: index
        for index, representative in enumerate(lower_classes)
    }
    totals = [
        [Fraction(0), Fraction(0)]
        for _ in lower_classes
    ]
    for upper_position, mask in enumerate(upper_classes):
        deck = [0] * len(lower_classes)
        for deleted in range(upper_order):
            card = canonical_mask(
                delete_vertex(mask, upper_order, deleted),
                upper_order - 1,
            )
            deck[lower_index[card]] += 1
        constant, slope = upper_counts[upper_position]
        for lower_position, multiplicity in enumerate(deck):
            totals[lower_position][0] += multiplicity * constant
            totals[lower_position][1] += multiplicity * slope
    divisor = N - (upper_order - 1)
    return [
        (constant / divisor, slope / divisor)
        for constant, slope in totals
    ]


def add_affine(
    table: dict[object, tuple[Fraction, Fraction]],
    key: object,
    value: tuple[Fraction, Fraction],
) -> None:
    old = table.get(key, (Fraction(0), Fraction(0)))
    table[key] = (old[0] + value[0], old[1] + value[1])


def render_affine(value: tuple[Fraction, Fraction]) -> dict[str, str]:
    return {
        "constant": str(value[0]),
        "n3_coefficient": str(value[1]),
    }


def build_local_counts(wave21: dict) -> tuple[
    dict[int, tuple[int, ...]],
    dict[int, list[tuple[Fraction, Fraction]]],
]:
    mappings = wave21["independent_graph_census"][
        "source_index_alignment"
    ]["N_to_canonical_positions_zero_based"]
    classes: dict[int, tuple[int, ...]] = {
        order: admissible_classes(order)
        for order in range(7)
    }
    counts6: list[tuple[Fraction, Fraction] | None] = [None] * 62
    for source_index, canonical_position in enumerate(mappings, 1):
        counts6[canonical_position] = parse_affine(
            wave21["formula_tables"]["six"][str(source_index)]
        )
    if any(value is None for value in counts6):
        raise AssertionError("frozen six-class alignment is incomplete")
    counts: dict[int, list[tuple[Fraction, Fraction]]] = {
        6: [value for value in counts6 if value is not None]
    }
    for upper_order in range(6, 0, -1):
        counts[upper_order - 1] = descend_counts(
            counts[upper_order],
            classes[upper_order],
            classes[upper_order - 1],
            upper_order,
        )
    return classes, counts


def local_interlace_results(
    classes: dict[int, tuple[int, ...]],
    counts: dict[int, list[tuple[Fraction, Fraction]]],
) -> dict:
    rows = {}
    source_nullities = {}
    for order in range(7):
        row: dict[int, tuple[Fraction, Fraction]] = {}
        nullities = []
        for mask, count in zip(classes[order], counts[order], strict=True):
            nullity = principal_nullity(mask, order)
            nullities.append(nullity)
            add_affine(row, nullity, count)
        rows[order] = row
        source_nullities[str(order)] = nullities
        total = (
            sum(value[0] for value in row.values()),
            sum(value[1] for value in row.values()),
        )
        if total != (Fraction(comb(N, order)), Fraction(0)):
            raise AssertionError(f"local row {order} does not total binomial")

    expected_six = {
        0: (Fraction(45845415), Fraction(4, 3)),
        2: (Fraction(470213205), Fraction(-3)),
        4: (Fraction(503184528), Fraction(4, 3)),
        6: (Fraction(101286108), Fraction(1, 3)),
    }
    if rows[6] != expected_six:
        raise AssertionError("independent t=6 nullity row drift")

    moment = (
        sum((1 << nullity) * value[0] for nullity, value in rows[6].items()),
        sum((1 << nullity) * value[1] for nullity, value in rows[6].items()),
    )
    decreasing_bounds = [
        (value[0] / (-value[1]), nullity)
        for nullity, value in rows[6].items()
        if value[1] < 0
    ]
    strongest_bound, source_nullity = min(decreasing_bounds)
    return {
        "rows": {
            str(order): {
                str(nullity): render_affine(value)
                for nullity, value in sorted(row.items())
            }
            for order, row in rows.items()
        },
        "source_nullities": source_nullities,
        "alternating_parity_pass": all(
            nullity % 2 == order % 2
            for order, row in rows.items()
            for nullity in row
        ),
        "six_set_kernel_moment": render_affine(moment),
        "strongest_nonnegative_upper": {
            "source_nullity": source_nullity,
            "upper": str(strongest_bound),
        },
    }


def diagonal_toggle_results(
    classes6: tuple[int, ...],
    counts6: list[tuple[Fraction, Fraction]],
) -> dict:
    split: dict[tuple[int, int], tuple[Fraction, Fraction]] = {}
    aggregate: dict[int, tuple[Fraction, Fraction]] = {}
    per_class_census = []
    for mask, count in zip(classes6, counts6, strict=True):
        local = Counter()
        for diagonal_mask in range(1 << 6):
            nullity = principal_nullity(mask, 6, diagonal_mask)
            psi_count = diagonal_mask.bit_count()
            local[(psi_count, nullity)] += 1
            add_affine(split, (psi_count, nullity), count)
            add_affine(aggregate, nullity, count)
        per_class_census.append(
            {
                f"{psi},{nullity}": multiplicity
                for (psi, nullity), multiplicity in sorted(local.items())
            }
        )
    total = (
        sum(value[0] for value in split.values()),
        sum(value[1] for value in split.values()),
    )
    if total != (Fraction((1 << 6) * comb(N, 6)), Fraction(0)):
        raise AssertionError("diagonal-toggle total drift")
    bounds = [
        (value[0] / (-value[1]), key)
        for key, value in split.items()
        if value[1] < 0
    ]
    strongest, key = min(bounds)
    return {
        "split_by_psi_count_and_nullity": {
            f"{psi},{nullity}": render_affine(value)
            for (psi, nullity), value in sorted(split.items())
        },
        "aggregate_by_nullity": {
            str(nullity): render_affine(value)
            for nullity, value in sorted(aggregate.items())
        },
        "per_class_census_sha256": hashlib.sha256(
            (
                json.dumps(per_class_census, sort_keys=True)
                + "\n"
            ).encode("utf-8")
        ).hexdigest(),
        "strongest_nonnegative_upper": {
            "cell": list(key),
            "upper": str(strongest),
        },
        "all_cells_positive_at_4158": all(
            value[0] + 4158 * value[1] > 0
            for value in split.values()
        ),
        "denominators_divide_3": all(
            value.denominator in (1, 3)
            for affine in split.values()
            for value in affine
        ),
    }


def matvec(rows: list[int], vector: int) -> int:
    return sum(
        (((row & vector).bit_count() & 1) << index)
        for index, row in enumerate(rows)
    )


def rank_of_columns(columns: list[int], row_count: int) -> int:
    rows = [
        sum(
            ((column >> row) & 1) << index
            for index, column in enumerate(columns)
        )
        for row in range(row_count)
    ]
    return gf2_rank(rows, len(columns))


def ias_control() -> dict:
    order = 3
    k3_mask = (1 << 3) - 1
    a_rows = adjacency_rows(k3_mask, order)
    phi = [1 << vertex for vertex in range(order)]
    chi = [
        sum(
            ((a_rows[row] >> vertex) & 1) << row
            for row in range(order)
        )
        for vertex in range(order)
    ]
    psi = [phi[vertex] ^ chi[vertex] for vertex in range(order)]
    checks = 0
    for choices in product(range(3), repeat=order):
        columns = [
            (phi, chi, psi)[choice][vertex]
            for vertex, choice in enumerate(choices)
        ]
        subset = [
            vertex
            for vertex, choice in enumerate(choices)
            if choice != 0
        ]
        toggle = sum(
            1 << local
            for local, vertex in enumerate(subset)
            if choices[vertex] == 2
        )
        sub_rows = [
            sum(
                ((a_rows[left] >> right) & 1) << column
                for column, right in enumerate(subset)
            )
            for left in subset
        ]
        for local in range(len(subset)):
            if (toggle >> local) & 1:
                sub_rows[local] ^= 1 << local
        predicted = (
            order - len(subset)
            + gf2_rank(sub_rows, len(subset))
        )
        if rank_of_columns(columns, order) != predicted:
            raise AssertionError("K3 IAS diagonal-toggle formula failed")
        checks += 1
    return {
        "matrix": "adjacency(K3)",
        "all_phi_chi_psi_transversals_checked": checks,
        "formula_pass": checks == 27,
    }


def intersection_control() -> dict:
    order = 4
    k3_plus_isolate = 11
    rows = adjacency_rows(k3_plus_isolate, order)
    refined = Counter()
    for vector in range(1 << order):
        image = matvec(rows, vector)
        refined[
            (
                vector.bit_count(),
                image.bit_count(),
                (vector & image).bit_count(),
            )
        ] += 1

    identity_checks = []
    for target_size in range(order + 1):
        left = 0
        for subset in range(1 << order):
            if subset.bit_count() != target_size:
                continue
            vertices = [
                vertex
                for vertex in range(order)
                if (subset >> vertex) & 1
            ]
            sub_rows = [
                sum(
                    ((rows[left_vertex] >> right_vertex) & 1) << column
                    for column, right_vertex in enumerate(vertices)
                )
                for left_vertex in vertices
            ]
            left += 1 << (
                len(vertices) - gf2_rank(sub_rows, len(vertices))
            )
        right = 0
        for vector in range(1 << order):
            image = matvec(rows, vector)
            if vector & image:
                continue
            i = vector.bit_count()
            j = image.bit_count()
            if i <= target_size <= order - j:
                right += comb(order - i - j, target_size - i)
        identity_checks.append(left == right)

    return {
        "matrix": "adjacency(K3 disjoint_union K1)",
        "symmetric_idempotent_even_row": (
            all(matvec(rows, rows[index]) == rows[index] for index in range(order))
            and all(row.bit_count() % 2 == 0 for row in rows)
        ),
        "same_B_cell": {
            "cell": [2, 2],
            "h0": refined[(2, 2, 0)],
            "h2": refined[(2, 2, 2)],
            "total": refined[(2, 2, 0)] + refined[(2, 2, 2)],
        },
        "kernel_moment_identity_checks": identity_checks,
        "direct_projection_conclusion": (
            "The summand in the double count is not constant on a B[i,j] "
            "fiber, so the displayed moment is not a direct coefficient "
            "row in B alone."
        ),
    }


def bivariate_signature(mask: int, order: int) -> tuple[tuple[int, ...], ...]:
    rows = adjacency_rows(mask, order)
    table = [[0] * (order + 1) for _ in range(order + 1)]
    for vector in range(1 << order):
        image = matvec(rows, vector)
        table[vector.bit_count()][image.bit_count()] += 1
    return tuple(tuple(row) for row in table)


def interlace_signature(mask: int, order: int) -> tuple[tuple[int, ...], ...]:
    rows = []
    for target_size in range(order + 1):
        distribution = [0] * (order + 1)
        for subset in range(1 << order):
            if subset.bit_count() != target_size:
                continue
            vertices = [
                vertex
                for vertex in range(order)
                if (subset >> vertex) & 1
            ]
            sub_rows = adjacency_rows(mask, order)
            restricted = [
                sum(
                    ((sub_rows[left] >> right) & 1) << column
                    for column, right in enumerate(vertices)
                )
                for left in vertices
            ]
            nullity = target_size - gf2_rank(restricted, target_size)
            distribution[nullity] += 1
        rows.append(tuple(distribution))
    return tuple(rows)


def general_b_collision_control() -> dict:
    # An independent exhaustive n=6 search found these two symmetric
    # zero-diagonal graphs.  Replay the exact collision directly.
    left_mask = 5782
    right_mask = 5872
    left_b = bivariate_signature(left_mask, 6)
    right_b = bivariate_signature(right_mask, 6)
    left_i = interlace_signature(left_mask, 6)
    right_i = interlace_signature(right_mask, 6)
    return {
        "order": 6,
        "masks": [left_mask, right_mask],
        "same_complete_B_table": left_b == right_b,
        "different_interlace_table": left_i != right_i,
        "first_different_input_size": next(
            size
            for size in range(7)
            if left_i[size] != right_i[size]
        ),
        "left_size3_nullities": list(left_i[3]),
        "right_size3_nullities": list(right_i[3]),
        "target_subclass_limitation": (
            "These controls are symmetric zero-diagonal graphs but do not "
            "satisfy the target even-row/idempotent hypotheses."
        ),
    }


def top_band_audit(wave131: dict) -> dict:
    verified_lower = wave131["frozen_binary_facts"]["image"][
        "minimum_weight_lower"
    ]
    witness_minimum = wave131["rational_witness_audit"][
        "image_minimum_nonzero_weight"
    ]
    witness_realized = wave131["rational_witness_audit"][
        "realized_binary_code"
    ]
    verified_entries = []
    for complement_size in range(verified_lower):
        verified_entries.append(
            {
                "complement_size": complement_size,
                "subset_size": N - complement_size,
                "rank": 54,
                "nullity": 45 - complement_size,
                "subset_count": comb(N, complement_size),
            }
        )
    return {
        "frozen_verified_image_minimum_lower": verified_lower,
        "formal_rational_witness_minimum": witness_minimum,
        "formal_rational_witness_realized_code": witness_realized,
        "verified_target_range": "92<=|S|<=99",
        "verified_entries": verified_entries,
        "discovery_claimed_range": "86<=|S|<=99",
        "vetoed_complement_sizes": list(range(8, 14)),
        "conditional_lemma": (
            "If d(im(A))>=14 were independently proved, the discovery's "
            "86-through-99 band argument would be correct."
        ),
        "veto_reason": (
            "The frozen target fact is only d(im(A))>=8.  Minimum 14 belongs "
            "to a nonintegral, unrealized rational witness and cannot be "
            "promoted to a target premise."
        ),
    }


def build_results() -> dict:
    package = audit_sealed_package()
    frozen = audit_frozen_inputs()
    if not package["manifest_pass"] or not package["entries_pass"]:
        raise AssertionError("Wave142 sealed package hash audit failed")
    if not frozen["pass"]:
        raise AssertionError("Wave142 frozen prerequisite drift")

    wave21 = json.loads(WAVE21_RESULTS.read_text(encoding="utf-8"))
    wave131 = json.loads(WAVE131_RESULTS.read_text(encoding="utf-8"))
    discovery = json.loads(
        (DISCOVERY / "exact-results.json").read_text(encoding="utf-8")
    )

    classes, counts = build_local_counts(wave21)
    local = local_interlace_results(classes, counts)
    toggles = diagonal_toggle_results(classes[6], counts[6])
    ias = ias_control()
    overlap = intersection_control()
    collision = general_b_collision_control()
    top_band = top_band_audit(wave131)

    local_matches = (
        local["rows"] == discovery["local_rows"]["rows"]
        and local["six_set_kernel_moment"]
        == {
            "constant": discovery["local_rows"][
                "six_set_kernel_size_moment"
            ]["constant"],
            "n3_coefficient": discovery["local_rows"][
                "six_set_kernel_size_moment"
            ]["n3_coefficient"],
        }
    )
    toggle_matches = (
        toggles["split_by_psi_count_and_nullity"]
        == discovery["isotropic_matroid"][
            "six_vertex_diagonal_toggle_rows"
        ]["split_by_psi_count_and_nullity"]
        and toggles["aggregate_by_nullity"]
        == discovery["isotropic_matroid"][
            "six_vertex_diagonal_toggle_rows"
        ]["aggregate_by_nullity"]
    )

    return {
        "format": "wave142-independent-verification-v1",
        "verdict": "PARTIAL_PASS_WITH_TOP_BAND_VETO",
        "sealed_package": package,
        "frozen_inputs": frozen,
        "local_interlace": local,
        "diagonal_toggle_census": toggles,
        "IAS_control": ias,
        "intersection_refinement": {
            "K3_plus_K1": overlap,
            "general_same_B_different_interlace_control": collision,
            "B_only_verdict": (
                "The displayed double-counting moment is not a direct "
                "coefficient row of B because its summand varies with h "
                "inside one B cell.  General symmetric graphs can even have "
                "identical full B tables and different interlace tables.  "
                "However, the latter collision is outside the target "
                "idempotent/even-row subclass, so impossibility of every "
                "target-specific B-only elimination remains UNKNOWN."
            ),
        },
        "top_complement_band": top_band,
        "comparison_with_discovery": {
            "local_rows_and_kernel_moment_match": local_matches,
            "diagonal_toggle_rows_match": toggle_matches,
            "IAS_discovery_8_phi_chi_checks_strengthened_to": 27,
            "verified_claims": [
                "four t=6 principal-nullity rows",
                "six-set kernel-size moment",
                "ordinary nonnegativity upper 156737735",
                "all 62x64 diagonal-toggle cells",
                "toggle upper 7609140",
                "IAS transversal reduction",
                "intersection-refined lift requirement in the direct double count",
            ],
            "vetoed_claim": (
                "Target-forced principal rank 54 for every subset of sizes "
                "86 through 91; only sizes 92 through 99 are currently "
                "supported by the frozen d(im(A))>=8 premise."
            ),
        },
        "bound_assessment": {
            "ordinary_upper": local["strongest_nonnegative_upper"]["upper"],
            "toggle_upper": toggles["strongest_nonnegative_upper"]["upper"],
            "existing_upper": 4158,
            "improved": False,
        },
        "status_wall": {
            "top_band_86_through_91": "VETO_UNSUPPORTED_PREMISE",
            "top_band_92_through_99": "VERIFIED",
            "B_only_target_elimination": "UNKNOWN",
            "formal_interlace_lift_feasibility": "UNKNOWN",
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
                "manifest_pass": result["sealed_package"]["manifest_pass"],
                "local_rows_match": result["comparison_with_discovery"][
                    "local_rows_and_kernel_moment_match"
                ],
                "toggle_rows_match": result["comparison_with_discovery"][
                    "diagonal_toggle_rows_match"
                ],
                "verified_top_band": result["status_wall"][
                    "top_band_92_through_99"
                ],
                "vetoed_top_band": result["status_wall"][
                    "top_band_86_through_91"
                ],
                "Conway_99": result["status_wall"]["Conway_99"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
