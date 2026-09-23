#!/usr/bin/env python3
"""Export one exact prism-free refined endpoint branch as canonical OPB.

This is a formula exporter, not a solver and not a proof.  It combines:

* the complete compact rooted SRG encoding;
* the theorem-forced N3 normalization;
* one member of the verified 78-way refined cover;
* all 84 root-triangle consequences of ``P=0``; and
* the six fixed-coordinate-triangle prism clause families from Wave 36.

No completed-graph automorphism is assumed.  An UNSAT conclusion counts only
after a retained proof is independently checked; a SAT conclusion counts only
after the decoded 99-vertex graph passes independent SRG and prism checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CODE_ROOT = REPOSITORY_ROOT / "code"
WAVE36_ROOT = REPOSITORY_ROOT / "attempts" / "wave36-rooted-branches"
for import_root in (CODE_ROOT, WAVE36_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from matching_orbits import n3_refined_branch_specification, n3_refined_orbits
from rooted_branch_scout import (
    SURVIVING_BRANCHES,
    add_fixed_triangle_prism_constraints,
    endpoint_edge_sha256,
    endpoint_edges,
)
from sat_model import EncodedRootModel


FORMAT = "wave37-proof-producing-prism-free-refined-opb-v1"
PUBLIC_BASE_COMMIT = "efbf74e3edf4d11d853d0129634507b01ff7b577"


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refined-branch", type=int, required=True)
    parser.add_argument("--opb", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    return parser.parse_args()


def build_endpoint_formula(
    refined_branch: int,
) -> tuple[EncodedRootModel, int, dict[str, object]]:
    orbit_count = len(n3_refined_orbits())
    if not 1 <= refined_branch <= orbit_count:
        raise ValueError(f"refined branch must be in 1..{orbit_count}")

    encoded = EncodedRootModel.build(
        7,
        variant="compact",
        cardinality_backend="native",
    )
    for edge in endpoint_edges(encoded.root):
        encoded.cnf.append([-encoded.edge_variables[edge]])
    encoded.add_n3_normalization()
    encoded.add_n3_refined_branch(refined_branch)

    _, refinement_edge, parent_branch = n3_refined_branch_specification(
        encoded.root, refined_branch
    )
    if parent_branch not in SURVIVING_BRANCHES:
        raise ValueError(
            f"refined branch {refined_branch} has endpoint-incompatible "
            f"parent {parent_branch}"
        )
    strengthening = add_fixed_triangle_prism_constraints(encoded, parent_branch)
    refinement_literal = encoded.edge_variables[refinement_edge]
    return encoded, parent_branch, {
        "refinement_edge": list(refinement_edge),
        "refinement_literal": refinement_literal,
        "fixed_triangle_prism_strengthening": strengthening,
    }


def main() -> int:
    args = parse_args()
    encoded, parent_branch, branch_metadata = build_endpoint_formula(
        args.refined_branch
    )
    opb_payload = encoded.opb_text().encode("ascii")

    args.opb.parent.mkdir(parents=True, exist_ok=True)
    args.opb.write_bytes(opb_payload)

    statistics = encoded.statistics()
    constraint_count = int(statistics["clauses"]) + int(
        statistics["native_atmost_constraints"]
    )
    metadata = {
        "format": FORMAT,
        "role": "construction",
        "claim_label": "CANDIDATE_FORMULA_ONLY",
        "git_commit": PUBLIC_BASE_COMMIT,
        "scope": (
            "one exact member of the complete refined N3 cover, conditional "
            "on n3=4158, with no completed-graph automorphism assumption"
        ),
        "refined_branch": args.refined_branch,
        "parent_branch": parent_branch,
        "completed_graph_automorphism_assumed": False,
        "endpoint_unit_count": 84,
        "endpoint_edge_catalog_sha256": endpoint_edge_sha256(
            endpoint_edges(encoded.root)
        ),
        "branch": branch_metadata,
        "encoding": statistics,
        "opb": {
            "path": args.opb.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
            "bytes": len(opb_payload),
            "sha256": sha256_bytes(opb_payload),
            "constraint_count": constraint_count,
        },
        "limitations": [
            "The formula is only one refined branch, not the whole endpoint.",
            "Formula export is not a SAT or UNSAT conclusion.",
            "An UNSAT result requires a retained independently checked proof.",
            "A SAT result requires independent decoding and complete graph checks.",
            "The fixed-triangle clauses do not enumerate every possible prism.",
        ],
    }
    metadata_payload = (
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_bytes(metadata_payload)
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
