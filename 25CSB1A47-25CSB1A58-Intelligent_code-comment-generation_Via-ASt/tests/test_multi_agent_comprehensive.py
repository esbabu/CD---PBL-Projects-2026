"""Comprehensive test suite for Multi-Agent Security Lab and Remediation Agents."""

import unittest
from backend.app import app
from backend.validator import validate_code
from backend.security_attack_agent import simulate_attacks
from backend.security_fixing_agent import (
    fix_attack_vulnerabilities,
    _remediate_sql_injection,
    _remediate_command_injection,
    _remediate_hardcoded_secrets,
    _remediate_deserialization,
    _remediate_ssl_verification,
    _remediate_path_traversal,
    _remediate_insecure_hashing,
    _remediate_insecure_tempfiles,
    _remediate_insecure_xml,
    _remediate_exposed_debug,
    _remediate_redos,
    _remediate_ssrf,
)


class MultiAgentComprehensiveTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    # -------------------------------------------------------------
    # 1. INDIVIDUAL REMEDIATION TESTS
    # -------------------------------------------------------------
    def test_remediate_sql_injection(self):
        code = "def query(uid):\n    query = f\"SELECT * FROM users WHERE id = {uid}\"\n    cursor.execute(query)\n"
        fixed, fixes = _remediate_sql_injection(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("?", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_sql_injection_binds_all_values_for_non_cursor_receiver(self):
        code = (
            "def query(uid, name):\n"
            "    query = f\"SELECT * FROM users WHERE id = {uid} AND name = '{name}'\"\n"
            "    return db.execute(query)\n"
        )
        fixed, fixes = _remediate_sql_injection(code)

        self.assertIn("id = ? AND name = ?", fixed)
        self.assertIn("db.execute(query, (uid, name))", fixed)
        self.assertEqual(len(fixes), 1)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_command_injection_eval(self):
        code = "def calc(expr):\n    return eval(expr)\n"
        fixed, fixes = _remediate_command_injection(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("ast.literal_eval", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_command_injection_system(self):
        code = "import os\ndef ping(host):\n    os.system(f'ping {host}')\n"
        fixed, fixes = _remediate_command_injection(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("subprocess.run", fixed)
        self.assertIn("shell=False", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_hardcoded_secrets(self):
        code = "API_KEY = \"sk-12345abcdef\"\n"
        fixed, fixes = _remediate_hardcoded_secrets(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("os.getenv", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_deserialization_pickle(self):
        code = "import pickle\ndef load(data):\n    return pickle.loads(data)\n"
        fixed, fixes = _remediate_deserialization(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("json.loads", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_ssl_verification(self):
        code = "import requests\ndef fetch(url):\n    return requests.get(url, verify=False)\n"
        fixed, fixes = _remediate_ssl_verification(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("verify=True", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_path_traversal(self):
        code = "def read_file(name):\n    with open(f'/var/data/{name}') as f:\n        return f.read()\n"
        fixed, fixes = _remediate_path_traversal(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("basename", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_insecure_hashing(self):
        code = "import hashlib\ndef hash_pwd(pwd):\n    return hashlib.md5(pwd.encode()).hexdigest()\n"
        fixed, fixes = _remediate_insecure_hashing(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("sha256", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_insecure_tempfiles(self):
        code = "import tempfile\ndef get_temp():\n    return tempfile.mktemp()\n"
        fixed, fixes = _remediate_insecure_tempfiles(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("NamedTemporaryFile", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_insecure_xml(self):
        code = "import xml.etree.ElementTree as ET\ndef parse(data):\n    return ET.fromstring(data)\n"
        fixed, fixes = _remediate_insecure_xml(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("defusedxml", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_exposed_debug(self):
        code = "app.run(debug=True)\n"
        fixed, fixes = _remediate_exposed_debug(code)
        self.assertTrue(len(fixes) > 0)
        self.assertIn("debug=False", fixed)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_redos(self):
        code = "import re\npattern = re.compile(r'^(a+)+$')\n"
        fixed, fixes = _remediate_redos(code)
        self.assertTrue(len(fixes) > 0)
        self.assertEqual(validate_code(fixed), True)

    def test_remediate_ssrf(self):
        code = "import requests\ndef fetch(target_url):\n    return requests.get(target_url)\n"
        fixed, fixes = _remediate_ssrf(code)
        self.assertEqual(fixed, code)
        self.assertEqual(fixes, [])

    # -------------------------------------------------------------
    # 2. COMPOUND MULTI-VULNERABILITY REMEDIATION
    # -------------------------------------------------------------
    def test_compound_multi_vulnerability_remediation(self):
        source = (
            "import sqlite3\n"
            "import os\n"
            "import hashlib\n"
            "import tempfile\n\n"
            "def worker(user_id, cmd, text):\n"
            "    tmp = tempfile.mktemp()\n"
            "    digest = hashlib.md5(text.encode()).hexdigest()\n"
            "    query = f\"SELECT * FROM accounts WHERE id = {user_id}\"\n"
            "    os.system(cmd)\n"
        )
        sim_before = simulate_attacks(source)
        self.assertGreaterEqual(sim_before["vulnerabilities_detected"], 3)

        result = fix_attack_vulnerabilities(source)
        self.assertTrue(result["fixed"])
        self.assertEqual(result["remaining_vulnerabilities"], 0)
        self.assertGreaterEqual(result["neutralized_count"], 3)
        self.assertTrue(result["verification"]["syntax_valid"])
        self.assertTrue(result["verification"]["definitions_preserved"])

    # -------------------------------------------------------------
    # 3. /security/simulate-custom-attack API EDGE CASES
    # -------------------------------------------------------------
    def test_api_simulate_custom_attack_syntax_error(self):
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={"code": "def broken(:\n    pass\n", "payload": "' OR 1=1"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Syntax error", response.get_json()["error"])

    def test_api_simulate_custom_attack_oversized_code(self):
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={"code": "x = 1\n" * 15000, "payload": "test"},
        )
        self.assertEqual(response.status_code, 413)

    def test_api_simulate_custom_attack_matching_ssrf(self):
        code = "import requests\ndef fetch(url):\n    return requests.get(url)\n"
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={"code": code, "attack_type": "ssrf", "payload": "http://169.254.169.254/"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["detected"])
        self.assertEqual(data["cwe"], "CWE-918: Server-Side Request Forgery (SSRF)")

    def test_api_simulate_custom_attack_matching_redos(self):
        code = "import re\npattern = re.compile(r'^(a+)+$')\n"
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={"code": code, "attack_type": "redos", "payload": "^(a+)+$"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["detected"])
        self.assertIn("1333", data["cwe"])

    def test_api_simulate_custom_attack_matching_xxe(self):
        code = "import xml.etree.ElementTree as ET\ndef parse(d):\n    return ET.fromstring(d)\n"
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={"code": code, "attack_type": "xxe", "payload": "<!ENTITY xxe SYSTEM 'file:///etc/passwd'>"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["detected"])
        self.assertIn("611", data["cwe"])

    def test_api_simulate_custom_attack_matching_crypto_hash(self):
        code = "import hashlib\ndef h(p):\n    return hashlib.md5(p).hexdigest()\n"
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={"code": code, "attack_type": "hash", "payload": "hash_vector"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["detected"])
        self.assertIn("327", data["cwe"])

    def test_api_simulate_custom_attack_matching_tempfile(self):
        code = "import tempfile\ndef f():\n    return tempfile.mktemp()\n"
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={"code": code, "attack_type": "tempfile", "payload": "symlink_race"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["detected"])
        self.assertIn("377", data["cwe"])

    def test_api_simulate_custom_attack_matching_debug(self):
        code = "app.run(debug=True)\n"
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={"code": code, "attack_type": "debug", "payload": "console_rce"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["detected"])
        self.assertIn("215", data["cwe"])

    def test_api_simulate_custom_attack_pure_payload_xxe(self):
        response = self.client.post(
            "/security/simulate-custom-attack",
            json={"payload": "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>", "attack_type": "custom"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["detected"])
        self.assertIn("611", data["cwe"])


if __name__ == "__main__":
    unittest.main()
