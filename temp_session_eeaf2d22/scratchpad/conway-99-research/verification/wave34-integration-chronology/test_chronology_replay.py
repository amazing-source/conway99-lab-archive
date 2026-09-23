from __future__ import annotations

import hashlib
import subprocess
import unittest

import chronology_replay as replay


class ChronologyProtocolTests(unittest.TestCase):
    def test_frozen_status_blob(self) -> None:
        payload = subprocess.run(
            ["git", "show", f"{replay.BASE_COMMIT}:STATUS.yaml"],
            cwd=replay.ROOT,
            check=True,
            capture_output=True,
        ).stdout
        self.assertEqual(hashlib.sha256(payload).hexdigest(), replay.FROZEN_STATUS_SHA256)

    def test_current_status_is_later_than_freeze(self) -> None:
        self.assertNotEqual(
            replay.sha256_path(replay.ROOT / "STATUS.yaml"),
            replay.FROZEN_STATUS_SHA256,
        )

    def test_integrated_status_hash_comes_from_requested_commit(self) -> None:
        integrated_commit = "0e11485de2ccdf0c1f2aa1c3e2d53a3413d9b6ea"
        integrated_hash = replay.git_blob_sha256(
            integrated_commit,
            "STATUS.yaml",
        )
        self.assertEqual(
            integrated_hash,
            "319dfbe6e38ed78726adc9a5ae7fe50a6a82a333506d299816559e1cd42510ba",
        )
        self.assertNotEqual(
            integrated_hash,
            replay.sha256_path(replay.ROOT / "STATUS.yaml"),
        )

    def test_pass_summary_requires_exact_test_count(self) -> None:
        summary = replay.parse_unittest_summary("Ran 11 tests in 1.000s\n\nOK\n")
        self.assertEqual(summary["tests_run"], 11)
        self.assertEqual(summary["status"], "PASS")

    def test_wrong_count_fails_summary(self) -> None:
        summary = replay.parse_unittest_summary("Ran 10 tests in 1.000s\n\nOK\n")
        self.assertEqual(summary["status"], "FAIL")

    def test_failed_suite_fails_summary(self) -> None:
        summary = replay.parse_unittest_summary(
            "Ran 11 tests in 1.000s\n\nFAILED (failures=1)\n"
        )
        self.assertEqual(summary["status"], "FAIL")

    def test_only_status_is_substituted_by_protocol(self) -> None:
        protocol = (replay.HERE / "protocol.md").read_text(encoding="utf-8")
        self.assertIn("replace that one file", protocol)
        self.assertIn("No verifier code", protocol)

    def test_published_command_is_portable(self) -> None:
        self.assertEqual(
            replay.PORTABLE_TEST_COMMAND,
            "python -B -m unittest discover "
            "-s verification/wave34-rooted-structural "
            "-p test_static_compare.py -v",
        )
        self.assertNotIn("\\", replay.PORTABLE_TEST_COMMAND)
        self.assertNotIn(":", replay.PORTABLE_TEST_COMMAND)


if __name__ == "__main__":
    unittest.main()
