#!/usr/bin/env python3
"""Exact companion for the Wave 31 projector-block commutator theorem.

The checker audits finite arithmetic and symbolic coefficients in a
conditional human proof.  It does not instantiate the unknown graph, and it
does not treat a successful symbolic replay as an existence certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_BASE_COMMIT = "5652578111999645a9d5427d0716053de79e0902"

FROZEN_INPUTS = {
    "agents/2026-07-23-wave20-global-schur.md":
        "64352e1d96ed9a924e075c2d0659be8de887751194068a14b096e112a9320632",
    "verification/2026-07-23-wave20-global-schur-audit.md":
        "6311a893e1802382bfaaf00f8d366ba7f25ff036cda8032978dc5c6b4fdf35a3",
    "verification/wave21-lattice-extension/2026-07-23T184926Z-audit.md":
        "45814560f1d5bffb3b00144022a3a1f8d069e71dfe430247a1871822ac08f268",
    "verification/2026-07-22-n3-side-incidence-audit.md":
        "9b6ff3cc9ec8bec13ffd93a8abe0bf0f35398c99f676d00064d6bf5fe6db6787",
    "agents/2026-07-24-wave30-general-h729.md":
        "fd1f11a2ab5c5dfd2732a4ba1fb8d063dea1ae0e96d417aaf9d45eade4f2281a",
    "verification/wave30-general-h729/reverification-audit.md":
        "523a84e2a490f3626a791fb16f43b77b7631b3f26f2de8dcecc83f5e03f4d2cc",
}

VERTICES = 99
TRIANGLES = 231
TRIANGLES_PER_VERTEX = 7
FRAME_RANK = 44
FRAME_SCALE = 21
ROW_NORM = 4
ADJACENCY_EIGENVALUES = (14, 3, -4)
ADJACENCY_MULTIPLICITIES = (1, 54, 44)

ESSENTIAL_PREMISES = (
    "target_vertex_triangle_incidence",
    "zero_projector_transport",
    "rootless_integral_orthogonal_split",
    "block_sign_commutes_with_projector",
    "symmetric_transport",
    "minus_four_projector_formula",
    "unique_triangle_on_every_edge",
    "target_connectedness",
)


class PremiseError(ValueError):
    """Raised when a named premise is removed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_inputs() -> dict[str, str]:
    observed: dict[str, str] = {}
    for relative, expected in FROZEN_INPUTS.items():
        actual = sha256_file(REPO_ROOT / relative)
        if actual != expected:
            raise RuntimeError(
                f"frozen input drift for {relative}: {actual} != {expected}"
            )
        observed[relative] = actual
    return observed


def require(enabled: set[str], premise: str, stage: str) -> None:
    if premise not in enabled:
        raise PremiseError(f"{stage} requires {premise}")


def minus_four_projector_values() -> dict[int, int]:
    """Evaluate (27I-9A+J)/63 on the three adjacency eigenspaces.

    J acts by 99 on the all-ones eigenvector and by zero on the other two
    eigenspaces.
    """

    values = {}
    for eigenvalue in ADJACENCY_EIGENVALUES:
        j_value = VERTICES if eigenvalue == 14 else 0
        numerator = 27 - 9 * eigenvalue + j_value
        if numerator % 63:
            raise AssertionError("projector evaluation is not integral")
        values[eigenvalue] = numerator // 63
    return values


def transport_coefficients() -> dict[str, int]:
    """Return the exact scalar coefficients in the commutator transport."""

    # [K,P_-4]=0 with P_-4=(27I-9A+J)/63 gives
    # 9[K,A]=[K,J].  Since K1=3d and K is symmetric,
    # [K,J]=3(d1^T-1d^T), hence 3[K,A]=d1^T-1d^T.
    projector_a_coefficient = 9
    k_one_coefficient = 3
    reduced_commutator_coefficient = (
        projector_a_coefficient // k_one_coefficient
    )
    if projector_a_coefficient % k_one_coefficient:
        raise AssertionError("commutator coefficient does not divide")
    return {
        "projector_A_coefficient": projector_a_coefficient,
        "K_one_coefficient": k_one_coefficient,
        "reduced_commutator_coefficient": reduced_commutator_coefficient,
    }


def local_signed_edge_cancellation(
    first_edge_sign: int,
    second_edge_sign: int,
) -> dict[str, int | bool]:
    """Audit the unique-common-neighbor contribution on an adjacent pair."""

    if first_edge_sign not in (-1, 1) or second_edge_sign not in (-1, 1):
        raise ValueError("edge signs must be +/-1")
    z_commutator = first_edge_sign - second_edge_sign
    return {
        "first_edge_sign": first_edge_sign,
        "second_edge_sign": second_edge_sign,
        "ZA_minus_AZ_xy": z_commutator,
        "cancels": z_commutator == 0,
    }


