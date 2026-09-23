#!/usr/bin/env python3
"""Independent exact checks for the frozen Wave 32 literature package.

This checker makes no network request and imports no submitted code.  It
validates frozen bytes, JSON accounting, the submitted manifest, and the
elementary arithmetic/spectral/lattice consequences used to delimit the
literature search.  Source-content inspection is recorded separately in
audit.md; an offline checker cannot certify a paper's prose.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent
CANDIDATE_DIR = ROOT / "verification" / "wave32-literature-audit"

FROZEN = {
    "agents/2026-07-24-wave32-statement-literature.md":
        "9ae998d92296e9467041a431fc04121fe1411f8ac620d3b08c4016bfc3fc57ff",
    "verification/wave32-literature-audit/protocol-freeze.md":
        "3c645dcd4188c9c34ba9e04e2fbd966708d05080a33caa95c720a1fde46283d2",
    "verification/wave32-literature-audit/query-ledger.json":
        "7e7812a3dbf8c19a31eec58cc43c764aa1b61e7ad0fa1b8147b02fccfadef2c6",
    "verification/wave32-literature-audit/source-metadata.json":
        "6da7402bc6dbfa9f1b6a7c59d5f1ca74a841bb65e6ad3b0f5595afcf322f890e",
    "verification/wave32-literature-audit/audit.md":
        "71b6f184cf35bf3407529b42a20be4f0ccb957a39d0bbf294d19200b37bcb02f",
    "verification/wave32-literature-audit/correction-ledger.md":
        "3d2e10fe8ad8e2fbf24d9d449e69eecda950e40ba7b2f29c81867f2b5600cf4f",
    "verification/wave32-literature-audit/run-report.yaml":
        "d411bcc7c9e92d4c06ee5c96a0b8496551ea73488c21b7e9becae169bbe9f025",
    "verification/wave32-literature-audit/artifact-manifest.sha256":
        "9bdf458203beb32c76b993af2cb6130641546b5a7816f8bed507661e640173c6",
}

SUPPORTING = {
    "verification/wave28-glue-discriminant/audit.md":
        "5c1dc7978d571a9471837b45a36663c7c457b6434800776501e4967146956b86",
    "verification/wave31-sign-commutant/audit.md":
        "f6145a3c4f4e787b23440a6ea071d606477821abab0ab8e7e5fe52042d6528a0",
    "verification/wave28-theta-modular/audit.md":
        "adc90e404735ca147bc0a5418974d8af0bde71c4ddc2dc62a8c07dee670dbfeb",
    "verification/wave28-literature-audit/audit.md":
        "ef18079970e410d114ab24752d4b738bc26ff4e6266a8cc775a4e14813fe1128",
    "SOURCES.bib":
        "3c93b322ee4b0a61cf1407fdf5b082dbb90801459300289c7097b56833914a8e",
}

ENDPOINTS = [9, 21, 49, 81, 189, 441, 729, 1029]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_bytes(payload: object) -> bytes:
    return (
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)
        .encode("utf-8")
        + b"\n"
    )


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_frozen_bytes() -> dict[str, str]:
    observed = {name: sha256(ROOT / name) for name in FROZEN}
    if observed != FROZEN:
        raise AssertionError(
            f"candidate byte drift: expected={FROZEN}, observed={observed}"
        )
    return observed


def verify_supporting_bytes() -> dict[str, str]:
    observed = {name: sha256(ROOT / name) for name in SUPPORTING}
    if observed != SUPPORTING:
        raise AssertionError(
            f"supporting-input byte drift: expected={SUPPORTING}, "
            f"observed={observed}"
        )
    return observed


def verify_candidate_manifest() -> dict[str, str]:
    manifest = CANDIDATE_DIR / "artifact-manifest.sha256"
    observed: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        observed[name] = digest
    expected_names = {
        "protocol-freeze.md",
        "query-ledger.json",
        "source-metadata.json",
        "audit.md",
        "correction-ledger.md",
        "run-report.yaml",
    }
    if set(observed) != expected_names:
        raise AssertionError(f"candidate manifest names drifted: {observed}")
    recomputed = {
        name: sha256(CANDIDATE_DIR / name)
        for name in sorted(expected_names)
    }
    if observed != recomputed:
        raise AssertionError(
            f"candidate manifest mismatch: listed={observed}, actual={recomputed}"
        )
    return observed


def prime_valuation(value: int, prime: int) -> int:
    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent


def endpoint_arithmetic() -> dict[str, object]:
    # The frozen endpoint has det(B)<=6525 and det(Q)>=5.
    h_cap = 6525 // 5
    smooth = set()
    power_three = 1
    while power_three <= h_cap:
        power_seven = 1
        while power_three * power_seven <= h_cap:
            value = power_three * power_seven
            if value != 1 and value % 4 == 1:
                smooth.add(value)
            power_seven *= 7
        power_three *= 3
    derived = sorted(smooth)
    if derived != ENDPOINTS:
        raise AssertionError(f"endpoint list drifted: {derived}")

    rows = []
    for h in ENDPOINTS:
        u = prime_valuation(h, 3)
        v = prime_valuation(h, 7)
        remainder = h // (3**u * 7**v)
        if remainder != 1:
            raise AssertionError(f"endpoint {h} is not 3,7-smooth")
        level = 21 if u and v else (3 if u else 7)
        rows.append({
            "h": h,
            "v3": u,
            "v7": v,
            "exact_level": level,
            "root_complement_determinant": 2 * h,
            "modular_determinant_required": level**22,
            "modularity_veto": h != level**22,
            "strong_21_modularity_veto": h != 21**22,
        })
    if not all(
        row["modularity_veto"] and row["strong_21_modularity_veto"]
        for row in rows
    ):
        raise AssertionError("a modular determinant unexpectedly survived")
    return {
        "det_B_cap": 6525,
        "det_Q_floor": 5,
        "h_cap": h_cap,
        "derived_endpoints": derived,
        "rows": rows,
    }


def incidence_spectrum() -> dict[str, object]:
    # A has spectrum 14^1, 3^54, (-4)^44.  NN^T=7I+A is
    # positive definite, so N has rank 99.  N^TN has 132 additional zeros;
    # Gamma=N^TN-3I.
    adjacency = [(14, 1), (3, 54), (-4, 44)]
    nnt = [(7 + eigenvalue, multiplicity) for eigenvalue, multiplicity in adjacency]
    if sum(mult for _, mult in nnt) != 99:
        raise AssertionError("vertex-space multiplicities do not sum to 99")
    if any(eigenvalue <= 0 for eigenvalue, _ in nnt):
        raise AssertionError("NN^T unexpectedly singular")
    gamma = [
        (eigenvalue - 3, multiplicity)
        for eigenvalue, multiplicity in nnt
    ] + [(-3, 231 - 99)]
    expected = [(18, 1), (7, 54), (0, 44), (-3, 132)]
    if gamma != expected:
        raise AssertionError(f"triangle spectrum drifted: {gamma}")
    return {
        "hypotheses": [
            "putative srg(99,14,1,2)",
            "lambda=1, hence every edge lies in a unique triangle",
            "N*N^T=7I+A",
            "N^T*N=3I+Gamma",
        ],
        "triangle_count": 99 * 14 // 6,
        "rank_N": 99,
        "gamma_spectrum": [
            {"eigenvalue": value, "multiplicity": multiplicity}
            for value, multiplicity in gamma
        ],
        "scope": "actual-incidence only",
    }


def query_accounting() -> dict[str, object]:
    ledger = load_json(CANDIDATE_DIR / "query-ledger.json")
    batches = ledger["batches"]
    queries = [
        query
        for batch in batches
        for query in batch["queries"]
    ]
    expected_ids = [f"B{index:02d}" for index in range(1, 18)]
    observed_ids = [batch["id"] for batch in batches]
    if observed_ids != expected_ids:
        raise AssertionError(f"batch IDs drifted: {observed_ids}")
    if len(batches) != 17 or len(queries) != 68:
        raise AssertionError("query accounting is not 17 batches / 68 strings")
    if len(set(queries)) != 68:
        raise AssertionError("exact query strings are not unique")
    counts = ledger["counts"]
    if counts != {"web_search_batches": 17, "exact_query_strings": 68}:
        raise AssertionError(f"declared query counts drifted: {counts}")
    failures = ledger["failed_or_incomplete_access"]
    if len(failures) != 3 or any(row["use_as_evidence"] for row in failures):
        raise AssertionError("failed-access evidence boundary drifted")
    return {
        "batch_count": len(batches),
        "query_count": len(queries),
        "unique_query_count": len(set(queries)),
        "lane_count": len({batch["lane"] for batch in batches}),
        "direct_inspection_event_count": len(ledger["direct_inspection_events"]),
        "failed_or_incomplete_access_count": len(failures),
        "failed_access_used_as_evidence": False,
    }


def source_accounting() -> dict[str, object]:
    metadata = load_json(CANDIDATE_DIR / "source-metadata.json")
    records = metadata["records"]
    expected_ids = [f"S{index:02d}" for index in range(1, 16)]
    observed_ids = [record["id"] for record in records]
    if observed_ids != expected_ids:
        raise AssertionError(f"source IDs drifted: {observed_ids}")
    if metadata["record_count"] != 15 or len(records) != 15:
        raise AssertionError("corrected source count is not 15")
    retention = metadata["retention_policy"]
    raw_counts = {
        key: retention[key]
        for key in (
            "raw_pdfs_retained",
            "raw_html_retained",
            "raw_api_or_search_payloads_retained",
        )
    }
    if set(raw_counts.values()) != {0}:
        raise AssertionError(f"raw-retention count drifted: {raw_counts}")

    by_id = {record["id"]: record for record in records}
    petro = by_id["S01"]
    if (
        petro["title"] != "On Clique Graphs and Clique Regular Graphs"
        or petro["authors"] != ["Robert R. Petro", "Connor M. Phillips"]
        or petro["identifiers"]["arxiv"] != "2502.17845"
        or petro["identifiers"]["doi"] != "10.1016/j.disc.2025.114862"
    ):
        raise AssertionError(f"Petro-Phillips metadata drifted: {petro}")
    if "18^1, 7^54, 0^44, (-3)^132" not in petro["supports"]:
        raise AssertionError("Petro-Phillips spectrum not recorded")

    phillips = by_id["S02"]
    if (
        phillips["identifiers"]["arxiv"] != "2605.22867"
        or phillips["submitted_utc"] != "2026-05-19T20:49:26Z"
    ):
        raise AssertionError(f"Phillips thesis metadata drifted: {phillips}")

    keramatipour = by_id["S15"]
    if (
        keramatipour["authors"] != ["Ali Keramatipour"]
        or keramatipour["identifiers"]["arxiv"] != "2604.23037"
        or keramatipour["chronology"]
        != "PRE_WAVE32_REPOSITORY_PRIOR_ART_ADDED_AFTER_INDEPENDENT_AUDIT"
    ):
        raise AssertionError(
            f"Keramatipour correction metadata drifted: {keramatipour}"
        )

    conclusion = metadata["conclusion"]
    if (
        conclusion["novelty"] != "UNKNOWN"
        or conclusion["global_conway_99_status"] != "UNKNOWN"
    ):
        raise AssertionError(f"status wall drifted: {conclusion}")

    chronology: dict[str, int] = {}
    for record in records:
        label = record["chronology"]
        chronology[label] = chronology.get(label, 0) + 1
    return {
        "record_count": len(records),
        "source_ids": observed_ids,
        "chronology_counts": chronology,
        "raw_retention_counts": raw_counts,
        "petro_phillips": {
            "title": petro["title"],
            "authors": petro["authors"],
            "doi": petro["identifiers"]["doi"],
            "arxiv": petro["identifiers"]["arxiv"],
            "chronology": petro["chronology"],
        },
        "phillips_thesis": {
            "arxiv": phillips["identifiers"]["arxiv"],
            "submitted_utc": phillips["submitted_utc"],
        },
        "keramatipour": {
            "arxiv": keramatipour["identifiers"]["arxiv"],
            "chronology": keramatipour["chronology"],
            "scope": "no existence or nonexistence certificate",
        },
        "originally_frozen_record_count": 14,
        "post_verifier_source_additions": 1,
        "novelty": conclusion["novelty"],
        "global_conway_99_status": conclusion["global_conway_99_status"],
    }


def source_quality_findings() -> dict[str, object]:
    metadata = load_json(CANDIDATE_DIR / "source-metadata.json")
    by_id = {record["id"]: record for record in metadata["records"]}
    correction_ledger = (
        CANDIDATE_DIR / "correction-ledger.md"
    ).read_text(encoding="utf-8")

    # Replay the three v1 objections against the corrected v2 bytes.  The
    # correction ledger must preserve the original defects and frozen hashes;
    # the corrected metadata must resolve, rather than erase, them.
    s06_authors = by_id["S06"]["authors"]
    if s06_authors != ["Rudolf Scharlau", "Britta Blaschke"]:
        raise AssertionError(f"S06 correction regressed: {s06_authors}")
    s10_support = by_id["S10"]["supports"]
    required_s10 = (
        "complete generating system containing all lattice vectors through "
        "the required bound"
    )
    if required_s10 not in s10_support:
        raise AssertionError(f"S10 correction regressed: {s10_support}")

    s15 = by_id["S15"]
    if (
        s15["identifiers"]["arxiv"] != "2604.23037"
        or "neither existence nor nonexistence" not in s15["does_not_support"]
    ):
        raise AssertionError(f"S15 correction regressed: {s15}")
    sources_bib = (ROOT / "SOURCES.bib").read_text(encoding="utf-8")
    if "2604.23037" not in sources_bib or "Keramatipour" not in sources_bib:
        raise AssertionError("repository bibliography no longer corroborates S15")

    v1_hashes = {
        "agent report":
            "8e0d7950eac55e5eb36db9c6b015e7761e80f42f890ed1146fbb4b04036b4c43",
        "source-metadata.json":
            "9db780c7db0151ca90e44781608f6139145b482f65dfa1132ae7fbad580ea85c",
        "audit.md":
            "24dd1de8c3c8a6a6a84abddf2edf65492576643a4e58ed3dd669e4f471b69fab",
        "run-report.yaml":
            "b410a42a2ab7a019609954edc69990794070404206f5c4f04f591b24639c5bda",
        "artifact manifest":
            "7c3c46499f38289690cfd4b51769d98f93c530eeab130b9a73a1d1317eb44572",
    }
    for label, digest in v1_hashes.items():
        if label not in correction_ledger or digest not in correction_ledger:
            raise AssertionError(f"v1 chronology missing {label}: {digest}")

    required_correction_fragments = [
        "Source `S06` reversed the published author order.",
        "complete generating system containing all lattice vectors through the",
        "14-record set omitted Ali Keramatipour",
        "rootless integrally decomposable actual-incidence endpoint:",
    ]
    for fragment in required_correction_fragments:
        if fragment not in correction_ledger:
            raise AssertionError(f"correction ledger missing: {fragment!r}")

    agent_report = (
        ROOT / "agents" / "2026-07-24-wave32-statement-literature.md"
    ).read_text(encoding="utf-8")
    corrected_audit = (
        CANDIDATE_DIR / "audit.md"
    ).read_text(encoding="utf-8")
    for name, text in (
        ("agent report", agent_report),
        ("candidate audit", corrected_audit),
    ):
        if "rootless integrally decomposable actual endpoint:" not in text:
            raise AssertionError(f"{name} lost actual-incidence shorthand scope")

    return {
        "candidate_version": "v2_corrected",
        "fatal_source_or_applicability_defect": False,
        "v1_objections_preserved": True,
        "v1_frozen_hashes": v1_hashes,
        "resolved_findings": [
            {
                "source_id": "S06",
                "v1_finding": "published author order reversed",
                "v2_status": "RESOLVED",
                "corrected": s06_authors,
            },
            {
                "source_id": "S10",
                "v1_finding": (
                    "'supplied lattice' compresses the algorithm's complete-"
                    "generating-system input requirement"
                ),
                "v2_status": "RESOLVED",
                "corrected_scope": required_s10,
            },
            {
                "source_id": "S15",
                "v1_finding": (
                    "Wave 32 metadata omits Keramatipour arXiv:2604.23037v2"
                ),
                "v2_status": "RESOLVED",
                "corrected_chronology": s15["chronology"],
            },
        ],
        "scope_hardening": "actual-incidence qualifier retained in integration",
        "global_status_change": False,
    }


def statement_scope() -> dict[str, object]:
    protocol = (
        CANDIDATE_DIR / "protocol-freeze.md"
    ).read_text(encoding="utf-8")
    audit = (CANDIDATE_DIR / "audit.md").read_text(encoding="utf-8")
    correction_ledger = (
        CANDIDATE_DIR / "correction-ledger.md"
    ).read_text(encoding="utf-8")
    required_protocol_fragments = [
        "h in {9,21,49,81,189,441,729,1029}",
        "M=7N^T P_-4 N",
        "r is primitive",
        "div(r)=1",
        "det(K_r)=2h",
        "rooted endpoint S-form:                             UNKNOWN",
        "rootless integrally indecomposable endpoint S-form: UNKNOWN",
        "novelty:                                           UNKNOWN",
    ]
    for fragment in required_protocol_fragments:
        if fragment not in protocol:
            raise AssertionError(f"missing protocol fragment: {fragment!r}")
    bounded_sentence = (
        "No exact prior result for either surviving endpoint branch was "
        "found in\n> the sources searched as of 2026-07-24."
    )
    if bounded_sentence not in audit:
        raise AssertionError("bounded no-hit sentence drifted")
    if "matrix/projector/Schur lane: no N, A, Gamma" not in audit:
        raise AssertionError("matrix/actual-incidence separation drifted")
    if (
        "rootless integrally decomposable actual-incidence endpoint:"
        not in correction_ledger
    ):
        raise AssertionError("corrected actual-incidence qualifier drifted")
    return {
        "actual_surviving_branches": [
            "rooted",
            "rootless_integrally_indecomposable",
        ],
        "actual_excluded_branch": "rootless_integrally_decomposable",
        "weaker_matrix_package_decomposable_branch": "not excluded by Wave 31 alone",
        "all_eight_h_retained": True,
        "automorphism_assumed": False,
        "h_729_assumed": False,
        "bounded_no_hit_only": True,
        "v1_scope_objection_preserved_and_resolved": True,
        "novelty": "UNKNOWN",
    }


def build_results() -> dict[str, object]:
    return {
        "schema_version": 2,
        "claim_label": "INDEPENDENT_CORRECTED_BYTE_REPLAY",
        "candidate_version": "v2_corrected",
        "frozen_candidate": verify_frozen_bytes(),
        "supporting_inputs": verify_supporting_bytes(),
        "candidate_manifest": verify_candidate_manifest(),
        "statement_scope": statement_scope(),
        "endpoint_arithmetic": endpoint_arithmetic(),
        "actual_incidence_spectrum": incidence_spectrum(),
        "query_accounting": query_accounting(),
        "source_accounting": source_accounting(),
        "source_quality": source_quality_findings(),
        "verdict": {
            "core_statement_boundary": "PASS",
            "actual_vs_matrix_separation": "PASS",
            "root_divisibility_index_determinant": "PASS",
            "petro_phillips_spectrum_and_hypotheses": "PASS",
            "modularity_wall": "PASS",
            "literature_search_accounting": "PASS",
            "metadata_quality": "PASS_CORRECTIONS_INTEGRATED",
            "current_status_language": "PASS_CONSERVATIVE",
            "exact_endpoint_prior_result": "NOT_FOUND_IN_SEARCHED_SOURCES",
            "novelty": "UNKNOWN",
            "global_conway_99": "UNKNOWN",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = canonical_bytes(build_results())
    if args.output:
        args.output.write_bytes(encoded)
    else:
        print(encoded.decode("utf-8"), end="")


if __name__ == "__main__":
    main()
