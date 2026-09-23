from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_COMMIT = "0fa5b8161baf8b2a5404a67051b7d61cbc906da3"
FROZEN_STATUS_SHA256 = (
    "feda17934162602804015e17130c029ffdba7bf0307cdf234f4a7d8979298864"
)
TEST_PATH = "verification/wave34-rooted-structural"
TEST_PATTERN = "test_static_compare.py"
EXPECTED_TESTS = 11
PORTABLE_TEST_COMMAND = (
    "python -B -m unittest discover "
    "-s verification/wave34-rooted-structural "
    "-p test_static_compare.py -v"
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_checked(
    command: list[str],
    *,
    cwd: Path,
    capture_output: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=capture_output,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if result.returncode != 0:
        detail = (result.stdout or "") + (result.stderr or "")
        raise RuntimeError(
            f"command failed with exit {result.returncode}: {' '.join(command)}\n"
            f"{detail[-4000:]}"
        )
    return result


def git_text(args: list[str], *, cwd: Path = ROOT) -> str:
    return run_checked(["git", *args], cwd=cwd).stdout.strip()


def git_blob_sha256(commit: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or b"").decode("utf-8", errors="replace")
        raise RuntimeError(
            f"could not read {path} from {commit}: {detail[-2000:]}"
        )
    return sha256_bytes(result.stdout)


def export_commit(commit: str, destination: Path, archive_path: Path) -> None:
    run_checked(
        [
            "git",
            "archive",
            "--format=zip",
            f"--output={archive_path}",
            commit,
        ],
        cwd=ROOT,
    )
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)


def frozen_status_bytes(archive_path: Path, extraction_root: Path) -> bytes:
    run_checked(
        [
            "git",
            "archive",
            "--format=zip",
            f"--output={archive_path}",
            BASE_COMMIT,
            "STATUS.yaml",
        ],
        cwd=ROOT,
    )
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(extraction_root)
    payload = (extraction_root / "STATUS.yaml").read_bytes()
    if sha256_bytes(payload) != FROZEN_STATUS_SHA256:
        raise AssertionError("frozen STATUS.yaml blob hash mismatch")
    return payload


def parse_unittest_summary(output: str) -> dict[str, object]:
    matches = re.findall(r"Ran (\d+) tests? in [^\r\n]+", output)
    tests = int(matches[-1]) if matches else None
    passed = tests == EXPECTED_TESTS and bool(
        re.search(r"(?m)^OK(?:\s|\Z)", output)
    )
    return {
        "tests_run": tests,
        "expected_tests": EXPECTED_TESTS,
        "status": "PASS" if passed else "FAIL",
    }


def build_result(commit: str) -> dict[str, object]:
    resolved_commit = git_text(["rev-parse", f"{commit}^{{commit}}"])
    before_status = git_text(["status", "--porcelain=v1", "--untracked-files=all"])
    current_status_sha256 = git_blob_sha256(resolved_commit, "STATUS.yaml")

    with tempfile.TemporaryDirectory(prefix="conway-wave34-chronology-") as tmp:
        temp_root = Path(tmp)
        shadow = temp_root / "shadow"
        frozen = temp_root / "frozen"
        shadow.mkdir()
        frozen.mkdir()
        export_commit(resolved_commit, shadow, temp_root / "integrated.zip")
        if sha256_path(shadow / "STATUS.yaml") != current_status_sha256:
            raise AssertionError("integrated STATUS.yaml archive/hash drift")
        payload = frozen_status_bytes(temp_root / "status.zip", frozen)
        (shadow / "STATUS.yaml").write_bytes(payload)

        shadow_status_sha256 = sha256_path(shadow / "STATUS.yaml")
        if shadow_status_sha256 != FROZEN_STATUS_SHA256:
            raise AssertionError("isolated STATUS.yaml replacement drift")

        env = os.environ.copy()
        env["WAVE34_FULL_CENSUS"] = "1"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        command = [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            TEST_PATH,
            "-p",
            TEST_PATTERN,
            "-v",
        ]
        replay = subprocess.run(
            command,
            cwd=shadow,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        combined = (replay.stdout or "") + (replay.stderr or "")
        summary = parse_unittest_summary(combined)
        if replay.returncode != 0 or summary["status"] != "PASS":
            raise RuntimeError(
                "isolated structural replay failed\n" + combined[-4000:]
            )

    after_status = git_text(["status", "--porcelain=v1", "--untracked-files=all"])
    if after_status != before_status:
        raise AssertionError("source checkout status changed during replay")

    return {
        "schema_version": 1,
        "role": "verifier",
        "claim_label": "VERIFIED",
        "scope": "Wave 34 rooted structural historical-input replay only",
        "integrated_commit": resolved_commit,
        "frozen_status_commit": BASE_COMMIT,
        "current_status_sha256": current_status_sha256,
        "frozen_status_sha256": FROZEN_STATUS_SHA256,
        "current_status_differs_from_frozen": (
            current_status_sha256 != FROZEN_STATUS_SHA256
        ),
        "archive_method": "git archive; no local or hardlink clone reuse",
        "substituted_paths": ["STATUS.yaml"],
        "unchanged_verifier_path": (
            "verification/wave34-rooted-structural/static_compare.py"
        ),
        "command": PORTABLE_TEST_COMMAND,
        "full_census_enabled": True,
        "exit_code": replay.returncode,
        "tests_run": summary["tests_run"],
        "test_status": summary["status"],
        "source_checkout_status_unchanged": True,
        "rooted_binary_solution_status": "UNKNOWN",
        "rooted_exclusion_status": "UNKNOWN",
        "n3_708": "UNKNOWN",
        "conway_99": "UNKNOWN",
        "novelty": "UNKNOWN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay the Wave 34 rooted structural verifier at its frozen STATUS input."
    )
    parser.add_argument("--commit", default="HEAD")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build_result(args.commit)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_bytes(rendered.encode("utf-8"))
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
