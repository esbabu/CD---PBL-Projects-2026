import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import backend.app as app_module
from backend.agentic.runtime import AgentRuntime
from backend.agentic.session import SessionManager
from backend.multi_agent_orchestrator import run_multi_agent_workflow
from backend.optimization_agent import detect_optimization_opportunities, optimize_code
from backend.security_attack_agent import simulate_attacks
from backend.security_fixing_agent import fix_attack_vulnerabilities


def _run_agentic_workflow_without_provider(source_code, task, auto_approve=False):
    if auto_approve:
        raise AssertionError("Tests must review candidates before approving them.")
    runtime = AgentRuntime(session_manager=SessionManager(), model_client=None)
    session = runtime.start_session(source_code, task)
    result = runtime.execute_session(session.session_id)
    while result["status"] == "awaiting_approval":
        pending = session.pending_approval
        if not pending or not pending.get("diff"):
            raise AssertionError("A candidate must be reviewed before approval.")
        runtime.handle_user_action(
            session.session_id,
            "approve",
            "Test reviewed the staged candidate diff.",
            candidate_digest=pending["candidate_digest"],
        )
        result = runtime.execute_session(session.session_id)
    return result


class MultiAgentTests(unittest.TestCase):
    def setUp(self):
        self.client = app_module.app.test_client()

    # -------------------------------------------------------------
    # OPTIMIZATION AGENT TESTS
    # -------------------------------------------------------------
    def test_optimization_agent_detects_quadratic_sort(self):
        source = (
            "def bubble_sort(items):\n"
            "    arr = list(items)\n"
            "    n = len(arr)\n"
            "    for i in range(n):\n"
            "        for j in range(i + 1, n):\n"
            "            if arr[j] < arr[i]:\n"
            "                arr[i], arr[j] = arr[j], arr[i]\n"
            "    return arr\n"
        )
        opps = detect_optimization_opportunities(source)
        self.assertTrue(any(o["type"] == "algorithmic_sorting" for o in opps))

        result = optimize_code(source)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["complexity_before"], "O(n^2)")
        self.assertTrue(result["optimized"])
        self.assertIn("sorted", result["optimized_code"])
        self.assertTrue(result["verification"]["syntax_valid"])
        self.assertTrue(result["verification"]["definitions_preserved"])

    def test_optimization_agent_optimizes_example_duplicate_search_in_linear_time(self):
        source = (
            "def find_duplicates(numbers):\n"
            "    \"\"\"Suboptimal O(n^2) nested loop; can be optimized to O(n) with a set.\"\"\"\n"
            "    duplicates = []\n"
            "    for i in range(len(numbers)):\n"
            "        for j in range(i + 1, len(numbers)):\n"
            "            if numbers[i] == numbers[j] and numbers[i] not in duplicates:\n"
            "                duplicates.append(numbers[i])\n"
            "    return duplicates\n"
        )
        opportunities = detect_optimization_opportunities(source)
        duplicate_opportunity = next(
            item
            for item in opportunities
            if item["type"] == "quadratic_duplicate_search"
        )

        result = optimize_code(source, model_client=None)
        original_namespace = {}
        optimized_namespace = {}
        exec(compile(source, "<original>", "exec"), original_namespace)
        exec(
            compile(result["optimized_code"], "<optimized>", "exec"),
            optimized_namespace,
        )

        self.assertEqual(duplicate_opportunity["complexity_impact"], "O(n^2) -> O(n)")
        self.assertTrue(result["optimized"])
        self.assertEqual(result["complexity_before"], "O(n^2)")
        self.assertEqual(result["complexity_after"], "O(n)")
        self.assertTrue(result["verification"]["syntax_valid"])
        self.assertIn("seen = set()", result["optimized_code"])
        self.assertIn("AST optimization:", result["optimized_code"])
        for values in ([1, 2, 2, 1], [3, 5, 3, 5, 3], [], [4, 4, 4]):
            self.assertEqual(
                optimized_namespace["find_duplicates"](values),
                original_namespace["find_duplicates"](values),
            )

    def test_optimization_agent_rewrites_simple_string_concatenation_loop(self):
        source = (
            "def build(items):\n"
            "    result = ''\n"
            "    for item in items:\n"
            "        result += str(item)\n"
            "    return result\n"
        )
        result = optimize_code(source, model_client=None)
        optimized_namespace = {}
        exec(
            compile(result["optimized_code"], "<optimized>", "exec"),
            optimized_namespace,
        )

        self.assertTrue(result["optimized"])
        self.assertIn(".append(", result["optimized_code"])
        self.assertIn("''.join(", result["optimized_code"])
        self.assertIn("AST optimization:", result["optimized_code"])
        self.assertEqual(optimized_namespace["build"]([1, 2, 3]), "123")

    def test_optimization_agent_detects_eager_list_comp_in_sum(self):
        source = (
            "def calculate_total(items):\n"
            "    return sum([item['price'] for item in items if item['active']])\n"
        )
        opps = detect_optimization_opportunities(source)
        self.assertTrue(any(o["type"] == "generator_expression" for o in opps))

        result = optimize_code(source)
        self.assertTrue(result["optimized"])
        self.assertIn("sum(", result["optimized_code"])
        # Should not have [item inside sum([
        self.assertNotIn("sum([", result["optimized_code"])
        self.assertTrue(result["verification"]["syntax_valid"])

    def test_optimization_agent_detects_redundant_dict_keys(self):
        source = (
            "def iterate_records(data):\n"
            "    for key in data.keys():\n"
            "        print(key)\n"
        )
        opps = detect_optimization_opportunities(source)
        self.assertTrue(any(o["type"] == "redundant_dict_keys" for o in opps))

        result = optimize_code(source)
        self.assertTrue(result["optimized"])
        self.assertIn("for key in data:", result["optimized_code"])

    def test_optimization_agent_with_ai_model(self):
        source = "def add(a, b):\n    return a + b\n"
        candidate = "def add(a, b):\n    return a + b\n"

        fake_model = SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(
                    create=MagicMock(
                        return_value=SimpleNamespace(
                            choices=[
                                SimpleNamespace(
                                    message=SimpleNamespace(content=candidate)
                                )
                            ]
                        )
                    )
                )
            )
        )
        result = optimize_code(source, model_client=fake_model)
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["verification"]["syntax_valid"])

    # -------------------------------------------------------------
    # SECURITY ATTACK SIMULATION AGENT (RED TEAM) TESTS
    # -------------------------------------------------------------
    def test_attack_simulation_detects_sql_injection(self):
        source = (
            "import sqlite3\n"
            "def get_user(user_id):\n"
            "    conn = sqlite3.connect('users.db')\n"
            "    cursor = conn.cursor()\n"
            "    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n"
            "    cursor.execute(query)\n"
            "    return cursor.fetchone()\n"
        )
        sim = simulate_attacks(source)
        self.assertEqual(sim["status"], "completed")
        self.assertTrue(sim["is_vulnerable"])
        self.assertGreater(sim["vulnerabilities_detected"], 0)
        self.assertTrue(any("CWE-89" in s["cwe"] for s in sim["attack_scenarios"]))
        self.assertTrue(
            all(
                "not executed" in s["attack_payload"]
                for s in sim["attack_scenarios"]
            )
        )
        self.assertEqual(sim["execution_status"], "not_executed")
        self.assertLess(sim["resilience_score"], 100)

    def test_attack_simulation_detects_command_injection(self):
        source = (
            "import os\n"
            "def run_command(cmd):\n"
            "    return os.system(cmd)\n"
        )
        sim = simulate_attacks(source)
        self.assertTrue(sim["is_vulnerable"])
        self.assertTrue(any("CWE-78" in s["cwe"] for s in sim["attack_scenarios"]))
        self.assertGreater(sim["risk_breakdown"]["critical"], 0)

    def test_attack_simulation_detects_eval_execution(self):
        source = (
            "def eval_expression(expr):\n"
            "    return eval(expr)\n"
        )
        sim = simulate_attacks(source)
        self.assertTrue(sim["is_vulnerable"])
        self.assertTrue(any("CWE-94" in s["cwe"] or "CWE-78" in s["cwe"] for s in sim["attack_scenarios"]))

    def test_attack_simulation_detects_builtins_eval_aliases(self):
        source = (
            "from builtins import eval as evaluate\n"
            "def parse_expression(expression):\n"
            "    return evaluate(expression)\n"
        )
        sim = simulate_attacks(source)
        self.assertTrue(any("CWE-94" in item["cwe"] for item in sim["attack_scenarios"]))

        direct_source = (
            "import builtins\n"
            "def parse_expression(expression):\n"
            "    return builtins.eval(expression)\n"
        )
        direct = simulate_attacks(direct_source)
        self.assertTrue(any("CWE-94" in item["cwe"] for item in direct["attack_scenarios"]))

        safe_source = (
            "import ast\n"
            "def parse_expression(expression):\n"
            "    return ast.literal_eval(expression)\n"
        )
        safe = simulate_attacks(safe_source)
        self.assertFalse(any("CWE-94" in item["cwe"] for item in safe["attack_scenarios"]))

    def test_attack_simulation_tracks_augmented_sql_to_execute(self):
        source = (
            "def get_user(user_id):\n"
            "    query = 'SELECT * FROM users WHERE id = '\n"
            "    query += user_id\n"
            "    cursor.execute(query)\n"
        )
        sim = simulate_attacks(source)
        finding = next(
            item for item in sim["attack_scenarios"] if "CWE-89" in item["cwe"]
        )
        self.assertEqual(finding["target_line"], 3)
        self.assertEqual(finding["sink_line"], 4)
        self.assertEqual(finding["status"], "vulnerable")
        self.assertIn("ast.AugAssign", finding["ast_node_type"])
        self.assertEqual(finding["ast_sink_symbol"], "cursor.execute")

    def test_attack_simulation_does_not_flag_static_sql_append(self):
        source = (
            "def get_user(user_id):\n"
            "    query = 'SELECT * FROM users WHERE id = ?'\n"
            "    query += ' ORDER BY id'\n"
            "    cursor.execute(query, (user_id,))\n"
        )
        sim = simulate_attacks(source)
        self.assertFalse(any("CWE-89" in item["cwe"] for item in sim["attack_scenarios"]))

    def test_ssrf_detection_is_call_specific_and_does_not_trust_scheme_only(self):
        guarded_source = (
            "from urllib.parse import urlsplit\n"
            "import requests\n"
            "ALLOWED_HOSTS = {'api.example.com'}\n"
            "def fetch(target):\n"
            "    parsed = urlsplit(target)\n"
            "    if parsed.hostname not in ALLOWED_HOSTS:\n"
            "        raise ValueError('host not allowed')\n"
            "    return requests.get(target)\n"
            "def fetch_unchecked(target):\n"
            "    return requests.get(target)\n"
        )
        guarded = simulate_attacks(guarded_source)
        ssrf_findings = [
            item
            for item in guarded["attack_scenarios"]
            if "CWE-918" in item["cwe"]
        ]
        self.assertEqual(len(ssrf_findings), 2)
        guarded_finding = next(item for item in ssrf_findings if item["status"] == "needs_review")
        unguarded_finding = next(item for item in ssrf_findings if item["status"] == "vulnerable")
        self.assertEqual(guarded_finding["severity"], "medium")
        self.assertIn("DNS", guarded_finding["simulation_trace"])
        self.assertEqual(unguarded_finding["severity"], "high")

        scheme_only_source = (
            "import requests\n"
            "def fetch(target):\n"
            "    if not target.startswith(('http://', 'https://')):\n"
            "        raise ValueError('scheme not allowed')\n"
            "    return requests.get(target)\n"
        )
        scheme_only = simulate_attacks(scheme_only_source)
        ssrf = next(
            item
            for item in scheme_only["attack_scenarios"]
            if "CWE-918" in item["cwe"]
        )
        self.assertEqual(ssrf["status"], "vulnerable")

        safe_constant_source = (
            "import requests\n"
            "def fetch():\n"
            "    return requests.get('https://api.example.com/status')\n"
        )
        safe_constant = simulate_attacks(safe_constant_source)
        self.assertFalse(any("CWE-918" in item["cwe"] for item in safe_constant["attack_scenarios"]))

        private_constant_source = (
            "import requests\n"
            "def fetch():\n"
            "    return requests.get('http://127.0.0.1/admin')\n"
        )
        private_constant = simulate_attacks(private_constant_source)
        self.assertTrue(any("CWE-918" in item["cwe"] for item in private_constant["attack_scenarios"]))

    def test_attack_simulation_detects_hardcoded_secrets(self):
        source = (
            "API_TOKEN = 'secret-token-xyz-12345'\n"
            "def fetch():\n"
            "    return API_TOKEN\n"
        )
        sim = simulate_attacks(source)
        self.assertTrue(sim["is_vulnerable"])
        self.assertTrue(any("CWE-522" in s["cwe"] or "CWE-798" in s["cwe"] for s in sim["attack_scenarios"]))

    def test_attack_simulation_hardened_code(self):
        safe_source = (
            "def add(a, b):\n"
            "    return a + b\n"
        )
        sim = simulate_attacks(safe_source)
        self.assertEqual(sim["vulnerabilities_detected"], 0)
        self.assertFalse(sim["is_vulnerable"])
        self.assertEqual(sim["resilience_score"], 100)
        self.assertIn("not a security certification", sim["defense_verdict"])

    # -------------------------------------------------------------
    # SECURITY FIXING AGENT (BLUE TEAM) TESTS
    # -------------------------------------------------------------
    def test_security_fixing_agent_remediates_sql_injection(self):
        source = (
            "import sqlite3\n"
            "def get_user(user_id):\n"
            "    conn = sqlite3.connect('users.db')\n"
            "    cursor = conn.cursor()\n"
            "    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n"
            "    cursor.execute(query)\n"
            "    return cursor.fetchone()\n"
        )
        fixed = fix_attack_vulnerabilities(source)
        self.assertEqual(fixed["status"], "completed")
        self.assertTrue(fixed["fixed"])
        self.assertIn("?", fixed["fixed_code"])
        self.assertIn("(user_id,)", fixed["fixed_code"])
        self.assertTrue(fixed["verification"]["syntax_valid"])
        self.assertTrue(fixed["verification"]["definitions_preserved"])
        self.assertTrue(fixed["verification"]["all_attacks_neutralized"])
        self.assertEqual(fixed["post_fix_resilience_score"], 100)
        self.assertGreater(fixed["neutralized_count"], 0)

    def test_security_fixing_agent_remediates_eval(self):
        source = (
            "def parse_payload(payload):\n"
            "    return eval(payload)\n"
        )
        fixed = fix_attack_vulnerabilities(source)
        self.assertTrue(fixed["fixed"])
        self.assertIn("ast.literal_eval", fixed["fixed_code"])
        self.assertTrue(fixed["verification"]["syntax_valid"])
        self.assertTrue(fixed["verification"]["all_attacks_neutralized"])

    def test_security_fixing_agent_remediates_command_injection(self):
        source = (
            "import os\n"
            "def run_command(cmd):\n"
            "    return os.system(cmd)\n"
        )
        fixed = fix_attack_vulnerabilities(source)
        self.assertTrue(fixed["fixed"])
        self.assertIn("subprocess.run", fixed["fixed_code"])
        self.assertTrue(fixed["verification"]["syntax_valid"])

    def test_security_fixing_agent_remediates_secrets(self):
        source = (
            "API_TOKEN = 'sample-secret-token'\n"
            "def get_key():\n"
            "    return API_TOKEN\n"
        )
        fixed = fix_attack_vulnerabilities(source)
        self.assertTrue(fixed["fixed"])
        self.assertIn("os.getenv", fixed["fixed_code"])
        self.assertTrue(fixed["verification"]["syntax_valid"])

    def test_security_fixing_agent_on_safe_code(self):
        source = "def multiply(x, y):\n    return x * y\n"
        fixed = fix_attack_vulnerabilities(source)
        self.assertEqual(fixed["status"], "already_secure")
        self.assertFalse(fixed["fixed"])
        self.assertEqual(fixed["post_fix_resilience_score"], 100)

    def test_security_fixing_agent_remediates_path_traversal(self):
        source = (
            "import os\n"
            "def read_file(name):\n"
            "    path = os.path.join('/safe/dir', name)\n"
            "    with open(path, 'r') as f:\n"
            "        return f.read()\n"
        )
        fixed = fix_attack_vulnerabilities(source)
        self.assertTrue(fixed["fixed"])
        self.assertIn("os.path.basename", fixed["fixed_code"])
        self.assertEqual(fixed["post_fix_resilience_score"], 100)

    def test_security_fixing_agent_remediates_ssl_verification(self):
        source = (
            "import requests\n"
            "def fetch(url):\n"
            "    return requests.get('https://api.example.com/status', verify=False)\n"
        )
        fixed = fix_attack_vulnerabilities(source)
        self.assertTrue(fixed["fixed"])
        self.assertIn("verify=True", fixed["fixed_code"])
        self.assertEqual(fixed["post_fix_resilience_score"], 100)

    def test_optimization_agent_sort_complexity_transition(self):
        source = (
            "def bubble_sort(arr):\n"
            "    for i in range(len(arr)):\n"
            "        for j in range(len(arr) - 1):\n"
            "            if arr[j] > arr[j + 1]:\n"
            "                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n"
            "    return arr\n"
        )
        opt = optimize_code(source)
        self.assertTrue(opt["optimized"])
        self.assertEqual(opt["complexity_before"], "O(n^2)")
        self.assertEqual(opt["complexity_after"], "O(n log n)")


    # -------------------------------------------------------------
    # MULTI-AGENT COLLABORATIVE ORCHESTRATOR TESTS
    # -------------------------------------------------------------
    def test_multi_agent_workflow_full_pipeline(self):
        # Code containing both optimization opportunities and security vulnerabilities
        source = (
            "import sqlite3\n\n"
            "def query_users(user_id):\n"
            "    conn = sqlite3.connect('app.db')\n"
            "    cursor = conn.cursor()\n"
            "    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n"
            "    cursor.execute(query)\n"
            "    return cursor.fetchall()\n"
        )
        result = run_multi_agent_workflow(source)
        self.assertEqual(result["workflow"], "multi_agent_collaboration")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(result["timeline"]), 4)
        self.assertTrue(result["code_changed"])
        self.assertEqual(result["summary"]["final_resilience_score"], 100)
        self.assertEqual(result["summary"]["remaining_vulnerabilities"], 0)
        self.assertIn("optimizer", result["agents"])
        self.assertIn("attack_simulator", result["agents"])
        self.assertIn("security_fixer", result["agents"])

    # -------------------------------------------------------------
    # HTTP ENDPOINT INTEGRATION TESTS
    # -------------------------------------------------------------
    def test_api_agent_optimize_endpoint(self):
        source = (
            "def total(items):\n"
            "    return sum([x for x in items])\n"
        )
        response = self.client.post("/agent/optimize", json={"code": source})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["agent"], "code_optimizer")
        self.assertTrue(
            "sum(x for x in items)" in data["optimized_code"]
            or "sum((x for x in items))" in data["optimized_code"]
        )

    def test_api_agent_simulate_attacks_endpoint(self):
        source = (
            "import sqlite3\n"
            "def get_item(item_id):\n"
            "    query = f\"SELECT * FROM items WHERE id = {item_id}\"\n"
            "    cursor.execute(query)\n"
        )
        response = self.client.post("/agent/simulate-attacks", json={"code": source})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["agent"], "security_attack_simulation")
        self.assertTrue(data["is_vulnerable"])
        self.assertGreater(len(data["attack_scenarios"]), 0)

    def test_api_agent_fix_attacks_endpoint(self):
        source = (
            "import sqlite3\n"
            "def get_user(user_id):\n"
            "    conn = sqlite3.connect('users.db')\n"
            "    cursor = conn.cursor()\n"
            "    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n"
            "    cursor.execute(query)\n"
            "    return cursor.fetchone()\n"
        )
        response = self.client.post("/agent/fix-attacks", json={"code": source})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["agent"], "security_fixing_agent")
        self.assertTrue(data["fixed"])
        self.assertEqual(data["post_fix_resilience_score"], 100)

    def test_api_agent_multi_agent_workflow_endpoint(self):
        source = (
            "import sqlite3\n"
            "def get_user(user_id):\n"
            "    conn = sqlite3.connect('users.db')\n"
            "    cursor = conn.cursor()\n"
            "    query = f\"SELECT * FROM users WHERE id = {user_id}\"\n"
            "    cursor.execute(query)\n"
            "    return cursor.fetchone()\n"
        )
        with patch.object(app_module, "agentic_model_ready", return_value=True), patch.object(
            app_module,
            "run_agentic_workflow_sync",
            side_effect=_run_agentic_workflow_without_provider,
        ):
            response = self.client.post(
                "/agent/multi-agent-workflow", json={"code": source}
            )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["workflow"], "multi_agent_collaboration")
        self.assertEqual(data["status"], "completed")
        self.assertEqual(len(data["timeline"]), 4)

    def test_api_health_includes_new_agent_modules(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        modules = response.get_json()["modules"]
        self.assertIn("optimization_agent", modules)
        self.assertIn("security_attack_agent", modules)
        self.assertIn("security_fixing_agent", modules)
        self.assertIn("multi_agent_orchestrator", modules)


if __name__ == "__main__":
    unittest.main()
