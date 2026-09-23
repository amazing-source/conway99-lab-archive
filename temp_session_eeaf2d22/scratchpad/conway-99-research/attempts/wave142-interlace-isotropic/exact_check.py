#!/usr/bin/env python3
"""Exact bounded checks for the Wave142 interlace/isotropic-matroid lane.

The checker uses the already frozen Wave21 induced-subgraph census.  It
performs no graph search and no exponential computation on 99 vertices.
The largest local loop is 62 six-vertex types times 64 diagonal toggles.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


N = 99
RANK_A = 54
NULLITY_A = 45
IMAGE_MINIMUM = 14
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WAVE21_CHECK = ROOT / "attempts" / "wave21-six-vertex-lp" / "exact_check.py"
WAVE141_RESULT = (
    ROOT / "attempts" / "wave141-bivariate-graph-code" / "exact-results.json"
)
DEFAULT_OUTPUT = HERE / "exact-results.json"

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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed = {}
    for relative, expected in FROZEN_INPUTS.items():
        actual = sha256(ROOT / relative)
        require(actual == expected, f"frozen input drift: {relative}")
        observed[relative] = actual
    return observed


def load_wave21():
    spec = importlib.util.spec_from_file_location("wave142_wave21_input", WAVE21_CHECK)
    require(spec is not None and spec.loader is not None, "cannot load Wave21 input")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def edge_position(order: int) -> dict[tuple[int, int], int]:
    return {
        edge: index
        for index, edge in enumerate(itertools.combinations(range(order), 2))
    }


def adjacency_rows(mask: int, order: int, diagonal_mask: int = 0) -> list[int]:
    positions = edge_position(order)
    rows = [((diagonal_mask >> vertex) & 1) << vertex for vertex in range(order)]
    for (left, right), position in positions.items():
        if (mask >> position) & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return rows


def gf2_rank(rows: Iterable[int], columns: int) -> int:
    work = list(rows)
    rank = 0
    for column in range(columns):
        pivot = next(
            (
                index
                for index in range(rank, len(work))
                if (work[index] >> column) & 1
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for index in range(len(work)):
            if index != rank and ((work[index] >> column) & 1):
                work[index] ^= work[rank]
        rank += 1
    return rank


def principal_nullity(mask: int, order: int, diagonal_mask: int = 0) -> int:
    return order - gf2_rank(adjacency_rows(mask, order, diagonal_mask), order)


def ftext(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def affine_json(form: Any) -> dict[str, str]:
    return {"constant": ftext(form.c), "n3_coefficient": ftext(form.x)}


def add_form(table: dict[Any, Any], key: Any, form: Any, wave21: Any) -> None:
    table[key] = table.get(key, wave21.A()) + form


def local_interlace_rows() -> dict[str, Any]:
    """Return the exact size-refined principal-nullity rows through order six."""

    wave21 = load_wave21()
    l_mapping, m_mapping = wave21.align_four_five()
    n_mapping = wave21.align_five_six(
        m_mapping,
        wave21.corrected_five_to_six(),
    )

    rows: dict[int, dict[int, Any]] = {
        0: {0: wave21.A(1)},
        1: {1: wave21.A(N)},
        2: {0: wave21.A(693), 2: wave21.A(4158)},
        3: {1: wave21.A(58443), 3: wave21.A(98406)},
    }
    class_nullities: dict[str, list[int]] = {}
    for order, forms, mapping in (
        (4, wave21.four_counts(), l_mapping),
        (5, wave21.five_counts(), m_mapping),
        (6, wave21.six_counts(), n_mapping),
    ):
        classes = wave21.locally_admissible_classes(order)
        row: dict[int, Any] = {}
        source_nullities = []
        for source_index, form in forms.items():
            nullity = principal_nullity(
                classes[mapping[source_index - 1]],
                order,
            )
            source_nullities.append(nullity)
            add_form(row, nullity, form, wave21)
        rows[order] = row
        class_nullities[str(order)] = source_nullities

    expected_six = {
        0: ("45845415", "4/3"),
        2: ("470213205", "-3"),
        4: ("503184528", "4/3"),
        6: ("101286108", "1/3"),
    }
    observed_six = {
        nullity: (ftext(form.c), ftext(form.x))
        for nullity, form in rows[6].items()
    }
    require(observed_six == expected_six, "order-six interlace row drift")

    rendered = {
        str(order): {
            str(nullity): affine_json(form)
            for nullity, form in sorted(row.items())
        }
        for order, row in sorted(rows.items())
    }
    for order, row in rows.items():
        total = sum(row.values(), wave21.A())
        require(total.c == math.comb(N, order), f"row {order} total drift")
        require(total.x == 0, f"row {order} n3 slope does not cancel")

    # The kernel-size moment is the first place where the interlace lift can
    # be written directly as an intersection-zero graph-code count.
    t6_kernel_moment = sum(
        form * (1 << nullity)
        for nullity, form in rows[6].items()
    )
    require(
        (t6_kernel_moment.c, t6_kernel_moment.x)
        == (16459961595, 32),
        "six-set kernel moment drift",
    )

    negative_bounds = [
        (form.c / (-form.x), nullity)
        for nullity, form in rows[6].items()
        if form.x < 0
    ]
    strongest_bound, source_nullity = min(negative_bounds)
    return {
        "definition": (
            "I_t,nu=#{S subset V: |S|=t and nullity_F2(A[S])=nu}"
        ),
        "rows": rendered,
        "source_class_nullities": class_nullities,
        "alternating_support_rule": "I_t,nu=0 unless nu == t (mod 2)",
        "six_set_kernel_size_moment": {
            "definition": "sum_|S|=6 2^nullity(A[S])",
            "constant": ftext(t6_kernel_moment.c),
            "n3_coefficient": ftext(t6_kernel_moment.x),
        },
        "nonnegativity_bound": {
            "source_nullity": source_nullity,
            "rational_upper": ftext(strongest_bound),
            "integer_upper": strongest_bound.numerator // strongest_bound.denominator,
            "improves_n3_le_4158": strongest_bound < 4158,
        },
    }


def isotropic_toggle_rows() -> dict[str, Any]:
    """Aggregate ranks of A[S]+diag(T) for all local six-vertex types."""

    wave21 = load_wave21()
    _, m_mapping = wave21.align_four_five()
    n_mapping = wave21.align_five_six(
        m_mapping,
        wave21.corrected_five_to_six(),
    )
    classes = wave21.locally_admissible_classes(6)
    forms = wave21.six_counts()
    split: dict[tuple[int, int], Any] = {}
    aggregate: dict[int, Any] = {}
    for source_index, form in forms.items():
        mask = classes[n_mapping[source_index - 1]]
        for diagonal_mask in range(1 << 6):
            nullity = principal_nullity(mask, 6, diagonal_mask)
            psi_count = diagonal_mask.bit_count()
            add_form(split, (psi_count, nullity), form, wave21)
            add_form(aggregate, nullity, form, wave21)

    total = sum(split.values(), wave21.A())
    require(total.c == (1 << 6) * math.comb(N, 6), "toggle total drift")
    require(total.x == 0, "toggle n3 slope does not cancel")
    negative_bounds = [
        (form.c / (-form.x), key)
        for key, form in split.items()
        if form.x < 0
    ]
    strongest_bound, key = min(negative_bounds)
    require((strongest_bound, key) == (Fraction(7609140), (3, 5)),
            "strongest toggle bound drift")
    return {
        "definition": (
            "J_r,nu=sum_|S|=6 #{T subset S: |T|=r and "
            "nullity_F2(A[S]+diag(1_T))=nu}"
        ),
        "split_by_psi_count_and_nullity": {
            f"{psi_count},{nullity}": affine_json(form)
            for (psi_count, nullity), form in sorted(split.items())
        },
        "aggregate_by_nullity": {
            str(nullity): affine_json(form)
            for nullity, form in sorted(aggregate.items())
        },
        "strongest_nonnegativity_bound": {
            "cell_psi_count_nullity": list(key),
            "rational_upper": ftext(strongest_bound),
            "improves_n3_le_4158": strongest_bound < 4158,
        },
    }


def rank_columns(columns: list[int], row_count: int) -> int:
    # Transpose a column list into row bitmasks.
    rows = [
        sum(((column >> row) & 1) << index for index, column in enumerate(columns))
        for row in range(row_count)
    ]
    return gf2_rank(rows, len(columns))


def small_isotropic_control() -> dict[str, Any]:
    """Check the transversal-rank formula on adjacency(K3)."""

    order = 3
    mask = (1 << 3) - 1
    a_rows = adjacency_rows(mask, order)
    phi = [1 << vertex for vertex in range(order)]
    chi = [
        sum(((a_rows[row] >> vertex) & 1) << row for row in range(order))
        for vertex in range(order)
    ]
    checks = 0
    for subset in range(1 << order):
        columns = [
            chi[vertex] if ((subset >> vertex) & 1) else phi[vertex]
            for vertex in range(order)
        ]
        sub_vertices = [v for v in range(order) if (subset >> v) & 1]
        sub_rows = []
        for left in sub_vertices:
            sub_rows.append(
                sum(
                    ((a_rows[left] >> right) & 1) << index
                    for index, right in enumerate(sub_vertices)
                )
            )
        sub_rank = gf2_rank(sub_rows, len(sub_vertices))
        predicted = order - len(sub_vertices) + sub_rank
        require(rank_columns(columns, order) == predicted,
                "K3 isotropic transversal formula failed")
        checks += 1
    return {
        "matrix": "adjacency(K3)",
        "transversals_checked": checks,
        "identity": (
            "rank({phi_v:v notin S} union {chi_v:v in S})="
            "99-|S|+rank(A[S])"
        ),
        "all_pass": True,
    }


def matvec(rows: list[int], vector: int) -> int:
    result = 0
    for row_index, row in enumerate(rows):
        if (row & vector).bit_count() & 1:
            result |= 1 << row_index
    return result


def intersection_zero_control() -> dict[str, Any]:
    """Show the exact lift needed beyond B[i,j], using K3 plus an isolate."""

    order = 4
    # Edge order is 01,02,03,12,13,23; mask 11 is K3 on 0,1,2 plus isolate 3.
    mask = 11
    rows = adjacency_rows(mask, order)
    refined: dict[tuple[int, int, int], int] = defaultdict(int)
    for vector in range(1 << order):
        image = matvec(rows, vector)
        refined[
            (vector.bit_count(), image.bit_count(), (vector & image).bit_count())
        ] += 1
    require(refined[(2, 2, 0)] == refined[(2, 2, 2)] == 3,
            "same B-cell intersection split control drift")

    moment_checks = 0
    for target_size in range(order + 1):
        left = 0
        for subset in range(1 << order):
            if subset.bit_count() != target_size:
                continue
            vertices = [v for v in range(order) if (subset >> v) & 1]
            sub_rows = [
                sum(
                    ((rows[left_vertex] >> right_vertex) & 1) << index
                    for index, right_vertex in enumerate(vertices)
                )
                for left_vertex in vertices
            ]
            left += 1 << (len(vertices) - gf2_rank(sub_rows, len(vertices)))

        right = 0
        for vector in range(1 << order):
            image = matvec(rows, vector)
            if vector & image:
                continue
            i = vector.bit_count()
            j = image.bit_count()
            if i <= target_size <= order - j:
                right += math.comb(order - i - j, target_size - i)
        require(left == right, f"intersection-zero identity failed at {target_size}")
        moment_checks += 1
    return {
        "matrix": "adjacency(K3 disjoint_union K1)",
        "same_Wave141_cell": {
            "input_weight": 2,
            "output_weight": 2,
            "intersection_0_count": refined[(2, 2, 0)],
            "intersection_2_count": refined[(2, 2, 2)],
            "B_2_2_total": (
                refined[(2, 2, 0)] + refined[(2, 2, 2)]
            ),
        },
        "kernel_moment_identity_checks": moment_checks,
        "identity": (
            "sum_|S|=t 2^nullity(A[S]) = sum_x:[supp(x) disjoint "
            "supp(Ax)] binom(n-wt(x)-wt(Ax),t-wt(x))"
        ),
        "consequence": (
            "B[i,j] sums over intersection sizes, so the h=0 slice needed "
            "by the interlace moment is not a coordinate of the Wave141 table."
        ),
    }


def top_complement_band() -> dict[str, Any]:
    entries = []
    for complement_size in range(IMAGE_MINIMUM):
        subset_size = N - complement_size
        nullity = NULLITY_A - complement_size
        rank = subset_size - nullity
        require(rank == RANK_A, "top-band rank drift")
        entries.append(
            {
                "complement_size": complement_size,
                "subset_size": subset_size,
                "rank": rank,
                "nullity": nullity,
                "subset_count": math.comb(N, complement_size),
            }
        )
    return {
        "premise": "minimum nonzero weight of im(A) is at least 14",
        "range": "86<=|S|<=99",
        "entries": entries,
        "proof": (
            "For C=V\\S with |C|<14, Ax supported in C implies Ax=0 "
            "because Ax lies in im(A). The coordinate restriction "
            "ker(A)->F2^C is onto because its annihilator would be an "
            "im(A) word supported in C. Hence nullity(A[S])=45-|C|."
        ),
    }


def build_results() -> dict[str, Any]:
    frozen = verify_frozen_inputs()
    wave141 = json.loads(WAVE141_RESULT.read_text(encoding="utf-8"))
    local = local_interlace_rows()
    toggles = isotropic_toggle_rows()
    small_iso = small_isotropic_control()
    intersection = intersection_zero_control()
    top_band = top_complement_band()
    require(wave141["D8_equality_space"]["raw_bivariate_states"] == 10000,
            "Wave141 state-count drift")

    return {
        "format": "wave142-interlace-isotropic-v1",
        "claim_label": "DERIVED_INCONCLUSIVE",
        "scope": (
            "Exact vertex-nullity and isotropic-transversal consequences of "
            "the frozen hypothetical SRG and its binary projection; no graph "
            "construction, endpoint exclusion, or improved n3 bound"
        ),
        "parameters": {
            "srg": [99, 14, 1, 2],
            "A_squared_equals_A_mod_2": True,
            "A_one_equals_zero_mod_2": True,
            "rank_F2_A": RANK_A,
            "nullity_F2_A": NULLITY_A,
            "minimum_weight_im_A": ">=14",
        },
        "vertex_nullity_polynomial": {
            "definition": (
                "q_N(G;y)=sum_(S subset V)(y-1)^nullity_F2(A[S])"
            ),
            "size_refinement": (
                "Q_G(z,y)=sum_S z^|S|(y-1)^nullity_F2(A[S])"
            ),
            "alternating_matrix_parity": (
                "rank_F2(A[S]) is even, hence nullity(A[S]) == |S| mod 2"
            ),
            "universal_evaluations": {
                "q_N_G_2": str(1 << N),
                "q_N_G_0": "0",
            },
        },
        "local_rows": local,
        "top_complement_band": top_band,
        "isotropic_matroid": {
            "representation": "IAS(G)=[I | A | I+A] over F2",
            "transversal_formula": (
                "rank(phi_(V\\S) union chi_S)=99-|S|+rank(A[S])"
            ),
            "three_full_transversal_nullities": {
                "all_phi": 0,
                "all_chi": NULLITY_A,
                "all_psi": RANK_A,
            },
            "small_control": small_iso,
            "six_vertex_diagonal_toggle_rows": toggles,
        },
        "comparison_with_wave141": {
            "Wave141_definition": wave141["definition"],
            "Wave141_raw_states": 10000,
            "required_refinement": (
                "C[i,j,h]=#{x:wt(x)=i,wt(Ax)=j,"
                "|supp(x) intersect supp(Ax)|=h}"
            ),
            "projection": "B[i,j]=sum_h C[i,j,h]",
            "intersection_zero_control": intersection,
            "verdict": (
                "Interlace data require an h=0 support-overlap lift. They are "
                "not an additional row in the existing B[i,j] coordinates. "
                "No exact inequality eliminating that lift back to B, and no "
                "new B-only coefficient or sign constraint, was derived."
            ),
        },
        "bound_assessment": {
            "ordinary_interlace_nonnegativity_upper":
                local["nonnegativity_bound"]["rational_upper"],
            "isotropic_toggle_nonnegativity_upper":
                toggles["strongest_nonnegativity_bound"]["rational_upper"],
            "existing_general_upper": 4158,
            "upper_bound_improved": False,
            "new_n3_congruence": None,
            "reason": (
                "All local interlace/toggle coefficients remain positive at "
                "n3=4158. Their nonnegativity inequalities are much weaker "
                "than the prism identity n3<=4158."
            ),
        },
        "frozen_inputs_sha256": frozen,
        "limitations": [
            "No 99-vertex adjacency matrix is available, so the full interlace polynomial is not computed.",
            "The local rows use the frozen, separately audited Wave21 affine induced-subgraph census.",
            "The h=0 lift is a required new variable family, not a formal realization.",
            "No rational or integral global interlace/isotropic enumerator is constructed.",
            "No literature novelty claim is made.",
            "Discovery does not verify itself.",
        ],
        "status_wall": {
            "new_general_n3_upper_bound": "NONE",
            "formal_interlace_lift_feasibility": "UNKNOWN",
            "isotropic_matroid_realizability": "UNKNOWN",
            "strongly_regular_graph_realizability": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    rendered = canonical_json(build_results())
    if args.write:
        args.output.write_text(rendered, encoding="utf-8", newline="\n")
    if args.verify:
        require(args.output.exists(), f"missing output: {args.output}")
        require(args.output.read_text(encoding="utf-8") == rendered,
                "canonical result mismatch")
    print(
        "PASS Wave142: exact local interlace/isotropic rows replayed; "
        "no n3 bound below 4158"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
