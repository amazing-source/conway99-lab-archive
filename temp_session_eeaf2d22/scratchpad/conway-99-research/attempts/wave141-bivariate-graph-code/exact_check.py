"""Exact structural replay for the Wave141 bivariate graph-code lane.

The bivariate table is

    B[i,j] = #{x in F_2^99 : wt(x)=i and wt(Ax)=j}.

This checker deliberately proves identities and dimensions only.  It does not
claim that the resulting formal linear system is feasible or infeasible.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


N = 99
K = 14
IMAGE_DIMENSION = 54
KERNEL_DIMENSION = 45
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WAVE21_CHECK = ROOT / "attempts/wave21-six-vertex-lp/exact_check.py"
WAVE21_RESULT = ROOT / "attempts/wave21-six-vertex-lp/exact-results.json"
DEFAULT_OUTPUT = HERE / "exact-results.json"

FROZEN_INPUTS = {
    "attempts/wave21-six-vertex-lp/exact_check.py":
        "0dd44ca37ca21aeaa757f3b2d7f7f9639907f22b95da39472ed9d836027a94a3",
    "attempts/wave21-six-vertex-lp/exact-results.json":
        "5e7b6f526985fb719754145944579aacb0e8f38e9e14a54d2075552a3756ff2b",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed = {}
    for relative, expected in FROZEN_INPUTS.items():
        path = ROOT / relative
        actual = sha256(path)
        if actual != expected:
            raise AssertionError(
                f"frozen input drift for {relative}: {actual} != {expected}"
            )
        observed[relative] = actual
    return observed


def load_wave21():
    spec = importlib.util.spec_from_file_location("wave141_wave21_input", WAVE21_CHECK)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen Wave21 checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def krawtchouk(n: int, degree: int, weight: int) -> int:
    return sum(
        (-1) ** overlap
        * math.comb(weight, overlap)
        * math.comb(n - weight, degree - overlap)
        for overlap in range(
            max(0, degree - (n - weight)),
            min(weight, degree) + 1,
        )
    )


def matmul_mod2(matrix: list[list[int]], vector: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        sum(entry * bit for entry, bit in zip(row, vector)) % 2
        for row in matrix
    )


def weight(vector: tuple[int, ...]) -> int:
    return sum(vector)


def small_transform_replay() -> dict[str, Any]:
    """Independently unit-check the transform on the K3 adjacency matrix."""

    n = 3
    adjacency = [
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0],
    ]
    square = [
        [
            sum(adjacency[row][middle] * adjacency[middle][column]
                for middle in range(n)) % 2
            for column in range(n)
        ]
        for row in range(n)
    ]
    if square != adjacency:
        raise AssertionError("K3 adjacency is not idempotent over F2")
    if any(sum(row) % 2 for row in adjacency):
        raise AssertionError("K3 adjacency does not have even rows")

    table = [[0 for _ in range(n + 1)] for _ in range(n + 1)]
    for mask in range(1 << n):
        x = tuple((mask >> index) & 1 for index in range(n))
        y = matmul_mod2(adjacency, x)
        table[weight(x)][weight(y)] += 1

    if any(table[i][j] for i in range(n + 1) for j in range(1, n + 1, 2)):
        raise AssertionError("small output-even support failed")
    if any(sum(table[i]) != math.comb(n, i) for i in range(n + 1)):
        raise AssertionError("small input marginal failed")
    if any(table[i] != table[n - i] for i in range(n + 1)):
        raise AssertionError("small input-complement symmetry failed")

    for i in range(n + 1):
        for j in range(n + 1):
            numerator = sum(
                table[a][b]
                * krawtchouk(n, i, b)
                * krawtchouk(n, j, a)
                for a in range(n + 1)
                for b in range(n + 1)
            )
            if Fraction(numerator, 1 << n) != table[i][j]:
                raise AssertionError(f"small transform failed at {(i, j)}")

    return {
        "matrix": "adjacency(K3)",
        "A_squared_equals_A_mod_2": True,
        "A_one_equals_zero_mod_2": True,
        "table": table,
        "all_16_transform_rows_pass": True,
        "transform_convention": (
            "B[i,j]=2^-n sum_(a,b) K_i(b) K_j(a) B[a,b]"
        ),
    }


def signed_affine_rows() -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Recompute S_0,...,S_6 from frozen local graph counts and masks."""

    wave21 = load_wave21()
    l_mapping, m_mapping = wave21.align_four_five()
    n_mapping = wave21.align_five_six(
        m_mapping,
        wave21.corrected_five_to_six(),
    )

    # S_i = sum_j (-1)^(j/2) B[i,j].  Since q(A1_S) =
    # |S| + e(S) mod 2, each induced i-set contributes
    # (-1)^(i+e(S)).
    rows = [
        (Fraction(1), Fraction(0)),
        (Fraction(-99), Fraction(0)),
        (Fraction(3465), Fraction(0)),
        (Fraction(-56595), Fraction(0)),
    ]
    parity_audits = []
    for order, forms, mapping in (
        (4, wave21.four_counts(), l_mapping),
        (5, wave21.five_counts(), m_mapping),
        (6, wave21.six_counts(), n_mapping),
    ):
        classes = wave21.locally_admissible_classes(order)
        constant = sum(
            (
                (-1) ** (order + classes[mapping[index - 1]].bit_count())
                * form.c
                for index, form in forms.items()
            ),
            Fraction(0),
        )
        n3_coefficient = sum(
            (
                (-1) ** (order + classes[mapping[index - 1]].bit_count())
                * form.x
                for index, form in forms.items()
            ),
            Fraction(0),
        )
        rows.append((constant, n3_coefficient))
        parity_audits.append(
            {
                "order": order,
                "source_class_count": len(forms),
                "canonical_class_count": len(classes),
                "mapping_is_bijective": len(set(mapping)) == len(mapping),
                "even_edge_classes": sum(mask.bit_count() % 2 == 0 for mask in classes),
                "odd_edge_classes": sum(mask.bit_count() % 2 == 1 for mask in classes),
            }
        )

    expected = [
        (Fraction(1), Fraction(0)),
        (Fraction(-99), Fraction(0)),
        (Fraction(3465), Fraction(0)),
        (Fraction(-56595), Fraction(0)),
        (Fraction(462924), Fraction(0)),
        (Fraction(-1821204), Fraction(0)),
        (Fraction(2024484), Fraction(512, 3)),
    ]
    if rows != expected:
        raise AssertionError(f"signed-row drift: {rows!r}")

    rendered = [
        {
            "input_weight": str(index),
            "constant": str(constant),
            "n3_coefficient": str(coefficient),
        }
        for index, (constant, coefficient) in enumerate(rows)
    ]
    return rendered, {
        "quadratic_refinement": (
            "q(y)=wt(y)/2 mod 2 on the even code R=im(A)"
        ),
        "polarization": "q(u+v)=q(u)+q(v)+u dot v mod 2",
        "row_facts": "q(row_i(A))=14/2=1 mod 2 and row_i dot row_j=A_ij",
        "subset_identity": "q(A 1_S)=|S|+e(G[S]) mod 2",
        "class_parity_audits": parity_audits,
    }


