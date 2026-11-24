import tempfile
import unittest
from pathlib import Path

from zen.sandbox import (
    REQUIRED_CONTROLS,
    CapabilityReport,
    SandboxExecutionError,
    SandboxPolicy,
    SandboxResult,
    SandboxRuntime,
    SandboxUnavailableError,
)
from zen.sandbox.contracts import SandboxOutputCollector


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

    def execute(self, request, policy, output):
        self.request = request
        output.write_stdout(b"ok")
        return SandboxResult(0)


class SandboxPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.policy = SandboxPolicy(
            self.root,
            allowed_environment=frozenset({"LANG", "LC_ALL"}),
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
        with self.assertRaises(SandboxUnavailableError):
            SandboxRuntime(self.policy).run(["echo"], cwd=self.root)

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
        self.assertIsNone(backend.request)

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
                ["echo"], cwd=self.root, environment={"HOME": "/tmp"}
            )
        self.assertIsNone(backend.request)

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
        self.assertEqual(backend.request.argv, ("echo", "ok; id"))

    def test_stdin_exact_limit_is_accepted(self):
        backend = FakeBackend()
        policy = SandboxPolicy(self.root, max_stdin_bytes=3)
        SandboxRuntime(policy, backend).run(
            ["echo"], cwd=self.root, stdin=b"123"
        )
        self.assertEqual(backend.request.stdin, b"123")

    def test_stdin_over_limit_rejected_before_backend(self):
        backend = FakeBackend()
        policy = SandboxPolicy(self.root, max_stdin_bytes=3)
        with self.assertRaises(ValueError):
            SandboxRuntime(policy, backend).run(
                ["echo"], cwd=self.root, stdin=b"1234"
            )
        self.assertIsNone(backend.request)

    def test_argv_count_limit(self):
        backend = FakeBackend()
        policy = SandboxPolicy(self.root, max_argv_count=2)
        with self.assertRaises(ValueError):
            SandboxRuntime(policy, backend).run(
                ["echo", "one", "two"], cwd=self.root
            )
        self.assertIsNone(backend.request)

    def test_argv_item_limit_uses_utf8_bytes(self):
        backend = FakeBackend()
        policy = SandboxPolicy(self.root, max_argv_item_bytes=3)
        with self.assertRaises(ValueError):
            SandboxRuntime(policy, backend).run(
                ["echo", "éé"], cwd=self.root
            )
        self.assertIsNone(backend.request)

    def test_argv_total_limit(self):
        backend = FakeBackend()
        policy = SandboxPolicy(
            self.root,
            max_argv_item_bytes=8,
            max_argv_total_bytes=5,
        )
        with self.assertRaises(ValueError):
            SandboxRuntime(policy, backend).run(
                ["echo", "abc"], cwd=self.root
            )
        self.assertIsNone(backend.request)

    def test_environment_count_limit(self):
        backend = FakeBackend()
        policy = SandboxPolicy(
            self.root,
            allowed_environment=frozenset({"LANG", "LC_ALL"}),
            max_environment_count=1,
        )
        with self.assertRaises(ValueError):
            SandboxRuntime(policy, backend).run(
                ["echo"],
                cwd=self.root,
                environment={"LANG": "C", "LC_ALL": "C"},
            )
        self.assertIsNone(backend.request)

    def test_environment_value_limit_uses_utf8_bytes(self):
        backend = FakeBackend()
        policy = SandboxPolicy(
            self.root,
            max_environment_value_bytes=3,
        )
        with self.assertRaises(ValueError):
            SandboxRuntime(policy, backend).run(
                ["echo"], cwd=self.root, environment={"LANG": "éé"}
            )
        self.assertIsNone(backend.request)

    def test_environment_total_limit_includes_key_and_value(self):
        backend = FakeBackend()
        policy = SandboxPolicy(
            self.root,
            max_environment_total_bytes=4,
        )
        with self.assertRaises(ValueError):
            SandboxRuntime(policy, backend).run(
                ["echo"], cwd=self.root, environment={"LANG": "C"}
            )
        self.assertIsNone(backend.request)

    def test_streamed_output_exact_limit_is_accepted_per_stream(self):
        class ExactBackend(FakeBackend):
            def execute(self, request, policy, output):
                output.write_stdout(b"x" * policy.max_output_bytes)
                output.write_stderr(b"y" * policy.max_output_bytes)
                return SandboxResult(0)

        result = SandboxRuntime(
            self.policy, ExactBackend()
        ).run(["echo"], cwd=self.root)
        self.assertEqual(len(result.stdout), self.policy.max_output_bytes)
        self.assertEqual(len(result.stderr), self.policy.max_output_bytes)

    def test_streamed_stdout_over_limit_is_rejected(self):
        class OversizedBackend(FakeBackend):
            def execute(self, request, policy, output):
                output.write_stdout(b"x" * (policy.max_output_bytes + 1))
                return SandboxResult(0)

        with self.assertRaises(SandboxExecutionError):
            SandboxRuntime(
                self.policy, OversizedBackend()
            ).run(["echo"], cwd=self.root)

    def test_streamed_stderr_over_limit_is_rejected(self):
        class OversizedBackend(FakeBackend):
            def execute(self, request, policy, output):
                output.write_stderr(b"x" * (policy.max_output_bytes + 1))
                return SandboxResult(0)

        with self.assertRaises(SandboxExecutionError):
            SandboxRuntime(
                self.policy, OversizedBackend()
            ).run(["echo"], cwd=self.root)

    def test_backend_cannot_bypass_streaming_collector(self):
        class BypassBackend(FakeBackend):
            def execute(self, request, policy, output):
                return SandboxResult(0, b"unbounded", b"")

        with self.assertRaises(SandboxExecutionError):
            SandboxRuntime(
                self.policy, BypassBackend()
            ).run(["echo"], cwd=self.root)

    def test_collector_rejects_non_bytes_chunks(self):
        output = SandboxOutputCollector(4)
        with self.assertRaises(SandboxExecutionError):
            output.write_stdout("not bytes")

    def test_invalid_policy_resource_limits_are_rejected(self):
        fields = (
            "max_output_bytes",
            "max_stdin_bytes",
            "max_argv_count",
            "max_argv_item_bytes",
            "max_argv_total_bytes",
            "max_environment_count",
            "max_environment_value_bytes",
            "max_environment_total_bytes",
        )
        for field in fields:
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    SandboxPolicy(self.root, **{field: 0})

    def test_boolean_policy_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            SandboxPolicy(self.root, max_stdin_bytes=True)


if __name__ == "__main__":
    unittest.main()
