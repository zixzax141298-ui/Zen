import tempfile
import unittest
from pathlib import Path

from zen.sandbox import (
    REQUIRED_CONTROLS,
    CapabilityReport,
    SandboxPolicy,
    SandboxResult,
    SandboxRuntime,
    SandboxUnavailableError,
)


class FakeBackend:
    def __init__(
        self,
        controls=REQUIRED_CONTROLS,
        evidence="test-only fake backend",
    ):
        self.controls = frozenset(controls)
        self.evidence = evidence
        self.request = None

    def probe(self, policy):
        return CapabilityReport(self.controls, self.evidence)

    def execute(self, request, policy):
        self.request = request
        return SandboxResult(0, b"ok", b"")


class SandboxPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.policy = SandboxPolicy(
            self.root,
            allowed_environment=frozenset({"LANG"}),
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_network_is_rejected_by_policy(self):
        with self.assertRaises(ValueError):
            SandboxPolicy(self.root, network_enabled=True)

    def test_path_must_remain_inside_workspace(self):
        self.assertTrue(self.policy.contains_path(self.root))
        self.assertFalse(self.policy.contains_path(self.root.parent))

    def test_missing_backend_fails_closed(self):
        runtime = SandboxRuntime(self.policy)
        with self.assertRaises(SandboxUnavailableError):
            runtime.run(["echo", "unsafe"], cwd=self.root)

    def test_missing_isolation_capability_fails_closed(self):
        backend = FakeBackend(
            REQUIRED_CONTROLS - {"network_isolation"}
        )
        with self.assertRaises(SandboxUnavailableError):
            SandboxRuntime(self.policy, backend).run(
                ["echo"], cwd=self.root
            )
        self.assertIsNone(backend.request)

    def test_empty_backend_evidence_fails_closed(self):
        backend = FakeBackend(evidence=" ")
        with self.assertRaises(SandboxUnavailableError):
            SandboxRuntime(self.policy, backend).run(
                ["echo"], cwd=self.root
            )

    def test_sensitive_environment_is_rejected(self):
        backend = FakeBackend()
        with self.assertRaises(ValueError):
            SandboxRuntime(self.policy, backend).run(
                ["echo"],
                cwd=self.root,
                environment={"GITHUB_TOKEN": "not-a-real-token"},
            )
        self.assertIsNone(backend.request)

    def test_non_allowlisted_environment_is_rejected(self):
        backend = FakeBackend()
        with self.assertRaises(ValueError):
            SandboxRuntime(self.policy, backend).run(
                ["echo"],
                cwd=self.root,
                environment={"HOME": "/tmp"},
            )

    def test_only_allowlisted_environment_reaches_backend(self):
        backend = FakeBackend()
        result = SandboxRuntime(self.policy, backend).run(
            ["echo", "ok"],
            cwd=self.root,
            environment={"LANG": "C"},
        )
        self.assertEqual(result.stdout, b"ok")
        self.assertEqual(backend.request.environment, {"LANG": "C"})

    def test_working_directory_outside_workspace_is_rejected(self):
        backend = FakeBackend()
        with self.assertRaises(ValueError):
            SandboxRuntime(self.policy, backend).run(
                ["echo"], cwd=self.root.parent
            )
        self.assertIsNone(backend.request)

    def test_shell_command_string_is_rejected(self):
        backend = FakeBackend()
        with self.assertRaises(ValueError):
            SandboxRuntime(self.policy, backend).run(
                "echo ok; id", cwd=self.root
            )
        self.assertIsNone(backend.request)

    def test_argument_vector_is_forwarded_without_shell_interpretation(self):
        backend = FakeBackend()
        SandboxRuntime(self.policy, backend).run(
            ["echo", "ok; id"], cwd=self.root
        )
        self.assertEqual(
            backend.request.argv,
            ("echo", "ok; id"),
        )

    def test_output_limit_is_checked(self):
        class OversizedBackend(FakeBackend):
            def execute(self, request, policy):
                return SandboxResult(
                    0,
                    b"x" * (policy.max_output_bytes + 1),
                    b"",
                )

        with self.assertRaises(Exception):
            SandboxRuntime(
                self.policy,
                OversizedBackend(),
            ).run(["echo"], cwd=self.root)


if __name__ == "__main__":
    unittest.main()