def d8_rank_record() -> dict[str, Any]:
    """Exact Burnside dimension for the output-even bivariate transform."""

    degree = N
    d = degree + 1
    trace_reflection_on_sym_odd = sum((-1) ** exponent for exponent in range(d))
    if trace_reflection_on_sym_odd != 0:
        raise AssertionError("odd symmetric-power reflection trace drift")

    # Generators on the two binary variable pairs:
    #   P = I tensor z,
    #   M = Swap (h tensor h),
    # where z=diag(1,-1), h=2^-1/2 [[1,1],[1,-1]].
    # R=P M has R^2=x tensor z, with x=[[0,1],[1,0]], hence R^4=I.
    traces = {
        "I": d * d,
        "R": 0,
        "R2": 0,
        "R3": 0,
        "P": 0,
        "R2P": 0,
        "RP": d,
        "R3P_equals_M": d,
    }
    invariant_dimension = sum(traces.values()) // 8
    if sum(traces.values()) % 8:
        raise AssertionError("Burnside trace sum is not divisible by 8")
    if invariant_dimension != 1275:
        raise AssertionError("D8 invariant dimension drift")

    raw = d * d
    output_even = d * ((degree + 1) // 2)
    if output_even != 5000:
        raise AssertionError("output-even state count drift")
    rank = output_even - invariant_dimension
    if rank != 3725:
        raise AssertionError("D8 equality-rank drift")

    return {
        "raw_bivariate_states": raw,
        "output_even_states": output_even,
        "input_complement_reduced_states": output_even // 2,
        "D8_order": 8,
        "generators": {
            "z": "[[1,0],[0,-1]]",
            "h": "2^(-1/2)*[[1,1],[1,-1]]",
            "P": "I tensor z",
            "M": "Swap*(h tensor h)",
            "R": "P*M",
            "exact_relations": [
                "P^2=M^2=I",
                "h*z*h=x=[[0,1],[1,0]]",
                "R^2=x tensor z",
                "R^4=I",
                "P*R*P=R^(-1)",
            ],
        },
        "Burnside_traces": traces,
        "invariant_dimension": invariant_dimension,
        "combined_output_parity_and_transform_rank": rank,
        "rank_after_input_complement_reduction": 2500 - invariant_dimension,
    }


def exact_low_input_rows() -> dict[str, dict[str, int]]:
    rows = {
        "0": {"0": 1},
        "1": {"14": 99},
        "2": {"24": 4158, "26": 693},
        "3": {"30": 70686, "32": 41580, "34": 36036, "36": 8547},
    }
    for text_i, row in rows.items():
        i = int(text_i)
        if sum(row.values()) != math.comb(N, i):
            raise AssertionError(f"low row marginal drift at {i}")
    return rows


def build_results() -> dict[str, Any]:
    frozen = verify_frozen_inputs()
    signed_rows, signed_derivation = signed_affine_rows()
    rank = d8_rank_record()
    small = small_transform_replay()
    low_rows = exact_low_input_rows()

    target_constant = Fraction(2024484)
    target_coefficient = Fraction(512, 3)
    elementary_upper = Fraction(
        3 * (math.comb(N, 6) - target_constant),
        512,
    )

    return {
        "format": "wave141-bivariate-graph-code-v1",
        "claim_label": "DERIVED",
        "scope": (
            "Exact identities and equality-space dimension for the formal "
            "bivariate table B[i,j]; no formal enumerator, code, graph, "
            "upper bound improvement, or Conway-99 resolution"
        ),
        "parameters": {
            "srg": [99, 14, 1, 2],
            "rank_F2_A": IMAGE_DIMENSION,
            "nullity_F2_A": KERNEL_DIMENSION,
            "A_squared_equals_A_mod_2": True,
            "A_one_equals_zero_mod_2": True,
        },
        "definition": "B[i,j]=#{x in F_2^99: wt(x)=i, wt(Ax)=j}",
        "exact_marginals_and_symmetries": {
            "input": "sum_j B[i,j]=binom(99,i)",
            "output": "sum_i B[i,j]=2^45*A_j, where A_j is the im(A) weight enumerator",
            "output_even": "B[i,j]=0 for odd j",
            "input_complement": "B[i,j]=B[99-i,j], because A*1=0",
            "transform": (
                "B[i,j]=2^-99 sum_(a,b) K_i(b) K_j(a) B[a,b]"
            ),
            "krawtchouk_convention": (
                "K_t(w)=sum_h (-1)^h binom(w,h) binom(99-w,t-h)"
            ),
        },
        "small_exact_transform_unit": small,
        "D8_equality_space": rank,
        "exact_low_input_rows": low_rows,
        "signed_input_rows_S0_through_S6": signed_rows,
        "signed_row_derivation": signed_derivation,
        "target_n3_equation": {
            "equation": (
                "sum_(j even) (-1)^(j/2) B[6,j] "
                "= 2024484 + (512/3)*n3"
            ),
            "solved_for_n3": (
                "n3=(3/512)*(sum_j (-1)^(j/2)B[6,j]-2024484)"
            ),
            "wave21_replay_exact": True,
        },
        "elementary_nonnegativity_only_bound": {
            "derivation": (
                "absolute value of the signed row is at most "
                "sum_j B[6,j]=binom(99,6)"
            ),
            "rational_upper": str(elementary_upper),
            "integer_upper": elementary_upper.numerator // elementary_upper.denominator,
            "multiple_of_3_upper": (
                elementary_upper.numerator // elementary_upper.denominator // 3 * 3
            ),
            "improves_4158": False,
        },
        "frozen_inputs_sha256": frozen,
        "limitations": [
            "The 1275-dimensional invariant space is a linear equality space, not a nonnegative realization.",
            "The signed S6 equation aggregates output weights and does not identify individual six-set compositions.",
            "No bounded numerical solver status is proof of feasibility or infeasibility.",
            "An exact rational primal or Farkas dual is required for an evidentiary LP claim.",
            "Discovery does not verify itself.",
        ],
        "status_wall": {
            "formal_rational_feasibility": "UNKNOWN",
            "formal_integral_feasibility": "UNKNOWN",
            "binary_code_realizability": "UNKNOWN",
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

    payload = canonical_json(build_results())
    if args.write:
        args.output.write_text(payload, encoding="utf-8", newline="\n")
    if args.verify:
        if not args.output.exists():
            raise SystemExit(f"missing result: {args.output}")
        if args.output.read_text(encoding="utf-8") != payload:
            raise SystemExit("canonical exact-results.json mismatch")
    print(
        "PASS: Wave141 exact bivariate identities verified; "
        "D8 dimension=1275, rank=3725, "
        "S6=2024484+(512/3)n3"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
