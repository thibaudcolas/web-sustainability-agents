import json
import tempfile
import unittest
from pathlib import Path

from benchmarks.publish_expanded import JSON, execution_evidence, invokes_collector


class ScopeExecutionEvidenceTests(unittest.TestCase):
    def test_collector_execution_is_distinct_from_reading_its_source(self):
        self.assertTrue(invokes_collector({"cmd": "python3 /app/collect.py"}))
        self.assertTrue(
            invokes_collector(
                {
                    "input": 'text(await tools.exec_command({cmd:"python3 /app/collect.py"}));'
                }
            )
        )
        self.assertFalse(invokes_collector({"cmd": "cat /app/collect.py"}))
        self.assertFalse(
            invokes_collector(
                {
                    "input": 'text(await tools.exec_command({cmd:"cat /app/collect.py"}));'
                }
            )
        )
        self.assertFalse(invokes_collector(None))

    def test_native_contexts_and_returned_calls_are_allowlisted(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            sessions = directory / "agent/sessions"
            sessions.mkdir(parents=True)
            (sessions / "session.jsonl").write_text(
                json.dumps(
                    {
                        "type": "turn_context",
                        "payload": {
                            "model": "gpt-6.1-sol",
                            "effort": "high",
                            "privateField": "private-transcript-sentinel",
                        },
                    }
                )
                + "\n"
            )
            (directory / "agent/trajectory.json").write_text(
                json.dumps(
                    {
                        "steps": [
                            {
                                "step_id": 7,
                                "tool_calls": [
                                    {
                                        "tool_call_id": "call7",
                                        "function_name": "exec_command",
                                        "arguments": {"cmd": "python3 /app/collect.py"},
                                    }
                                ],
                                "observation": {
                                    "results": [
                                        {
                                            "source_call_id": "call7",
                                            "content": "private-transcript-sentinel",
                                        }
                                    ]
                                },
                            }
                        ]
                    }
                )
            )
            agent: JSON = {
                "model_name": "openai/gpt-6.1-sol",
                "kwargs": {"reasoning_effort": "high"},
            }
            evidence = execution_evidence(directory, agent)
            self.assertTrue(evidence["nativeSettingsMatchRequested"])
            self.assertTrue(
                evidence["collectorInvocations"][0]["returnedObservationPresent"]
            )
            self.assertNotIn("private-transcript-sentinel", json.dumps(evidence))
            agent["kwargs"]["reasoning_effort"] = "low"
            self.assertFalse(
                execution_evidence(directory, agent)["nativeSettingsMatchRequested"]
            )
