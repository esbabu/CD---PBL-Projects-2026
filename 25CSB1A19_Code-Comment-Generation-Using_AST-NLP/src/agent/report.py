class AgentReportBuilder:
    def build(self, ast_result, security_issues, quality_findings, plan,
              secure_alternative=None, malware_assessment=None, language="python"):
        critical = sum(i.get("severity") == "critical" for i in security_issues)
        high = sum(i.get("severity") == "high" for i in security_issues)
        medium = sum(i.get("severity") == "medium" for i in security_issues)
        low = sum(i.get("severity") == "low" for i in security_issues)
        score = max(0, 100 - 30 * critical - 15 * high - 5 * medium - low)
        risk = "LOW" if score >= 80 else "MEDIUM" if score >= 50 else "HIGH"
        malware_status = (malware_assessment or {}).get("status")
        if malware_status == "high_risk":
            risk = "HIGH"
        elif malware_status == "suspicious" and risk == "LOW":
            risk = "MEDIUM"
        return {
            "score": score, "risk": risk, "critical": critical, "high": high,
            "medium": medium, "low": low, "security_issues": security_issues,
            "quality_findings": quality_findings, "ast": ast_result, "plan": plan,
            "secure_alternative": secure_alternative or {"code": "", "changes": [], "limitations": []},
            "malware_assessment": malware_assessment or {}, "language": language,
        }

    def to_text(self, report):
        ast_data = report.get("ast", {})
        malware = report.get("malware_assessment", {})
        lines = [
            "AGENTIC SECURITY ANALYSIS", "=" * 62, "",
            f"Language      : {report.get('language', 'unknown')}",
            f"Parser mode   : {ast_data.get('parser', 'Python AST')}",
            f"Risk Level    : {report['risk']}",
            f"Security Score: {report['score']}/100 (severity-weighted heuristic)", "",
            "MALWARE BEHAVIOUR ASSESSMENT", "-" * 42,
            malware.get("headline", "MALWARE ASSESSMENT INCONCLUSIVE"),
            malware.get("summary", "No malware assessment was returned."),
        ]
        malware_findings = malware.get("findings", [])
        if malware_findings:
            lines.append("")
            for finding in malware_findings:
                line_start = finding.get("line", "?")
                line_end = finding.get("line_end", line_start)
                line_label = f"line {line_start}" if line_end == line_start else f"lines {line_start}-{line_end}"
                location = f"{finding.get('filename') or '<source>'}:{line_label}"
                lines += [
                    f"[{finding.get('severity', 'unknown').upper()}] {finding.get('id')} - {finding.get('title')}",
                    f"Location: {location}",
                    f"Function: {finding.get('function', 'source/module')}",
                    f"Evidence: {finding.get('evidence', '')}",
                    f"Finding: {finding.get('message', '')}",
                    f"Recommended action: {finding.get('fix', '')}", "",
                ]
        lines += ["", "SECURITY SUMMARY", "-" * 42,
                  f"Critical : {report['critical']}", f"High     : {report['high']}",
                  f"Medium   : {report['medium']}", f"Low      : {report['low']}", "",
                  "AGENT PLAN", "-" * 42]
        for n, step in enumerate(report["plan"], 1):
            lines.append(f"{n}. {step}")
        lines += ["", "SECURITY FINDINGS", "-" * 42]
        if not report["security_issues"]:
            lines.append("No local security issues detected by the configured rules.")
        else:
            for issue in report["security_issues"]:
                lines += [f"[{issue.get('severity', 'unknown').upper()}] {issue.get('id')} - Line {issue.get('line', '?')}",
                          f"Function: {issue.get('function', 'source/module')}",
                          f"Problem: {issue.get('message', '')}",
                          f"Fix: {issue.get('fix', '')}", ""]
        lines += ["CODE QUALITY FINDINGS", "-" * 42]
        if not report["quality_findings"]:
            lines.append("No additional quality findings or no detailed checks are configured for this language.")
        else:
            for finding in report["quality_findings"]:
                lines += [f"[{finding.get('severity', 'unknown').upper()}] {finding.get('id')} - Line {finding.get('line', '?')}",
                          f"Function: {finding.get('function', 'source/module')}",
                          f"Problem: {finding.get('message', '')}", ""]
        lines += ["AST / SOURCE SUMMARY", "-" * 42,
                  f"Functions : {len(ast_data.get('functions', []))}",
                  f"Classes   : {len(ast_data.get('classes', []))}",
                  f"Imports   : {len(ast_data.get('imports', []))}",
                  f"Calls     : {len(ast_data.get('calls', []))}",
                  f"Loops     : {ast_data.get('loops', 0)}",
                  f"Conditions: {ast_data.get('conditionals', 0)}"]
        alternative = report.get("secure_alternative", {})
        lines += ["", "RECOMMENDED SECURE ALTERNATIVE", "-" * 42]
        if alternative.get("code"):
            lines.append(alternative["code"])
        else:
            lines.append("No automatic source rewrite was produced for this language or finding set.")
        if alternative.get("changes"):
            lines += ["", "SECURE REWRITE CHANGES", "-" * 42]
            lines.extend(f"• {change}" for change in alternative["changes"])
        if alternative.get("limitations"):
            lines += ["", "MANUAL REVIEW REQUIRED", "-" * 42]
            lines.extend(f"• {item}" for item in alternative["limitations"])
        lines += ["", "NOTE", "-" * 42,
                  "Risk level may be escalated when high-risk malware-behaviour combinations are found; the numeric score remains a separate severity-weighted heuristic.",
                  "This is static source analysis, not proof of malware or proof that code is safe. Submitted code was not executed. Review and test all recommendations in a controlled environment."]
        return "\n".join(lines)