def signed_block_sizes() -> list[dict[str, int]]:
    """Enumerate sizes implied by a constant signed triangle degree."""

    rows = []
    for signed_degree in range(-TRIANGLES_PER_VERTEX, TRIANGLES_PER_VERTEX + 1, 2):
        numerator = TRIANGLES + 33 * signed_degree
        if numerator % 2:
            raise AssertionError("signed block size is not integral")
        block_size = numerator // 2
        if not 0 <= block_size <= TRIANGLES:
            continue
        rows.append(
            {
                "constant_signed_degree": signed_degree,
                "block_size": block_size,
            }
        )
    return rows


def rootless_block_census() -> list[dict[str, int | str]]:
    """Enumerate every proper rank allowed by the norm-four trace identity."""

    census = []
    for block_rank in range(4, FRAME_RANK, 4):
        block_rows = FRAME_SCALE * block_rank // ROW_NORM
        if ROW_NORM * block_rows != FRAME_SCALE * block_rank:
            raise AssertionError("block row count drifted")
        census.append(
            {
                "block_rank": block_rank,
                "block_rows": block_rows,
                "rows_mod_33": block_rows % 33,
                "status": (
                    "EXCLUDED_DERIVED"
                    if block_rows % 33
                    else "SURVIVES_DIVISIBILITY"
                ),
            }
        )
    return census


def superseded_wave30_tensor_route() -> dict[str, object]:
    """Record the sharper U-row profile that the commutator now supersedes."""

    # B_U=I gives A4_U=M_U and hence A4_ii=4.  Tensor Cauchy gives
    # [6(q-2)]^2 <= 4*16.  The independently verified graph-local gap
    # deletes q=1.
    before_q_gap = [
        q_value
        for q_value in range(13)
        if 36 * (q_value - 2) ** 2 <= 64
    ]
    after_q_gap = [q_value for q_value in before_q_gap if q_value != 1]
    profiles = []
    for n_q3 in range(127):
        n_q2 = 126 - n_q3
        if 2 * n_q2 + 3 * n_q3 == 256:
            profiles.append({"n_q2": n_q2, "n_q3": n_q3})
    if (
        before_q_gap != [1, 2, 3]
        or after_q_gap != [2, 3]
        or profiles != [{"n_q2": 122, "n_q3": 4}]
    ):
        raise AssertionError("superseded U tensor route drifted")
    return {
        "status": "DERIVED_BUT_SUPERSEDED_BY_COMMUTATOR",
        "A4_U": "M_U",
        "q_before_graph_gap": before_q_gap,
        "q_after_graph_gap": after_q_gap,
        "unique_U_profile": profiles[0],
        "equivalent_c_profile": {"n_c9": 4, "n_c10": 122, "n_c11": 0},
        "A_sum_q": 216,
        "U_sum_q": 256,
        "scope": "necessary aggregate counts only; no M or frame",
    }


