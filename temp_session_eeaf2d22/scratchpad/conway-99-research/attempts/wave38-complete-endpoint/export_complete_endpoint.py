#!/usr/bin/env python3
"""Export Wave 38 endpoint inventories or proof-producing OPB candidates.

The normal, lightweight operation is ``--inventory``.  ``--branch-opb`` adds
an independently validated lazy-cut catalog to one exact refined branch.
``--static-complete-opb`` streams the complete all-prism clause schema, but is
deliberately guarded because the residual-only subfamily already exceeds
24 billion labelled constraints.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Mapping


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CODE_ROOT = REPOSITORY_ROOT / "code"
WAVE35_ROOT = CODE_ROOT
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from matching_orbits import n3_refined_branch_specification  # noqa: E402
from sat_model import EncodedRootModel  # noqa: E402
from wave35_n3_endpoint_root_scout import endpoint_edges  # noqa: E402

from complete_endpoint import (  # noqa: E402
    FORMAT,
    endpoint_refined_cases,
    iter_complete_static_clauses,
    static_size_inventory,
    validate_cut_catalog,
    validate_cut_pool,
)


PUBLIC_BASE_COMMIT = "3014f3b1c010cdde1687b8878d4ec58d2bb90f03"
HEADER_RE = re.compile(r"^\* #variable= ([1-9][0-9]*) #constraint= ([1-9][0-9]*)$")
STATIC_ACKNOWLEDGEMENT = "I_ACKNOWLEDGE_MORE_THAN_24_BILLION_STATIC_CLAUSES"


def canonical_payload(data: object) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validated_output_path(path: Path, label: str) -> Path:
    """Resolve one output inside the repository before any write occurs."""

    resolved = path.resolve()
    try:
        relative = resolved.relative_to(REPOSITORY_ROOT)
    except ValueError as error:
        raise ValueError(f"{label} must resolve inside the repository") from error
    if not relative.parts:
        raise ValueError(f"{label} must name a file below the repository root")
    return resolved


def endpoint_assignments(
    encoded: EncodedRootModel, refined_branch: int
) -> dict[int, bool]:
    assignments = {
        encoded.edge_variables[edge]: False for edge in endpoint_edges(encoded.root)
    }
    indices = encoded.root.label_index()
    normalized = tuple(sorted((indices[(0, 2)], indices[(2, 4)])))
    assignments[encoded.edge_variables[normalized]] = True
    decisions, refinement_edge, _ = n3_refined_branch_specification(
        encoded.root, refined_branch
    )
    for edge, value in decisions.items():
        variable = encoded.edge_variables[edge]
        prior = assignments.get(variable)
        if prior is not None and prior != value:
            raise ValueError("refined branch conflicts with endpoint units")
        assignments[variable] = value
    refinement_variable = encoded.edge_variables[refinement_edge]
    prior = assignments.get(refinement_variable)
    if prior is not None and prior is not True:
        raise ValueError("refinement edge conflicts with endpoint units")
    assignments[refinement_variable] = True
    return assignments


def build_branch_formula(
    refined_branch: int,
    cuts: tuple[tuple[int, ...], ...] = (),
) -> tuple[EncodedRootModel, dict[str, object]]:
    valid_cases = {
        case["refined_branch"]: case["parent_branch"]
        for case in endpoint_refined_cases()
    }
    if refined_branch not in valid_cases:
        raise ValueError("refined branch is not one of the 33 endpoint cases")

    encoded = EncodedRootModel.build(
        7,
        variant="compact",
        cardinality_backend="native",
    )
    for edge in endpoint_edges(encoded.root):
        encoded.cnf.append([-encoded.edge_variables[edge]])
    encoded.add_n3_normalization()
    encoded.add_n3_refined_branch(refined_branch)
    for clause in cuts:
        if not clause or any(literal >= 0 for literal in clause):
            raise ValueError("a prism cut must contain negative literals")
        encoded.cnf.append(list(clause))

    return encoded, {
        "refined_branch": refined_branch,
        "parent_branch": valid_cases[refined_branch],
        "completed_graph_automorphism_assumed": False,
        "lazy_cut_count": len(cuts),
    }


def branch_metadata(
    encoded: EncodedRootModel,
    branch: Mapping[str, object],
    opb_path: Path,
    opb_payload: bytes,
    strategy: str,
) -> dict[str, object]:
    statistics = encoded.statistics()
    constraint_count = int(statistics["clauses"]) + int(
        statistics["native_atmost_constraints"]
    )
    return {
        "format": "wave38-complete-endpoint-opb-v1",
        "role": "construction",
        "claim_label": "CANDIDATE_FORMULA_ONLY",
        "git_commit": PUBLIC_BASE_COMMIT,
        "scope": (
            "one of the exact 33 refined endpoint cases, conditional on "
            "n3=4158, with no completed-graph automorphism assumption"
        ),
        "strategy": strategy,
        "branch": dict(branch),
        "encoding": statistics,
        "opb": {
            "path": opb_path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
            "bytes": len(opb_payload),
            "sha256": sha256_bytes(opb_payload),
            "constraint_count": constraint_count,
        },
        "limitations": [
            "Formula export is not a SAT or UNSAT conclusion.",
            "A lazy-cut formula is not complete until solve-cut-check terminates.",
            "UNSAT requires a retained independently checked proof.",
            "SAT requires independent full-SRG and exhaustive prism checks.",
        ],
    }


def write_branch_opb(
    refined_branch: int,
    opb_path: Path,
    metadata_path: Path,
    cut_catalog_path: Path | None,
) -> dict[str, object]:
    opb_path = validated_output_path(opb_path, "OPB output")
    metadata_path = validated_output_path(metadata_path, "metadata output")
    if opb_path == metadata_path:
        raise ValueError("OPB and metadata outputs must be distinct")
    cuts: tuple[tuple[int, ...], ...] = ()
    if cut_catalog_path is not None:
        cut_source = json.loads(cut_catalog_path.read_text(encoding="utf-8"))
        if cut_source.get("format") == "wave38-prism-cut-catalog-v1":
            cuts = validate_cut_catalog(cut_source)
        elif cut_source.get("format") == "wave38-prism-cut-pool-v1":
            cuts = validate_cut_pool(cut_source)
        else:
            raise ValueError("unsupported prism cut source")
    encoded, branch = build_branch_formula(refined_branch, cuts)
    payload = encoded.opb_text().encode("ascii")
    opb_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    opb_path.write_bytes(payload)
    metadata = branch_metadata(
        encoded,
        branch,
        opb_path,
        payload,
        strategy="lazy_exact_separation",
    )
    metadata_path.write_bytes(canonical_payload(metadata))
    return metadata


def _render_clause(clause: tuple[int, ...]) -> bytes:
    if not clause:
        # x + (not x) is always exactly one, so requiring two is false.
        return b"+1 x1 +1 ~x1 >= 2 ;\n"
    terms = " ".join(f"+1 ~x{abs(literal)}" for literal in clause)
    return f"{terms} >= 1 ;\n".encode("ascii")


def write_static_complete_opb(
    refined_branch: int,
    opb_path: Path,
    metadata_path: Path,
    acknowledgement: str,
) -> dict[str, object]:
    if acknowledgement != STATIC_ACKNOWLEDGEMENT:
        raise ValueError(
            "static export refused: pass the exact acknowledgement string "
            f"{STATIC_ACKNOWLEDGEMENT!r}"
        )
    opb_path = validated_output_path(opb_path, "OPB output")
    metadata_path = validated_output_path(metadata_path, "metadata output")
    if opb_path == metadata_path:
        raise ValueError("OPB and metadata outputs must be distinct")

    encoded, branch = build_branch_formula(refined_branch)
    assignments = endpoint_assignments(encoded, refined_branch)
    base_text = encoded.opb_text()
    lines = base_text.splitlines(keepends=True)
    header = HEADER_RE.fullmatch(lines[0].rstrip("\n"))
    if header is None:
        raise AssertionError("unexpected base OPB header")
    variable_count = int(header.group(1))
    base_constraint_count = int(header.group(2))

    opb_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    body_path = opb_path.with_suffix(opb_path.suffix + ".body.tmp")
    output_path = opb_path.with_suffix(opb_path.suffix + ".tmp")
    prism_constraint_count = 0
    try:
        with body_path.open("wb") as body:
            body.write("".join(lines[1:]).encode("ascii"))
            for clause in iter_complete_static_clauses(
                encoded.root, fixed_assignments=assignments
            ):
                body.write(_render_clause(clause))
                prism_constraint_count += 1

        total_constraints = base_constraint_count + prism_constraint_count
        digest = hashlib.sha256()
        byte_count = 0
        with output_path.open("wb") as output, body_path.open("rb") as body:
            rendered_header = (
                f"* #variable= {variable_count} "
                f"#constraint= {total_constraints}\n"
            ).encode("ascii")
            output.write(rendered_header)
            digest.update(rendered_header)
            byte_count += len(rendered_header)
            while block := body.read(1024 * 1024):
                output.write(block)
                digest.update(block)
                byte_count += len(block)
        os.replace(output_path, opb_path)
    finally:
        if body_path.exists():
            body_path.unlink()
        if output_path.exists():
            output_path.unlink()

    metadata = {
        "format": "wave38-complete-static-endpoint-opb-v1",
        "role": "construction",
        "claim_label": "CANDIDATE_FORMULA_ONLY",
        "git_commit": PUBLIC_BASE_COMMIT,
        "scope": "one refined endpoint branch with every labelled prism forbidden",
        "strategy": "complete_static_all_prism_stream",
        "branch": branch,
        "static_schema": FORMAT,
        "base_constraint_count": base_constraint_count,
        "prism_constraint_count": prism_constraint_count,
        "opb": {
            "path": opb_path.resolve().relative_to(REPOSITORY_ROOT).as_posix(),
            "bytes": byte_count,
            "sha256": digest.hexdigest(),
            "constraint_count": total_constraints,
        },
        "limitations": [
            "Formula export alone does not decide satisfiability.",
            "UNSAT requires a retained independently checked proof.",
            "SAT requires independent decoding and full graph checks.",
        ],
    }
    metadata_path.write_bytes(canonical_payload(metadata))
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inventory", action="store_true")
    mode.add_argument("--branch-opb", action="store_true")
    mode.add_argument("--static-complete-opb", action="store_true")
    parser.add_argument("--refined-branch", type=int)
    parser.add_argument("--cut-catalog", type=Path)
    parser.add_argument("--opb", type=Path)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--acknowledge-static-size")
    args = parser.parse_args()

    if args.inventory:
        result = static_size_inventory()
        payload = canonical_payload(result)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(payload)
        else:
            print(payload.decode("utf-8"), end="")
        return 0

    if args.refined_branch is None or args.opb is None or args.metadata is None:
        raise SystemExit(
            "OPB modes require --refined-branch, --opb, and --metadata"
        )
    if args.branch_opb:
        result = write_branch_opb(
            args.refined_branch,
            args.opb,
            args.metadata,
            args.cut_catalog,
        )
    else:
        result = write_static_complete_opb(
            args.refined_branch,
            args.opb,
            args.metadata,
            args.acknowledge_static_size or "",
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
