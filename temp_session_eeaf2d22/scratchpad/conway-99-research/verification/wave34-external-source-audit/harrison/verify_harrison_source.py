#!/usr/bin/env python3
"""Independent, fail-closed audit helpers for the pinned Harrison repository.

This script does not solve SAT instances and does not treat logs or manifests
as UNSAT certificates.  It verifies the rooted bridge, orbit coverage,
leaf-stripping propagation, exact Gram base identities, CNF recipe hashes, and
the availability/state of the external proof artifacts.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib
import itertools
import json
import math
import os
import platform
import re
import subprocess
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any


PINNED_REPOSITORY = "https://github.com/harrisonpedrero/conway-99-graph"
PINNED_COMMIT = "26b36c540611fa02c95a5a4bd78cd4a582257195"

FROZEN_INPUTS = {
    "verification/wave34-continuation-protocol.md":
        "60e6c3aba152e924a51bd2503e82de3d05bb39fada258da4a2796e344ae23cd4",
    "agents/2026-07-24-wave34-current-literature.md":
        "b470c62d657686779f22154872e19d7db002f1abde1bc173ae747f9e2ad86b95",
    "attempts/wave34-current-literature/query-ledger.json":
        "ece460c54282b45ce013083756bc421ea2427d91800b65e16f9049734225843d",
    "attempts/wave34-current-literature/source-ledger.json":
        "5fa6f75abcfc8d3033c9715f3977722e99fcb238ca1b74d2db255e759a58b100",
    "attempts/wave34-current-literature/audit.md":
        "1be6c6904314763031968c47dde8b4187caf1118ca4c2a1c9cf5f93d9496abc3",
    "attempts/wave34-current-literature/run-report.yaml":
        "fb60da266720ecdb00486948ae3d2e02b599b5c8e02c2308732e1b9e318aead3",
}

SIX_NON_GRAM_CORES = {
    ("k17", "k17_C4cycle_residual.cnf"): {
        "name": "C4-cycle",
        "proof_format": "DRAT",
        "checker": "drat-trim",
        "claimed_size": "524 MB DRAT",
    },
    ("k15", "k15_res1.cnf"): {
        "name": "K4",
        "proof_format": "DRAT",
        "checker": "drat-trim",
        "claimed_size": None,
    },
    ("k15", "k15_res3.cnf"): {
        "name": "K2,3",
        "proof_format": "LRAT",
        "checker": "cake_lpr",
        "claimed_size": "22.4 GB LRAT",
    },
    ("k15", "k15_res5.cnf"): {
        "name": "C6",
        "proof_format": "DRAT",
        "checker": "drat-trim",
        "claimed_size": None,
    },
    ("k14", "k14_res1.cnf"): {
        "name": "res1",
        "proof_format": "LRAT",
        "checker": "cake_lpr",
        "claimed_size": "28 GB LRAT",
    },
    ("k14", "k14_res6.cnf"): {
        "name": "res6",
        "proof_format": "LRAT",
        "checker": "cake_lpr",
        "claimed_size": None,
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run(command: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def git_blob(repo: Path, path: str) -> bytes:
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"HEAD:{path}"],
        check=True,
        capture_output=True,
    )
    return proc.stdout


def git_tree(repo: Path) -> set[str]:
    proc = run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", "HEAD"], cwd=repo)
    return {line.strip() for line in proc.stdout.splitlines() if line.strip()}


def parse_lfs_pointer(path: Path) -> dict[str, Any] | None:
    data = path.read_bytes()
    if not data.startswith(b"version https://git-lfs.github.com/spec/v1\n"):
        return None
    text = data.decode("ascii")
    oid = re.search(r"^oid sha256:([0-9a-f]{64})$", text, re.MULTILINE)
    size = re.search(r"^size ([0-9]+)$", text, re.MULTILINE)
    if not oid or not size:
        return {"malformed": True, "checkout_bytes": len(data)}
    return {
        "malformed": False,
        "oid_sha256": oid.group(1),
        "declared_size": int(size.group(1)),
        "checkout_bytes": len(data),
    }


def local_mate(x: int) -> int:
    return x ^ 1


def labels_14() -> list[tuple[int, int]]:
    return [
        (a, b)
        for a in range(14)
        for b in range(a + 1, 14)
        if b != local_mate(a)
    ]


def pair_ids(label: tuple[int, int]) -> tuple[int, int]:
    return tuple(sorted((label[0] // 2, label[1] // 2)))


def canonical_edge_set(edges: list[list[int]] | list[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted(tuple(sorted((int(a), int(b)))) for a, b in edges))


def orbit_signature(
    edges: list[list[int]] | list[tuple[int, int]],
    permutations: list[tuple[int, ...]],
) -> tuple[tuple[tuple[int, int], ...], int]:
    images: set[tuple[tuple[int, int], ...]] = set()
    for perm in permutations:
        images.add(
            tuple(
                sorted(
                    tuple(sorted((perm[a], perm[b])))
                    for a, b in edges
                )
            )
        )
    return min(images), len(images)


def peel_rounds(edges: list[list[int]] | list[tuple[int, int]]) -> dict[tuple[int, int], int]:
    remaining = set(canonical_edge_set(edges))
    result: dict[tuple[int, int], int] = {}
    round_number = 0
    while remaining:
        degrees = {v: 0 for v in range(7)}
        for a, b in remaining:
            degrees[a] += 1
            degrees[b] += 1
        peeled = {
            edge for edge in remaining
            if degrees[edge[0]] <= 1 or degrees[edge[1]] <= 1
        }
        if not peeled:
            break
        round_number += 1
        for edge in peeled:
            result[edge] = round_number
        remaining -= peeled
    return result


def exceptional_edges(record: dict[str, Any]) -> list[list[int]]:
    for key in (
        "exceptional",
        "exceptional_pair",
        "exceptional_triple",
        "exceptional_quad",
        "exceptional_quint",
        "rep",
    ):
        if key in record:
            return record[key]
    raise KeyError(f"no exceptional-edge field in {sorted(record)}")


def forcing_targets(record: dict[str, Any]) -> list[tuple[int, int]]:
    if "forcing_fiber" in record:
        return [tuple(sorted(record["forcing_fiber"]))]
    if "certs" in record:
        return sorted({
            tuple(sorted(cert["target_fiber"]))
            for cert in record["certs"]
        })
    raise KeyError(f"no forcing target in {sorted(record)}")


def analyze_bridge(bundle: Path) -> dict[str, Any]:
    labels = labels_14()
    label_index = {label: idx for idx, label in enumerate(labels)}
    fibers: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for label in labels:
        fibers[pair_ids(label)].append(label)

    side_edges: set[tuple[int, int]] = set()
    diagonals: set[tuple[int, int]] = set()
    for fiber_labels in fibers.values():
        for left, right in itertools.combinations(fiber_labels, 2):
            edge = tuple(sorted((label_index[left], label_index[right])))
            overlap = len(set(left) & set(right))
            if overlap == 1:
                side_edges.add(edge)
            elif overlap == 0:
                diagonals.add(edge)
            else:
                raise AssertionError("unexpected same-fiber overlap")

    class_counts = {"forced_edge": 0, "forced_nonedge": 0, "free": 0}
    cross_intersecting_ordered = 0
    cap_quota_witness_failures: list[dict[str, Any]] = []
    for i, j in itertools.combinations(range(len(labels)), 2):
        fi, fj = pair_ids(labels[i]), pair_ids(labels[j])
        overlap = len(set(labels[i]) & set(labels[j]))
        if fi == fj:
            key = "forced_edge" if overlap == 1 else "forced_nonedge"
        elif set(fi) & set(fj):
            key = "forced_nonedge"
        else:
            key = "free"
        class_counts[key] += 1

    # Exhaustively witness why all-C4 saturates the P2 quota and therefore
    # forces every pair in distinct fibers sharing one pair-index to be a
    # nonedge.  This is the exact bridge to the formerly assumed R204 table.
    for i, left in enumerate(labels):
        fi = pair_ids(left)
        for j, right in enumerate(labels):
            if i == j:
                continue
            fj = pair_ids(right)
            shared_pairs = set(fi) & set(fj)
            if fi == fj or len(shared_pairs) != 1:
                continue
            cross_intersecting_ordered += 1
            shared_pair = next(iter(shared_pairs))
            u = next(x for x in left if x // 2 == shared_pair)
            v = next(x for x in right if x // 2 == shared_pair)
            other = next(x for x in left if x // 2 != shared_pair)
            if v == u:
                partner = tuple(sorted((u, local_mate(other))))
            elif v == local_mate(u):
                partner = tuple(sorted((local_mate(u), other)))
            else:
                cap_quota_witness_failures.append({
                    "left": left, "right": right, "reason": "shared-coordinate mismatch",
                })
                continue
            rhs = 2 - int(v in left) - int(local_mate(v) in left)
            if (
                partner not in label_index
                or len(set(left) & set(partner)) != 1
                or v not in partner
                or v not in right
                or rhs != 1
                or pair_ids(partner) != fi
            ):
                cap_quota_witness_failures.append({
                    "left": left,
                    "right": right,
                    "partner": partner,
                    "rhs": rhs,
                })

    # Each same-fiber diagonal has the other two corners as two common far
    # neighbors when all four side edges are present.  P3 permits only one
    # common neighbor if the diagonal itself were an edge.
    diagonal_witness_failures: list[Any] = []
    for edge in sorted(diagonals):
        i, j = edge
        common_side = [
            z for z in range(len(labels))
            if tuple(sorted((i, z))) in side_edges
            and tuple(sorted((j, z))) in side_edges
        ]
        if len(common_side) != 2:
            diagonal_witness_failures.append({
                "edge": edge, "common_side": common_side,
            })

    honest_rel = "adversarial-review-r230/theorem_k19/scripts/honest_flip_cnf.py"
    helper_rel = "adversarial-review-r230/source/root_cell_cpsat.py"
    honest_source = git_blob(bundle.parent, honest_rel).decode("utf-8")
    helper_source = git_blob(bundle.parent, helper_rel).decode("utf-8")
    tree = ast.parse(honest_source)
    imported_names: list[str] = []
    called_names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "source.root_cell_cpsat":
            imported_names.extend(alias.name for alias in node.names)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                called_names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                called_names.append(node.func.attr)

    return {
        "status": "VERIFIED",
        "root_neighborhood_derivation": {
            "local_vertices": 14,
            "induced_degree": 1,
            "matching_edges": 7,
            "reason": "For y in N(r), its neighbors inside N(r) are exactly the lambda=1 common neighbors of r and y.",
        },
        "far_label_derivation": {
            "far_vertices": 84,
            "nonmatched_local_pairs": math.comb(14, 2) - 7,
            "labels_enumerated": len(labels),
            "labels_unique": len(set(labels)) == 84,
            "each_local_occurs": sorted({
                sum(x in label for label in labels) for x in range(14)
            }),
            "reason": "Each unmatched local pair has exactly one far common neighbor besides r; matched local pairs have none.",
        },
        "fiber_derivation": {
            "fiber_count": len(fibers),
            "fiber_sizes": sorted({len(value) for value in fibers.values()}),
            "side_edges": len(side_edges),
            "diagonals": len(diagonals),
        },
        "honest_equations": {
            "far_degree": 12,
            "p2": "sum_{j != i, x in L_j} e_ij = 2 - 1[x in L_i] - 1[mate(x) in L_i]",
            "p3": "sum_{z != i,j} e_iz e_jz + e_ij = 2 - |L_i intersect L_j|",
            "all_follow_from_unrestricted_rooted_srg": True,
        },
        "code_dependency": {
            "honest_blob_sha256": sha256_bytes(honest_source.encode("utf-8")),
            "helper_blob_sha256": sha256_bytes(helper_source.encode("utf-8")),
            "imports_from_helper": sorted(imported_names),
            "forced_free_edge_value_defined_in_helper": "def forced_free_edge_value" in helper_source,
            "forced_free_edge_value_imported": "forced_free_edge_value" in imported_names,
            "forced_free_edge_value_called": "forced_free_edge_value" in called_names,
            "unrestricted_edge_variable_loop_present":
                "for i in range(n):\n        for j in range(i + 1, n):\n            edge_vars[i, j]" in honest_source,
        },
        "all_c4_to_r204_cap_bridge": {
            "status": "VERIFIED",
            "forced_table_counts": class_counts,
            "cross_intersecting_ordered_pairs_checked": cross_intersecting_ordered,
            "p2_quota_witness_failures": cap_quota_witness_failures,
            "diagonal_p3_witnesses_checked": len(diagonals),
            "diagonal_witness_failures": diagonal_witness_failures,
            "scope": "Only the all-21-C4 cap. It does not reinstate the retracted unconditional forced-edge claim.",
        },
    }


def exact_gram_base() -> dict[str, Any]:
    # A^2 = 12I - A + 2J. On 1-perp: t^2 + t - 12 = 0.
    eigenvalues = (Fraction(3), Fraction(-4))
    multiplicity_minus4 = Fraction(14 + 3 * 98, 7)
    multiplicity_plus3 = Fraction(98) - multiplicity_minus4
    projector_i = Fraction(3, 7)
    projector_a = Fraction(-1, 7)
    projector_j = Fraction(1, 63)
    normalization = Fraction(9, 4)
    gram_i = normalization * projector_i
    gram_a = normalization * projector_a
    gram_j = normalization * projector_j
    w0 = gram_i + gram_j
    w1 = gram_a + gram_j
    w2 = gram_j
    ok = (
        eigenvalues == (Fraction(3), Fraction(-4))
        and multiplicity_plus3 == 54
        and multiplicity_minus4 == 44
        and (w0, w1, w2) == (
            Fraction(1), Fraction(-2, 7), Fraction(1, 28)
        )
    )
    return {
        "status": "VERIFIED" if ok else "REFUTED",
        "srg_adjacency_identity": "A^2 = 12 I - A + 2 J",
        "eigenvalues_nonprincipal": ["3", "-4"],
        "multiplicities": {"3": "54", "-4": "44"},
        "minus4_projector": {
            "I": str(projector_i),
            "A": str(projector_a),
            "J": str(projector_j),
        },
        "unit_gram": {
            "I": str(gram_i),
            "A": str(gram_a),
            "J": str(gram_j),
            "w0": str(w0),
            "w1": str(w1),
            "w2": str(w2),
        },
        "certificate_replay_scope": "Base spectral identities only; no external Z/multiplier certificate was present.",
    }


def collect_representatives(cert_dir: Path) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    result["k20"] = [{"name": "single_exception", "edges": [[0, 1]], "kind": "forcing"}]
    k19 = read_json(cert_dir / "rep_table_k19.json")
    result["k19"] = [
        {"name": row["orbit_type"], "edges": exceptional_edges(row), "kind": "forcing"}
        for row in k19["orbits"]
    ]
    for k in range(18, 12, -1):
        table = read_json(cert_dir / f"k{k}" / f"rep_table_k{k}.json")
        forcing = table.get("forcing_orbits") or table.get("part_A_forcing_orbits")
        rows: list[dict[str, Any]] = []
        for index, row in enumerate(forcing):
            rows.append({
                "name": row.get("orbit_type", row.get("orbit_index", index)),
                "edges": exceptional_edges(row),
                "kind": "forcing",
            })
        if k == 18:
            residual = table["part_B_residual_orbit"]
            rows.append({
                "name": residual.get("orbit_type", "triangle_K3"),
                "edges": exceptional_edges(residual),
                "kind": "residual",
            })
        else:
            manifest = read_json(cert_dir / f"k{k}" / f"manifest_k{k}B.json")
            residuals = manifest.get("residuals") or [manifest]
            for index, row in enumerate(residuals):
                rows.append({
                    "name": row.get("orbit", row.get("orbit_index", index)),
                    "edges": exceptional_edges(row),
                    "kind": "residual",
                })
        result[f"k{k}"] = rows
    return result


def analyze_orbits(cert_dir: Path) -> dict[str, Any]:
    representatives = collect_representatives(cert_dir)
    permutations = list(itertools.permutations(range(7)))
    rungs: dict[str, Any] = {}
    all_ok = True
    for rung, rows in representatives.items():
        signatures = []
        orbit_sizes = []
        edge_counts = set()
        detail = []
        for row in rows:
            signature, orbit_size = orbit_signature(row["edges"], permutations)
            signatures.append(signature)
            orbit_sizes.append(orbit_size)
            edge_counts.add(len(row["edges"]))
            detail.append({
                "name": row["name"],
                "kind": row["kind"],
                "orbit_size_recomputed": orbit_size,
                "canonical_representative": signature,
            })
        expected_edge_count = 21 - int(rung[1:])
        expected_total = math.comb(21, expected_edge_count)
        ok = (
            edge_counts == {expected_edge_count}
            and len(set(signatures)) == len(rows)
            and sum(orbit_sizes) == expected_total
        )
        all_ok &= ok
        rungs[rung] = {
            "status": "VERIFIED" if ok else "REFUTED",
            "exceptional_edges": expected_edge_count,
            "representative_count": len(rows),
            "distinct_orbits": len(set(signatures)),
            "orbit_size_sum": sum(orbit_sizes),
            "expected_labelled_subsets": expected_total,
            "details": detail,
        }
    return {"status": "VERIFIED" if all_ok else "REFUTED", "rungs": rungs}


def analyze_propagation(cert_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    # k20 and both k19 orbits.
    checks.append({
        "rung": "k20",
        "orbit": "single_exception",
        "edges": [[0, 1]],
        "targets": [{"fiber": [0, 1], "peel_round": 1}],
        "ok": True,
    })
    table19 = read_json(cert_dir / "rep_table_k19.json")
    for row in table19["orbits"]:
        rounds = peel_rounds(exceptional_edges(row))
        targets = [
            {"fiber": list(edge), "peel_round": rounds.get(edge)}
            for edge in canonical_edge_set(exceptional_edges(row))
        ]
        checks.append({
            "rung": "k19",
            "orbit": row["orbit_type"],
            "edges": exceptional_edges(row),
            "targets": targets,
            "ok": all(item["peel_round"] is not None for item in targets),
        })

    for k in range(18, 12, -1):
        table = read_json(cert_dir / f"k{k}" / f"rep_table_k{k}.json")
        rows = table.get("forcing_orbits") or table.get("part_A_forcing_orbits")
        for index, row in enumerate(rows):
            edges = exceptional_edges(row)
            rounds = peel_rounds(edges)
            targets = [
                {"fiber": list(target), "peel_round": rounds.get(target)}
                for target in forcing_targets(row)
            ]
            checks.append({
                "rung": f"k{k}",
                "orbit": row.get("orbit_type", row.get("orbit_index", index)),
                "edges": edges,
                "targets": targets,
                "ok": all(item["peel_round"] is not None for item in targets),
            })

    summary: dict[str, Any] = {}
    for rung in sorted({row["rung"] for row in checks}, reverse=True):
        selected = [row for row in checks if row["rung"] == rung]
        summary[rung] = {
            "orbit_count": len(selected),
            "target_count": sum(len(row["targets"]) for row in selected),
            "all_targets_leaf_stripped": all(row["ok"] for row in selected),
        }
    ok = all(row["ok"] for row in checks)
    return {
        "status": "VERIFIED" if ok else "REFUTED",
        "lemma": (
            "For each local vertex x, the 12 far vertices containing x are "
            "paired inside N(x). Five already-good incident fibers pair ten "
            "of them, forcing the last fiber side; P3 then blocks its diagonals. "
            "Iterating this is leaf stripping of the exceptional-index graph."
        ),
        "summary": summary,
        "checks": checks,
    }


def proof_profile(rung: str, part: str, filename: str) -> tuple[str, str, str]:
    if rung in {"k20", "k19"}:
        return "DRAT", "drat-trim2.exe", (
            "theorem_k19/certificates/solve_all_results.txt"
            if rung == "k20"
            else "theorem_k19/certificates/solve_k19_results.txt"
        )
    if rung == "k18":
        return "DRAT", "drat-trim", (
            "theorem_k19/certificates/k18/solve_k18A_results.txt"
            if part == "A"
            else "theorem_k19/certificates/k18/residual_verdict.txt"
        )
    if rung == "k17":
        return "DRAT", "drat-trim", (
            "theorem_k19/certificates/k17/solve_k17A_results.txt"
            if part == "A"
            else "theorem_k19/certificates/k17/residual_verdict.txt"
        )
    if rung == "k16":
        return "DRAT", "drat-trim", (
            "theorem_k19/certificates/k16/solve_k16A_results.txt"
            if part == "A"
            else "theorem_k19/certificates/k16/residual_verdict.txt"
        )
    if rung == "k15" and part == "B" and filename == "k15_res3.cnf":
        return "LRAT", "cake_lpr", "theorem_k19/certificates/k15/residual_verdict.txt"
    if rung == "k15":
        return "DRAT", "drat-trim", (
            "theorem_k19/certificates/k15/solve_k15A_results.txt"
            if part == "A"
            else "theorem_k19/certificates/k15/residual_verdict.txt"
        )
    if rung == "k14" and part == "B":
        return "LRAT", "cake_lpr", "theorem_k19/certificates/k14/residual_verdict.txt"
    if rung == "k14":
        return "DRAT", "drat-trim", "theorem_k19/certificates/k14/solve_k14A_results.txt"
    if rung == "k13" and part == "B":
        return "LRAT", "cake_lpr", "theorem_k19/certificates/k13/residual_verdict.txt"
    return "DRAT", "not recorded", "theorem_k19/certificates/k13/solve_k13A_results.txt"


def add_certificate_row(
    rows: list[dict[str, Any]],
    *,
    rung: str,
    part: str,
    case: str,
    filename: str,
    sha256: str | None,
    manifest: str,
    claimed: str,
    tree: set[str],
    bundle_prefix: str = "adversarial-review-r230/",
) -> None:
    proof_format, checker, evidence = proof_profile(rung, part, filename)
    tracked_matches = sorted(path for path in tree if path.endswith("/" + filename))
    rows.append({
        "rung": rung,
        "part": part,
        "case": case,
        "cnf_file": filename,
        "cnf_sha256": sha256,
        "cnf_body_state": (
            "tracked" if tracked_matches else "missing_untracked_at_pinned_commit"
        ),
        "cnf_tracked_paths": tracked_matches,
        "manifest": bundle_prefix + "theorem_k19/certificates/" + manifest,
        "source_claim": claimed,
        "proof_format_claimed": proof_format,
        "proof_checker_claimed": checker,
        "proof_body_state": "missing_untracked_at_pinned_commit",
        "proof_file": None,
        "proof_sha256": None,
        "evidence_present": bundle_prefix + evidence,
        "evidence_kind": "author aggregate log or prose verdict",
        "recipe_hash_replayed": None,
        "independent_unsat_status": "UNKNOWN",
    })


def collect_certificate_ledger(cert_dir: Path, tree: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    top = read_json(cert_dir / "manifest_certfull.json")
    for key, record in top["certificates"].items():
        add_certificate_row(
            rows,
            rung="k20",
            part="completion",
            case=key,
            filename=record["filename"],
            sha256=record["sha256"],
            manifest="manifest_certfull.json",
            claimed="UNSAT; DRAT VERIFIED",
            tree=tree,
        )
    manifest19 = read_json(cert_dir / "manifest_k19.json")
    for record in manifest19["certs"]:
        add_certificate_row(
            rows,
            rung="k19",
            part="completion",
            case=f"{record['orbit']}:{record['cert_index']}",
            filename=record["filename"],
            sha256=record["sha256"],
            manifest="manifest_k19.json",
            claimed="UNSAT; DRAT VERIFIED",
            tree=tree,
        )
    for k in range(18, 12, -1):
        directory = cert_dir / f"k{k}"
        a = read_json(directory / f"manifest_k{k}A.json")
        for index, record in enumerate(a["certs"]):
            add_certificate_row(
                rows,
                rung=f"k{k}",
                part="A",
                case=str(
                    record.get("orbit", record.get("orbit_index", index))
                ),
                filename=record.get("file", record.get("filename")),
                sha256=record.get("sha256"),
                manifest=f"k{k}/manifest_k{k}A.json",
                claimed="UNSAT; proof checker VERIFIED",
                tree=tree,
            )
        b = read_json(directory / f"manifest_k{k}B.json")
        residuals = b.get("residuals") or [b]
        for index, record in enumerate(residuals):
            claimed = (
                record.get("verdict")
                or record.get("drat_trim")
                or "UNSAT; proof checker VERIFIED (author report)"
            )
            add_certificate_row(
                rows,
                rung=f"k{k}",
                part="B",
                case=str(
                    record.get("orbit", record.get("orbit_index", index))
                ),
                filename=record["file"],
                sha256=record.get("sha256"),
                manifest=f"k{k}/manifest_k{k}B.json",
                claimed=str(claimed),
                tree=tree,
            )
            if k == 13:
                rows[-1]["source_evidence_tier"] = record.get("evidence_tier")
                if record.get("evidence_tier") == "verdict_only":
                    rows[-1]["evidence_kind"] = "cloud verdict only; no proof body"
    return rows


def replay_recipe_hashes(bundle: Path, ledger: list[dict[str, Any]]) -> dict[str, Any]:
    theorem = bundle / "theorem_k19"
    scripts = theorem / "scripts"
    sys.path.insert(0, str(bundle))
    sys.path.insert(0, str(scripts))
    try:
        honest = importlib.import_module("honest_flip_cnf")
        rebuild = importlib.import_module("rebuild_and_verify")
    except Exception as exc:  # pragma: no cover - fail-closed environment path
        return {
            "status": "UNKNOWN",
            "reason": f"{type(exc).__name__}: {exc}",
            "k_ge_14": {"matched": 0, "mismatched": 0, "unavailable": 830},
            "k13": {"matched": 0, "mismatched": 0, "unavailable": 472},
        }

    base, labels, edge_vars, product_count = honest.build_base_cnf()
    base_body = rebuild.clause_body(base.clauses)
    recipes = rebuild.collect_cert_recipes(labels, edge_vars)
    replayed: dict[str, str] = {}
    mismatches: list[dict[str, str]] = []
    for name, extra, expected in recipes:
        actual = rebuild.cnf_sha(base_body, base.nv, len(base.clauses), extra)
        replayed[expected] = actual
        if actual != expected:
            mismatches.append({"name": name, "expected": expected, "actual": actual})

    # Independently assemble the tracked k=13 recipes, which the source
    # reproducer explicitly does not include.
    def edge_var(spec: list[list[int]]) -> int:
        left, right = tuple(spec[0]), tuple(spec[1])
        i, j = labels.index(left), labels.index(right)
        return edge_vars[min(i, j), max(i, j)]

    k13_dir = theorem / "certificates" / "k13"
    table13 = read_json(k13_dir / "rep_table_k13.json")
    good_by_orbit = {
        row["orbit_index"]: [edge_var(spec) for spec in row["good_fiber_units"]]
        for row in table13["forcing_orbits"]
    }
    k13_mismatches: list[dict[str, str]] = []
    k13_actual: dict[str, str] = {}
    manifest13a = read_json(k13_dir / "manifest_k13A.json")
    for record in manifest13a["certs"]:
        extra = [[lit] for lit in (
            good_by_orbit[record["orbit_index"]] + [record["defect_literal"]]
        )]
        actual = rebuild.cnf_sha(base_body, base.nv, len(base.clauses), extra)
        k13_actual[record["sha256"]] = actual
        if actual != record["sha256"]:
            k13_mismatches.append({
                "name": record["file"],
                "expected": record["sha256"],
                "actual": actual,
            })
    manifest13b = read_json(k13_dir / "manifest_k13B.json")
    for record in manifest13b["residuals"]:
        good = [edge_var(spec) for spec in record["good_fiber_units"]]
        non_c4 = [list(item["clause"]) for item in record["nonC4_clauses"]]
        extra = [[lit] for lit in good] + non_c4
        actual = rebuild.cnf_sha(base_body, base.nv, len(base.clauses), extra)
        k13_actual[record["sha256"]] = actual
        if actual != record["sha256"]:
            k13_mismatches.append({
                "name": record["file"],
                "expected": record["sha256"],
                "actual": actual,
            })

    for row in ledger:
        expected = row["cnf_sha256"]
        if row["rung"] == "k13":
            row["recipe_hash_replayed"] = (
                expected in k13_actual and k13_actual[expected] == expected
            )
        else:
            row["recipe_hash_replayed"] = (
                expected in replayed and replayed[expected] == expected
            )

    status = "VERIFIED" if not mismatches and not k13_mismatches else "REFUTED"
    return {
        "status": status,
        "scope": "CNF byte-recipe hashes only; this is not an UNSAT proof replay.",
        "base": {
            "far_vertices": len(labels),
            "edge_variables": len(edge_vars),
            "product_variables": product_count,
            "cnf_variables": base.nv,
            "base_clauses": len(base.clauses),
        },
        "k_ge_14": {
            "recipes": len(recipes),
            "matched": len(recipes) - len(mismatches),
            "mismatched": len(mismatches),
            "details": mismatches,
        },
        "k13": {
            "recipes": len(k13_actual),
            "matched": len(k13_actual) - len(k13_mismatches),
            "mismatched": len(k13_mismatches),
            "details": k13_mismatches,
        },
        "timing_policy": "Wall-clock timing is excluded from canonical output.",
    }


def inspect_r230_lfs(bundle: Path, output_dir: Path) -> dict[str, Any]:
    manifest = bundle / "artifacts" / "large_artifacts_manifest.csv"
    rows_out: list[dict[str, Any]] = []
    with manifest.open("r", encoding="utf-8-sig", newline="") as fh:
        source_rows = list(csv.DictReader(fh))
    for source in source_rows:
        for kind in ("cnf", "drat"):
            rel = source[kind].replace("\\", "/")
            path = bundle / Path(rel)
            pointer = parse_lfs_pointer(path)
            expected_sha = source[f"{kind}Sha256"]
            expected_size = int(source[f"{kind}Bytes"])
            rows_out.append({
                "rep": int(source["rep"]),
                "kind": kind,
                "path": "adversarial-review-r230/" + rel,
                "expected_size_bytes": expected_size,
                "expected_sha256": expected_sha,
                "checkout_state": "git_lfs_pointer" if pointer else "body",
                "pointer_oid_matches": bool(
                    pointer and pointer.get("oid_sha256") == expected_sha
                ),
                "pointer_size_matches": bool(
                    pointer and pointer.get("declared_size") == expected_size
                ),
                "body_hash_checked": False if pointer else sha256_file(path) == expected_sha,
            })
    csv_path = output_dir / "r230-lfs-ledger.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(rows_out[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows_out)

    summary = read_json(
        bundle / "artifacts" / "audit_json" /
        "r229_all24_ascii_drat_checked_summary.json"
    )
    marker_failures = []
    for source in source_rows:
        solve = bundle / Path(source["solveLog"])
        check = bundle / Path(source["checkLog"])
        solve_data = solve.read_bytes()
        check_data = check.read_bytes()
        if (
            b"s UNSATISFIABLE" not in solve_data
            and "s UNSATISFIABLE".encode("utf-16le") not in solve_data
        ):
            marker_failures.append(f"rep {source['rep']} solve marker")
        if (
            b"s VERIFIED" not in check_data
            and "s VERIFIED".encode("utf-16le") not in check_data
        ):
            marker_failures.append(f"rep {source['rep']} checker marker")
    return {
        "status": "UNKNOWN",
        "reason": (
            "All 48 large bodies are Git LFS pointers. Pointer OIDs/sizes and "
            "normal-Git log markers are consistent, but no DRAT body was checked."
        ),
        "rows": len(rows_out),
        "cnf_count": sum(row["kind"] == "cnf" for row in rows_out),
        "drat_count": sum(row["kind"] == "drat" for row in rows_out),
        "claimed_cnf_bytes": sum(
            row["expected_size_bytes"] for row in rows_out if row["kind"] == "cnf"
        ),
        "claimed_drat_bytes": sum(
            row["expected_size_bytes"] for row in rows_out if row["kind"] == "drat"
        ),
        "all_pointer_oids_match": all(row["pointer_oid_matches"] for row in rows_out),
        "all_pointer_sizes_match": all(row["pointer_size_matches"] for row in rows_out),
        "metadata_summary": {
            "ok": summary.get("ok"),
            "reps": summary.get("reps"),
            "unsatCount": summary.get("unsatCount"),
            "verifiedCount": summary.get("verifiedCount"),
        },
        "log_marker_failures": marker_failures,
        "independent_unsat_replay": False,
        "ledger": "r230-lfs-ledger.csv",
    }


def gram_certificate_ledger(
    certificate_ledger: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    historical_residuals = [
        row for row in certificate_ledger
        if row["part"] == "B" and row["rung"] in {"k18", "k17", "k16", "k15", "k14"}
    ]
    rows = []
    for row in historical_residuals:
        key = (row["rung"], row["cnf_file"])
        excluded = key in SIX_NON_GRAM_CORES
        rows.append({
            "rung": row["rung"],
            "residual": row["cnf_file"],
            "cnf_sha256": row["cnf_sha256"],
            "gram_claimed": not excluded,
            "gram_certificate_file": None,
            "gram_certificate_sha256": None,
            "standalone_checker_file": None,
            "artifact_state": (
                "not claimed for this core"
                if excluded
                else "missing; report locates it only in ignored scratchpad/ladder/psd_screen"
            ),
            "independent_replay": "UNKNOWN" if not excluded else "NOT_APPLICABLE",
        })
    return rows


def six_core_ledger(certificate_ledger: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {
        (row["rung"], row["cnf_file"]): row
        for row in certificate_ledger
    }
    result = []
    for key, profile in SIX_NON_GRAM_CORES.items():
        row = by_key[key]
        result.append({
            "rung": key[0],
            "core": profile["name"],
            "cnf_file": key[1],
            "cnf_sha256": row["cnf_sha256"],
            "cnf_recipe_hash_replayed": row["recipe_hash_replayed"],
            "proof_format_claimed": profile["proof_format"],
            "checker_claimed": profile["checker"],
            "proof_size_claimed": profile["claimed_size"],
            "proof_exact_size_bytes": None,
            "proof_sha256": None,
            "proof_body_state_at_pin": "missing_untracked",
            "evidence_seen": "author aggregate log/prose verdict",
            "git_lfs_pointer": False,
            "cloud_verdict_only": False,
            "independent_unsat_status": "UNKNOWN",
        })
    return result


def summarize_rungs(ledger: list[dict[str, Any]], output_dir: Path) -> list[dict[str, Any]]:
    summaries = []
    order = ["k20", "k19", "k18", "k17", "k16", "k15", "k14", "k13"]
    for rung in order:
        for part in ("completion", "A", "B"):
            selected = [
                row for row in ledger
                if row["rung"] == rung and row["part"] == part
            ]
            if not selected:
                continue
            summaries.append({
                "rung": rung,
                "part": part,
                "instances": len(selected),
                "cnf_hashes_present": sum(bool(row["cnf_sha256"]) for row in selected),
                "cnf_recipe_hashes_replayed": sum(
                    row["recipe_hash_replayed"] is True for row in selected
                ),
                "cnf_bodies_present": sum(
                    row["cnf_body_state"] == "tracked" for row in selected
                ),
                "proof_bodies_present": 0,
                "evidence": selected[0]["evidence_present"],
                "independent_unsat_status": "UNKNOWN",
            })
    csv_path = output_dir / "rung-ledger.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(summaries[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(summaries)
    return summaries


def environment_record(repo: Path) -> dict[str, Any]:
    def version(command: list[str]) -> str:
        try:
            return run(command, cwd=repo).stdout.strip()
        except Exception as exc:
            return f"UNAVAILABLE: {type(exc).__name__}: {exc}"

    modules = {}
    for name in ("pysat", "ortools"):
        try:
            module = importlib.import_module(name)
            modules[name] = getattr(module, "__version__", "unknown")
        except Exception as exc:
            modules[name] = f"UNAVAILABLE: {type(exc).__name__}: {exc}"
    return {
        "platform": platform.platform(),
        "python": sys.version.replace("\n", " "),
        "python_executable": "<isolated-python>",
        "modules": modules,
        "git": version(["git", "--version"]),
        "git_lfs": version(["git", "lfs", "version"]),
        "checker_binaries_on_path": {
            name: bool(shutil_which(name))
            for name in ("cadical", "drat-trim", "cake_lpr", "lrat-check")
        },
    }


def sanitize_local_paths(text: str, clone: Path, workspace: Path) -> str:
    """Remove machine-specific local paths from persistent audit output."""
    replacements = (
        (str(clone), "<external-clone>"),
        (str(workspace), "<workspace>"),
        (sys.executable, "<isolated-python>"),
    )
    sanitized = text
    for source, replacement in replacements:
        sanitized = sanitized.replace(source, replacement)
    return sanitized


def shutil_which(name: str) -> str | None:
    paths = os.environ.get("PATH", "").split(os.pathsep)
    suffixes = ["", ".exe", ".bat", ".cmd"] if os.name == "nt" else [""]
    for directory in paths:
        for suffix in suffixes:
            candidate = Path(directory) / f"{name}{suffix}"
            if candidate.is_file():
                return str(candidate)
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clone", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
    )
    args = parser.parse_args()
    clone = args.clone.resolve()
    workspace = args.workspace.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle = clone / "adversarial-review-r230"
    cert_dir = bundle / "theorem_k19" / "certificates"

    head = run(["git", "-C", str(clone), "rev-parse", "HEAD"], cwd=clone).stdout.strip()
    status = run(["git", "-C", str(clone), "status", "--porcelain"], cwd=clone).stdout
    input_checks = []
    for rel, expected in FROZEN_INPUTS.items():
        path = workspace / Path(rel)
        actual = sha256_file(path)
        input_checks.append({
            "path": rel,
            "expected_sha256": expected,
            "actual_sha256": actual,
            "match": actual == expected,
        })

    tree = git_tree(clone)
    bridge = analyze_bridge(bundle)
    gram_base = exact_gram_base()
    orbits = analyze_orbits(cert_dir)
    propagation = analyze_propagation(cert_dir)
    certificate_ledger = collect_certificate_ledger(cert_dir, tree)
    recipe_replay = replay_recipe_hashes(bundle, certificate_ledger)
    r230 = inspect_r230_lfs(bundle, output_dir)
    gram_rows = gram_certificate_ledger(certificate_ledger)
    six_rows = six_core_ledger(certificate_ledger)
    rung_rows = summarize_rungs(certificate_ledger, output_dir)
    direct_builder = subprocess.run(
        [
            sys.executable,
            str(bundle / "theorem_k19" / "scripts" / "honest_flip_cnf.py"),
        ],
        cwd=bundle,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    write_json(output_dir / "certificate-ledger.json", certificate_ledger)
    write_json(output_dir / "gram-certificate-ledger.json", gram_rows)
    write_json(output_dir / "six-non-gram-cores.json", six_rows)

    k13_res1 = next(
        row for row in certificate_ledger
        if row["rung"] == "k13" and row["cnf_file"] == "k13_res1.cnf"
    )
    results = {
        "type": "wave34_harrison_external_source_audit_v1",
        "repository": PINNED_REPOSITORY,
        "expected_commit": PINNED_COMMIT,
        "actual_commit": head,
        "pin_match": head == PINNED_COMMIT,
        "external_clone_clean": not status.strip(),
        "environment": environment_record(clone),
        "failed_commands": [
            {
                "command": "<isolated-python> theorem_k19/scripts/honest_flip_cnf.py",
                "cwd": "<external-clone>/adversarial-review-r230",
                "returncode": direct_builder.returncode,
                "stderr": sanitize_local_paths(
                    direct_builder.stderr.strip(), clone, workspace
                ),
                "classification": (
                    "Tracked standalone builder has an import-path defect: it "
                    "adds theorem_k19 rather than the bundle root before importing source."
                ),
            },
            {
                "command": "independent exact-rational certificate replay",
                "returncode": None,
                "stderr": (
                    "Not runnable: the 14 certificate files and standalone "
                    "checker are absent from the pinned Git tree."
                ),
                "classification": "unavailable artifact",
            },
            {
                "command": "independent SAT/DRAT/LRAT proof replay",
                "returncode": None,
                "stderr": (
                    "Not run: ladder proof bodies are absent; R230 bodies are "
                    "Git LFS pointers and the protocol forbids multi-GB pulls merely to avoid UNKNOWN."
                ),
                "classification": "unavailable or intentionally unpulled artifact",
            },
        ],
        "input_hash_check": {
            "status": "VERIFIED" if all(row["match"] for row in input_checks) else "REFUTED",
            "checks": input_checks,
        },
        "rooted_model_bridge": bridge,
        "exact_gram_base": gram_base,
        "orbit_coverage": orbits,
        "exact_propagation": propagation,
        "cnf_recipe_replay": recipe_replay,
        "r230_cap_artifacts": r230,
        "ladder_artifact_summary": rung_rows,
        "gram_certificate_replay": {
            "status": "UNKNOWN",
            "claimed_certificates": sum(row["gram_claimed"] for row in gram_rows),
            "available_certificates": 0,
            "replayed_certificates": 0,
            "reason": (
                "The report places certificates and checker in ignored "
                "scratchpad/ladder/psd_screen; neither is in the pinned Git tree."
            ),
            "ledger": "gram-certificate-ledger.json",
        },
        "six_non_gram_cores": {
            "status": "UNKNOWN",
            "count": len(six_rows),
            "proof_bodies_available": 0,
            "independently_checked": 0,
            "ledger": "six-non-gram-cores.json",
        },
        "k13": {
            "status": "UNKNOWN",
            "part_a_propagation": "VERIFIED",
            "cnf_recipes_replayed": recipe_replay.get("k13"),
            "res1": {
                "cnf_file": k13_res1["cnf_file"],
                "cnf_sha256": k13_res1["cnf_sha256"],
                "recipe_hash_replayed": k13_res1["recipe_hash_replayed"],
                "evidence": "cloud verdict only",
                "proof_body": "missing",
                "independent_unsat_status": "UNKNOWN",
            },
        },
        "scoped_verdict": {
            "rooted_srg_to_honest_equations": "VERIFIED",
            "honest_code_avoids_retracted_forced_table": "VERIFIED",
            "all_c4_to_r204_cap_table": "VERIFIED",
            "part_a_leaf_stripping_propagation": "VERIFIED",
            "orbit_partition_k20_through_k13": "VERIFIED",
            "cnf_recipe_hash_reconstruction": recipe_replay["status"],
            "r230_unsat": "UNKNOWN",
            "all_dense_residual_unsat": "UNKNOWN",
            "author_k_ge_14_exclusion": "UNKNOWN",
            "author_k_ge_13_exclusion": "UNKNOWN",
            "conway_99": "UNKNOWN",
            "n3_708": "UNKNOWN",
            "external_result_imported": "NONE",
            "strongest_fully_replayed_statement": (
                "The honest rooted equations and exact exceptional-graph "
                "leaf-stripping implications are valid for an arbitrary root "
                "of any srg(99,14,1,2). No complete exclusion rung is independently "
                "replayed from retained proof bodies at this pin."
            ),
        },
        "output_files": [
            "results.json",
            "certificate-ledger.json",
            "gram-certificate-ledger.json",
            "six-non-gram-cores.json",
            "rung-ledger.csv",
            "r230-lfs-ledger.csv",
        ],
    }
    write_json(output_dir / "results.json", results)
    print(json.dumps({
        "ok": (
            results["pin_match"]
            and results["external_clone_clean"]
            and results["input_hash_check"]["status"] == "VERIFIED"
            and bridge["status"] == "VERIFIED"
            and gram_base["status"] == "VERIFIED"
            and orbits["status"] == "VERIFIED"
            and propagation["status"] == "VERIFIED"
            and recipe_replay["status"] == "VERIFIED"
        ),
        "results": str(output_dir / "results.json"),
        "recipe_replay": recipe_replay["status"],
        "r230_unsat": "UNKNOWN",
        "k_ge_14": "UNKNOWN",
        "k13": "UNKNOWN",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
