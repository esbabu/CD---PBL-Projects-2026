"""Unit tests for the bounded multi-step ReAct loop in BaseAgent."""

import json
from types import SimpleNamespace
from typing import Any, List
import unittest

from backend.agentic.agents.specialists import ArchitectAgent
from backend.agentic.agents.base_agent import BaseAgent, extract_first_json_object
from backend.agentic.session import AgentSession
from backend.agentic.tools import create_standard_tool_registry


class FakeScriptedModelClient:
    """Hermetic, scripted fake model client for testing ReAct multi-step interactions."""

    def __init__(self, responses: List[str]) -> None:
        self.responses = list(responses)
        self.call_history: List[dict[str, Any]] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    @property
    def call_count(self) -> int:
        return len(self.call_history)

    def _create(self, **kwargs: Any) -> Any:
        self.call_history.append(kwargs)
        if not self.responses:
            raise RuntimeError("FakeScriptedModelClient ran out of scripted responses.")
        content = self.responses.pop(0)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content)
                )
            ]
        )


class BaseAgentReActLoopTests(unittest.TestCase):
    """Test suite for bounded ReAct loop, JSON repair, self-correction, and event sequences."""

    SAMPLE_CODE = (
        "def calculate_total(items):\n"
        "    total = 0\n"
        "    for item in items:\n"
        "        total += item\n"
        "    return total\n"
    )

    def setUp(self) -> None:
        self.tools = create_standard_tool_registry()
        self.events: List[tuple[str, dict[str, Any]]] = []
        self.session_id = "test-react-session"
        self.session = AgentSession(
            session_id=self.session_id,
            original_code=self.SAMPLE_CODE,
            original_code_digest="abc123digest",
            current_code=self.SAMPLE_CODE,
            task="Analyze AST topology and check type safety",
            event_callback=lambda event, data: self.events.append((event, data)),
        )

    def _filter_events(self, *event_names: str) -> List[tuple[str, dict[str, Any]]]:
        return [
            (event, data)
            for event, data in self.events
            if not event_names or event in event_names
        ]

    def test_json_repair_extracts_balanced_json_from_markdown_and_prose(self) -> None:
        """Verify extract_first_json_object handles prose, code fences, and braces in strings."""
        # Clean JSON
        res1 = extract_first_json_object('{"action": "finish"}')
        self.assertEqual(res1, {"action": "finish"})

        # Markdown fenced
        fenced = (
            "Here is the plan:\n"
            "```json\n"
            '{"action": "tool", "tool": "inspect_ast_structure", "arguments": {}}\n'
            "```\n"
            "End of plan."
        )
        res2 = extract_first_json_object(fenced)
        self.assertEqual(
            res2,
            {"action": "tool", "tool": "inspect_ast_structure", "arguments": {}},
        )

        # Braces inside string literal arguments
        with_code = (
            'I decided to call search:\n'
            '{"action": "tool", "tool": "search_project_code", '
            '"arguments": {"pattern": "def foo(): { pass }"}}\n'
            'Done.'
        )
        res3 = extract_first_json_object(with_code)
        self.assertEqual(res3["arguments"]["pattern"], "def foo(): { pass }")

        # Invalid JSON returns None
        self.assertIsNone(extract_first_json_object("I am a model! {invalid json"))

    def test_react_loop_calls_two_tools_then_finishes(self) -> None:
        """Requirement (a): Fake client calls two tools in sequence then finishes."""
        fake_client = FakeScriptedModelClient([
            json.dumps({"action": "tool", "tool": "inspect_ast_structure", "arguments": {}}),
            json.dumps({"action": "tool", "tool": "infer_type_errors", "arguments": {}}),
            json.dumps({"action": "finish"}),
        ])
        agent = ArchitectAgent(tools=self.tools, model_client=fake_client)

        result = agent.execute_turn(self.session, sub_task="Analyze architecture", task_id="T1")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["execution_mode"], "model")
        self.assertEqual(len(result["tool_observations"]), 2)
        self.assertEqual(fake_client.call_count, 3)

        # Assert exact sequence of step and tool events
        step_events = self._filter_events(
            "step_started", "tool_started", "tool_completed", "step_finished"
        )
        expected_sequence = [
            ("step_started", 1),
            ("tool_started", 1),
            ("tool_completed", 1),
            ("step_finished", 1),
            ("step_started", 2),
            ("tool_started", 2),
            ("tool_completed", 2),
            ("step_finished", 2),
            ("step_started", 3),
            ("step_finished", 3),
        ]
        actual_sequence = [
            (event, data.get("step"))
            for event, data in step_events
        ]
        self.assertEqual(actual_sequence, expected_sequence)

        # Verify scratchpad was passed in steps 2 and 3
        step2_messages = fake_client.call_history[1]["messages"]
        step2_user_content = step2_messages[-1]["content"]
        self.assertIn("ReAct Scratchpad", step2_user_content)
        self.assertIn("inspect_ast_structure", step2_user_content)

        step3_messages = fake_client.call_history[2]["messages"]
        step3_user_content = step3_messages[-1]["content"]
        self.assertIn("inspect_ast_structure", step3_user_content)
        self.assertIn("infer_type_errors", step3_user_content)

    def test_react_loop_invalid_json_retries_once_then_succeeds(self) -> None:
        """Requirement (b): Model returns invalid JSON once then valid JSON on retry prompt."""
        fake_client = FakeScriptedModelClient([
            "I will now inspect the AST: ```json {invalid: json",  # Bad JSON
            json.dumps({"action": "tool", "tool": "inspect_ast_structure", "arguments": {}}),  # Retry success
            json.dumps({"action": "finish"}),
        ])
        agent = ArchitectAgent(tools=self.tools, model_client=fake_client)

        result = agent.execute_turn(self.session, sub_task="Analyze architecture", task_id="T1")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["execution_mode"], "model")
        self.assertEqual(len(result["tool_observations"]), 1)
        self.assertEqual(fake_client.call_count, 3)

        # Verify retry prompt was sent
        retry_call = fake_client.call_history[1]
        retry_messages = retry_call["messages"]
        self.assertEqual(retry_messages[-1]["role"], "user")
        self.assertIn("Return only valid JSON", retry_messages[-1]["content"])

    def test_react_loop_detects_repeated_identical_call_and_stops(self) -> None:
        """Requirement (c): Detect repeated identical tool call and stop loop with clear message."""
        fake_client = FakeScriptedModelClient([
            json.dumps({"action": "tool", "tool": "inspect_ast_structure", "arguments": {}}),
            json.dumps({"action": "tool", "tool": "inspect_ast_structure", "arguments": {}}),  # Duplicate
        ])
        agent = ArchitectAgent(tools=self.tools, model_client=fake_client)

        result = agent.execute_turn(self.session, sub_task="Analyze architecture", task_id="T1")

        self.assertEqual(result["status"], "completed")
        self.assertIn("Repeated identical tool call detected", result["summary"])
        # Tool was executed only once
        self.assertEqual(len(result["tool_observations"]), 1)

        # Check event status for the stopped step
        step_finished_events = [d for e, d in self.events if e == "step_finished"]
        self.assertEqual(step_finished_events[-1]["status"], "loop_stopped")

    def test_react_loop_refuses_disallowed_tool_and_falls_back_after_consecutive(self) -> None:
        """Requirement (d): Refuse disallowed tool once; after 2 consecutive, fallback to deterministic."""
        fake_client = FakeScriptedModelClient([
            json.dumps({"action": "tool", "tool": "propose_file_patch", "arguments": {}}),  # 1st disallowed
            json.dumps({"action": "tool", "tool": "propose_file_patch", "arguments": {}}),  # 2nd disallowed
        ])
        agent = ArchitectAgent(tools=self.tools, model_client=fake_client)

        result = agent.execute_turn(self.session, sub_task="Analyze architecture", task_id="T1")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["execution_mode"], "deterministic_fallback")
        self.assertEqual(result["fallback_reason"], "disallowed_tool")

        # Step 1 was rejected and recorded as observation
        step_finished_events = [d for e, d in self.events if e == "step_finished"]
        self.assertEqual(step_finished_events[0]["status"], "rejected")
        self.assertEqual(step_finished_events[0]["step"], 1)

        # Fallback event was emitted on step 2
        fallback_events = [d for e, d in self.events if e == "fallback_to_deterministic"]
        self.assertEqual(len(fallback_events), 1)
        self.assertEqual(fallback_events[0]["reason"], "disallowed_tool")
        self.assertEqual(fallback_events[0]["step"], 2)

    def test_react_loop_self_corrects_after_first_disallowed_tool(self) -> None:
        """Model requests disallowed tool in step 1, receives refusal observation, and self-corrects in step 2."""
        fake_client = FakeScriptedModelClient([
            json.dumps({"action": "tool", "tool": "propose_file_patch", "arguments": {}}),  # Refused
            json.dumps({"action": "tool", "tool": "inspect_ast_structure", "arguments": {}}),  # Self-corrected!
            json.dumps({"action": "finish"}),
        ])
        agent = ArchitectAgent(tools=self.tools, model_client=fake_client)

        result = agent.execute_turn(self.session, sub_task="Analyze architecture", task_id="T1")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["execution_mode"], "model")
        self.assertEqual(len(result["tool_observations"]), 1)
        self.assertEqual(fake_client.call_count, 3)

        # Step 2 prompt should contain the rejection observation
        step2_messages = fake_client.call_history[1]["messages"]
        step2_user_content = step2_messages[-1]["content"]
        self.assertIn("Tool 'propose_file_patch' is not allowed", step2_user_content)

    def test_react_loop_invalid_arguments_schema_fallback(self) -> None:
        """Model sends arguments failing tool schema twice; falls back with invalid_tool_arguments."""
        fake_client = FakeScriptedModelClient([
            json.dumps({"action": "tool", "tool": "find_symbol", "arguments": {}}),  # Missing required 'name'
            json.dumps({"action": "tool", "tool": "find_symbol", "arguments": {"name": 123}}),  # Wrong type
        ])
        agent = ArchitectAgent(tools=self.tools, model_client=fake_client)

        result = agent.execute_turn(self.session, sub_task="Find symbol in code", task_id="T1")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["execution_mode"], "deterministic_fallback")
        self.assertEqual(result["fallback_reason"], "invalid_tool_arguments")

        fallback_events = [d for e, d in self.events if e == "fallback_to_deterministic"]
        self.assertEqual(len(fallback_events), 1)
        self.assertEqual(fallback_events[0]["reason"], "invalid_tool_arguments")

    def test_react_loop_configurable_max_steps_and_tokens(self) -> None:
        """Verify configurable max_steps and max_tokens (default 1500)."""
        fake_client = FakeScriptedModelClient([
            json.dumps({"action": "tool", "tool": "inspect_ast_structure", "arguments": {}}),
            json.dumps({"action": "tool", "tool": "inspect_undefined_names", "arguments": {}}),
        ])
        agent = BaseAgent(
            name="CUSTOM_AGENT",
            role_description="Custom test agent",
            system_prompt="Analyze code",
            tools=self.tools,
            model_client=fake_client,
            max_steps=2,
            max_tokens=2048,
        )

        result = agent.execute_turn(self.session, sub_task="Custom analysis", task_id="T1")

        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["execution_mode"], "model")
        self.assertIn("Reached step limit: 2", result["summary"])
        self.assertEqual(fake_client.call_history[0]["max_tokens"], 2048)


if __name__ == "__main__":
    unittest.main()
