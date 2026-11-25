from src.multilang.security import get_rule_count, get_security_rule_catalog, run_multilanguage_security_analysis


def test_catalog_has_more_than_600_distinct_rule_ids():
    catalog = get_security_rule_catalog()
    assert get_rule_count() >= 647
    assert len({item["id"] for item in catalog}) == len(catalog)


def test_each_rule_has_cwe_mapping_and_remediation():
    for item in get_security_rule_catalog():
        assert item["cwe"].startswith("CWE-")
        assert item["fix"].strip()
        assert item["category"].strip()


def test_command_injection_source_sink_pair_is_detected():
    findings = run_multilanguage_security_analysis("cmd = request.args.get('cmd'); os.system(cmd)", "python")
    assert any(item["cwe"] == "CWE-78" for item in findings)


def test_scanner_does_not_execute_source():
    findings = run_multilanguage_security_analysis("eval(user_input)", "python")
    assert isinstance(findings, list)