def derive(enabled: Iterable[str] = ESSENTIAL_PREMISES) -> dict[str, object]:
    active = set(enabled)
    require(
        active,
        "target_vertex_triangle_incidence",
        "N^T N=3I+Gamma and N N^T=7I+A",
    )
    require(
        active,
        "zero_projector_transport",
        "im(E) maps onto the adjacency -4 eigenspace",
    )
    require(
        active,
        "rootless_integral_orthogonal_split",
        "norm-four row support and 4|R|=21 rank",
    )
    require(
        active,
        "block_sign_commutes_with_projector",
        "D preserves im(E)",
    )
    require(
        active,
        "symmetric_transport",
        "K preserves both V and its orthogonal complement",
    )
    require(
        active,
        "minus_four_projector_formula",
        "the K/A/J commutator identity",
    )
    require(
        active,
        "unique_triangle_on_every_edge",
        "adjacent signed-edge cancellation",
    )
    require(
        active,
        "target_connectedness",
        "constant signed degree on all 99 vertices",
    )

    hashes = verify_frozen_inputs()
    projector_values = minus_four_projector_values()
    if projector_values != {14: 0, 3: 0, -4: 1}:
        raise AssertionError("minus-four projector formula drifted")

    coefficients = transport_coefficients()
    local = local_signed_edge_cancellation(1, 1)
    if not local["cancels"]:
        raise AssertionError("same-triangle edge signs did not cancel")

    sizes = signed_block_sizes()
    size_values = [row["block_size"] for row in sizes]
    if size_values != [0, 33, 66, 99, 132, 165, 198, 231]:
        raise AssertionError("signed block-size census drifted")

    block_census = rootless_block_census()
    if len(block_census) != 10:
        raise AssertionError("proper block-rank census drifted")
    if any(item["status"] != "EXCLUDED_DERIVED" for item in block_census):
        raise AssertionError("a proper rootless block survived divisibility")

    wave30_rows = {"rank20_A_rows": 105, "rank24_U_rows": 126}
    wave30_residues = {
        name: value % 33 for name, value in wave30_rows.items()
    }
    if any(value == 0 for value in wave30_residues.values()):
        raise AssertionError("Wave 30 block unexpectedly satisfies 33-divisibility")

    mutated = local_signed_edge_cancellation(1, -1)
    # With a mutated local contribution z=2, the adjacent equation becomes
    # 3((d_x-d_y)+2)=d_x-d_y, which permits d_x-d_y=-3.
    mutation_permitted_difference_numerator = (
        -coefficients["reduced_commutator_coefficient"]
        * int(mutated["ZA_minus_AZ_xy"])
    )
    mutation_permitted_difference_denominator = (
        coefficients["reduced_commutator_coefficient"] - 1
    )
    if (
        mutation_permitted_difference_numerator
        % mutation_permitted_difference_denominator
    ):
        raise AssertionError("mutation control difference is not integral")
    mutation_permitted_difference = (
        mutation_permitted_difference_numerator
        // mutation_permitted_difference_denominator
    )
    if mutation_permitted_difference != -3:
        raise AssertionError("mutation control drifted")

    return {
        "schema": "wave31-projector-block-commutator-discovery-v1",
        "status": "DERIVED_ENDPOINT_REMAINS_UNKNOWN",
        "public_base_commit": PUBLIC_BASE_COMMIT,
        "scope": (
            "Conditional exclusion, under actual target-graph incidence "
            "semantics, of every nontrivial rootless integral orthogonal "
            "decomposition of the rank-44 scaled-dual endpoint S-form."
        ),
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
        },
        "frozen_input_hashes": hashes,
        "target_data": {
            "vertices": VERTICES,
            "triangles": TRIANGLES,
            "triangles_per_vertex": TRIANGLES_PER_VERTEX,
            "adjacency_eigenvalues": list(ADJACENCY_EIGENVALUES),
            "adjacency_multiplicities": list(ADJACENCY_MULTIPLICITIES),
            "incidence_identities": {
                "N_transpose_N": "3I_231+Gamma",
                "N_N_transpose": "7I_99+A",
            },
        },
        "projector_transport": {
            "E": "zero-eigenspace projector of Gamma; M=21E",
            "imE_dimension": 44,
            "V": "minus-four eigenspace of A",
            "V_dimension": 44,
            "norm_identity": "||Nu||^2=3||u||^2 for u in im(E)",
            "minus_four_projector": "(27I-9A+J)/63",
            "projector_eigenspace_values": {
                str(key): value for key, value in projector_values.items()
            },
        },
        "block_involution": {
            "D": "diag(+1 on block rows R, -1 on the complement)",
            "commutation": "DE=ED",
            "K": "N D N^T",
            "K_symmetric": True,
            "K_preserves_V": True,
            "K_commutes_with_P_minus_four": True,
        },
        "commutator": {
            "coefficients": coefficients,
            "identity": "3(KA-AK)=d 1^T-1 d^T",
            "d_definition": "d_x=sum of triangle signs through vertex x",
            "K_one": "K1=3d",
            "K_entries": "K=diag(d)+Z, with Z_xy the unique edge-triangle sign",
            "adjacent_local_cancellation": local,
            "adjacent_consequence": "3(d_x-d_y)=d_x-d_y",
            "connected_consequence": "d is constant",
        },
        "divisibility": {
            "double_count": "99d=3(2|R|-231)",
            "consequence": "33 divides |R|",
            "constant_degree_size_census": sizes,
        },
        "rootless_block_trace": {
            "identity": "4|R|=21 rank(S_R)",
            "proper_block_census": block_census,
            "number_of_excluded_proper_ranks": len(block_census),
        },
        "wave30_boundary": {
            "rows": wave30_rows,
            "rows_mod_33": wave30_residues,
            "rank20_plus_rank24_rootless_decomposable_type":
                "EXCLUDED_DERIVED",
            "supersedes_wave30_surviving_decomposable_type": True,
        },
        "superseded_tensor_side_route": superseded_wave30_tensor_route(),
        "hostile_controls": {
            "different_signs_on_edges_of_one_graph_triangle": {
                "local": mutated,
                "adjacent_difference_permitted": mutation_permitted_difference,
                "conclusion": (
                    "The constant-d argument fails if edge signs do not come "
                    "from one shared triangle sign."
                ),
            },
            "drop_DE_equals_ED": (
                "D need not preserve im(E), so K need not preserve V."
            ),
            "drop_K_symmetry": (
                "Preservation of V alone need not imply commutation with its "
                "orthogonal projector."
            ),
            "drop_rootlessness": (
                "A norm-four row may split as two norm-two block components; "
                "E need not be coordinate block diagonal."
            ),
            "arbitrary_size_multiple_of_33": (
                "Divisibility is necessary only and constructs no commuting D."
            ),
        },
        "limitations": [
            "The theorem is conditional on a putative target graph.",
            "Actual vertex-triangle incidence semantics are essential.",
            "Rooted and integrally indecomposable endpoint forms remain untreated.",
            "No graph, X, M, S, frame, or Schur package is constructed.",
            "n3=708, Conway-99 existence, and novelty remain UNKNOWN.",
        ],
        "conclusions": {
            "nontrivial_rootless_integrally_decomposable_endpoint_S":
                "REFUTED_DERIVED",
            "wave30_rank20_plus_rank24_boundary": "REFUTED_DERIVED",
            "rooted_endpoint_forms": "UNKNOWN",
            "rootless_indecomposable_endpoint_forms": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "Conway_99": "UNKNOWN",
            "novelty": "UNKNOWN",
        },
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_json(args.output, derive())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
