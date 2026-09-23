from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any


KUBER_COMMIT = "be7b0ae3394721a4c3a1375008a1dbfca44981fc"
KUBER_TREE = "f37a1b03a96dc4be0dfab7156ed4408e37bffdb6"
KUBER_ZIP_SHA256 = "03a045788084e231a7a250157a667e42b77710d81c7fc74720da26200c06c606"
KUBER_ZIP_BYTES = 13185
COMMIT_JSON_SHA256 = "d4f3fd477120ca1b970e50d5fa6a5ea7afdd869d573500c18b2714446beaccfb"
COMMIT_JSON_BYTES = 4584
SELUB_SHA256 = "e533b92599e0f562e8ee63d5ca7e5ee5e2caaaa28de70fa6a73250cf333470f6"
SELUB_BYTES = 289879


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_file(path: Path, expected_bytes: int, expected_sha256: str) -> dict[str, Any]:
    size = path.stat().st_size
    digest = sha256(path)
    return {
        "path": str(path),
        "bytes": size,
        "sha256": digest,
        "bytes_match": size == expected_bytes,
        "sha256_match": digest == expected_sha256,
    }


def scan_lean_source(text: str) -> dict[str, Any]:
    prohibited = {
        "sorry": r"\bsorry\b",
        "admit": r"\badmit\b",
        "axiom_declaration": r"(?m)^\s*axiom\s+",
        "unsafe": r"\bunsafe\b",
        "native_decide": r"\bnative_decide\b",
        "native_eval": r"\bnative_eval\b",
        "implemented_by": r"\bimplemented_by\b",
        "run_tac": r"\brun_tac\b",
    }
    counts = {name: len(re.findall(pattern, text)) for name, pattern in prohibited.items()}
    packaged_body = re.search(
        r"theorem C3QuotientCertificate\.card_eq_six_or_twentySeven.*?"
        r"(?=\n#print axioms)",
        text,
        flags=re.DOTALL,
    )
    body = packaged_body.group(0) if packaged_body else ""
    return {
        "trust_sensitive_counts": counts,
        "has_simple_graph": "SimpleGraph" in text,
        "imports_formal_conjectures": "FormalConjectures" in text,
        "certificate_fields": re.findall(
            r"(?m)^\s{2}(B|triangularOrbits|quotientIdentity|regularity|diagonal|spectrum|triangle_congruence)\s*:",
            text,
        ),
        "packaged_endpoint_mentions_quotient_identity": "C.quotientIdentity" in body,
        "packaged_endpoint_mentions_regularity": "C.regularity" in body,
        "packaged_endpoint_mentions_diagonal": "C.diagonal" in body,
        "packaged_endpoint_mentions_spectrum": "C.spectrum" in body,
        "packaged_endpoint_mentions_triangle_congruence": "C.triangle_congruence" in body,
    }


def audit_kuber(zip_path: Path, commit_json_path: Path) -> dict[str, Any]:
    zip_check = check_file(zip_path, KUBER_ZIP_BYTES, KUBER_ZIP_SHA256)
    commit_check = check_file(commit_json_path, COMMIT_JSON_BYTES, COMMIT_JSON_SHA256)
    commit_data = json.loads(commit_json_path.read_text(encoding="utf-8"))
    expected_root = f"conway99-c3-orbit-restriction-{KUBER_COMMIT}/"
    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        basic_name = expected_root + "Conway99C3Orbits/Basic.lean"
        manifest_name = expected_root + "lake-manifest.json"
        toolchain_name = expected_root + "lean-toolchain"
        source = archive.read(basic_name).decode("utf-8")
        manifest = json.loads(archive.read(manifest_name).decode("utf-8"))
        toolchain = archive.read(toolchain_name).decode("utf-8").strip()
    pins = {package["name"]: package["rev"] for package in manifest["packages"]}
    return {
        "zip": zip_check,
        "commit_json": commit_check,
        "archive_root_matches": all(name.startswith(expected_root) for name in names),
        "commit_matches": commit_data.get("sha") == KUBER_COMMIT,
        "tree_matches": commit_data.get("commit", {}).get("tree", {}).get("sha") == KUBER_TREE,
        "toolchain": toolchain,
        "formal_conjectures_pin": pins.get("formal_conjectures"),
        "mathlib_pin": pins.get("mathlib"),
        "lean_scan": scan_lean_source(source),
    }


def audit_selub(pdf_path: Path) -> dict[str, Any]:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise SystemExit("pypdf is required for PDF inspection") from error

    file_check = check_file(pdf_path, SELUB_BYTES, SELUB_SHA256)
    reader = PdfReader(str(pdf_path))
    pages = [(page.extract_text() or "") for page in reader.pages]
    all_text = "\n".join(pages)
    normalized_text = " ".join(all_text.split())
    page4 = pages[3] if len(pages) >= 4 else ""
    normalized_page4 = " ".join(page4.split())
    page7 = pages[6] if len(pages) >= 7 else ""
    return {
        "file": file_check,
        "pages": len(pages),
        "title_present": "BOOLEAN SATISFIABILITY APPROACH" in all_text,
        "author_present": "NATHANIEL SELUB" in all_text,
        "reu_2023_present": "2023 University of Chicago REU" in normalized_text,
        "edge_variable_count_present": "4851" in all_text,
        "next_steps_present": "Next Steps" in all_text,
        "root_index_switch_present": "Let v1 be an arbitrary vertex" in all_text
        and "N(v0)" in all_text,
        "global_quadrilateral_disjunction_present": "For each Qi,j,E"
        in normalized_page4
        and "a,b,c,d distinct" in normalized_page4,
        "future_regularization_present": "current CNF encoding can be enhanced" in page7,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Re-audit temporary primary-source copies for the Wave 34 Kuber/Selub lane."
    )
    parser.add_argument("--kuber-zip", type=Path, required=True)
    parser.add_argument("--commit-json", type=Path, required=True)
    parser.add_argument("--selub-pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = {
        "kuber": audit_kuber(args.kuber_zip, args.commit_json),
        "selub": audit_selub(args.selub_pdf),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
